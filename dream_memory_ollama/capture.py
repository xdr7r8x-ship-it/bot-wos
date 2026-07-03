# Screen capture for BlueStacks
import win32gui
import win32ui
import win32con
from PIL import Image
import io
from typing import Optional, Tuple

import config


class ScreenCapture:
    """Capture screen region from BlueStacks window using client area."""

    def __init__(self):
        self.hwnd = None
        self.client_rect = None  # (x, y, width, height) - client area in screen coords
        self.viewport_rect = None  # (x, y, width, height) - actual game viewport
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
            self.client_rect = None
            return

        try:
            left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
            screen_left, screen_top = win32gui.ClientToScreen(self.hwnd, (left, top))
            screen_right, screen_bottom = win32gui.ClientToScreen(self.hwnd, (right, bottom))

            self.client_rect = (
                screen_left,
                screen_top,
                screen_right - screen_left,
                screen_bottom - screen_top
            )
        except Exception as e:
            print(f"[ERROR] Client rect failed: {e}")
            self.client_rect = None

    def detect_game_viewport(self, full_client_image: Image.Image, client_screen_rect: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Detect actual game viewport inside BlueStacks client.
        
        Args:
            full_client_image: Captured BlueStacks client area
            client_screen_rect: (x, y, width, height) in screen coordinates
            
        Returns:
            (x, y, width, height) of actual game viewport in screen coordinates
        """
        cx, cy, cw, ch = client_screen_rect
        img_width, img_height = full_client_image.size
        
        if img_width == 0 or img_height == 0:
            return client_screen_rect
        
        # Convert to numpy for fast processing
        import numpy as np
        img_array = np.array(full_client_image)
        
        # Calculate brightness
        brightness = img_array.mean(axis=2)
        
        # Threshold for non-black pixels
        threshold = 15
        
        # Find active columns (enough non-black pixels)
        col_active = (brightness > threshold).sum(axis=0) > (img_height * 0.3)
        
        # Find active rows
        row_active = (brightness > threshold).sum(axis=1) > (img_width * 0.3)
        
        # Find bounding box of active region
        active_cols = np.where(col_active)[0]
        active_rows = np.where(row_active)[0]
        
        if len(active_cols) == 0 or len(active_rows) == 0:
            # Fallback: centered portrait crop
            height = ch
            width = int(height * 9 / 16)
            x = cx + (cw - width) // 2
            y = cy
            return (x, y, width, height)
        
        # Get bounding box
        min_col = active_cols[0]
        max_col = active_cols[-1]
        min_row = active_rows[0]
        max_row = active_rows[-1]
        
        vx = min_col
        vy = min_row
        vw = max_col - min_col + 1
        vh = max_row - min_row + 1
        
        # Minimum size check
        if vw < 300 or vh < 500:
            # Fallback: centered portrait crop
            height = ch
            width = int(height * 9 / 16)
            x = cx + (cw - width) // 2
            y = cy
            return (x, y, width, height)
        
        # Convert to screen coordinates
        screen_x = cx + vx
        screen_y = cy + vy
        
        return (screen_x, screen_y, vw, vh)

    def capture_full_once(self) -> Optional[Tuple[Optional[Image.Image], Optional[Image.Image]]]:
        """Capture game viewport ONCE and return both scene and request bar.
        
        Returns:
            Tuple of (scene_image, request_bar_image) or (None, None) on failure
        """
        if not self.hwnd:
            return None, None

        self._update_client_rect()
        if not self.client_rect:
            return None, None

        cx, cy, cw, ch = self.client_rect

        # Try GDI capture first
        img = self._capture_gdi(cw, ch)
        
        # Fallback to MSS if GDI failed
        if img is None or self._is_invalid_image(img):
            img = self._capture_mss(cx, cy, cw, ch)

        if img is None or self._is_invalid_image(img):
            return None, None

        # Detect game viewport
        self.viewport_rect = self.detect_game_viewport(img, self.client_rect)
        
        if self.viewport_rect:
            vx, vy, vw, vh = self.viewport_rect
            
            # Convert screen coords back to image coords
            ix = vx - cx
            iy = vy - cy
            
            # Crop viewport from full client image
            img = img.crop((ix, iy, ix + vw, iy + vh))
            
            # Crop scene and request bar from SAME viewport frame
            bar_height = int(vh * config.REQUEST_BAR_HEIGHT_RATIO)
            scene = img.crop((0, 0, vw, vh - bar_height))
            request_bar = img.crop((0, vh - bar_height, vw, vh))
            
            return scene, request_bar
        
        return None, None

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
        return False

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

    def get_client_geometry(self) -> Optional[Tuple[int, int, int, int]]:
        """Get (x, y, width, height) of BlueStacks client."""
        return self.client_rect
    
    def get_viewport_geometry(self) -> Optional[Tuple[int, int, int, int]]:
        """Get (x, y, width, height) of detected game viewport."""
        return self.viewport_rect
