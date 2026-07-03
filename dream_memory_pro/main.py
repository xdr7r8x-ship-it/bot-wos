"""
Dream Memory Helper - PRO VERSION
✓ دقيق جداً
✓ ثقة قوية (85%+)
✓ سريع (0.2 ثانية)
"""

import cv2
import numpy as np
import mss
import platform
import time
import os
import glob

if platform.system() == "Windows":
    import win32gui
    import win32ui
    from ctypes import windll


class ProHelper:
    """مساعد محترف - بحث دقيق وسريع."""
    
    def __init__(self):
        self.hwnd = None
        self.running = True
        self.screen = None
        self.template_dir = "pro_templates"
        self.templates = {}
        self.auto_mode = True
        self.threshold = 0.80  # ثقة قوية 80%+
        self.scan_count = 0
        
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        
        self._load_templates()
        
        if platform.system() == "Windows":
            self._find_window()
    
    def _find_window(self):
        """Find BlueStacks."""
        try:
            self.hwnd = win32gui.FindWindow(None, "BlueStacks")
            if not self.hwnd:
                def cb(h, c):
                    if win32gui.IsWindowVisible(h):
                        t = win32gui.GetWindowText(h)
                        if t and "blue" in t.lower():
                            self.hwnd = h
                win32gui.EnumWindows(cb, None)
            
            if self.hwnd:
                r = win32gui.GetWindowRect(self.hwnd)
                w, h = r[2]-r[0], r[3]-r[1]
                print(f"[OK] Window: {w}x{h}")
        except:
            pass
    
    def _load_templates(self):
        """Load templates."""
        for f in glob.glob(f"{self.template_dir}/*.png"):
            name = os.path.basename(f)[:-4]
            img = cv2.imread(f)
            if img is not None:
                self.templates[name] = img
        print(f"[OK] Templates: {len(self.templates)}")
    
    def _capture(self):
        """Fast capture."""
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
                img = np.frombuffer(data, dtype=np.uint8).reshape(
                    (info['bmHeight'], info['bmWidth'], 4))
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
    
    def _find_all(self, image):
        """Find all matches with high confidence - multi scale."""
        results = []
        h, w = image.shape[:2]
        scene = image[:int(h*0.85), :]
        
        for name, template in self.templates.items():
            matches = []
            
            # Multi-scale matching for precision
            for scale in [0.7, 0.85, 1.0, 1.15, 1.3]:
                try:
                    tw, th = int(template.shape[1]*scale), int(template.shape[0]*scale)
                    if tw > scene.shape[1] or th > scene.shape[0]:
                        continue
                    
                    resized = cv2.resize(template, (tw, th))
                    result = cv2.matchTemplate(scene, resized, cv2.TM_CCOEFF_NORMED)
                    locations = np.where(result >= self.threshold)
                    
                    for pt in zip(*locations[::-1]):
                        x = int(pt[0] + tw//2)
                        y = int(pt[1] + th//2)
                        conf = float(result[pt[1], pt[0]])
                        matches.append((x, y, conf))
                except:
                    pass
            
            # Keep best match for this template
            if matches:
                best = max(matches, key=lambda x: x[2])
                results.append(best + (name,))
        
        # Remove duplicates
        filtered = []
        for r in sorted(results, key=lambda x: x[2], reverse=True):
            if not any(abs(r[0]-f[0]) < 40 and abs(r[1]-f[1]) < 40 for f in filtered):
                filtered.append(r)
        
        return filtered[:20]
    
    def _draw(self, image, results):
        """Draw results."""
        out = image.copy()
        h, w = image.shape[:2]
        
        # Top bar
        cv2.rectangle(out, (0, 0), (w, 60), (10, 10, 10), -1)
        cv2.putText(out, "DREAM MEMORY PRO", (15, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        status = "[AUTO]" if self.auto_mode else "[MANUAL]"
        color = (0, 255, 0) if self.auto_mode else (255, 200, 0)
        cv2.putText(out, status, (w-120, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw circles with numbers
        for i, (x, y, conf, name) in enumerate(results):
            # Big green circle
            cv2.circle(out, (x, y), 35, (0, 255, 0), 4)
            
            # Number
            cv2.putText(out, str(i+1), (x-12, y+12), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
            
            # Confidence %
            cv2.putText(out, f"{int(conf*100)}%", (x-30, y-45), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Bottom bar
        cv2.rectangle(out, (0, h-55), (w, h), (10, 10, 10), -1)
        
        # Stats
        cv2.putText(out, f"Scans: {self.scan_count}", (15, h-25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        # Found count
        if results:
            cv2.putText(out, f"FOUND: {len(results)}", (w//2-60, h-25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Help
        cv2.putText(out, "1:Add 2:Auto 3:Scan ESC:Exit", (w-280, h-25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
        
        return out
    
    def run(self):
        """Run."""
        print("=" * 50)
        print("   DREAM MEMORY PRO - HIGH PRECISION")
        print("=" * 50)
        print("Confidence: 80%+")
        print("Multi-scale matching enabled")
        print("=" * 50)
        
        if not self.hwnd:
            print("[!] BlueStacks not found!")
        
        win = "Dream Memory PRO"
        cv2.namedWindow(win)
        
        last_scan = 0
        interval = 0.2  # 200ms - SUPER FAST!
        results = []
        
        while self.running:
            # Capture
            self.screen = self._capture()
            
            # Auto scan
            if self.auto_mode and time.time() - last_scan > interval:
                if self.templates:
                    results = self._find_all(self.screen)
                    last_scan = time.time()
                    self.scan_count += 1
            
            # Draw and show
            display = self._draw(self.screen, results)
            cv2.imshow(win, display)
            
            key = cv2.waitKey(50) & 0xFF
            
            if key == 27:
                self.running = False
            elif key == ord('1'):  # Add template
                if self.screen is not None:
                    sh, sw = self.screen.shape[:2]
                    bar = self.screen[sh-int(sh*0.15):sh, :]
                    cv2.imshow("Click to save template", bar)
                    cv2.waitKey(0)
                    cv2.destroyWindow("Click to save template")
            elif key == ord('2'):  # Toggle auto
                self.auto_mode = not self.auto_mode
                print(f"[MODE] {'AUTO' if self.auto_mode else 'MANUAL'}")
            elif key == ord('3'):  # Manual scan
                if self.templates:
                    results = self._find_all(self.screen)
                    print(f"[SCAN] Found: {len(results)}")
        
        cv2.destroyAllWindows()
        print(f"[OK] Total scans: {self.scan_count}")


if __name__ == "__main__":
    try:
        ProHelper().run()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
