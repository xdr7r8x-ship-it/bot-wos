"""
Dream Memory Helper - ULTRA FAST
1. Click on items in request bar to save
2. Auto-finds them in the game scene
15 seconds per round - FAST!
"""

import cv2
import numpy as np
import mss
import platform
import time
import os
import json

if platform.system() == "Windows":
    import win32gui
    import win32ui
    from ctypes import windll


class UltraFastMatcher:
    """Fast template matching."""
    
    def __init__(self):
        self.templates = {}  # name -> (template, threshold)
        self.template_dir = "templates"
        self._load_templates()
    
    def _load_templates(self):
        if os.path.exists(self.template_dir):
            for f in os.listdir(self.template_dir):
                if f.endswith('.png'):
                    name = f[:-4]
                    path = os.path.join(self.template_dir, f)
                    img = cv2.imread(path)
                    if img is not None:
                        self.templates[name] = (img, 0.7)
    
    def add(self, name, template, threshold=0.7):
        self.templates[name] = (template, threshold)
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        cv2.imwrite(os.path.join(self.template_dir, f"{name}.png"), template)
    
    def find(self, screenshot):
        results = []
        h, w = screenshot.shape[:2]
        scene = screenshot[0:int(h*0.82), 0:w]  # Main scene only
        
        for name, (template, threshold) in self.templates.items():
            try:
                if template.shape[0] > scene.shape[0] or template.shape[1] > scene.shape[1]:
                    continue
                    
                result = cv2.matchTemplate(scene, template, cv2.TM_CCOEFF_NORMED)
                locations = np.where(result >= threshold)
                
                for pt in zip(*locations[::-1]):
                    x = int(pt[0] + template.shape[1]//2)
                    y = int(pt[1] + template.shape[0]//2)
                    conf = float(result[pt[1], pt[0]])
                    results.append((x, y, conf, name))
            except:
                pass
        
        # Remove overlaps
        filtered = []
        for r in sorted(results, key=lambda x: x[2], reverse=True):
            x, y, c, n = r
            is_dup = any(abs(x-fx) < 35 and abs(y-fy) < 35 for fx, fy, _, _ in filtered)
            if not is_dup:
                filtered.append(r)
        
        return filtered[:20]


class DreamMemoryFast:
    def __init__(self):
        self.hwnd = None
        self.running = True
        self.matcher = UltraFastMatcher()
        self.found = []
        self.screenshot = None
        
        if platform.system() == "Windows":
            self._find_window()
    
    def _find_window(self):
        try:
            self.hwnd = win32gui.FindWindow(None, "BlueStacks")
            if not self.hwnd:
                def cb(h, c):
                    if win32gui.IsWindowVisible(h) and "blue" in win32gui.GetWindowText(h).lower():
                        self.hwnd = h
                win32gui.EnumWindows(cb, None)
            if self.hwnd:
                r = win32gui.GetWindowRect(self.hwnd)
                print(f"[OK] Window: {r[2]-r[0]}x{r[3]-r[1]}")
        except:
            pass
    
    def capture(self):
        if self.hwnd and platform.system() == "Windows":
            try:
                l, t, r, b = win32gui.GetWindowRect(self.hwnd)
                w, h = r-l, b-t
                dc = win32gui.GetWindowDC(self.hwnd)
                mfc = win32ui.CreateDCFromHandle(dc)
                sdc = mfc.CreateCompatibleDC()
                bmp = win32ui.CreateBitmap()
                bmp.CreateCompatibleBitmap(mfc, w, h)
                sdc.SelectObject(bmp)
                windll.user32.PrintWindow(self.hwnd, sdc.GetSafeHdc(), 2)
                info = bmp.GetInfo()
                data = bmp.GetBitmapBits(True)
                img = np.frombuffer(data, dtype=np.uint8).reshape((info['bmHeight'], info['bmWidth'], 4))
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                win32gui.DeleteObject(bmp.GetHandle())
                sdc.DeleteDC()
                mfc.DeleteDC()
                win32gui.ReleaseDC(self.hwnd, dc)
                return img
            except:
                pass
        with mss.mss() as sct:
            return cv2.cvtColor(np.array(sct.grab(sct.monitors[1])), cv2.COLOR_BGRA2BGR)
    
    def get_bar(self, frame):
        h, w = frame.shape[:2]
        bar_h = int(h * 0.18)
        return frame[h-bar_h:h, 0:w]
    
    def add_item(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and self.screenshot is not None:
            bar = self.get_bar(self.screenshot)
            bh, bw = bar.shape[:2]
            sx = int(x * bw / 800)
            sy = int(y * bh / 600)
            sz = 20
            y1, y2 = max(0,sy-sz), min(bh,sy+sz)
            x1, x2 = max(0,sx-sz), min(bw,sx+sz)
            template = bar[y1:y2, x1:x2]
            
            name = f"item{len(self.matcher.templates)+1}"
            self.matcher.add(name, template)
            print(f"[ADD] Template '{name}' saved")
    
    def scan(self):
        if self.screenshot is None:
            return []
        return self.matcher.find(self.screenshot)
    
    def draw(self, frame, results):
        out = frame.copy()
        h, w = frame.shape[:2]
        
        # Bar indicator
        bar_h = int(h * 0.18)
        cv2.rectangle(out, (0, h-bar_h), (w, h), (50, 50, 50), -1)
        cv2.putText(out, "REQUEST BAR", (10, h-bar_h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 1)
        
        # Results
        for i, (x, y, conf, name) in enumerate(results):
            cv2.circle(out, (x, y), 20, (0, 255, 0), 2)
            cv2.putText(out, str(i+1), (x-6, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            cv2.putText(out, f"{int(conf*100)}%", (x-20, y-25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)
        
        # Status
        cv2.rectangle(out, (5, 5), (280, 40), (30,30,30), -1)
        cv2.putText(out, f"Found: {len(results)} | Templates: {len(self.matcher.templates)}", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,255,0), 2)
        
        # Help
        cv2.rectangle(out, (5, h-35), (550, h-5), (30,30,30), -1)
        cv2.putText(out, "CLICK BAR: Add item | S: Scan | A: Auto-scan | ESC: Exit", (10, h-15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
        
        return out
    
    def run(self):
        print("=" * 55)
        print("Dream Memory - ULTRA FAST")
        print("Click items in BAR to save, then auto-find!")
        print("=" * 55)
        
        win = "Dream Memory FAST"
        cv2.namedWindow(win)
        cv2.setMouseCallback(win, self.add_item)
        
        last_scan = 0
        auto = False
        
        while self.running:
            self.screenshot = self.capture()
            
            # Auto scan every 0.5s
            if auto and time.time() - last_scan > 0.5:
                self.found = self.scan()
                last_scan = time.time()
            
            display = cv2.resize(self.screenshot, (800, 600))
            output = self.draw(cv2.resize(self.screenshot, (800, 600)), 
                             [(x*800//self.screenshot.shape[1], y*600//self.screenshot.shape[0], c, n) 
                              for x, y, c, n in self.found])
            
            cv2.imshow(win, output)
            
            key = cv2.waitKey(100) & 0xFF
            
            if key == 27:
                self.running = False
            elif key == ord('s') or key == ord('S'):
                self.found = self.scan()
                print(f"[SCAN] {len(self.found)} found")
            elif key == ord('a') or key == ord('A'):
                auto = not auto
                print(f"[AUTO] {'ON' if auto else 'OFF'}")
                if auto:
                    self.found = self.scan()
        
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        DreamMemoryFast().run()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
