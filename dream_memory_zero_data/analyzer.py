"""
Dream Memory Zero-Data Overlay - Vision Analyzer
Uses Google Gemini API for object detection.
"""

import json
import sys
from datetime import datetime

from google import genai

from config import MODEL, VISION_PROMPT, MAX_REQUESTS, CONFIDENCE_MIN, ANALYSIS_TIMEOUT_SECONDS


class VisionAnalyzer:
    """Analyzes game screen using Google Gemini API."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")

        self.client = genai.Client(api_key=api_key)
        self.model = MODEL

    def analyze_screen(
        self,
        request_bar_base64: str,
        scene_base64: str
    ) -> dict:
        """
        Analyze the screen and return detected objects with coordinates.

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
            # Prepare images for Gemini
            import PIL.Image
            import io
            import base64
            
            # Decode and convert request bar
            req_bar_data = base64.b64decode(request_bar_base64)
            req_bar_img = PIL.Image.open(io.BytesIO(req_bar_data))
            
            # Decode and convert scene
            scene_data = base64.b64decode(scene_base64)
            scene_img = PIL.Image.open(io.BytesIO(scene_data))

            # Send to Gemini with both images
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    VISION_PROMPT,
                    req_bar_img,
                    scene_img
                ],
                config={
                    'response_mime_type': 'application/json',
                    'generation_config': {
                        'temperature': 0.3,
                        'max_output_tokens': 1024,
                    }
                }
            )

            # Get response text
            content = response.text

            # Parse JSON response
            result = self._parse_response(content)

            # Validate and filter results
            result = self._validate_results(result)

            return result

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            print(f"[ANALYZER] Error ({error_type}): {error_msg}", file=sys.stderr)
            return {"wave_id": "", "requests": [], "marks": [], "error": f"{error_type}: {error_msg}"}

    def _parse_response(self, content: str) -> dict:
        """Parse JSON from API response."""
        try:
            # Clean the content
            content = content.strip()

            # Handle markdown code blocks if present
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

            # Remove any leading/trailing backticks
            content = content.strip("`")

            data = json.loads(content)

            # Ensure required fields exist
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
            # Ensure required fields exist
            if "label" not in mark:
                continue

            # Get bbox
            bbox = mark.get("bbox", {})
            x1 = bbox.get("x1", 0)
            y1 = bbox.get("y1", 0)
            x2 = bbox.get("x2", 500)
            y2 = bbox.get("y2", 500)

            # Clamp coordinates
            x1 = max(0, min(1000, x1))
            y1 = max(0, min(1000, y1))
            x2 = max(0, min(1000, x2))
            y2 = max(0, min(1000, y2))

            # Calculate center
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # Get confidence
            confidence = mark.get("confidence", 50)

            # Filter by confidence
            if confidence < CONFIDENCE_MIN:
                continue

            validated_marks.append({
                "label": str(mark["label"])[:20],
                "x": cx,
                "y": cy,
                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                "confidence": confidence
            })

        # Sort by confidence (highest first) and limit count
        validated_marks.sort(key=lambda m: m["confidence"], reverse=True)
        validated_marks = validated_marks[:MAX_REQUESTS]

        return {
            "wave_id": result.get("wave_id", ""),
            "requests": result.get("requests", [])[:MAX_REQUESTS],
            "marks": validated_marks
        }
