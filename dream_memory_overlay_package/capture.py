"""
Dream Memory Live Overlay Assistant - Screen Capture Module
Handles screen capture, resizing, compression, and change detection.
Supports both full screen and specific window capture (BlueStacks, emulators).
"""

import base64
import io
import hashlib
import platform
from PIL import Image

from config import JPEG_QUALITY, MAX_WIDTH, MAX_HEIGHT, REQUEST_BAR_HEIGHT_RATIO, DEFAULT_WINDOW_TITLE

# Platform-specific imports
if platform.system() == "Windows":
    import win32gui
    import win32ui
    import ctypes
    from ctypes import windll


class ScreenCapture:
    """Handles screen capture and processing for the overlay assistant."""

    def __init__(self, window_title: str = None):
        self.platform = platform.system()
        self.window_title = window_title or DEFAULT_WINDOW_TITLE
        self.hwnd = None
        self._last_bar_hash = None
        self._last_full_image = None
        
        # Get window handle on Windows
        if self.platform == "Windows":
            self._find_window()

    def _find_window(self):
        """Find the target window (BlueStacks, etc)."""
        try:
            # Try exact match first
            self.hwnd = win32gui.FindWindow(None, self.window_title)
            
            # Try partial match if exact fails
            if not self.hwnd:
                self.hwnd = self._find_window_by_partial_title(self.window_title)
            
            if self.hwnd:
                print(f"[CAPTURE] Found window: {self.window_title}")
            else:
                print(f"[CAPTURE] Window '{self.window_title}' not found, using full screen")
                
        except Exception as e:
            print(f"[CAPTURE] Error finding window: {e}")
            self.hwnd = None

    def _find_window_by_partial_title(self, title: str) -> int:
        """Find window by partial title match."""
        hwnd_found = None
        
        def callback(hwnd, ctx):
            nonlocal hwnd_found
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if title.lower() in window_text.lower():
                    hwnd_found = hwnd
            return True
        
        try:
            win32gui.EnumWindows(callback, None)
        except:
            pass
        
        return hwnd_found or 0

    def get_window_bounds(self) -> dict:
        """Get the target window bounds."""
        if self.hwnd and self.platform == "Windows":
            try:
                rect = win32gui.GetWindowRect(self.hwnd)
                return {
                    "left": rect[0],
                    "top": rect[1],
                    "width": rect[2] - rect[0],
                    "height": rect[3] - rect[1]
                }
            except:
                pass
        
        # Fallback to primary monitor
        if self.platform == "Windows":
            try:
                user32 = ctypes.windll.user32
                return {
                    "left": 0,
                    "top": 0,
                    "width": user32.GetSystemMetrics(0),
                    "height": user32.GetSystemMetrics(1)
                }
            except:
                pass
        
        return {"left": 0, "top": 0, "width": 1920, "height": 1080}

    def capture_window(self) -> Image.Image:
        """Capture the target window (BlueStacks) using Windows GDI."""
        if not self.hwnd or self.platform != "Windows":
            return self.capture_full_screen_fallback()
        
        try:
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            width = right - left
            height = bottom - top
            
            # Create device context
            hwndDC = win32gui.GetWindowDC(self.hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Copy window content
            result = windll.user32.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), 2)
            
            # Convert to PIL Image
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwndDC)
            
            return img
            
        except Exception as e:
            print(f"[CAPTURE] Window capture failed: {e}")
            return self.capture_full_screen_fallback()

    def capture_full_screen_fallback(self) -> Image.Image:
        """Fallback capture using mss."""
        try:
            import mss
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                return Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        except:
            return Image.new('RGB', (1920, 1080), color='black')

    def capture_full_screen(self) -> Image.Image:
        """Capture the target window or full screen."""
        return self.capture_window()

    def capture_request_bar(self) -> Image.Image:
        """Capture only the bottom request bar region."""
        bounds = self.get_window_bounds()
        w = bounds["width"]
        h = bounds["height"]
        bar_height = int(h * REQUEST_BAR_HEIGHT_RATIO)

        # Get the full window first
        full_img = self.capture_window()
        
        # Crop to bottom bar
        bar_img = full_img.crop((
            0, 
            full_img.height - bar_height,
            full_img.width,
            full_img.height
        ))
        
        return bar_img

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

        # Calculate MD5 hash
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
        full_img = self.capture_window()
        self._last_full_image = full_img

        resized = self.resize_for_api(full_img)
        base64_data = self.compress_to_base64(resized)

        return base64_data, full_img.width, full_img.height

    def get_screen_dimensions(self) -> tuple:
        """Return (width, height) of the target window or primary screen."""
        bounds = self.get_window_bounds()
        return bounds["width"], bounds["height"]

    def is_window_available(self) -> bool:
        """Check if target window is available."""
        if self.platform != "Windows":
            return False
        if not self.hwnd:
            return False
        try:
            return win32gui.IsWindowVisible(self.hwnd)
        except:
            return False

    def close(self):
        """Clean up resources."""
        pass  # No persistent resources to clean up
