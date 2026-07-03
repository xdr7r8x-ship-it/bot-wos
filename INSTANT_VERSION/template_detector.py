"""
Dream Memory - Template-Based Object Detector
NO AI, NO API, NO WAITING - Instant Detection!
"""

import os
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Tuple

import config


class TemplateDetector:
    """
    Ultra-fast template matching detector.
    No AI needed - uses pre-saved templates.
    """
    
    def __init__(self):
        self.templates = {}
        self.template_folder = config.TEMPLATES_FOLDER
        self._load_templates()
        
    def _load_templates(self):
        """Load all templates from folder."""
        if not os.path.exists(self.template_folder):
            os.makedirs(self.template_folder)
            print(f"[TEMPLATE] Created folder: {self.template_folder}")
            print(f"[TEMPLATE] Add template images to detect objects!")
            return
            
        for filename in os.listdir(self.template_folder):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                name = os.path.splitext(filename)[0]
                path = os.path.join(self.template_folder, filename)
                template = cv2.imread(path)
                if template is not None:
                    self.templates[name] = template
                    print(f"[TEMPLATE] Loaded: {name}")
                    
        if not self.templates:
            print(f"[TEMPLATE] No templates found in {self.template_folder}")
            print(f"[TEMPLATE] Add PNG/JPG images to start detection!")
    
    def add_template(self, name: str, image: np.ndarray):
        """Add a new template dynamically."""
        self.templates[name] = image
        print(f"[TEMPLATE] Added: {name}")
        
    def save_template(self, name: str, image: np.ndarray):
        """Save template to disk."""
        path = os.path.join(self.template_folder, f"{name}.png")
        cv2.imwrite(path, image)
        print(f"[TEMPLATE] Saved: {path}")
        
    def detect(self, scene: np.ndarray) -> List[Dict]:
        """Detect all templates in scene."""
        results = []
        
        for name, template in self.templates.items():
            matches = self._match_template(scene, template, name)
            results.extend(matches)
            
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        return results[:config.TEMPLATE_MAX_RESULTS]
    
    def _match_template(self, scene: np.ndarray, template: np.ndarray, name: str) -> List[Dict]:
        """Match single template against scene."""
        matches = []
        
        try:
            # Multi-scale matching
            for scale in np.linspace(config.TEMPLATE_SCALE_RANGE[0], 
                                     config.TEMPLATE_SCALE_RANGE[1], 5):
                # Resize template
                w, h = template.shape[1], template.shape[0]
                new_w, new_h = int(w * scale), int(h * scale)
                
                if new_w > scene.shape[1] or new_h > scene.shape[0]:
                    continue
                    
                resized = cv2.resize(template, (new_w, new_h))
                
                # Template matching
                result = cv2.matchTemplate(scene, resized, cv2.TM_CCOEFF_NORMED)
                
                # Find matches above threshold
                locations = np.where(result >= config.TEMPLATE_MATCH_THRESHOLD)
                
                for pt in zip(*locations[::-1]):
                    confidence = float(result[pt[1], pt[0]])
                    matches.append({
                        'name': name,
                        'x': pt[0] + new_w // 2,
                        'y': pt[1] + new_h // 2,
                        'confidence': int(confidence * 100),
                        'bbox': {
                            'x1': pt[0], 'y1': pt[1],
                            'x2': pt[0] + new_w, 'y2': pt[1] + new_h
                        }
                    })
                    
        except Exception as e:
            print(f"[TEMPLATE] Match error for {name}: {e}")
            
        return matches


class ColorDetector:
    """
    Color-based object detection.
    Detects objects by their color signature.
    """
    
    def __init__(self):
        self.color_profiles = {}
        
    def add_color_profile(self, name: str, rgb: Tuple[int, int, int], tolerance: int = 30):
        """Add color profile for detection."""
        self.color_profiles[name] = {
            'rgb': rgb,
            'tolerance': tolerance
        }
        
    def detect(self, scene: np.ndarray) -> List[Dict]:
        """Detect objects by color."""
        results = []
        
        # Convert to RGB
        scene_rgb = cv2.cvtColor(scene, cv2.COLOR_BGR2RGB)
        
        for name, profile in self.color_profiles.items():
            rgb = np.array(profile['rgb'])
            tolerance = profile['tolerance']
            
            # Create mask
            lower = np.clip(rgb - tolerance, 0, 255)
            upper = np.clip(rgb + tolerance, 0, 255)
            
            mask = cv2.inRange(scene_rgb, lower, upper)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area >= config.COLOR_MIN_AREA:
                    x, y, w, h = cv2.boundingRect(cnt)
                    results.append({
                        'name': name,
                        'x': x + w // 2,
                        'y': y + h // 2,
                        'confidence': min(100, int(area / 10)),
                        'bbox': {'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h}
                    })
                    
        return results


class InstantDetector:
    """
    Main detector - combines template and color detection.
    NO AI, NO API, INSTANT RESULTS!
    """
    
    def __init__(self):
        self.template = TemplateDetector()
        self.color = ColorDetector()
        self.mode = config.DETECTION_MODE
        
        # Pre-defined common game items
        self._setup_common_items()
        
    def _setup_common_items(self):
        """Setup common game item colors."""
        # Add color profiles for common items
        common_items = [
            ("gold", (255, 215, 0), 40),
            ("red_gem", (255, 0, 0), 30),
            ("blue_gem", (0, 0, 255), 30),
            ("green_gem", (0, 255, 0), 30),
            ("purple_gem", (128, 0, 128), 35),
            ("coin", (255, 200, 0), 35),
            ("chest", (139, 69, 19), 40),
            ("key", (255, 215, 0), 25),
            ("star", (255, 255, 0), 30),
            ("heart", (255, 0, 0), 25),
        ]
        
        for name, rgb, tol in common_items:
            self.color.add_color_profile(name, rgb, tol)
            
        print(f"[DETECTOR] Loaded {len(common_items)} color profiles")
        
    def detect(self, scene: Image.Image) -> List[Dict]:
        """Detect objects using configured mode."""
        # Convert PIL to OpenCV
        scene_cv = cv2.cvtColor(np.array(scene), cv2.COLOR_RGB2BGR)
        
        results = []
        
        if self.mode in ("template", "hybrid"):
            template_results = self.template.detect(scene_cv)
            results.extend(template_results)
            
        if self.mode in ("color", "hybrid"):
            color_results = self.color.detect(scene_cv)
            results.extend(color_results)
            
        # Deduplicate and sort
        seen = set()
        unique = []
        for r in results:
            key = (r['name'], r['x'] // 20, r['y'] // 20)  # Group nearby
            if key not in seen:
                seen.add(key)
                unique.append(r)
                
        unique.sort(key=lambda x: x['confidence'], reverse=True)
        return unique[:config.TEMPLATE_MAX_RESULTS]
    
    def add_item_template(self, name: str, image: Image.Image):
        """Add custom template from screenshot."""
        scene_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        self.template.add_template(name, scene_cv)
        
    def get_status(self) -> Dict:
        """Get detector status."""
        return {
            'mode': self.mode,
            'templates': len(self.template.templates),
            'colors': len(self.color.color_profiles),
            'ready': True
        }
