# Dream Memory - Ollama Vision Overlay
# Main application - VIEWPORT VERSION

import sys
import time
import threading
import base64
import win32gui
import win32con
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication

import config
from capture import ScreenCapture
from analyzer import OllamaAnalyzer
from overlay import TransparentOverlay


# Windows hotkey constants
WM_HOTKEY = 0x0312
MOD_NONE = 0x0000

# Hotkey IDs
HOTKEY_F8 = 1
HOTKEY_F10 = 2
HOTKEY_ESC = 3


class AnalysisSignals(QObject):
    """Signals for thread-safe analysis updates."""
    status_changed = pyqtSignal(str)
    marks_updated = pyqtSignal(list)


class HotkeySignals(QObject):
    """Signals for hotkey events."""
    toggle_overlay = pyqtSignal()
    force_analyze = pyqtSignal()
    exit_app = pyqtSignal()


class HotkeyThread:
    """Thread for handling Windows global hotkeys using pywin32."""
    
    def __init__(self, signals):
        self.signals = signals
        self.running = True
        self._thread = None
        
    def start(self):
        """Start hotkey thread."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        
    def stop(self):
        """Stop hotkey thread."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=1)
            
    def _run(self):
        """Run hotkey message loop."""
        # Register hotkeys using win32gui
        win32gui.RegisterHotKey(None, HOTKEY_F8, MOD_NONE, 0x77)
        win32gui.RegisterHotKey(None, HOTKEY_F10, MOD_NONE, 0x79)
        win32gui.RegisterHotKey(None, HOTKEY_ESC, MOD_NONE, 0x1B)
        
        print("GLOBAL HOTKEYS REGISTERED")
        
        try:
            msg = win32gui.GetMessage(None, 0, 0)
            while self.running and msg[1]:
                msg = msg[1]
                
                if msg.message == WM_HOTKEY:
                    if msg.wParam == HOTKEY_F8:
                        print("F8 RECEIVED")
                        self.signals.toggle_overlay.emit()
                    elif msg.wParam == HOTKEY_F10:
                        print("F10 RECEIVED")
                        self.signals.force_analyze.emit()
                    elif msg.wParam == HOTKEY_ESC:
                        print("ESC RECEIVED")
                        self.signals.exit_app.emit()
                    # Unregister after triggered
                    win32gui.UnregisterHotKey(None, msg.wParam)
                    # Re-register for next use
                    if msg.wParam == HOTKEY_F8:
                        win32gui.RegisterHotKey(None, HOTKEY_F8, MOD_NONE, 0x77)
                    elif msg.wParam == HOTKEY_F10:
                        win32gui.RegisterHotKey(None, HOTKEY_F10, MOD_NONE, 0x79)
                    elif msg.wParam == HOTKEY_ESC:
                        win32gui.RegisterHotKey(None, HOTKEY_ESC, MOD_NONE, 0x1B)
                
                msg = win32gui.GetMessage(None, 0, 0)
        except Exception as e:
            print(f"[ERROR] Hotkey thread: {e}")
        finally:
            # Unregister all hotkeys
            try:
                win32gui.UnregisterHotKey(None, HOTKEY_F8)
                win32gui.UnregisterHotKey(None, HOTKEY_F10)
                win32gui.UnregisterHotKey(None, HOTKEY_ESC)
            except:
                pass


class DreamMemoryApp:
    """Main application."""

    def __init__(self):
        print("APP STARTED")
        
        self.running = True
        self.viewport_rect = None
        self.analysis_in_progress = False
        self.analysis_count = 0
        self._window_was_found = False
        self._viewport_was_found = False
        self._overlay_shown = False

        # Thread-safe signals
        self.signals = AnalysisSignals()
        self.hotkey_signals = HotkeySignals()

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

        # Create overlay (hidden initially)
        self.overlay = TransparentOverlay()
        self.overlay.hide()
        self.overlay.update_status(config.STATUS_WAITING)

        # Connect signals to overlay
        self.signals.status_changed.connect(self.overlay.update_status)
        self.signals.marks_updated.connect(self.overlay.update_marks)

        # Find window and viewport
        self._find_viewport()

        # Show overlay if viewport found
        if self.viewport_rect:
            vx, vy, vw, vh = self.viewport_rect
            self.overlay.update_geometry(vx, vy, vw, vh)
            self.overlay.show()
            self.overlay.update_status(config.STATUS_READY)
            print("OVERLAY MOVED TO VIEWPORT:", vx, vy, vw, vh)
            self._overlay_shown = True
        else:
            print("NO VIEWPORT - RETRYING...")

        print("READY")

    def _find_viewport(self):
        """Find BlueStacks and detect game viewport."""
        if self.capture.find_window():
            if not self._window_was_found:
                print("BLUESTACKS FOUND")
                self._window_was_found = True
            
            # Get client rect
            client_rect = self.capture.get_client_geometry()
            if client_rect:
                cx, cy, cw, ch = client_rect
                print(f"CLIENT RECT: {cx} {cy} {cw} {ch}")
            
            # Capture to detect viewport
            scene, bar = self.capture.capture_full_once()
            if scene:
                viewport = self.capture.get_viewport_geometry()
                if viewport:
                    vx, vy, vw, vh = viewport
                    if not self._viewport_was_found:
                        print(f"GAME VIEWPORT FOUND: {vx} {vy} {vw} {vh}")
                        self._viewport_was_found = True
                    self.viewport_rect = viewport
                    return
                    
            # Viewport not found
            if self._viewport_was_found:
                print("GAME VIEWPORT LOST")
                self._viewport_was_found = False
            self.viewport_rect = None
        else:
            if self._window_was_found:
                print("WAITING FOR BLUESTACKS")
                self._window_was_found = False
                self._viewport_was_found = False
            self.viewport_rect = None

    def force_analyze(self):
        """Force analysis on F10."""
        self._find_viewport()
            
        if not self.viewport_rect:
            print("NO VIEWPORT")
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
            # Capture viewport
            print("CAPTURE STARTED")
            scene, request_bar = self.capture.capture_full_once()
            
            if scene is None:
                print("CAPTURE FAILED")
                self._on_analysis_complete([], "CAPTURE FAILED")
                return
            
            viewport = self.capture.get_viewport_geometry()
            if viewport:
                vx, vy, vw, vh = viewport
                print(f"VIEWPORT: {vx} {vy} {vw} {vh}")
            
            print(f"CAPTURE SIZE: {scene.width} {scene.height}")
            print(f"SCENE SIZE: {scene.width} {scene.height}")
            if request_bar:
                print(f"REQUEST BAR SIZE: {request_bar.width} {request_bar.height}")
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
        if self.viewport_rect:
            self.overlay.toggle_overlay()

    def refresh_geometry(self):
        """Refresh viewport geometry."""
        old_viewport = self.viewport_rect
        
        self._find_viewport()
        
        if self.viewport_rect and not self._overlay_shown:
            # First time viewport found - show overlay
            vx, vy, vw, vh = self.viewport_rect
            self.overlay.update_geometry(vx, vy, vw, vh)
            self.overlay.show()
            self.overlay.update_status(config.STATUS_READY)
            print("OVERLAY MOVED TO VIEWPORT:", vx, vy, vw, vh)
            self._overlay_shown = True
        elif self.viewport_rect and old_viewport != self.viewport_rect:
            # Viewport changed - update
            vx, vy, vw, vh = self.viewport_rect
            self.overlay.update_geometry(vx, vy, vw, vh)
            print("OVERLAY MOVED TO VIEWPORT:", vx, vy, vw, vh)
        elif not self.viewport_rect and self._overlay_shown:
            # Viewport lost - hide overlay
            self.overlay.hide()
            self.overlay.update_status(config.STATUS_WAITING)
            self._overlay_shown = False

    def cleanup(self):
        """Cleanup resources."""
        self.running = False


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Create app
    dream = DreamMemoryApp()
    
    # Create hotkey handler
    hotkey = HotkeyThread(dream.hotkey_signals)
    
    # Connect hotkey signals
    dream.hotkey_signals.toggle_overlay.connect(dream.toggle_overlay)
    dream.hotkey_signals.force_analyze.connect(dream.force_analyze)
    dream.hotkey_signals.exit_app.connect(app.quit)
    
    # Start hotkey thread
    hotkey.start()
    
    # Geometry refresh timer
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
    hotkey.stop()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
