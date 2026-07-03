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

    def get_centered_portrait_viewport(self, client_screen_rect: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Calculate centered portrait viewport with margin ignores."""
        cx, cy, cw, ch = client_screen_rect
        
        # Calculate usable area
        usable_x = cx + config.LEFT_IGNORE_PX
        usable_y = cy + config.TOP_IGNORE_PX
        usable_w = cw - config.LEFT_IGNORE_PX - config.RIGHT_TOOLBAR_IGNORE_PX
        usable_h = ch - config.TOP_IGNORE_PX - config.BOTTOM_IGNORE_PX
        
        # Start with full usable height
        viewport_h = usable_h
        viewport_w = int(viewport_h * config.VIEWPORT_ASPECT)
        
        # If wider than usable, fit to width
        if viewport_w > usable_w:
            viewport_w = usable_w
            viewport_h = int(viewport_w / config.VIEWPORT_ASPECT)
        
        # Center in usable area
        viewport_x = usable_x + (usable_w - viewport_w) // 2
        viewport_y = usable_y + (usable_h - viewport_h) // 2
        
        return (viewport_x, viewport_y, viewport_w, viewport_h)

    def _is_valid_viewport(self, vx: int, vy: int, vw: int, vh: int, 
                           cx: int, cy: int, cw: int, ch: int) -> bool:
        """Check if detected viewport is valid."""
        # Minimum size
        if vw < 300 or vh < 500:
            return False
        
        # Aspect ratio check (portrait between 0.45 and 0.75)
        aspect = vw / vh if vh > 0 else 0
        if aspect < 0.45 or aspect > 0.75:
            return False
        
        # If viewport_x is near client_x while client is much wider, it's invalid
        if vx <= cx + 10 and cw > vw * 1.3:
            return False
        
        # If viewport takes most of client width, it's probably the whole client
        if vw > cw * 0.8:
            return False
        
        return True

    def detect_game_viewport(self, full_client_image: Image.Image, client_screen_rect: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Detect actual game viewport inside BlueStacks client.
        
        Args:
            full_client_image: Captured BlueStacks client area
            client_screen_rect: (x, y, width, height) in screen coordinates
            
        Returns:
            (x, y, width, height) of actual game viewport in screen coordinates
        """
        # Manual override
        if config.VIEWPORT_MODE == "manual":
            if all(v is not None for v in [config.MANUAL_VIEWPORT_X, config.MANUAL_VIEWPORT_Y, 
                                            config.MANUAL_VIEWPORT_W, config.MANUAL_VIEWPORT_H]):
                return (config.MANUAL_VIEWPORT_X, config.MANUAL_VIEWPORT_Y,
                        config.MANUAL_VIEWPORT_W, config.MANUAL_VIEWPORT_H)
        
        # Center portrait mode
        if config.VIEWPORT_MODE == "center_portrait":
            return self.get_centered_portrait_viewport(client_screen_rect)
        
        # Auto mode - try brightness detection first
        cx, cy, cw, ch = client_screen_rect
        img_width, img_height = full_client_image.size
        
        if img_width == 0 or img_height == 0:
            return self.get_centered_portrait_viewport(client_screen_rect)
        
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
            return self.get_centered_portrait_viewport(client_screen_rect)
        
        # Get bounding box
        min_col = active_cols[0]
        max_col = active_cols[-1]
        min_row = active_rows[0]
        max_row = active_rows[-1]
        
        # Convert to viewport coords
        vx = cx + min_col
        vy = cy + min_row
        vw = max_col - min_col + 1
        vh = max_row - min_row + 1
        
        # Validate viewport
        if not self._is_valid_viewport(vx, vy, vw, vh, cx, cy, cw, ch):
            return self.get_centered_portrait_viewport(client_screen_rect)
        
        return (vx, vy, vw, vh)

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
