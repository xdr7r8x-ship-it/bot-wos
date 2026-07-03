"""
Dream Memory Ollama Overlay - Vision Analyzer
Uses Ollama (Local AI) for object detection - No API, No limits!
"""

import json
import sys
import base64
import io
from datetime import datetime
import requests

from config import MODEL, FALLBACK_MODEL, VISION_PROMPT, MAX_REQUESTS, CONFIDENCE_MIN, OLLAMA_HOST, ANALYSIS_TIMEOUT_SECONDS


class VisionAnalyzer:
    """Analyzes game screen using Ollama Local AI."""

    def __init__(self, host: str = OLLAMA_HOST):
        self.host = host
        self.model = MODEL
        self.fallback_model = FALLBACK_MODEL
        self._check_connection()

    def _check_connection(self):
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"[OLLAMA] Connected! Models: {len(models)}")
                
                # Check for vision models
                has_llava = any("llava" in m.get("name", "").lower() for m in models)
                has_vision = any("vision" in m.get("name", "").lower() for m in models)
                
                if has_vision:
                    self.model = self.fallback_model
                    print(f"[OLLAMA] Using: {self.fallback_model}")
                elif has_llava:
                    self.model = MODEL
                    print(f"[OLLAMA] Using: {MODEL}")
                else:
                    print(f"[OLLAMA] No vision model found! Install with: ollama pull llava:7b")
            else:
                print(f"[OLLAMA] Connection error: {response.status_code}")
        except Exception as e:
            print(f"[OLLAMA] Not connected: {e}")
            print(f"[OLLAMA] Install Ollama from: https://ollama.com")

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=3)
            return response.status_code == 200
        except:
            return False

    def analyze_screen(
        self,
        request_bar_base64: str,
        scene_base64: str
    ) -> dict:
        """
        Analyze the screen using Ollama local AI.
        
        Returns:
            dict with structure:
            {
                "wave_id": "string",
                "requests": ["item1", "item2", ...],
                "marks": [
                    {
                        "label": "item1",
                        "bbox": {"x1": 0, "y1": 0, "x2": 1000, "y2": 1000},
                        "confidence": 87
                    },
                    ...
                ]
            }
        """
        try:
            # Prepare images as base64 data URIs
            req_bar_uri = f"data:image/jpeg;base64,{request_bar_base64}"
            scene_uri = f"data:image/jpeg;base64,{scene_base64}"

            # Build prompt with images
            prompt = VISION_PROMPT

            # Ollama API request
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [req_bar_uri, scene_uri],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1024
                }
            }

            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=ANALYSIS_TIMEOUT_SECONDS
            )

            if response.status_code != 200:
                return {"wave_id": "", "requests": [], "marks": [], "error": f"Ollama error: {response.status_code}"}

            result = response.json()
            content = result.get("response", "")

            # Parse JSON response
            parsed = self._parse_response(content)
            
            # Validate and filter
            parsed = self._validate_results(parsed)
            
            return parsed

        except requests.exceptions.Timeout:
            return {"wave_id": "", "requests": [], "marks": [], "error": "Timeout - Ollama too slow"}
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            print(f"[ANALYZER] Error ({error_type}): {error_msg}", file=sys.stderr)
            return {"wave_id": "", "requests": [], "marks": [], "error": f"{error_type}: {error_msg}"}

    def _parse_response(self, content: str) -> dict:
        """Parse JSON from Ollama response."""
        try:
            # Clean the content
            content = content.strip()

            # Handle markdown code blocks
            if "```" in content:
                lines = content.split("\n")
                cleaned = []
                in_code = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_code = not in_code
                        continue
                    if not in_code and line.strip():
                        cleaned.append(line)
                content = "\n".join(cleaned)

            # Try to find JSON
            start = content.find("{")
            end = content.rfind("}") + 1
            
            if start >= 0 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
            else:
                data = json.loads(content)

            # Ensure required fields
            if "marks" not in data:
                data["marks"] = []
            if "requests" not in data:
                data["requests"] = []
            if "wave_id" not in data:
                data["wave_id"] = datetime.now().isoformat()

            return data

        except Exception as e:
            print(f"[ANALYZER] JSON parse error: {e}", file=sys.stderr)
            return {"wave_id": "", "marks": [], "requests": [], "error": f"Parse error: {e}"}

    def _validate_results(self, result: dict) -> dict:
        """Validate and filter analysis results."""
        validated_marks = []

        for mark in result.get("marks", []):
            if "label" not in mark:
                continue

            bbox = mark.get("bbox", {})
            x1 = max(0, min(1000, bbox.get("x1", 0)))
            y1 = max(0, min(1000, bbox.get("y1", 0)))
            x2 = max(0, min(1000, bbox.get("x2", 500)))
            y2 = max(0, min(1000, bbox.get("y2", 500)))

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            confidence = mark.get("confidence", 50)
            if confidence < CONFIDENCE_MIN:
                continue

            validated_marks.append({
                "label": str(mark["label"])[:20],
                "x": cx,
                "y": cy,
                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                "confidence": confidence
            })

        # Sort by confidence and limit
        validated_marks.sort(key=lambda m: m["confidence"], reverse=True)
        validated_marks = validated_marks[:MAX_REQUESTS]

        return {
            "wave_id": result.get("wave_id", ""),
            "requests": result.get("requests", [])[:MAX_REQUESTS],
            "marks": validated_marks
        }
