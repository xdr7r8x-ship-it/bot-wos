"""
Dream Memory Helper - 9:16 Portrait Mode
✓ For BlueStacks 497x888
✓ Fast & Accurate
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


class DreamHelper:
    """Helper for 9:16 portrait mode (497x888)."""
    
    def __init__(self):
        self.hwnd = None
        self.running = True
        self.screen = None
        self.template_dir = "templates_9x16"
        self.templates = {}
        self.auto_mode = True
        self.threshold = 0.75
        self.scan_count = 0
        
        # Portrait mode settings
        self.width = 497
        self.height = 888
        self.bar_ratio = 0.12  # Bottom 12% is request bar
        
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        
        self._load_templates()
        
        if platform.system() == "Windows":
            self._find_window()
    
    def _find_window(self):
        """Find BlueStacks - AUTO DETECT SIZE."""
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
                self.width = r[2] - r[0]
                self.height = r[3] - r[1]
                # Auto detect ratio
                if self.height > self.width:
                    self.bar_ratio = 0.12  # Portrait
                    ratio_str = "9:16"
                else:
                    self.bar_ratio = 0.15  # Landscape
                    ratio_str = "16:9"
                
                print(f"[OK] Detected: {self.width}x{self.height} ({ratio_str})")
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
        """Capture screen."""
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
        """Find all matches."""
        results = []
        h, w = image.shape[:2]
        # Main scene (top 88%)
        scene = image[:int(h*(1-self.bar_ratio)), :]
        
        for name, template in self.templates.items():
            matches = []
            
            # Multi-scale for portrait
            for scale in [0.6, 0.8, 1.0, 1.2]:
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
            
            if matches:
                best = max(matches, key=lambda x: x[2])
                results.append(best + (name,))
        
        # Remove duplicates
        filtered = []
        for r in sorted(results, key=lambda x: x[2], reverse=True):
            if not any(abs(r[0]-f[0]) < 30 and abs(r[1]-f[1]) < 30 for f in filtered):
                filtered.append(r)
        
        return filtered[:10]
    
    def _draw(self, image, results):
        """Draw results - optimized for portrait."""
        out = image.copy()
        h, w = image.shape[:2]
        
        # Top bar (smaller for portrait)
        cv2.rectangle(out, (0, 0), (w, 45), (10, 10, 10), -1)
        cv2.putText(out, "DREAM MEMORY", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        mode = "[A]" if self.auto_mode else "[M]"
        color = (0, 255, 0) if self.auto_mode else (255, 200, 0)
        cv2.putText(out, mode, (w-50, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw circles - adjusted for portrait
        for i, (x, y, conf, name) in enumerate(results):
            # Circle
            cv2.circle(out, (x, y), 25, (0, 255, 0), 3)
            
            # Number
            cv2.putText(out, str(i+1), (x-8, y+6), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Confidence
            cv2.putText(out, f"{int(conf*100)}%", (x-22, y-32), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Bottom bar (request bar zone)
        bar_y = int(h * (1-self.bar_ratio))
        cv2.rectangle(out, (0, bar_y), (w, h), (20, 20, 20), -1)
        cv2.putText(out, "REQUEST BAR", (10, bar_y + 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        # Status bar
        cv2.rectangle(out, (0, h-40), (w, h), (10, 10, 10), -1)
        
        if results:
            cv2.putText(out, f"FOUND: {len(results)}", (10, h-15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.putText(out, "1:Add 2:Auto ESC", (w-150, h-15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 180, 180), 1)
        
        return out
    
    def run(self):
        """Run."""
        print("=" * 40)
        print("   DREAM MEMORY - AUTO SIZE")
        print("=" * 40)
        print(f"Detected: {self.width}x{self.height}")
        print("=" * 40)
        
        if not self.hwnd:
            print("[!] BlueStacks not found!")
        
        win = "Dream Memory"
        cv2.namedWindow(win)
        
        # Calculate scale to fit screen
        import ctypes
        user32 = ctypes.windll.user32
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
        
        # Scale to fit 80% of screen
        scale_w = (screen_w * 0.8) / self.width
        scale_h = (screen_h * 0.8) / self.height
        scale = min(scale_w, scale_h, 1.5)  # Max 1.5x
        
        display_w = int(self.width * scale)
        display_h = int(self.height * scale)
        
        print(f"[OK] Display: {display_w}x{display_h} (scale: {scale:.1f}x)")
        
        last_scan = 0
        interval = 0.25
        results = []
        
        while self.running:
            self.screen = self._capture()
            
            # Auto scan
            if self.auto_mode and time.time() - last_scan > interval:
                if self.templates:
                    results = self._find_all(self.screen)
                    last_scan = time.time()
                    self.scan_count += 1
            
            # Draw and resize for display
            display = self._draw(self.screen, results)
            display = cv2.resize(display, (display_w, display_h))
            
            cv2.imshow(win, display)
            
            key = cv2.waitKey(100) & 0xFF
            
            if key == 27:
                self.running = False
            elif key == ord('1'):
                if self.screen is not None:
                    sh, sw = self.screen.shape[:2]
                    bar = self.screen[sh-int(sh*self.bar_ratio):sh, :]
                    bar_disp = cv2.resize(bar, (display_w//2, display_h//4))
                    cv2.imshow("Click to save", bar_disp)
                    cv2.waitKey(0)
                    cv2.destroyWindow("Click to save")
            elif key == ord('2'):
                self.auto_mode = not self.auto_mode
                print(f"[MODE] {'AUTO' if self.auto_mode else 'MANUAL'}")
        
        cv2.destroyAllWindows()
        print(f"[OK] Done! Scans: {self.scan_count}")


if __name__ == "__main__":
    try:
        DreamHelper().run()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
