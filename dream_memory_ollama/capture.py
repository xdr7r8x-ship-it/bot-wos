# Screen capture for BlueStacks
import win32gui
import win32ui
import win32con
import mss
from PIL import Image
import io
from typing import Optional, Tuple

import config


class ScreenCapture:
    """Capture screen region from BlueStacks using manual viewport."""

    def __init__(self):
        self.hwnd = None
        self.viewport_rect = None
        self._last_bar_hash = None

    def find_window(self, title: str = "BlueStacks") -> bool:
        """Find BlueStacks window."""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                text = win32gui.GetWindowText(hwnd)
                if title.lower() in text.lower():
                    windows.append(hwnd)
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        if windows:
            self.hwnd = windows[0]
            return True

        return False

    def get_viewport(self) -> Optional[Tuple[int, int, int, int]]:
        """Get viewport based on mode."""
        if config.VIEWPORT_MODE == "manual":
            vx = config.MANUAL_VIEWPORT_X
            vy = config.MANUAL_VIEWPORT_Y
            vw = config.MANUAL_VIEWPORT_W
            vh = config.MANUAL_VIEWPORT_H
            
            if vx is None or vy is None or vw is None or vh is None:
                print("MANUAL VIEWPORT INVALID")
                return None
                
            self.viewport_rect = (vx, vy, vw, vh)
            return self.viewport_rect
        
        # Not implemented - use manual
        return None

    def capture_viewport(self) -> Optional[Tuple[Optional[Image.Image], Optional[Image.Image]]]:
        """Capture viewport once, return scene and request bar."""
        viewport = self.get_viewport()
        if not viewport:
            return None, None
            
        vx, vy, vw, vh = viewport

        # Capture using MSS
        try:
            with mss.mss() as sct:
                monitor = {"left": vx, "top": vy, "width": vw, "height": vh}
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        except Exception as e:
            print(f"[ERROR] MSS capture failed: {e}")
            return None, None

        # Crop scene and request bar from viewport
        bar_height = int(vh * config.REQUEST_BAR_HEIGHT_RATIO)
        scene = img.crop((0, 0, vw, vh - bar_height))
        request_bar = img.crop((0, vh - bar_height, vw, vh))

        return scene, request_bar

    def encode_jpeg(self, img: Image.Image, quality: int = None) -> Optional[bytes]:
        """Encode image to JPEG bytes."""
        if quality is None:
            quality = config.JPEG_QUALITY

        try:
            max_w = config.MAX_WIDTH
            if img.width > max_w:
                ratio = max_w / img.width
                new_h = int(img.height * ratio)
                img = img.resize((max_w, new_h), Image.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality)
            return buffer.getvalue()
        except Exception as e:
            print(f"[ERROR] JPEG encode failed: {e}")
            return None

    def get_viewport_geometry(self) -> Optional[Tuple[int, int, int, int]]:
        """Get viewport geometry."""
        return self.viewport_rect
