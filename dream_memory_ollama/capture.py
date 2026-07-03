# Screen capture for BlueStacks
import win32gui
import win32ui
import win32con
from PIL import Image
import io
from typing import Optional, Tuple

import config


class ScreenCapture:
    """Capture screen region from BlueStacks window."""

    def __init__(self):
        self.hwnd = None
        self.game_rect = None  # (left, top, right, bottom)

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
            self._update_rect()
            return True

        return False

    def _update_rect(self):
        """Update window rectangle."""
        if self.hwnd:
            self.game_rect = win32gui.GetWindowRect(self.hwnd)

    def capture_full(self) -> Optional[Image.Image]:
        """Capture full game window."""
        if not self.hwnd:
            return None

        self._update_rect()
        left, top, right, bottom = self.game_rect
        width = right - left
        height = bottom - top

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
            print(f"[ERROR] Capture failed: {e}")
            return None

    def capture_request_bar(self) -> Optional[Image.Image]:
        """Capture request bar (BOTTOM of game screen)."""
        full = self.capture_full()
        if full is None:
            return None

        bar_height = int(full.height * config.REQUEST_BAR_HEIGHT_RATIO)
        # Request bar is at BOTTOM
        return full.crop((0, full.height - bar_height, full.width, full.height))

    def capture_scene(self) -> Optional[Image.Image]:
        """Capture game scene (TOP part, above request bar)."""
        full = self.capture_full()
        if full is None:
            return None

        bar_height = int(full.height * config.REQUEST_BAR_HEIGHT_RATIO)
        # Scene is TOP part (everything except bottom request bar)
        return full.crop((0, 0, full.width, full.height - bar_height))

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
        if not self.game_rect:
            return None
        left, top, right, bottom = self.game_rect
        return (left, top, right - left, bottom - top)
