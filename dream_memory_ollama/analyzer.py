# Ollama Vision Analyzer for Dream Memory
import base64
import json
import time
import requests
from typing import Optional

import config
from models import AnalysisResult, DetectedObject


class OllamaAnalyzer:
    """Analyze game screen using Ollama Vision (qwen2.5vl)."""

    def __init__(self):
        self.url = config.OLLAMA_URL
        self.model = config.OLLAMA_MODEL
        self.timeout = config.ANALYSIS_TIMEOUT_SECONDS
        self.available = False
        self.model_installed = False
        self._check_ollama()

    def _check_ollama(self):
        """Check if Ollama is running and model is installed."""
        try:
            response = requests.get(
                f"{config.OLLAMA_HOST}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                
                for m in models:
                    if config.OLLAMA_MODEL in m.get('name', ''):
                        self.model_installed = True
                        self.available = True
                        break
                
        except requests.exceptions.ConnectionError:
            pass
        except Exception:
            pass

    def is_available(self) -> bool:
        """Check if analyzer is available."""
        return self.available

    def get_status(self) -> dict:
        """Get analyzer status."""
        return {
            'available': self.available,
            'model_installed': self.model_installed,
            'model': self.model,
            'backend': 'ollama'
        }

    def analyze(self, request_bar_b64: str, scene_b64: str) -> AnalysisResult:
        """Analyze game screen with Ollama Vision.
        
        Args:
            request_bar_b64: Base64 encoded request bar image (bottom)
            scene_b64: Base64 encoded scene image (top)
        """
        
        # Prompt: Only find requested objects
        prompt = """You receive two images:
1. request_bar_image: bottom bar showing current requested objects.
2. scene_image: main hidden-object scene.

Task:
1. Read every currently visible requested object from request_bar_image.
2. Find only those requested objects inside scene_image.
3. Return approximate center coordinates for each found object.
4. Ignore request bar icons, UI, completed objects, future objects, and emulator controls.
5. Do not mark random collectibles - only find the objects requested in request_bar_image.

Return JSON only:
{
  "objects": [
    {"name": "item name", "x": 500, "y": 500, "confidence": 85}
  ]
}

Rules:
- x and y are 0-1000 relative to scene_image only (NOT including request bar).
- Max 20 objects.
- If nothing found: {"objects":[]}
"""

        # Build images list (both images if available)
        images = []
        if request_bar_b64:
            images.append(request_bar_b64)
        if scene_b64:
            images.append(scene_b64)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": images,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 500
            }
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code != 200:
                return AnalysisResult(
                    success=False,
                    objects=[],
                    error=f"HTTP {response.status_code}"
                )

            data = response.json()
            content = data.get('response', '')

            return self._parse_response(content)

        except requests.exceptions.Timeout:
            return AnalysisResult(
                success=False,
                objects=[],
                error="TIMEOUT"
            )
        except Exception as e:
            return AnalysisResult(
                success=False,
                objects=[],
                error=str(e)
            )

    def _parse_response(self, content: str) -> AnalysisResult:
        """Parse Ollama response into AnalysisResult."""
        try:
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                return AnalysisResult(
                    success=False,
                    objects=[],
                    error="NO JSON IN RESPONSE"
                )

            json_str = content[json_start:json_end]
            data = json.loads(json_str)

            objects = []
            for obj in data.get('objects', []):
                if obj.get('confidence', 0) >= config.CONFIDENCE_MIN:
                    objects.append(DetectedObject(
                        name=obj.get('name', 'unknown'),
                        x=int(obj.get('x', 0)),
                        y=int(obj.get('y', 0)),
                        confidence=int(obj.get('confidence', 0))
                    ))

            objects.sort(key=lambda o: o.confidence, reverse=True)
            objects = objects[:config.MAX_REQUESTS]

            return AnalysisResult(
                success=True,
                objects=objects
            )

        except json.JSONDecodeError:
            return AnalysisResult(
                success=False,
                objects=[],
                error="JSON PARSE ERROR"
            )
        except Exception as e:
            return AnalysisResult(
                success=False,
                objects=[],
                error=str(e)
            )
