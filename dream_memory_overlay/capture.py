"""
Dream Memory Live Overlay Assistant - Screen Capture Module
Handles screen capture, resizing, compression, and change detection.
"""

import base64
import io
import hashlib
import mss
import numpy as np
from PIL import Image

from config import JPEG_QUALITY, MAX_WIDTH, MAX_HEIGHT, REQUEST_BAR_HEIGHT_RATIO


class ScreenCapture:
    """Handles screen capture and processing for the overlay assistant."""

    def __init__(self):
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]  # Primary monitor
        self._last_bar_hash = None
        self._last_full_image = None

    def get_monitor_bounds(self) -> dict:
        """Return the primary monitor bounds."""
        return self.monitor

    def capture_full_screen(self) -> Image.Image:
        """Capture the full screen and return as PIL Image."""
        screenshot = self.sct.grab(self.monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img

    def capture_request_bar(self) -> Image.Image:
        """Capture only the bottom request bar region."""
        w = self.monitor["width"]
        h = self.monitor["height"]
        bar_height = int(h * REQUEST_BAR_HEIGHT_RATIO)

        # Define region for bottom bar
        bar_region = {
            "left": self.monitor["left"],
            "top": self.monitor["top"] + h - bar_height,
            "width": w,
            "height": bar_height
        }

        screenshot = self.sct.grab(bar_region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img

    def resize_for_api(self, img: Image.Image) -> Image.Image:
        """Resize image to reduce API payload size."""
        w, h = img.size

        # Calculate scale to fit within max dimensions
        scale_w = MAX_WIDTH / w if w > MAX_WIDTH else 1
        scale_h = MAX_HEIGHT / h if h > MAX_HEIGHT else 1
        scale = min(scale_w, scale_h)

        if scale < 1:
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        return img

    def compress_to_base64(self, img: Image.Image) -> str:
        """Compress image to JPEG and return as base64 string."""
        buffer = io.BytesIO()
        img = img.convert("RGB")  # Ensure RGB mode for JPEG
        img.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

    def image_to_base64(self, img: Image.Image) -> str:
        """Convert PIL Image to base64 without additional compression."""
        buffer = io.BytesIO()
        img = img.convert("RGB")
        img.save(buffer, format="JPEG", quality=JPEG_QUALITY)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

    def detect_bar_change(self) -> bool:
        """
        Check if the request bar has changed since last check.
        Returns True if changed, False if same.
        """
        bar_img = self.capture_request_bar()

        # Convert to smaller size for faster hashing
        bar_small = bar_img.resize((100, 30), Image.Resampling.LANCZOS)
        bar_bytes = bar_small.tobytes()

        # Calculate perceptual hash
        current_hash = hashlib.md5(bar_bytes).hexdigest()

        if self._last_bar_hash is None:
            self._last_bar_hash = current_hash
            self._last_full_image = None  # Force first analysis
            return True

        if current_hash != self._last_bar_hash:
            self._last_bar_hash = current_hash
            self._last_full_image = None  # Mark for re-analysis
            return True

        return False

    def should_analyze(self) -> bool:
        """
        Check if full analysis should be triggered.
        Returns True if request bar changed or this is first capture.
        """
        return self.detect_bar_change()

    def get_capture_for_analysis(self) -> tuple:
        """
        Get the data needed for API analysis.
        Returns (full_image_base64, screen_width, screen_height).
        """
        full_img = self.capture_full_screen()
        self._last_full_image = full_img

        resized = self.resize_for_api(full_img)
        base64_data = self.compress_to_base64(resized)

        return base64_data, full_img.width, full_img.height

    def get_screen_dimensions(self) -> tuple:
        """Return (width, height) of the primary screen."""
        return self.monitor["width"], self.monitor["height"]

    def close(self):
        """Clean up resources."""
        if self.sct:
            self.sct.close()
