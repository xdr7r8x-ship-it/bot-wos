# Dream Memory - Ollama Vision Overlay
# Main application - LIVE AUTO MODE

import sys
import time
import threading
import base64
import hashlib
import win32gui
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication

import config
from capture import ScreenCapture
from analyzer import OllamaAnalyzer
from overlay import TransparentOverlay


# Windows hotkey constants
WM_HOTKEY = 0x0312
MOD_NONE = 0x0000
HOTKEY_F8 = 1
HOTKEY_ESC = 2


class Signals(QObject):
    """Thread-safe signals."""
    status_changed = pyqtSignal(str)
    marks_updated = pyqtSignal(list)
    toggle_overlay = pyqtSignal()
    force_analyze = pyqtSignal()
    exit_app = pyqtSignal()


class DreamMemoryApp:
    """Main application with live auto watching."""

    def __init__(self):
        print("APP STARTED")
        
        self.running = True
        self.viewport_rect = None
        self.analysis_in_progress = False
        self.pending_analysis = False
        self._last_bar_hash = None
        self._last_change_time = 0
        self._analysis_count = 0

        # Signals
        self.signals = Signals()

        # Components
        self.capture = ScreenCapture()
        self.analyzer = OllamaAnalyzer()

        # Check Ollama
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

        # Overlay (hidden until viewport ready)
        self.overlay = TransparentOverlay()
        self.overlay.hide()

        # Connect signals
        self.signals.status_changed.connect(self.overlay.update_status)
        self.signals.marks_updated.connect(self.overlay.update_marks)
        self.signals.toggle_overlay.connect(self._toggle_overlay)
        self.signals.force_analyze.connect(self._force_analyze)
        self.signals.exit_app.connect(lambda: sys.exit(0))

        # Setup viewport
        self._setup_viewport()

    def _setup_viewport(self):
        """Setup viewport and show overlay."""
        if not self.capture.find_window():
            print("WAITING FOR BLUESTACKS")
            return
            
        print("BLUESTACKS FOUND")
        
        viewport = self.capture.get_viewport()
        if not viewport:
            print("MANUAL VIEWPORT INVALID")
            return
            
        vx, vy, vw, vh = viewport
        print(f"VIEWPORT READY: {vx} {vy} {vw} {vh}")
        
        self.viewport_rect = viewport
        self.overlay.update_geometry(vx, vy, vw, vh)
        self.overlay.show()
        print(f"OVERLAY MOVED TO VIEWPORT: {vx} {vy} {vw} {vh}")
        
        # Start live watcher
        self._start_live_watcher()
        
        print("LIVE WATCH STARTED")
        self.signals.status_changed.emit(config.STATUS_WATCHING)
        
        # Auto analyze immediately
        QTimer.singleShot(500, self._run_analysis)

    def _start_live_watcher(self):
        """Start the live request bar watcher."""
        if not config.AUTO_WATCH_REQUEST_BAR:
            return
            
        self._watch_timer = QTimer()
        self._watch_timer.timeout.connect(self._check_request_bar)
        self._watch_timer.start(config.WATCH_INTERVAL_MS)
        
        # Initial capture
        self._capture_initial_request_bar()

    def _capture_initial_request_bar(self):
        """Capture and hash initial request bar."""
        scene, request_bar = self.capture.capture_viewport()
        if request_bar:
            bar_bytes = request_bar.tobytes()
            self._last_bar_hash = hashlib.md5(bar_bytes).hexdigest()
            print("REQUEST BAR INITIALIZED")

    def _check_request_bar(self):
        """Check request bar for changes."""
        if self.analysis_in_progress:
            return
            
        # Check cooldown
        now = time.time()
        if now - self._last_change_time < config.API_COOLDOWN_MS / 1000:
            return
            
        # Capture request bar
        scene, request_bar = self.capture.capture_viewport()
        if request_bar is None:
            return
            
        # Hash request bar
        bar_bytes = request_bar.tobytes()
        bar_hash = hashlib.md5(bar_bytes).hexdigest()
        
        # Check for change
        if self._last_bar_hash is None:
            self._last_bar_hash = bar_hash
            return
            
        if bar_hash != self._last_bar_hash:
            # Debounce
            if now - self._last_change_time < config.REQUEST_DEBOUNCE_MS / 1000:
                return
                
            print("REQUEST BAR CHANGED")
            self._last_bar_hash = bar_hash
            self._last_change_time = now
            self._run_analysis()

    def _force_analyze(self):
        """Force analysis."""
        print("FORCE ANALYZE RECEIVED")
        self._run_analysis()

    def _run_analysis(self):
        """Run analysis in background."""
        if self.analysis_in_progress:
            self.pending_analysis = True
            print("PENDING ANALYSIS QUEUED")
            return
            
        if not self.analyzer.is_available():
            self.signals.status_changed.emit(config.STATUS_API_ERROR)
            return

        self.analysis_in_progress = True
        self._analysis_count += 1
        self.signals.status_changed.emit(config.STATUS_ANALYZING)
        print("AUTO ANALYSIS STARTED")

        thread = threading.Thread(target=self._analysis_worker, daemon=True)
        thread.start()

    def _analysis_worker(self):
        """Background analysis worker."""
        start_time = time.time()
        
        try:
            scene, request_bar = self.capture.capture_viewport()
            
            if scene is None:
                self._on_analysis_complete([], "CAPTURE FAILED")
                return
            
            # Encode images
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
            result = self.analyzer.analyze(bar_b64_str, scene_b64_str)
            elapsed = time.time() - start_time
            print(f"AUTO ANALYSIS FINISHED in {elapsed:.1f} seconds")

            self._on_analysis_complete(result.objects, result.error)

        except Exception as e:
            print(f"ERROR: {e}")
            self._on_analysis_complete([], str(e))

    def _on_analysis_complete(self, objects, error: str):
        """Handle analysis completion."""
        self.analysis_in_progress = False

        if error:
            if "TIMEOUT" in error.upper():
                print("TIMEOUT")
                self.signals.status_changed.emit(config.STATUS_TIMEOUT)
            else:
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

        # Check for pending analysis
        if self.pending_analysis:
            self.pending_analysis = False
            print("PENDING ANALYSIS STARTED")
            QTimer.singleShot(100, self._run_analysis)

    def _toggle_overlay(self):
        """Toggle overlay visibility."""
        if self.viewport_rect:
            self.overlay.toggle_overlay()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Create app
    dream = DreamMemoryApp()
    
    # Hotkeys using win32gui
    def hotkey_loop():
        win32gui.RegisterHotKey(None, HOTKEY_F8, MOD_NONE, 0x77)  # F8
        win32gui.RegisterHotKey(None, HOTKEY_ESC, MOD_NONE, 0x1B)  # ESC
        
        try:
            msg = win32gui.GetMessage(None, 0, 0)
            while msg[1]:
                msg = msg[1]
                if msg.message == WM_HOTKEY:
                    if msg.wParam == HOTKEY_F8:
                        dream.signals.toggle_overlay.emit()
                    elif msg.wParam == HOTKEY_ESC:
                        dream.signals.exit_app.emit()
                    win32gui.UnregisterHotKey(None, msg.wParam)
                    if msg.wParam == HOTKEY_F8:
                        win32gui.RegisterHotKey(None, HOTKEY_F8, MOD_NONE, 0x77)
                    elif msg.wParam == HOTKEY_ESC:
                        win32gui.RegisterHotKey(None, HOTKEY_ESC, MOD_NONE, 0x1B)
                msg = win32gui.GetMessage(None, 0, 0)
        except:
            pass

    hotkey_thread = threading.Thread(target=hotkey_loop, daemon=True)
    hotkey_thread.start()

    print("=" * 50)
    print("DREAM MEMORY - LIVE AUTO MODE")
    print(f"Model: {config.OLLAMA_MODEL}")
    print("=" * 50)
    print("F8 - Toggle overlay")
    print("ESC - Exit")
    print("=" * 50)
    print("READY")

    exit_code = app.exec()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
