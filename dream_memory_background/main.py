"""
Dream Memory Helper - BACKGROUND VERSION
✓ بدون نافذة
✓ يعمل في الخلفية
✓ يرسم على الشاشة مباشرة
✓ بحث تلقائي
"""

import cv2
import numpy as np
import platform
import time
import os
import glob
import threading
import sys

# Windows imports
if platform.system() == "Windows":
    import win32gui
    import win32ui
    import win32con
    import win32api
    from ctypes import windll, Structure, c_int, POINTER
    from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM, HINSTANCE

# Transparent overlay window
class OverlayWindow:
    """نافذة شفافة للرسم على الشاشة."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.hwnd = None
        self.marks = []
        self.running = True
        
        if platform.system() == "Windows":
            self._create_window()
    
    def _create_window(self):
        """إنشاء نافذة شفافة."""
        try:
            # Get desktop window
            hwnd_parent = win32gui.GetDesktopWindow()
            
            # Register window class
            wc = win32gui.WNDCLASS()
            wc.lpszClassName = "DreamOverlay"
            wc.lpfnWndProc = self._wnd_proc
            try:
                win32gui.RegisterClass(wc)
            except:
                pass
            
            # Create window
            self.hwnd = win32gui.CreateWindow(
                "DreamOverlay",
                "Dream Memory",
                win32con.WS_POPUP | win32con.WS_VISIBLE,
                0, 0, self.width, self.height,
                0, 0, 0, None
            )
            
            # Make transparent and click-through
            ex_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(
                self.hwnd, win32con.GWL_EXSTYLE,
                ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            )
            
            # Set transparency
            win32gui.SetLayeredWindowAttributes(
                self.hwnd, 0, 200, win32con.LWA_ALPHA
            )
            
            print(f"[OK] Overlay created: {self.width}x{self.height}")
            
        except Exception as e:
            print(f"[ERROR] Overlay: {e}")
    
    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        """Window procedure."""
        if msg == win32con.WM_DESTROY:
            self.running = False
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    
    def update_marks(self, marks):
        """تحديث العلامات."""
        self.marks = marks
        if self.hwnd and platform.system() == "Windows":
            self._redraw()
    
    def _redraw(self):
        """إعادة رسم."""
        if not self.hwnd:
            return
        
        try:
            hdc = win32gui.GetDC(self.hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hdc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            # Create bitmap
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(mfc_dc, self.width, self.height)
            save_dc.SelectObject(bmp)
            
            # Draw on memory DC
            save_dc.PatBlt((0, 0), (self.width, self.height), win32con.BLACKNESS)
            
            # Draw circles
            for i, (x, y, conf) in enumerate(self.marks):
                # Circle
                save_dc.SelectObject(win32ui.CreatePen(win32con.PS_SOLID, 3, win32api.RGB(0, 255, 0)))
                save_dc.SelectObject(win32ui.CreateBrush(win32con.BS_NULL))
                save_dc.Ellipse((x-25, y-25, x+25, y+25))
                
                # Number
                save_dc.SetBkMode(win32con.TRANSPARENT)
                save_dc.SetTextColor(win32api.RGB(255, 255, 255))
                save_dc.TextOut(x-5, y-5, str(i+1))
                
                # Confidence
                save_dc.TextOut(x-20, y-35, f"{int(conf*100)}%")
            
            # Copy to screen
            win32gui.BitBlt(hdc, 0, 0, self.width, self.height, save_dc.GetSafeHdc(), 0, 0, win32con.SRCCOPY)
            
            # Cleanup
            win32gui.ReleaseDC(self.hwnd, hdc)
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.DeleteObject(bmp.GetHandle())
            
        except Exception as e:
            pass
    
    def close(self):
        """إغلاق."""
        if self.hwnd:
            try:
                win32gui.DestroyWindow(self.hwnd)
            except:
                pass


class DreamMemoryBackground:
    """نسخة تعمل في الخلفية."""
    
    def __init__(self):
        self.hwnd = None
        self.overlay = None
        self.running = True
        self.template_dir = "bg_templates"
        self.templates = {}
        self.threshold = 0.75
        self.scan_interval = 0.3
        self.bar_ratio = 0.12
        
        # Screen info
        self.screen_width = 497
        self.screen_height = 888
        
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        
        self._load_templates()
        self._find_window()
    
    def _find_window(self):
        """البحث عن نافذة."""
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
                self.screen_width = r[2] - r[0]
                self.screen_height = r[3] - r[1]
                print(f"[OK] Window: {self.screen_width}x{self.screen_height}")
                
                # Create overlay
                self.overlay = OverlayWindow(self.screen_width, self.screen_height)
        except Exception as e:
            print(f"[ERROR] {e}")
    
    def _load_templates(self):
        """تحميل القوالب."""
        for f in glob.glob(f"{self.template_dir}/*.png"):
            name = os.path.basename(f)[:-4]
            img = cv2.imread(f)
            if img is not None:
                self.templates[name] = img
        print(f"[OK] Templates: {len(self.templates)}")
    
    def _capture(self):
        """التقاط الشاشة."""
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
        
        return None
    
    def _find_all(self, image):
        """البحث."""
        if image is None:
            return []
        
        results = []
        h, w = image.shape[:2]
        scene = image[:int(h*(1-self.bar_ratio)), :]
        
        for name, template in self.templates.items():
            for scale in [0.6, 0.8, 1.0, 1.2]:
                try:
                    tw = int(template.shape[1]*scale)
                    th = int(template.shape[0]*scale)
                    if tw > scene.shape[1] or th > scene.shape[0]:
                        continue
                    
                    resized = cv2.resize(template, (tw, th))
                    result = cv2.matchTemplate(scene, resized, cv2.TM_CCOEFF_NORMED)
                    locations = np.where(result >= self.threshold)
                    
                    for pt in zip(*locations[::-1]):
                        x = int(pt[0] + tw//2)
                        y = int(pt[1] + th//2)
                        conf = float(result[pt[1], pt[0]])
                        results.append((x, y, conf))
                except:
                    pass
        
        # Remove duplicates
        filtered = []
        for r in sorted(results, key=lambda x: x[2], reverse=True):
            if not any(abs(r[0]-f[0]) < 30 and abs(r[1]-f[1]) < 30 for f in filtered):
                filtered.append(r)
        
        return filtered[:10]
    
    def run(self):
        """تشغيل."""
        print("=" * 50)
        print("   DREAM MEMORY - BACKGROUND MODE")
        print("=" * 50)
        print("Works in background!")
        print("Press Ctrl+C to exit")
        print("=" * 50)
        
        if not self.hwnd:
            print("[!] BlueStacks not found!")
            return
        
        last_scan = 0
        
        while self.running:
            try:
                # Capture
                screen = self._capture()
                
                # Scan
                if time.time() - last_scan > self.scan_interval:
                    if self.templates and screen is not None:
                        results = self._find_all(screen)
                        
                        # Update overlay
                        if self.overlay:
                            self.overlay.update_marks(results)
                        
                        if results:
                            print(f"[FOUND] {len(results)} items")
                    
                    last_scan = time.time()
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(1)
        
        # Cleanup
        if self.overlay:
            self.overlay.close()
        
        print("[OK] Stopped")


if __name__ == "__main__":
    try:
        DreamMemoryBackground().run()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
