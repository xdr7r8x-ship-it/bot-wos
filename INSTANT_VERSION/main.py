"""
Dream Memory - Instant Detection App
NO AI, NO API, NO WAITING - Works Immediately!
"""

import sys
import time
import threading
import win32gui
import win32ui
import win32con
from typing import Optional, List, Dict
from PIL import Image
import numpy as np

from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QScreen

import config
from template_detector import InstantDetector


class ScreenCapture:
    """Fast screen capture for Windows."""
    
    def __init__(self):
        self.hwnd = None
        self.game_rect = None
        
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
            rect = win32gui.GetWindowRect(self.hwnd)
            self.game_rect = (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
    
    def capture(self) -> Optional[Image.Image]:
        """Capture game window."""
        if not self.hwnd:
            return None
            
        self._update_rect()
        
        try:
            hwndDC = win32gui.GetWindowDC(self.hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, self.game_rect[2], self.game_rect[3])
            saveDC.SelectObject(saveBitMap)
            
            result = saveDC.BitBlt((0, 0), (self.game_rect[2], self.game_rect[3]), 
                                   mfcDC, (0, 0), win32con.SRCCOPY)
            
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            
            img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                                  bmpstr, 'raw', 'BGRX', 0, 1)
            
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwndDC)
            
            return img
            
        except Exception as e:
            print(f"[CAPTURE] Error: {e}")
            return None
    
    def crop_scene(self, img: Image.Image) -> Image.Image:
        """Crop game scene area."""
        return img.crop((0, config.GAME_TOP, img.width, config.GAME_BOTTOM))
    
    def crop_bar(self, img: Image.Image) -> Image.Image:
        """Crop request bar area."""
        return img.crop((0, config.BAR_TOP, img.width, config.BAR_BOTTOM))


class OverlayWindow(QWidget):
    """Transparent overlay window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dream Memory Overlay")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                          Qt.WindowType.WindowStaysOnTopHint |
                          Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setGeometry(0, 0, 1920, 1080)
        self.showFullScreen()
        
        self.marks = []
        self.status = "READY"
        
    def paintEvent(self, event):
        """Draw overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Semi-transparent background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 30))
        
        # Draw marks
        for i, mark in enumerate(self.marks):
            x, y = mark['x'], mark['y']
            confidence = mark['confidence']
            
            # Circle color based on confidence
            if confidence >= 80:
                color = QColor(0, 255, 0)  # Green
            elif confidence >= 60:
                color = QColor(255, 255, 0)  # Yellow
            else:
                color = QColor(255, 0, 0)  # Red
                
            pen = QPen(color, config.OVERLAY_LINE_WIDTH)
            painter.setPen(pen)
            painter.drawEllipse(QPoint(x, y), config.OVERLAY_RADIUS, config.OVERLAY_RADIUS)
            
            # Label
            font = QFont("Arial", 10)
            painter.setFont(font)
            painter.drawText(x + 20, y + 5, f"{i+1}. {mark['name']} ({confidence}%)")
            
        # Status
        font = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(0, 255, 0)))
        painter.drawText(20, 30, f"STATUS: {self.status}")
        painter.drawText(20, 50, f"MARKS: {len(self.marks)}")
        
    def update_marks(self, marks: List[Dict]):
        """Update detected marks."""
        self.marks = marks
        self.status = f"LIVE ({len(marks)} found)" if marks else "SCANNING..."
        self.update()
    
    def toggle(self):
        """Toggle visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()


class DreamMemoryApp:
    """Main application."""
    
    def __init__(self):
        self.running = True
        self.monitoring = False
        self.analysis_in_progress = False
        
        # Components
        self.capture = ScreenCapture()
        self.detector = InstantDetector()
        
        # Overlay
        self.overlay = OverlayWindow()
        
        # State
        self.last_image_hash = None
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self._scan_loop)
        
        print("=" * 50)
        print("Dream Memory - Instant Detection")
        print("NO AI, NO API - Works Immediately!")
        print("=" * 50)
        
        # Check status
        status = self.detector.get_status()
        print(f"Mode: {status['mode']}")
        print(f"Templates: {status['templates']}")
        print(f"Colors: {status['colors']}")
        print("=" * 50)
        
    def find_game(self) -> bool:
        """Find BlueStacks window."""
        print("[INFO] Looking for BlueStacks...")
        if self.capture.find_window():
            print(f"[OK] Found at {self.capture.game_rect}")
            return True
        print("[ERROR] BlueStacks not found!")
        return False
    
    def _scan_loop(self):
        """Main scanning loop."""
        if not self.monitoring or self.analysis_in_progress:
            return
            
        try:
            # Capture
            img = self.capture.capture()
            if img is None:
                return
                
            # Quick change detection
            img_hash = hash(img.tobytes())
            if img_hash == self.last_image_hash:
                return
            self.last_image_hash = img_hash
            
            # Crop scene
            scene = self.capture.crop_scene(img)
            
            # Detect
            self.analysis_in_progress = True
            marks = self.detector.detect(scene)
            
            # Update overlay
            self.overlay.update_marks(marks)
            self.overlay.status = f"LIVE - {len(marks)} items"
            
            print(f"[DETECT] Found {len(marks)} items")
            for m in marks[:5]:
                print(f"  - {m['name']} at ({m['x']}, {m['y']})")
                
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.analysis_in_progress = False
    
    def start_monitoring(self):
        """Start monitoring."""
        self.monitoring = True
        self.scan_timer.start(config.SCAN_INTERVAL_MS)
        print("[INFO] Monitoring started - Press F9 to stop")
        
    def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring = False
        self.scan_timer.stop()
        print("[INFO] Monitoring stopped - Press F9 to start")
    
    def toggle_monitoring(self):
        """Toggle monitoring."""
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def toggle_overlay(self):
        """Toggle overlay visibility."""
        self.overlay.toggle()
    
    def force_scan(self):
        """Force immediate scan."""
        self.last_image_hash = None
        self._scan_loop()
    
    def cleanup(self):
        """Cleanup."""
        self.scan_timer.stop()
        self.capture = None


class HotkeyManager:
    """Hotkey manager using threading."""
    def __init__(self, app):
        self.app = app
        self.running = True
        
    def run(self):
        """Check hotkeys in background."""
        try:
            import keyboard
            while self.running:
                if keyboard.is_pressed('f8'):
                    self.app.toggle_overlay()
                    time.sleep(0.3)
                elif keyboard.is_pressed('f9'):
                    self.app.toggle_monitoring()
                    time.sleep(0.3)
                elif keyboard.is_pressed('f10'):
                    self.app.force_scan()
                    time.sleep(0.3)
                elif keyboard.is_pressed('esc'):
                    self.running = False
                    self.app.cleanup()
                    break
                time.sleep(0.05)
        except ImportError:
            print("[INFO] Install 'keyboard' module for hotkeys")
            print("[INFO] Run: pip install keyboard")
        except Exception as e:
            print(f"[HOTKEY] Error: {e}")


def main():
    """Main entry."""
    print("=" * 50)
    print("DREAM MEMORY - INSTANT DETECTION")
    print("No AI, No API, No Waiting!")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    dream = DreamMemoryApp()
    
    if not dream.find_game():
        print("\n[ERROR] Cannot find BlueStacks!")
        print("Make sure BlueStacks is running.")
        return
        
    # Show overlay
    dream.overlay.show()
    
    # Start monitoring
    dream.start_monitoring()
    
    # Hotkey thread
    hotkey = HotkeyManager(dream)
    hotkey_thread = threading.Thread(target=hotkey.run, daemon=True)
    hotkey_thread.start()
    
    print("\n" + "=" * 50)
    print("CONTROLS:")
    print("  F8 - Toggle overlay")
    print("  F9 - Start/Stop monitoring")
    print("  F10 - Force scan")
    print("  ESC - Exit")
    print("=" * 50)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
