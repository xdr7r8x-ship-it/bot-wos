# Ollama Vision Analyzer for Dream Memory
import base64
import json
import time
import requests
from typing import Optional
from dataclasses import asdict

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
        print("CHECKING OLLAMA")
        
        try:
            # Check if Ollama is running
            response = requests.get(
                f"{config.OLLAMA_HOST}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                print("OLLAMA RUNNING")
                models = response.json().get('models', [])
                
                # Check for qwen2.5vl:3b
                for m in models:
                    if config.OLLAMA_MODEL in m.get('name', ''):
                        self.model_installed = True
                        self.available = True
                        print("MODEL FOUND")
                        break
                
                if not self.model_installed:
                    print("MODEL NOT FOUND")
                    print(f"Run: ollama pull {self.OLLAMA_MODEL}")
            else:
                print("OLLAMA NOT RUNNING")
                
        except requests.exceptions.ConnectionError:
            print("OLLAMA NOT RUNNING")
            print("Start Ollama and run: ollama pull qwen2.5vl:3b")
        except Exception as e:
            print(f"OLLAMA CHECK ERROR: {e}")

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
        """Analyze game screen with Ollama Vision."""
        
        # Build prompt for Dream Memory objects
        prompt = """You are playing Dream Memory game in Whiteout Survival.
Analyze the game screen and identify all collectible objects.
Focus on the GAME SCENE (bottom part) where objects appear.

Look for these types of objects:
- Gold coins, gems (red, blue, green, purple, yellow)
- Chests, keys, crystals
- Any shiny or colorful collectibles
- Flowers, hearts, stars
- Butterflies, shells

Respond ONLY with valid JSON in this exact format:
{
  "objects": [
    {"name": "gold", "x": 500, "y": 500, "confidence": 85},
    {"name": "blue_gem", "x": 300, "y": 400, "confidence": 90}
  ]
}

Rules:
- x and y are coordinates from 0-1000 (relative to scene width/height)
- confidence is 0-100
- Only list objects visible in the SCENE (not the request bar)
- Maximum 20 objects
- If no objects found, return empty objects array
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [scene_b64],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 500
            }
        }

        try:
            print("ANALYSIS STARTED")
            start_time = time.time()
            
            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout
            )
            
            elapsed = time.time() - start_time
            print(f"ANALYSIS FINISHED ({elapsed:.1f}s)")

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
            print(f"ANALYSIS ERROR: {e}")
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

            if not objects:
                print("NO MARKS")

            return AnalysisResult(
                success=True,
                objects=objects
            )

        except json.JSONDecodeError as e:
            return AnalysisResult(
                success=False,
                objects=[],
                error=f"JSON PARSE ERROR: {e}"
            )
        except Exception as e:
            return AnalysisResult(
                success=False,
                objects=[],
                error=str(e)
            )
