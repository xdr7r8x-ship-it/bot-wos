"""
Dream Memory Helper - FREE VERSION
You click on objects, it remembers and helps you track them!
No API key needed - 100% FREE!
"""

import cv2
import numpy as np
import mss
import platform
import pickle
import os

from config import *

# Platform imports
if platform.system() == "Windows":
    import win32gui
    import win32ui
    import ctypes
    from ctypes import windll


class DreamMemoryHelper:
    """Free helper - you mark objects manually, it tracks them!"""
    
    def __init__(self):
        self.hwnd = None
        self.running = True
        self.marks = []  # User-marked positions
        self.current_screenshot = None
        self.display_scale = 1.0
        
        if platform.system() == "Windows":
            self._find_window()
    
    def _find_window(self):
        """Find BlueStacks window."""
        try:
            self.hwnd = win32gui.FindWindow(None, "BlueStacks")
            if not self.hwnd:
                def callback(hwnd, ctx):
                    if win32gui.IsWindowVisible(hwnd):
                        text = win32gui.GetWindowText(hwnd)
                        if "blue" in text.lower():
                            self.hwnd = hwnd
                win32gui.EnumWindows(callback, None)
            if self.hwnd:
                rect = win32gui.GetWindowRect(self.hwnd)
                print(f"[OK] Found BlueStacks: {rect[2]-rect[0]}x{rect[3]-rect[1]}")
        except Exception as e:
            print(f"[WARN] Window search: {e}")
    
    def capture_screen(self):
        """Capture screen or window."""
        if self.hwnd and platform.system() == "Windows":
            try:
                left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
                w, h = right - left, bottom - top
                
                hwndDC = win32gui.GetWindowDC(self.hwnd)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
                saveDC.SelectObject(saveBitMap)
                
                windll.user32.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), 2)
                
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                img = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4))
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(self.hwnd, hwndDC)
                
                return img
            except Exception as e:
                print(f"[WARN] Window capture: {e}")
        
        # Fallback to mss
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = np.array(sct.grab(monitor))
            return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
    
    def click_callback(self, event, x, y, flags, param):
        """Handle mouse clicks to mark objects."""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Convert display coords to actual coords
            actual_x = int(x / self.display_scale)
            actual_y = int(y / self.display_scale)
            
            self.marks.append((actual_x, actual_y))
            print(f"[MARK] Position {len(self.marks)}: ({actual_x}, {actual_y})")
        
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Right click to remove last mark
            if self.marks:
                removed = self.marks.pop()
                print(f"[REMOVE] Position: ({removed[0]}, {removed[1]})")
    
    def draw_interface(self, frame):
        """Draw marks and UI on frame."""
        h, w = frame.shape[:2]
        display = frame.copy()
        
        # Draw marks
        for i, (x, y) in enumerate(self.marks):
            # Circle
            cv2.circle(display, (x, y), CIRCLE_RADIUS, CIRCLE_COLOR, 2)
            
            # Number
            cv2.putText(display, str(i+1), (x-8, y+5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, TEXT_COLOR, 2)
        
        # Status bar (top)
        cv2.rectangle(display, (5, 5), (250, 45), BG_COLOR, -1)
        cv2.rectangle(display, (5, 5), (250, 45), CIRCLE_COLOR, 2)
        cv2.putText(display, f"Marks: {len(self.marks)}", (15, 32), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 2)
        
        # Help bar (bottom)
        help_y = h - 50
        cv2.rectangle(display, (5, help_y), (450, h-5), BG_COLOR, -1)
        help_text = "L-Click: Mark | R-Click: Remove | C: Clear | R: Refresh | ESC: Exit"
        cv2.putText(display, help_text, (15, help_y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, TEXT_COLOR, 1)
        
        return display
    
    def run(self):
        """Main loop."""
        print("=" * 60)
        print("Dream Memory Helper - FREE VERSION (No API)")
        print("=" * 60)
        print("Instructions:")
        print("  LEFT CLICK  - Mark an object location")
        print("  RIGHT CLICK - Remove last mark")
        print("  C key       - Clear all marks")
        print("  R key       - Refresh screen")
        print("  ESC         - Exit")
        print("=" * 60)
        
        window_name = "Dream Memory Helper - Click to Mark Objects!"
        
        while self.running:
            # Capture screen
            self.current_screenshot = self.capture_screen()
            
            # Calculate display scale (fit to screen)
            screen_h, screen_w = self.current_screenshot.shape[:2]
            max_width = 1200
            if screen_w > max_width:
                self.display_scale = max_width / screen_w
                new_w = max_width
                new_h = int(screen_h * self.display_scale)
                display_frame = cv2.resize(self.current_screenshot, (new_w, new_h))
            else:
                self.display_scale = 1.0
                display_frame = self.current_screenshot
            
            # Draw interface
            output = self.draw_interface(display_frame)
            
            # Show window
            cv2.namedWindow(window_name)
            cv2.setMouseCallback(window_name, self.click_callback)
            cv2.imshow(window_name, output)
            
            # Handle keys
            key = cv2.waitKey(500) & 0xFF
            
            if key == 27:  # ESC
                self.running = False
            elif key == ord('c') or key == ord('C'):  # Clear
                self.marks.clear()
                print("[CLEAR] All marks cleared")
            elif key == ord('r') or key == ord('R'):  # Refresh
                print("[REFRESH] Screen refreshed")
        
        cv2.destroyAllWindows()
        print("[OK] Goodbye!")


def main():
    try:
        helper = DreamMemoryHelper()
        helper.run()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
