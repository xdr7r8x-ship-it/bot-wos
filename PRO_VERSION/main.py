"""
Dream Memory PRO - Professional Overlay Application
High performance, multi-threaded, zero dependencies on AI
"""

import sys
import time
import queue
import threading
from dataclasses import dataclass
from typing import List, Tuple, Optional
from PIL import Image
import numpy as np

# Windows imports (only on Windows)
import platform
if platform.system() == "Windows":
    import win32gui
    import win32ui
    import win32con
    import win32api

# PyQt6 for overlay
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject, QThread
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QCloseEvent


@dataclass
class DetectedObject:
    """Detected object data."""
    name: str
    x: int
    y: int
    confidence: int
    color: Tuple[int, int, int]


class Signals(QObject):
    """Thread-safe signals."""
    objects_detected = pyqtSignal(list)
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)


class ColorDetector:
    """High-performance color-based object detector."""
    
    def __init__(self):
        import config
        self.colors = config.GAME_COLORS
        self.threshold = config.COLOR_THRESHOLD
        self.min_size = config.MIN_OBJECT_SIZE
        
    def detect(self, img: np.ndarray) -> List[DetectedObject]:
        """Detect objects by color."""
        results = []
        h, w = img.shape[:2]
        
        # Resize for speed
        scale = min(1.0, 500 / max(w, h))
        if scale < 1.0:
            new_w, new_h = int(w * scale), int(h * scale)
            img = np.array(Image.fromarray(img).resize((new_w, new_h)))
            scale_back = 1.0 / scale
        else:
            scale_back = 1.0
        
        h, w = img.shape[:2]
        
        # Convert to RGB once
        rgb = img[:, :, ::-1] if len(img.shape) == 3 else img
        
        for name, (color_rgb, tolerance) in self.colors.items():
            # Create mask
            lower = np.array([max(0, c - tolerance) for c in color_rgb], dtype=np.uint8)
            upper = np.array([min(255, c + tolerance) for c in color_rgb], dtype=np.uint8)
            
            mask = ((rgb[:, :, 0] >= lower[0]) & (rgb[:, :, 0] <= upper[0]) &
                    (rgb[:, :, 1] >= lower[1]) & (rgb[:, :, 1] <= upper[1]) &
                    (rgb[:, :, 2] >= lower[2]) & (rgb[:, :, 2] <= upper[2])).astype(np.uint8) * 255
            
            # Find contours
            try:
                import cv2
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area >= self.min_size:
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"] * scale_back)
                            cy = int(M["m01"] / M["m00"] * scale_back)
                            results.append(DetectedObject(
                                name=name,
                                x=cx, y=cy,
                                confidence=min(100, int(area / 10)),
                                color=tuple(color_rgb)
                            ))
            except:
                pass
                
        # Sort by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:20]  # Limit results


class ScreenCapture:
    """High-performance screen capture."""
    
    def __init__(self):
        self.hwnd = None
        self.rect = None
        self.last_capture_time = 0
        self.capture_interval = 0.05  # 50ms minimum
        
    def find_window(self, title: str = "BlueStacks") -> bool:
        """Find game window."""
        windows = []
        
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                text = win32gui.GetWindowText(hwnd)
                if title.lower() in text.lower():
                    windows.append(hwnd)
            return True
        
        win32gui.EnumWindows(callback, None)
        
        if windows:
            self.hwnd = windows[0]
            self._update_rect()
            return True
        return False
    
    def _update_rect(self):
        """Update window rectangle."""
        if self.hwnd:
            self.rect = win32gui.GetWindowRect(self.hwnd)
    
    def capture(self) -> Optional[np.ndarray]:
        """Capture game window."""
        if not self.hwnd:
            return None
            
        # Rate limit captures
        now = time.time()
        if now - self.last_capture_time < self.capture_interval:
            return None
        self.last_capture_time = now
        
        try:
            self._update_rect()
            x, y, x2, y2 = self.rect
            width, height = x2 - x, y2 - y
            
            hwndDC = win32gui.GetWindowDC(self.hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(bitmap)
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
            
            bmpinfo = bitmap.GetInfo()
            bits = bitmap.GetBitmapBits(True)
            
            img = np.frombuffer(bits, dtype=np.uint8)
            img = img.reshape((bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4))[:, :, :3]
            
            win32gui.DeleteObject(bitmap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwndDC)
            
            return img
            
        except Exception as e:
            print(f"[ERROR] Capture failed: {e}")
            return None


class OverlayWindow(QWidget):
    """Transparent overlay with detected objects."""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Fullscreen on primary monitor
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
        
        self.objects: List[DetectedObject] = []
        self.status = "READY"
        self.show()
        
    def update_objects(self, objects: List[DetectedObject], status: str):
        """Update detected objects."""
        self.objects = objects
        self.status = status
        self.update()
        
    def paintEvent(self, event):
        """Draw overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw objects
        for i, obj in enumerate(self.objects):
            x, y = obj.x, obj.y
            r, g, b = obj.color
            color = QColor(b, g, r)
            
            pen = QPen(color, 3)
            painter.setPen(pen)
            painter.drawEllipse(x - 12, y - 12, 24, 24)
            
            # Label
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.drawText(x + 18, y + 5, f"{i+1}. {obj.name}")
            
        # Status bar
        painter.fillRect(0, 0, 400, 70, QColor(0, 0, 0, 150))
        font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(0, 255, 0)))
        painter.drawText(15, 25, f"STATUS: {self.status}")
        painter.drawText(15, 50, f"OBJECTS: {len(self.objects)}")


class CaptureThread(QThread):
    """Background capture thread."""
    
    def __init__(self, capture: ScreenCapture, detector: ColorDetector, signals: Signals):
        super().__init__()
        self.capture = capture
        self.detector = detector
        self.signals = signals
        self.running = True
        self.monitoring = True
        self._last_img = None
        
    def run(self):
        """Capture and detect loop."""
        while self.running:
            if self.monitoring:
                img = self.capture.capture()
                if img is not None and id(img) != id(self._last_img):
                    self._last_img = img
                    try:
                        objects = self.detector.detect(img)
                        self.signals.objects_detected.emit(objects)
                    except Exception as e:
                        self.signals.error_occurred.emit(str(e))
            time.sleep(0.05)
            
    def stop(self):
        """Stop thread."""
        self.running = False
        
    def toggle_monitoring(self):
        """Toggle monitoring."""
        self.monitoring = not self.monitoring
        return self.monitoring


def main():
    """Main entry."""
    print("=" * 50)
    print("DREAM MEMORY PRO")
    print("Professional Overlay - Zero AI")
    print("=" * 50)
    
    # Initialize
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Components
    capture = ScreenCapture()
    detector = ColorDetector()
    signals = Signals()
    
    # Find window
    print("[INFO] Searching for BlueStacks...")
    if not capture.find_window():
        print("[ERROR] BlueStacks not found!")
        print("[INFO] Make sure BlueStacks is running in window mode.")
        return
        
    print(f"[OK] Found window: {capture.rect}")
    
    # Overlay
    overlay = OverlayWindow()
    
    # Capture thread
    capture_thread = CaptureThread(capture, detector, signals)
    capture_thread.start()
    
    # Connect signals
    def on_objects(objects):
        status = f"LIVE ({len(objects)} objects)" if objects else "SCANNING..."
        overlay.update_objects(objects, status)
        
    signals.objects_detected.connect(on_objects)
    
    # Hotkey timer (non-blocking)
    hotkey_timer = QTimer()
    hotkey_timer.timeout.connect(lambda: _check_hotkeys(capture_thread, overlay, app))
    hotkey_timer.start(50)
    
    print("\n" + "=" * 50)
    print("CONTROLS:")
    print("  F8 - Toggle overlay visibility")
    print("  F9 - Toggle monitoring on/off")
    print("  ESC - Exit")
    print("=" * 50)
    
    sys.exit(app.exec())


def _check_hotkeys(thread: CaptureThread, overlay: OverlayWindow, app: QApplication):
    """Check for hotkeys."""
    try:
        vk_f8 = 0x77  # F8
        vk_f9 = 0x78  # F9
        vk_esc = 0x1B  # ESC
        
        if win32api.GetAsyncKeyState(vk_f8) < 0:
            overlay.setVisible(not overlay.isVisible())
            time.sleep(0.3)
        elif win32api.GetAsyncKeyState(vk_f9) < 0:
            active = thread.toggle_monitoring()
            print(f"[INFO] Monitoring: {'ON' if active else 'OFF'}")
            time.sleep(0.3)
        elif win32api.GetAsyncKeyState(vk_esc) < 0:
            thread.stop()
            app.quit()
    except:
        pass


if __name__ == "__main__":
    main()
