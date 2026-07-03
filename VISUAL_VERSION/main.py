"""
Dream Memory Visual - BlueStacks Optimized
Captures BlueStacks screen and shows detected objects in overlay
"""

import sys
import time
import os
from typing import List, Tuple, Optional
import platform

# Windows only imports
if platform.system() == "Windows":
    import win32gui
    import win32ui
    import win32con
    import win32api

import numpy as np
from PIL import Image

from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QScreen

import config


class Signals(QObject):
    """Thread-safe signals."""
    frame_ready = pyqtSignal(np.ndarray)
    objects_found = pyqtSignal(list)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)


class GameCapture:
    """BlueStacks game capture."""
    
    def __init__(self):
        self.hwnd = None
        self.rect = None
        self.found = False
        
    def find_bluestacks(self) -> bool:
        """Find BlueStacks window."""
        titles = [config.WINDOW_TITLE] + config.ALT_TITLES
        
        def enum_handler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                for t in titles:
                    if t.lower() in title.lower():
                        ctx['hwnd'] = hwnd
                        ctx['title'] = title
                        return False
            return True
        
        ctx = {'hwnd': None, 'title': ''}
        win32gui.EnumWindows(enum_handler, ctx)
        
        if ctx['hwnd']:
            self.hwnd = ctx['hwnd']
            self.rect = win32gui.GetWindowRect(self.hwnd)
            self.found = True
            print(f"[OK] Found: {ctx['title']}")
            print(f"[OK] Window: {self.rect}")
            return True
        
        print("[ERROR] BlueStacks not found!")
        return False
    
    def capture(self) -> Optional[np.ndarray]:
        """Capture BlueStacks screen."""
        if not self.hwnd:
            return None
        
        try:
            # Get current rect (in case window moved)
            self.rect = win32gui.GetWindowRect(self.hwnd)
            x, y, x2, y2 = self.rect
            w, h = x2 - x, y2 - y
            
            # Capture
            hwnd_dc = win32gui.GetWindowDC(self.hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
            save_dc.SelectObject(bitmap)
            save_dc.BitBlt((0, 0), (w, h), mfc_dc, (0, 0), win32con.SRCCOPY)
            
            # Convert to numpy
            bmpinfo = bitmap.GetInfo()
            bmpstr = bitmap.GetBitmapBits(True)
            
            img = np.frombuffer(bmpstr, dtype=np.uint8)
            img = img.reshape((h, w, 4))[:, :, :3]  # BGRA to BGR
            
            # Cleanup
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwnd_dc)
            
            return img
            
        except Exception as e:
            print(f"[ERROR] Capture: {e}")
            return None


class ObjectDetector:
    """Detect objects by color in game scene."""
    
    def __init__(self):
        self.colors = config.DETECTION_COLORS
        self.draw_colors = config.DRAW_COLORS
        self.tolerance = config.COLOR_TOLERANCE
        self.min_pixels = config.MIN_OBJECT_PIXELS
        
    def detect(self, img: np.ndarray) -> List[dict]:
        """Detect all colored objects."""
        if img is None:
            return []
        
        results = []
        h, w = img.shape[:2]
        
        # Resize for speed if needed
        max_dim = 600
        scale = 1.0
        if max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            img_small = np.array(Image.fromarray(img).resize((new_w, new_h)))
        else:
            img_small = img
        
        # BGR to RGB
        rgb = img_small[:, :, ::-1]
        
        for name, props in self.colors.items():
            rgb_target = np.array(props['rgb'])
            tol = props.get('tol', self.tolerance)
            
            # Create color mask
            diff = np.abs(rgb.astype(int) - rgb_target.astype(int))
            mask = np.all(diff <= tol, axis=2).astype(np.uint8) * 255
            
            # Find connected regions
            try:
                import cv2
                
                # Morphological ops to clean
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area >= self.min_pixels * (scale ** 2):
                        # Get center
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"] / scale)
                            cy = int(M["m01"] / M["m00"] / scale)
                            
                            # Get color for drawing
                            draw_color = self.draw_colors.get(name, (0, 255, 0))
                            
                            results.append({
                                'name': name,
                                'x': cx,
                                'y': cy,
                                'confidence': min(100, int(area / 5)),
                                'color': draw_color,
                                'area': int(area)
                            })
            except Exception as e:
                pass
        
        # Sort by confidence and dedupe nearby
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Remove duplicates (keep highest confidence)
        filtered = []
        seen = set()
        for r in results:
            key = (r['x'] // 30, r['y'] // 30)
            if key not in seen:
                seen.add(key)
                filtered.append(r)
        
        return filtered[:30]  # Max 30 objects


class OverlayWindow(QWidget):
    """Transparent overlay showing detected objects."""
    
    def __init__(self, capture: GameCapture):
        super().__init__()
        self.capture = capture
        self.objects: List[dict] = []
        self.status = "STARTING..."
        
        # Window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Position over BlueStacks
        self.position_overlay()
        
        self.show()
    
    def position_overlay(self):
        """Position overlay over BlueStacks window."""
        if self.capture.found and self.capture.rect:
            x, y, x2, y2 = self.capture.rect
            self.setGeometry(x, y, x2 - x, y2 - y)
        else:
            # Fallback to primary screen
            screen = QApplication.primaryScreen()
            if screen:
                self.setGeometry(screen.geometry())
    
    def update_objects(self, objects: List[dict], status: str):
        """Update detected objects."""
        self.objects = objects
        self.status = status
        self.update()
        self.position_overlay()  # Keep aligned
    
    def paintEvent(self, event):
        """Draw overlay with detected objects."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw semi-transparent background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 20))
        
        # Draw each object
        for i, obj in enumerate(self.objects[:20]):  # Max 20 circles
            x, y = obj['x'], obj['y']
            color = obj['color']
            r, g, b = color
            
            # Draw circle
            pen = QPen(QColor(b, g, r), config.LINE_WIDTH)
            painter.setPen(pen)
            painter.drawEllipse(
                x - config.CIRCLE_SIZE // 2,
                y - config.CIRCLE_SIZE // 2,
                config.CIRCLE_SIZE,
                config.CIRCLE_SIZE
            )
            
            # Draw label
            font = QFont("Arial", config.FONT_SIZE, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(QColor(255, 255, 255)))
            text = f"{i+1}. {obj['name']}"
            painter.drawText(
                x + config.LABEL_OFFSET_X,
                y + config.LABEL_OFFSET_Y,
                text
            )
        
        # Draw status bar
        self.draw_status(painter)
    
    def draw_status(self, painter):
        """Draw status information."""
        painter.fillRect(5, 5, 300, 70, QColor(0, 0, 0, 180))
        
        font = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(0, 255, 0)))
        painter.drawText(15, 28, f"STATUS: {self.status}")
        
        font2 = QFont("Arial", 12)
        painter.setFont(font2)
        painter.drawText(15, 50, f"OBJECTS: {len(self.objects)}")
        
        # Controls hint
        font3 = QFont("Arial", 10)
        painter.setFont(font3)
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.drawText(15, 68, "F8: Toggle | F9: Scan | ESC: Exit")


class ScanThread(QThread):
    """Background thread for capture and detection."""
    
    def __init__(self, capture: GameCapture, detector: ObjectDetector, signals: Signals):
        super().__init__()
        self.capture = capture
        self.detector = detector
        self.signals = signals
        self.running = True
        self.scanning = True
        self.last_frame = None
        self.frame_count = 0
        self.fps_time = time.time()
        self.fps = 0
        
    def run(self):
        """Main loop."""
        while self.running:
            if self.scanning and self.capture.hwnd:
                # Capture frame
                frame = self.capture.capture()
                
                if frame is not None:
                    # Check if frame changed
                    frame_hash = hash(frame.tobytes())
                    if frame_hash != self.last_frame:
                        self.last_frame = frame_hash
                        self.frame_count += 1
                        
                        # Detect objects
                        objects = self.detector.detect(frame)
                        
                        # Emit signals
                        self.signals.frame_ready.emit(frame)
                        self.signals.objects_found.emit(objects)
                        
                        # FPS counter
                        now = time.time()
                        if now - self.fps_time >= 1.0:
                            self.fps = self.frame_count
                            self.frame_count = 0
                            self.fps_time = now
                            self.signals.status_changed.emit(f"LIVE ({self.fps} fps, {len(objects)} items)")
            
            self.msleep(50)  # ~20 fps
    
    def stop(self):
        """Stop thread."""
        self.running = False
    
    def toggle(self):
        """Toggle scanning."""
        self.scanning = not self.scanning
        return self.scanning


def main():
    """Main entry point."""
    print("=" * 55)
    print("  Dream Memory Visual - BlueStacks Optimized")
    print("=" * 55)
    
    # Check platform
    if platform.system() != "Windows":
        print("[ERROR] This program requires Windows!")
        return
    
    # Initialize Qt
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Find BlueStacks
    capture = GameCapture()
    if not capture.find_bluestacks():
        print("\n[ERROR] Cannot find BlueStacks!")
        print("Please make sure BlueStacks is running.")
        input("\nPress Enter to exit...")
        return
    
    # Create detector and signals
    detector = ObjectDetector()
    signals = Signals()
    
    # Create overlay
    overlay = OverlayWindow(capture)
    
    # Create scan thread
    scan_thread = ScanThread(capture, detector, signals)
    scan_thread.start()
    
    # Connect signals
    def on_objects(objects):
        status = scan_thread.status if hasattr(scan_thread, 'status') else "SCANNING"
        overlay.update_objects(objects, status)
    
    def on_status(status):
        overlay.status = status
    
    signals.objects_found.connect(on_objects)
    signals.status_changed.connect(on_status)
    
    # Hotkey timer
    hotkey_timer = QTimer()
    hotkey_timer.timeout.connect(lambda: check_hotkeys(scan_thread, overlay, app))
    hotkey_timer.start(30)
    
    print("\n" + "=" * 55)
    print("  CONTROLS:")
    print("  F8 - Toggle overlay visibility")
    print("  F9 - Toggle scanning on/off")
    print("  ESC - Exit program")
    print("=" * 55)
    
    print("\n[INFO] Application started!")
    print("[INFO] Overlay should appear over BlueStacks.")
    
    sys.exit(app.exec())


def check_hotkeys(thread: ScanThread, overlay: OverlayWindow, app: QApplication):
    """Check for keyboard input."""
    try:
        if win32api.GetAsyncKeyState(0x77) < 0:  # F8
            overlay.setVisible(not overlay.isVisible())
            time.sleep(0.3)
        elif win32api.GetAsyncKeyState(0x78) < 0:  # F9
            state = thread.toggle()
            print(f"[INFO] Scanning: {'ON' if state else 'OFF'}")
            time.sleep(0.3)
        elif win32api.GetAsyncKeyState(0x1B) < 0:  # ESC
            thread.stop()
            app.quit()
    except:
        pass


if __name__ == "__main__":
    main()
