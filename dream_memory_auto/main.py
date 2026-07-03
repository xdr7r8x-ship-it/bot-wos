"""
Dream Memory Helper - FULLY AUTOMATIC
No API key needed! Uses color and shape detection.
"""

import cv2
import numpy as np
import mss
import platform
import time

from config import *

# Platform imports
if platform.system() == "Windows":
    import win32gui
    import win32ui
    from ctypes import windll


class ColorDetector:
    """Detect objects by color."""
    
    def __init__(self):
        self.colors = [
            ("Red", (0, 0, 255), (10, 100, 100), (20, 255, 255)),
            ("Blue", (255, 0, 0), (100, 100, 50), (130, 255, 255)),
            ("Green", (0, 255, 0), (40, 100, 100), (80, 255, 255)),
            ("Yellow", (0, 255, 255), (20, 100, 100), (40, 255, 255)),
            ("Orange", (0, 165, 255), (5, 100, 100), (20, 255, 255)),
            ("Purple", (255, 0, 255), (130, 100, 100), (170, 255, 255)),
            ("Pink", (180, 105, 255), (140, 100, 100), (170, 255, 255)),
            ("Cyan", (255, 255, 0), (90, 100, 100), (110, 255, 255)),
        ]
    
    def detect(self, frame, min_area=300):
        """Find all colored objects."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        results = []
        
        for name, bgr, lower, upper in self.colors:
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > min_area:
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        results.append((cx, cy, area, name))
        
        return results


class ShapeDetector:
    """Detect objects by shape."""
    
    def detect(self, frame, min_area=300):
        """Find circles and shapes."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        edges = cv2.Canny(blurred, 50, 150)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        results = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Check if circular
                    perimeter = cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)
                    
                    if len(approx) > 8:
                        shape = "Circle"
                    elif len(approx) <= 6:
                        shape = "Shape"
                    else:
                        shape = "Object"
                    
                    results.append((cx, cy, area, shape))
        
        return results


class DreamMemoryAuto:
    """Fully automatic helper."""
    
    def __init__(self):
        self.hwnd = None
        self.running = True
        self.color_detector = ColorDetector()
        self.shape_detector = ShapeDetector()
        self.detections = []
        self.mode = "all"
        
        if platform.system() == "Windows":
            self._find_window()
    
    def _find_window(self):
        try:
            self.hwnd = win32gui.FindWindow(None, "BlueStacks")
            if not self.hwnd:
                def callback(hwnd, ctx):
                    if win32gui.IsWindowVisible(hwnd):
                        if "blue" in win32gui.GetWindowText(hwnd).lower():
                            self.hwnd = hwnd
                win32gui.EnumWindows(callback, None)
            if self.hwnd:
                r = win32gui.GetWindowRect(self.hwnd)
                print(f"[OK] BlueStacks: {r[2]-r[0]}x{r[3]-r[1]}")
        except Exception as e:
            print(f"[WARN] {e}")
    
    def capture(self):
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
            except:
                pass
        
        with mss.mss() as sct:
            return cv2.cvtColor(np.array(sct.grab(sct.monitors[1])), cv2.COLOR_BGRA2BGR)
    
    def detect_objects(self, frame):
        """Auto-detect all objects."""
        objects = []
        
        if self.mode in ["all", "color"]:
            objects.extend(self.color_detector.detect(frame))
        
        if self.mode in ["all", "shape"]:
            objects.extend(self.shape_detector.detect(frame))
        
        # Remove duplicates
        filtered = []
        for obj in objects:
            is_dup = False
            for f in filtered:
                if abs(obj[0] - f[0]) < 50 and abs(obj[1] - f[1]) < 50:
                    is_dup = True
                    break
            if not is_dup:
                filtered.append(obj)
        
        filtered.sort(key=lambda x: x[2], reverse=True)
        self.detections = filtered[:MAX_DETECTIONS]
        return self.detections
    
    def draw(self, frame):
        """Draw detection markers."""
        h, w = frame.shape[:2]
        out = frame.copy()
        
        for i, (x, y, area, obj_type) in enumerate(self.detections):
            r = max(15, min(30, int(np.sqrt(area) / 2)))
            cv2.circle(out, (x, y), r, CIRCLE_COLOR, 2)
            cv2.putText(out, str(i+1), (x-6, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT_COLOR, 2)
        
        # Status
        cv2.rectangle(out, (5, 5), (200, 40), BG_COLOR, -1)
        cv2.putText(out, f"Found: {len(self.detections)}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOR, 2)
        
        # Help
        cv2.rectangle(out, (5, h-40), (450, h-5), BG_COLOR, -1)
        cv2.putText(out, "1:All 2:Color 3:Shape | R:Refresh | ESC:Exit", (15, h-15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_COLOR, 1)
        
        return out
    
    def run(self):
        print("=" * 50)
        print("Dream Memory AUTO - No Clicking Needed!")
        print("=" * 50)
        
        last_time = 0
        interval = 0.5
        
        while self.running:
            frame = self.capture()
            
            if time.time() - last_time > interval:
                self.detect_objects(frame)
                last_time = time.time()
            
            cv2.imshow("Dream Memory AUTO", self.draw(frame))
            
            key = cv2.waitKey(100) & 0xFF
            
            if key == 27:
                self.running = False
            elif key == ord('1'):
                self.mode = "all"
                print("[MODE] All detections")
            elif key == ord('2'):
                self.mode = "color"
                print("[MODE] Color only")
            elif key == ord('3'):
                self.mode = "shape"
                print("[MODE] Shape only")
            elif key in [ord('r'), ord('R')]:
                self.detect_objects(frame)
        
        cv2.destroyAllWindows()


def main():
    try:
        DreamMemoryAuto().run()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
