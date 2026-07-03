# Dream Memory - Ollama Vision Overlay
# Main application - HARDENED VERSION

import sys
import time
import threading
import base64
import ctypes
from ctypes import wintypes
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject, QThread
from PyQt6.QtWidgets import QApplication

import config
from capture import ScreenCapture
from analyzer import OllamaAnalyzer
from overlay import TransparentOverlay


# Windows constants
WM_HOTKEY = 0x0312
MOD_NONE = 0x0000
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

# Hotkey IDs
HOTKEY_F8 = 1
HOTKEY_F10 = 2
HOTKEY_ESC = 3


class AnalysisSignals(QObject):
    """Signals for thread-safe analysis updates."""
    status_changed = pyqtSignal(str)
    marks_updated = pyqtSignal(list)


class HotkeyThread(QThread):
    """Thread for handling Windows global hotkeys."""
    
    toggle_overlay = pyqtSignal()
    force_analyze = pyqtSignal()
    exit_app = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.running = True
        self._user32 = ctypes.windll.user32
        
    def run(self):
        """Run hotkey message loop."""
        msg = wintypes.MSG()
        
        while self.running:
            # PeekMessage with timeout
            ret = self._user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1)
            if ret:
                if msg.message == WM_HOTKEY:
                    if msg.wParam == HOTKEY_F8:
                        self.toggle_overlay.emit()
                    elif msg.wParam == HOTKEY_F10:
                        self.force_analyze.emit()
                    elif msg.wParam == HOTKEY_ESC:
                        self.exit_app.emit()
                    # Remove hotkey after triggered
                    self._user32.UnregisterHotKey(None, msg.wParam)
                    
                # Translate and dispatch
                self._user32.TranslateMessage(ctypes.byref(msg))
                self._user32.DispatchMessageW(ctypes.byref(msg))
            
            time.sleep(0.01)
    
    def stop(self):
        """Stop hotkey thread."""
        self.running = False


class DreamMemoryApp:
    """Main application."""

    def __init__(self):
        print("APP STARTED")
        
        self.running = True
        self.game_rect = None
        self.analysis_in_progress = False
        self.analysis_count = 0
        self._window_was_found = False

        # Thread-safe signals
        self.signals = AnalysisSignals()

        # Components
        self.capture = ScreenCapture()
        self.analyzer = OllamaAnalyzer()

        # Check Ollama status
        print("CHECKING OLLAMA")
        if self.analyzer.is_available():
            print("OLLAMA CHECK OK")
        else:
            print("OLLAMA NOT RUNNING")
            
        if self.analyzer.model_installed:
            print("MODEL FOUND")
        else:
            print("MODEL NOT FOUND")
            print(f"Run: ollama pull {config.OLLAMA_MODEL}")

        # Overlay
        self.overlay = TransparentOverlay()

        # Find window
        self._find_game()

        # Connect signals to overlay
        self.signals.status_changed.connect(self.overlay.update_status)
        self.signals.marks_updated.connect(self.overlay.update_marks)

        # Show UI
        self.overlay.show_overlay()
        print("OVERLAY STARTED")
        print("READY")

    def _find_game(self):
        """Find BlueStacks window - only print on status change."""
        found = self.capture.find_window()
        
        if found:
            if not self._window_was_found:
                print("BLUESTACKS FOUND")
                self._window_was_found = True
            self.game_rect = self.capture.get_geometry()
            if self.game_rect:
                self.overlay.update_geometry(*self.game_rect)
        else:
            if self._window_was_found:
                print("WAITING FOR BLUESTACKS")
                self._window_was_found = False
            self.game_rect = None

    def force_analyze(self):
        """Force analysis on F10."""
        print("F10 RECEIVED")
        
        # Refresh geometry
        self._find_game()
            
        if not self.game_rect:
            print("NO WINDOW")
            self.signals.status_changed.emit(config.STATUS_NO_WINDOW)
            return
            
        if self.analysis_in_progress:
            print("ANALYSIS IN PROGRESS")
            return
            
        self._run_analysis()

    def _run_analysis(self):
        """Run analysis in background thread."""
        if self.analysis_in_progress:
            return
            
        if not self.analyzer.is_available():
            self.signals.status_changed.emit(config.STATUS_API_ERROR)
            return

        self.analysis_in_progress = True
        self.analysis_count += 1
        self.signals.status_changed.emit(config.STATUS_ANALYZING)

        # Run in thread
        thread = threading.Thread(target=self._analysis_worker, daemon=True)
        thread.start()

    def _analysis_worker(self):
        """Background analysis worker."""
        start_time = time.time()
        
        try:
            # Capture once - both scene and request bar
            print("CAPTURE STARTED")
            scene, request_bar = self.capture.capture_full_once()
            
            if scene is None:
                print("CAPTURE FAILED")
                self._on_analysis_complete([], "CAPTURE FAILED")
                return
                
            print("CAPTURE OK")
            
            # Encode
            scene_b64 = self.capture.encode_jpeg(scene)
            if scene_b64 is None:
                self._on_analysis_complete([], "ENCODE FAILED")
                return

            scene_b64_str = base64.b64encode(scene_b64).decode('utf-8')
            bar_b64_str = ""
            if request_bar:
                bar_bytes = self.capture.encode_jpeg(request_bar)
                if bar_bytes:
                    bar_b64_str = base64.b64encode(bar_bytes).decode('utf-8')

            # Analyze
            print("ANALYSIS STARTED")
            result = self.analyzer.analyze(bar_b64_str, scene_b64_str)
            elapsed = time.time() - start_time
            print(f"ANALYSIS FINISHED in {elapsed:.1f} seconds")

            self._on_analysis_complete(result.objects, result.error)

        except Exception as e:
            print(f"ANALYSIS ERROR: {e}")
            self._on_analysis_complete([], str(e))
        finally:
            # Ensure analysis_in_progress is always reset
            pass

    def _on_analysis_complete(self, objects, error: str):
        """Handle analysis completion on main thread."""
        self.analysis_in_progress = False

        if error:
            print(f"ERROR: {error}")
            self.signals.status_changed.emit(config.STATUS_API_ERROR)
        elif not objects:
            print("NO MARKS")
            self.signals.status_changed.emit(config.STATUS_NO_MARKS)
            self.signals.marks_updated.emit([])
        else:
            print(f"FOUND {len(objects)} OBJECTS")
            self.signals.status_changed.emit(config.STATUS_LIVE)
            self.signals.marks_updated.emit(objects)

    def toggle_overlay(self):
        """Toggle overlay visibility."""
        self.overlay.toggle_overlay()

    def refresh_geometry(self):
        """Refresh overlay geometry."""
        self._find_game()
        if self.game_rect:
            self.overlay.update_geometry(*self.game_rect)

    def cleanup(self):
        """Cleanup resources."""
        self.running = False


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Create app
    dream = DreamMemoryApp()
    
    # Setup hotkeys using Windows API
    user32 = ctypes.windll.user32
    
    # Register hotkeys (works even when BlueStacks is focused)
    # F8 = VK_F8 = 0x77
    user32.RegisterHotKey(None, HOTKEY_F8, MOD_NONE, 0x77)
    # F10 = VK_F10 = 0x79
    user32.RegisterHotKey(None, HOTKEY_F10, MOD_NONE, 0x79)
    # ESC = VK_ESCAPE = 0x1B
    user32.RegisterHotKey(None, HOTKEY_ESC, MOD_NONE, 0x1B)
    
    # Connect hotkey signals
    dream.signals.status_changed.connect(lambda s: None)  # Keep reference
    
    # Create hotkey message thread
    hotkey_thread = HotkeyThread()
    hotkey_thread.toggle_overlay.connect(dream.toggle_overlay)
    hotkey_thread.force_analyze.connect(dream.force_analyze)
    hotkey_thread.exit_app.connect(lambda: sys.exit(0))
    hotkey_thread.start()
    
    # Geometry refresh timer (slower to reduce spam)
    geo_timer = QTimer()
    geo_timer.timeout.connect(dream.refresh_geometry)
    geo_timer.start(config.GEOMETRY_REFRESH_MS)

    print("=" * 50)
    print("DREAM MEMORY - OLLAMA VISION")
    print(f"Model: {config.OLLAMA_MODEL}")
    print("=" * 50)
    print("F8 - Toggle overlay")
    print("F10 - Analyze scene")
    print("ESC - Exit")
    print("=" * 50)

    # Run app
    exit_code = app.exec()
    
    # Cleanup
    hotkey_thread.stop()
    hotkey_thread.wait()
    user32.UnregisterHotKey(None, HOTKEY_F8)
    user32.UnregisterHotKey(None, HOTKEY_F10)
    user32.UnregisterHotKey(None, HOTKEY_ESC)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
