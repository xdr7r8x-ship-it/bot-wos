"""
Dream Memory Ollama Overlay - Vision Analyzer
Uses Ollama Qwen2.5-VL for object detection - No API, No limits!
"""

import json
import sys
from datetime import datetime
import requests

from config import (
    OLLAMA_HOST, 
    OLLAMA_URL, 
    OLLAMA_MODEL, 
    OLLAMA_STRONG_MODEL,
    VISION_PROMPT, 
    MAX_REQUESTS, 
    CONFIDENCE_MIN, 
    ANALYSIS_TIMEOUT_SECONDS
)


class VisionAnalyzer:
    """Analyzes game screen using Ollama Qwen2.5-VL Local AI."""

    def __init__(self):
        self.host = OLLAMA_HOST
        self.url = OLLAMA_URL
        self.model = OLLAMA_MODEL
        self.available = False
        self.model_installed = False
        self._check_ollama()

    def _check_ollama(self):
        """Check if Ollama server is running and model is installed."""
        try:
            # Check server
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                self.available = True
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                # Check for qwen2.5vl
                has_fast = any(OLLAMA_MODEL in name for name in model_names)
                has_strong = any(OLLAMA_STRONG_MODEL in name for name in model_names)
                
                if has_fast:
                    self.model = OLLAMA_MODEL
                    self.model_installed = True
                    print(f"[OLLAMA] ✓ Model found: {self.model}")
                elif has_strong:
                    self.model = OLLAMA_STRONG_MODEL
                    self.model_installed = True
                    print(f"[OLLAMA] ✓ Model found: {self.model}")
                else:
                    self.model_installed = False
                    print(f"[OLLAMA] ✗ Model not found!")
                    print(f"[OLLAMA] Run: ollama pull {OLLAMA_MODEL}")
            else:
                self.available = False
                print(f"[OLLAMA] ✗ Server error: {response.status_code}")
        except Exception as e:
            self.available = False
            print(f"[OLLAMA] ✗ Not running!")
            print(f"[OLLAMA] Install from: https://ollama.com")

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        return self.available

    def is_model_installed(self) -> bool:
        """Check if model is installed."""
        return self.model_installed

    def analyze_screen(
        self,
        request_bar_base64: str,
        scene_base64: str
    ) -> dict:
        """
        Analyze the screen using Ollama Qwen2.5-VL.
        
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
            if not self.available:
                return {"wave_id": "", "requests": [], "marks": [], "error": "Ollama not running"}
            
            if not self.model_installed:
                return {"wave_id": "", "requests": [], "marks": [], "error": f"Model not installed: {self.model}"}

            # Qwen2.5-VL API request with images as base64
            payload = {
                "model": self.model,
                "prompt": VISION_PROMPT,
                "images": [request_bar_base64, scene_base64],  # Raw base64 strings
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1024
                }
            }

            response = requests.post(
                self.url,
                json=payload,
                timeout=ANALYSIS_TIMEOUT_SECONDS
            )

            if response.status_code != 200:
                return {"wave_id": "", "requests": [], "marks": [], "error": f"Ollama error: {response.status_code}"}

            result = response.json()
            
            # Get response text
            content = result.get("response", "")
            
            # Parse JSON response
            parsed = self._parse_response(content)
            
            # Validate and filter
            parsed = self._validate_results(parsed)
            
            return parsed

        except requests.exceptions.Timeout:
            return {"wave_id": "", "requests": [], "marks": [], "error": "Timeout - model too slow"}
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            return {"wave_id": "", "requests": [], "marks": [], "error": f"{error_type}: {error_msg}"}

    def _parse_response(self, content: str) -> dict:
        """Parse JSON from Ollama response."""
        try:
            # Clean the content
            content = content.strip()
            
            # Remove markdown code fences
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:].strip()
            
            # Find JSON boundaries
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
            return {"wave_id": "", "marks": [], "requests": [], "error": f"Parse error: {e}"}

    def _validate_results(self, result: dict) -> dict:
        """Validate and filter analysis results."""
        validated_marks = []

        for mark in result.get("marks", []):
            # Discard invalid marks only
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
