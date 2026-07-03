"""
Dream Memory Live Overlay Assistant - Vision Analyzer Module
Handles OpenAI Vision API analysis for object detection.
"""

import json

from openai import OpenAI
from openai import APIError, RateLimitError, Timeout

from config import MODEL, VISION_PROMPT, MAX_REQUESTS, CONFIDENCE_MIN


class VisionAnalyzer:
    """Analyzes game screen using OpenAI Vision API."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required")

        self.client = OpenAI(api_key=api_key)
        self.model = MODEL

    def analyze_screen(
        self,
        image_base64: str,
        screen_width: int,
        screen_height: int
    ) -> dict:
        """
        Analyze the screen and return detected objects with coordinates.

        Returns:
            dict with structure:
            {
                "requests": ["item1", "item2", ...],
                "marks": [
                    {"label": "item1", "x": 123, "y": 456, "confidence": 87},
                    ...
                ]
            }
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": VISION_PROMPT
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "low"  # Faster analysis
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1024,
                temperature=0.3,  # Lower temperature for consistent output
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content

            # Parse JSON response
            result = self._parse_response(content)

            # Validate and filter results
            result = self._validate_results(result)

            return result

        except RateLimitError:
            return {"requests": [], "marks": [], "error": "rate_limit"}
        except Timeout:
            return {"requests": [], "marks": [], "error": "timeout"}
        except APIError as e:
            return {"requests": [], "marks": [], "error": str(e)}
        except Exception as e:
            return {"requests": [], "marks": [], "error": str(e)}

    def _parse_response(self, content: str) -> dict:
        """Parse JSON from API response."""
        try:
            # Try to extract JSON from the content
            content = content.strip()

            # Handle markdown code blocks if present
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

            data = json.loads(content)

            # Ensure required fields exist
            if "marks" not in data:
                data["marks"] = []
            if "requests" not in data:
                data["requests"] = []

            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    def _validate_results(self, result: dict) -> dict:
        """Validate and filter analysis results."""
        validated_marks = []

        for mark in result.get("marks", []):
            # Ensure required fields exist
            if not all(k in mark for k in ["label", "x", "y"]):
                continue

            # Get confidence with default
            confidence = mark.get("confidence", 50)

            # Filter by confidence
            if confidence < CONFIDENCE_MIN:
                continue

            # Validate coordinates are in range
            x = self._clamp(mark["x"], 0, 1000)
            y = self._clamp(mark["y"], 0, 1000)

            validated_marks.append({
                "label": str(mark["label"])[:20],  # Limit label length
                "x": x,
                "y": y,
                "confidence": confidence
            })

        # Sort by confidence (highest first) and limit count
        validated_marks.sort(key=lambda m: m["confidence"], reverse=True)
        validated_marks = validated_marks[:MAX_REQUESTS]

        return {
            "requests": result.get("requests", [])[:MAX_REQUESTS],
            "marks": validated_marks
        }

    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp value between min and max."""
        return max(min_val, min(max_val, value))
