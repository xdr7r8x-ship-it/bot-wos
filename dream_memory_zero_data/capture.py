"""
Dream Memory Zero-Data Overlay - Screen Capture
Captures game viewport, crops areas, encodes images.
"""

import base64
import io
import platform
import numpy as np
import mss
from PIL import Image

from config import JPEG_QUALITY, MAX_WIDTH, REQUEST_BAR_HEIGHT_RATIO


class ScreenCapture:
    """Handles screen capture and image processing."""

    def __init__(self):
        self.sct = None
        self.platform = platform.system()

        if self.platform == "Windows":
            import win32gui
            import win32ui
            from ctypes import windll
            self.win32gui = win32gui
            self.win32ui = win32ui
            self.windll = windll

            # Create mss for fallback
            self.sct = mss.mss()

    def capture_rect(self, rect):
        """
        Capture a specific rectangle from the screen.
        rect: (x, y, width, height) in screen coordinates.
        Returns PIL Image or None.
        """
        if rect is None:
            return None

        x, y, width, height = rect

        if self.platform == "Windows":
            return self._capture_windows(x, y, width, height)
        else:
            return self._capture_mss(x, y, width, height)

    def _capture_windows(self, x, y, width, height):
        """Capture using Windows GDI."""
        try:
            # Create device contexts
            hwnd = self.win32gui.GetDesktopWindow()
            hwndDC = self.win32gui.GetWindowDC(hwnd)
            mfcDC = self.win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            # Create bitmap
            saveBitMap = self.win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            # Copy from screen
            result = self.windll.gdi32.BitBlt(
                saveDC.GetSafeHdc(),
                0, 0, width, height,
                hwndDC,
                x, y,
                0x00CC0020  # SRCCOPY
            )

            if not result:
                return None

            # Convert to PIL Image
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )

            # Cleanup
            self.win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            self.win32gui.ReleaseDC(hwnd, hwndDC)

            return img

        except Exception as e:
            print(f"[CAPTURE] Windows capture error: {e}")
            return self._capture_mss(x, y, width, height)

    def _capture_mss(self, x, y, width, height):
        """Capture using mss as fallback."""
        try:
            monitor = {"left": x, "top": y, "width": width, "height": height}
            screenshot = self.sct.grab(monitor)
            return Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        except Exception as e:
            print(f"[CAPTURE] MSS capture error: {e}")
            return None

    def crop_scene(self, image):
        """
        Crop the main scene area (exclude request bar).
        Returns PIL Image.
        """
        if image is None:
            return None

        width, height = image.size
        bar_height = int(height * REQUEST_BAR_HEIGHT_RATIO)
        scene_height = height - bar_height

        # Crop top portion (scene)
        scene = image.crop((0, 0, width, scene_height))
        return scene

    def crop_request_bar(self, image):
        """
        Crop the request bar (bottom area).
        Returns PIL Image.
        """
        if image is None:
            return None

        width, height = image.size
        bar_height = int(height * REQUEST_BAR_HEIGHT_RATIO)

        # Crop bottom portion (request bar)
        bar = image.crop((0, height - bar_height, width, height))
        return bar

    def encode_jpeg_base64(self, image, max_width=MAX_WIDTH, quality=JPEG_QUALITY):
        """
        Resize image if needed and encode as JPEG base64.
        Returns base64 string.
        """
        if image is None:
            return None

        # Resize if too wide
        width, height = image.size
        if width > max_width:
            new_width = max_width
            new_height = int(height * (max_width / width))
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Encode to JPEG
        buffer = io.BytesIO()
        image = image.convert("RGB")
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        buffer.seek(0)

        return base64.b64encode(buffer.read()).decode("utf-8")

    def image_fingerprint(self, image):
        """
        Compute a simple fingerprint for change detection.
        Uses downscaled grayscale hash.
        """
        if image is None:
            return None

        try:
            # Convert to grayscale and downscale
            gray = image.convert("L")
            thumb = gray.resize((64, 64), Image.Resampling.LANCZOS)
            pixels = list(thumb.getdata())

            # Simple XOR hash
            fingerprint = 0
            for i, pixel in enumerate(pixels):
                fingerprint ^= pixel ^ (i * 7)

            return fingerprint
        except Exception as e:
            print(f"[CAPTURE] Fingerprint error: {e}")
            return None

    def close(self):
        """Cleanup resources."""
        if self.sct:
            self.sct.close()
