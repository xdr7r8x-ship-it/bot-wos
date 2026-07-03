"""
Dream Memory Hybrid Analyzer - Supports Both Ollama AND Gemini
Auto-detects available backend, works offline with Ollama or online with Gemini
"""

import json
import os
import sys
from datetime import datetime
import requests

from config import (
    # Backend selection
    VISION_BACKEND,
    
    # Ollama settings
    OLLAMA_HOST, 
    OLLAMA_URL, 
    OLLAMA_MODEL, 
    OLLAMA_STRONG_MODEL,
    ANALYSIS_TIMEOUT_SECONDS,
    
    # Gemini settings
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_API_URL,
    GEMINI_TIMEOUT_SECONDS,
    
    # Common
    VISION_PROMPT, 
    MAX_REQUESTS, 
    CONFIDENCE_MIN
)


class HybridAnalyzer:
    """
    Hybrid AI analyzer that supports both:
    1. Ollama (local, free, unlimited) - Auto-detected
    2. Gemini (cloud, free tier) - Fallback
    
    Works with NO prerequisites - auto-selects available backend.
    """

    def __init__(self):
        self.backend = None
        self.model_name = None
        self.available = False
        self.ollama_available = False
        self.gemini_available = False
        self.ollama_model_installed = False
        self.gemini_key = None
        
        self._detect_backends()

    def _detect_backends(self):
        """Detect and setup available AI backends."""
        print("=" * 50)
        print("AI BACKEND DETECTION")
        print("=" * 50)
        
        # Check Ollama first
        self._check_ollama()
        
        # Check Gemini
        self._check_gemini()
        
        # Auto-select backend
        if VISION_BACKEND == "auto":
            if self.ollama_available and self.ollama_model_installed:
                self.backend = "ollama"
                self.available = True
            elif self.gemini_available:
                self.backend = "gemini"
                self.available = True
            else:
                self.backend = None
                self.available = False
        elif VISION_BACKEND == "ollama":
            if self.ollama_available and self.ollama_model_installed:
                self.backend = "ollama"
                self.available = True
            else:
                print("⚠️ Ollama not available, trying Gemini...")
                if self.gemini_available:
                    self.backend = "gemini"
                    self.available = True
        elif VISION_BACKEND == "gemini":
            if self.gemini_available:
                self.backend = "gemini"
                self.available = True
        
        # Print summary
        print("=" * 50)
        print(f"SELECTED BACKEND: {self.backend or 'NONE'}")
        print(f"MODEL: {self.model_name or 'N/A'}")
        print(f"STATUS: {'✅ READY' if self.available else '❌ NOT AVAILABLE'}")
        print("=" * 50)

    def _check_ollama(self):
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
            if response.status_code == 200:
                self.ollama_available = True
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                has_fast = any(OLLAMA_MODEL in name for name in model_names)
                has_strong = any(OLLAMA_STRONG_MODEL in name for name in model_names)
                
                if has_fast:
                    self.model_name = OLLAMA_MODEL
                    self.ollama_model_installed = True
                    print(f"✅ OLLAMA: {OLLAMA_MODEL} installed")
                elif has_strong:
                    self.model_name = OLLAMA_STRONG_MODEL
                    self.ollama_model_installed = True
                    print(f"✅ OLLAMA: {OLLAMA_STRONG_MODEL} installed")
                else:
                    self.ollama_model_installed = False
                    print(f"⚠️ OLLAMA: No qwen2.5vl model found")
                    print(f"   Install with: ollama pull {OLLAMA_MODEL}")
            else:
                self.ollama_available = False
                print(f"⚠️ OLLAMA: Server error {response.status_code}")
        except Exception as e:
            self.ollama_available = False
            self.ollama_model_installed = False
            print(f"⚠️ OLLAMA: Not running ({type(e).__name__})")

    def _check_gemini(self):
        """Check if Gemini API is available."""
        # Check environment variable
        key = os.environ.get("GEMINI_API_KEY", "") or GEMINI_API_KEY
        
        # Accept both key formats: AIza... (Google Cloud) or AQ.... (AI Studio)
        if key and (key.startswith("AIza") or key.startswith("AQ.")):
            self.gemini_key = key
            self.gemini_available = True
            print(f"✅ GEMINI: API key configured")
        else:
            self.gemini_key = None
            self.gemini_available = False
            print(f"⚠️ GEMINI: No API key (set GEMINI_API_KEY env var)")

    def is_available(self) -> bool:
        """Check if any backend is available."""
        return self.available

    def get_backend_name(self) -> str:
        """Get the name of the active backend."""
        return self.backend or "NONE"

    def get_status_info(self) -> dict:
        """Get detailed status information."""
        return {
            "available": self.available,
            "backend": self.backend,
            "model": self.model_name,
            "ollama_available": self.ollama_available,
            "ollama_model_installed": self.ollama_model_installed,
            "gemini_available": self.gemini_available,
        }

    def analyze_screen(self, request_bar_base64: str, scene_base64: str) -> dict:
        """
        Analyze the screen using available backend.
        Auto-fallbacks between Ollama and Gemini.
        """
        if not self.available:
            if self.gemini_available:
                return self._analyze_gemini(request_bar_base64, scene_base64)
            elif self.ollama_available and self.ollama_model_installed:
                return self._analyze_ollama(request_bar_base64, scene_base64)
            return {"wave_id": "", "requests": [], "marks": [], "error": "No AI available"}
        
        if self.backend == "ollama":
            return self._analyze_ollama(request_bar_base64, scene_base64)
        else:
            return self._analyze_gemini(request_bar_base64, scene_base64)

    def _analyze_ollama(self, request_bar_b64: str, scene_b64: str) -> dict:
        """Analyze using Ollama."""
        try:
            if not self.ollama_available:
                return {"wave_id": "", "requests": [], "marks": [], "error": "Ollama not available"}
            
            if not self.ollama_model_installed:
                return {"wave_id": "", "requests": [], "marks": [], "error": f"Model not installed: {self.model_name}"}

            payload = {
                "model": self.model_name,
                "prompt": VISION_PROMPT,
                "images": [request_bar_b64, scene_b64],
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1024
                }
            }

            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=ANALYSIS_TIMEOUT_SECONDS
            )

            if response.status_code != 200:
                return {"wave_id": "", "requests": [], "marks": [], "error": f"Ollama error: {response.status_code}"}

            result = response.json()
            content = result.get("response", "")
            
            parsed = self._parse_response(content)
            return self._validate_results(parsed)

        except requests.exceptions.Timeout:
            return {"wave_id": "", "requests": [], "marks": [], "error": "Timeout - model too slow"}
        except Exception as e:
            return {"wave_id": "", "requests": [], "marks": [], "error": f"{type(e).__name__}: {e}"}

    def _analyze_gemini(self, request_bar_b64: str, scene_b64: str) -> dict:
        """Analyze using Gemini API."""
        try:
            if not self.gemini_key:
                return {"wave_id": "", "requests": [], "marks": [], "error": "Gemini API key missing"}

            url = f"{GEMINI_API_URL}?key={self.gemini_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": VISION_PROMPT},
                        {"inline_data": {"mime_type": "image/jpeg", "data": request_bar_b64}},
                        {"inline_data": {"mime_type": "image/jpeg", "data": scene_b64}}
                    ]
                }],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.3,
                    "maxOutputTokens": 1024
                }
            }

            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=GEMINI_TIMEOUT_SECONDS
            )

            if response.status_code != 200:
                return {"wave_id": "", "requests": [], "marks": [], "error": f"Gemini error: {response.status_code}"}

            result = response.json()
            
            # Extract text from Gemini response
            try:
                content = result["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                return {"wave_id": "", "requests": [], "marks": [], "error": "Invalid Gemini response"}

            parsed = self._parse_response(content)
            return self._validate_results(parsed)

        except requests.exceptions.Timeout:
            return {"wave_id": "", "requests": [], "marks": [], "error": "Gemini timeout"}
        except Exception as e:
            return {"wave_id": "", "requests": [], "marks": [], "error": f"{type(e).__name__}: {e}"}

    def _parse_response(self, content: str) -> dict:
        """Parse JSON from AI response."""
        try:
            content = content.strip()
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:].strip()
            
            start = content.find("{")
            end = content.rfind("}") + 1
            
            if start >= 0 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
            else:
                data = json.loads(content)

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

        validated_marks.sort(key=lambda m: m["confidence"], reverse=True)
        validated_marks = validated_marks[:MAX_REQUESTS]

        return {
            "wave_id": result.get("wave_id", ""),
            "requests": result.get("requests", [])[:MAX_REQUESTS],
            "marks": validated_marks
        }
