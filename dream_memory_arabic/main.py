"""
مساعد ذاكرة الأحلام - نسخة عربية
تلقائي + واضح + بدون كليك
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
    """مساعد ذاكرة الأحلام."""
    
    def __init__(self):
        self.hwnd = None
        self.running = True
        self.screen = None
        self.auto_mode = True
        
        # Templates folder
        self.template_dir = "templates_arabic"
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        
        # Load saved templates
        self.templates = {}
        self._load_templates()
        
        if platform.system() == "Windows":
            self._find_window()
    
    def _find_window(self):
        """Find BlueStacks window."""
        try:
            self.hwnd = win32gui.FindWindow(None, "BlueStacks")
            
            if not self.hwnd:
                def callback(h, ctx):
                    if win32gui.IsWindowVisible(h):
                        title = win32gui.GetWindowText(h)
                        if title and "blue" in title.lower():
                            self.hwnd = h
                win32gui.EnumWindows(callback, None)
            
            if self.hwnd:
                rect = win32gui.GetWindowRect(self.hwnd)
                w = rect[2] - rect[0]
                h = rect[3] - rect[1]
                title = win32gui.GetWindowText(self.hwnd)
                print(f"[OK] Found: {title} ({w}x{h})")
        except Exception as e:
            print(f"[ERROR] {e}")
    
    def _load_templates(self):
        """Load saved templates."""
        for f in glob.glob(f"{self.template_dir}/*.png"):
            name = os.path.basename(f)[:-4]
            img = cv2.imread(f)
            if img is not None:
                self.templates[name] = img
        print(f"[OK] Loaded {len(self.templates)} templates")
    
    def _capture_screen(self):
        """Capture screen."""
        if self.hwnd and platform.system() == "Windows":
            try:
                l, t, r, b = win32gui.GetWindowRect(self.hwnd)
                w, h = r - l, b - t
                
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
    
    def _find_templates(self, image):
        """Find all templates in image."""
        results = []
        h, w = image.shape[:2]
        scene = image[:int(h*0.85), :]
        
        for name, template in self.templates.items():
            try:
                if template.shape[0] > scene.shape[0]:
                    continue
                
                result = cv2.matchTemplate(scene, template, cv2.TM_CCOEFF_NORMED)
                locations = np.where(result >= 0.65)
                
                for pt in zip(*locations[::-1]):
                    x = int(pt[0] + template.shape[1]//2)
                    y = int(pt[1] + template.shape[0]//2)
                    conf = float(result[pt[1], pt[0]])
                    results.append((x, y, conf, name))
            except:
                pass
        
        # Remove duplicates
        results = self._remove_dupes(results)
        return sorted(results, key=lambda x: x[2], reverse=True)[:15]
    
    def _remove_dupes(self, results):
        """Remove duplicates."""
        filtered = []
        for r in results:
            is_dup = any(abs(r[0]-f[0]) < 35 and abs(r[1]-f[1]) < 35 for f in filtered)
            if not is_dup:
                filtered.append(r)
        return filtered
    
    def _draw_results(self, image, results):
        """Draw results."""
        out = image.copy()
        h, w = image.shape[:2]
        
        # Top bar
        cv2.rectangle(out, (0, 0), (w, 55), (15, 15, 15), -1)
        
        # Title
        cv2.putText(out, "Dream Memory Helper", (15, 38), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Template count
        cv2.putText(out, f"Templates: {len(self.templates)}", (w-180, 38), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Draw circles
        for i, (x, y, conf, name) in enumerate(results):
            cv2.circle(out, (x, y), 30, (0, 255, 0), 3)
            cv2.putText(out, str(i+1), (x-10, y+10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
            cv2.putText(out, f"{int(conf*100)}%", (x-25, y-40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Bottom bar - Instructions
        cv2.rectangle(out, (0, h-50), (w, h), (15, 15, 15), -1)
        
        status = "AUTO ON" if self.auto_mode else "MANUAL"
        cv2.putText(out, f"[{status}]", (15, h-20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.putText(out, "1:Add 2:Auto 3:Scan ESC:Exit", (150, h-20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        if results:
            cv2.putText(out, f"Found: {len(results)} items!", 
                       (w-200, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return out
    
    def run(self):
        """Run the helper."""
        print("=" * 55)
        print("   Dream Memory Helper - Arabic Version")
        print("=" * 55)
        print("Instructions:")
        print("  1: Add template from request bar")
        print("  2: Toggle auto search")
        print("  3: Manual scan")
        print("  ESC: Exit")
        print("=" * 55)
        
        if not self.hwnd:
            print("[WARNING] BlueStacks not found!")
        
        window = "Dream Memory Helper [Arabic]"
        cv2.namedWindow(window)
        
        auto_mode = True
        last_scan = 0
        interval = 0.3
        results = []
        
        while self.running:
            # Capture
            self.screen = self._capture_screen()
            
            # Auto scan
            if auto_mode and time.time() - last_scan > interval:
                if self.templates:
                    results = self._find_templates(self.screen)
                    last_scan = time.time()
                    if results:
                        print(f"[FOUND] {len(results)} items")
            
            # Draw and show
            display = self._draw_results(self.screen, results)
            cv2.imshow(window, display)
            
            # Key
            key = cv2.waitKey(100) & 0xFF
            
            if key == 27:  # Exit
                self.running = False
            elif key == ord('1'):  # Add template
                if self.screen is not None:
                    h, w = self.screen.shape[:2]
                    bar = int(h * 0.15)
                    request_bar = self.screen[h-bar:h, :]
                    
                    # Show bar and wait for click
                    cv2.imshow("Click item to save", request_bar)
                    print("[INFO] Click on item, then press any key")
                    cv2.waitKey(0)
                    cv2.destroyWindow("Click item to save")
            elif key == ord('2'):  # Toggle auto
                auto_mode = not auto_mode
                mode = "AUTO" if auto_mode else "MANUAL"
                print(f"[MODE] {mode}")
            elif key == ord('3'):  # Manual scan
                if self.templates:
                    results = self._find_templates(self.screen)
                    print(f"[SCAN] Found {len(results)} items")
        
        cv2.destroyAllWindows()
        print("[OK] Goodbye!")


def main():
    try:
        DreamHelper().run()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
