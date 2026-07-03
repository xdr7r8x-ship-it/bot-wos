# Screen capture for BlueStacks
import win32gui
import win32ui
import win32con
import win32api
from ctypes import windll, pointer, c_int
from PIL import Image
import io
from typing import Optional, Tuple

import config


class ScreenCapture:
    """Capture screen region from BlueStacks window using client area."""

    def __init__(self):
        self.hwnd = None
        self.game_rect = None  # (x, y, width, height) - client area in screen coords
        self._cached_frame = None

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
            self._update_client_rect()
            return True

        return False

    def _update_client_rect(self):
        """Update client area rectangle in screen coordinates."""
        if not self.hwnd:
            return

        try:
            # Get client rect (relative to window)
            client_rect = win32gui.GetClientRect(self.hwnd)
            client_left, client_top = 0, 0
            client_right, client_bottom = client_rect[2], client_rect[3]

            # Convert to screen coordinates
            # Top-left
            pt_top_left = win32api.MAKELONG(client_left, client_top)
            windll.user32.ClientToScreen(self.hwnd, pointer(c_int(pt_top_left)))
            x1 = win32api.LOWORD(pt_top_left)
            y1 = win32api.HIWORD(pt_top_left)

            # Bottom-right
            pt_bottom_right = win32api.MAKELONG(client_right, client_bottom)
            windll.user32.ClientToScreen(self.hwnd, pointer(c_int(pt_bottom_right)))
            x2 = win32api.LOWORD(pt_bottom_right)
            y2 = win32api.HIWORD(pt_bottom_right)

            self.game_rect = (x1, y1, x2 - x1, y2 - y1)
        except Exception as e:
            print(f"[ERROR] Client rect failed: {e}")

    def capture_full_once(self) -> Optional[Tuple[Optional[Image.Image], Optional[Image.Image]]]:
        """Capture full frame ONCE and return both scene and request bar.
        
        Returns:
            Tuple of (scene_image, request_bar_image) or (None, None) on failure
        """
        if not self.hwnd:
            return None, None

        self._update_client_rect()
        if not self.game_rect:
            return None, None

        x, y, width, height = self.game_rect

        # Try GDI capture first
        img = self._capture_gdi(width, height)
        
        # Fallback to MSS if GDI failed or returned invalid image
        if img is None or self._is_invalid_image(img):
            print("[INFO] Falling back to MSS capture")
            img = self._capture_mss(x, y, width, height)

        if img is None or self._is_invalid_image(img):
            print("[ERROR] All capture methods failed")
            return None, None

        # Crop scene and request bar from SAME frame
        bar_height = int(height * config.REQUEST_BAR_HEIGHT_RATIO)
        scene = img.crop((0, 0, width, height - bar_height))
        request_bar = img.crop((0, height - bar_height, width, height))

        return scene, request_bar

    def _capture_gdi(self, width: int, height: int) -> Optional[Image.Image]:
        """Capture using GDI."""
        try:
            hwnd_dc = win32gui.GetWindowDC(self.hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bitmap)
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

            bmpinfo = bitmap.GetInfo()
            bmpstr = bitmap.GetBitmapBits(True)

            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )

            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwnd_dc)

            return img

        except Exception as e:
            print(f"[ERROR] GDI capture failed: {e}")
            return None

    def _capture_mss(self, x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
        """Fallback capture using MSS."""
        try:
            import mss
            with mss.mss() as sct:
                monitor = {"left": x, "top": y, "width": width, "height": height}
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                return img
        except Exception as e:
            print(f"[ERROR] MSS capture failed: {e}")
            return None

    def _is_invalid_image(self, img: Image.Image) -> bool:
        """Check if image is invalid (all black or wrong size)."""
        if img is None:
            return True
        if img.width < 100 or img.height < 100:
            return True
        # Check if mostly black
        pixels = list(img.getdata())
        black_count = sum(1 for p in pixels[:1000] if sum(p[:3]) < 30)
        return black_count > 900

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

    def get_geometry(self) -> Optional[Tuple[int, int, int, int]]:
        """Get (x, y, width, height) of game window."""
        return self.game_rect
