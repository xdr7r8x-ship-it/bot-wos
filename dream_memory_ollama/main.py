# Dream Memory - Ollama Vision Overlay
# Main application - STABLE VERSION

import sys
import time
import threading
import base64
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QApplication

import config
from capture import ScreenCapture
from analyzer import OllamaAnalyzer
from overlay import TransparentOverlay


class AnalysisSignals(QObject):
    """Signals for thread-safe analysis updates."""
    status_changed = pyqtSignal(str)
    marks_updated = pyqtSignal(list)


class DreamMemoryApp:
    """Main application."""

    def __init__(self):
        print("APP STARTED")
        
        self.running = True
        self.game_rect = None
        self.analysis_in_progress = False
        self.analysis_count = 0

        # Thread-safe signals
        self.signals = AnalysisSignals()

        # Components
        self.capture = ScreenCapture()
        self.analyzer = OllamaAnalyzer()

        # Check Ollama status
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
        """Find BlueStacks window."""
        if self.capture.find_window():
            print("BLUESTACKS FOUND")
            self.game_rect = self.capture.get_geometry()
            if self.game_rect:
                self.overlay.update_geometry(*self.game_rect)
        else:
            print("WAITING FOR BLUESTACKS")

    def force_analyze(self):
        """Force analysis on F10."""
        # Refresh geometry
        self._find_game()
            
        if not self.game_rect:
            print("NO WINDOW")
            self.signals.status_changed.emit(config.STATUS_NO_WINDOW)
            return
            
        if self.analysis_in_progress:
            print("ANALYSIS IN PROGRESS")
            return
            
        print("F10 FORCE ANALYZE")
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
        try:
            # Capture images
            scene = self.capture.capture_scene()
            if scene is None:
                self._on_analysis_complete([], "CAPTURE FAILED")
                return

            bar = self.capture.capture_request_bar()

            # Encode
            scene_b64 = self.capture.encode_jpeg(scene)
            if scene_b64 is None:
                self._on_analysis_complete([], "ENCODE FAILED")
                return

            scene_b64_str = base64.b64encode(scene_b64).decode('utf-8')
            bar_b64_str = ""
            if bar:
                bar_bytes = self.capture.encode_jpeg(bar)
                if bar_bytes:
                    bar_b64_str = base64.b64encode(bar_bytes).decode('utf-8')

            # Analyze
            print("ANALYSIS STARTED")
            result = self.analyzer.analyze(bar_b64_str, scene_b64_str)
            print("ANALYSIS FINISHED")

            self._on_analysis_complete(result.objects, result.error)

        except Exception as e:
            print(f"ANALYSIS ERROR: {e}")
            self._on_analysis_complete([], str(e))

    def _on_analysis_complete(self, objects, error: str):
        """Handle analysis completion on main thread."""
        self.analysis_in_progress = False

        if error:
            print(f"ANALYSIS ERROR: {error}")
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

    # Hotkeys
    QShortcut(QKeySequence("F8"), app, activated=dream.toggle_overlay)
    QShortcut(QKeySequence("F10"), app, activated=dream.force_analyze)
    QShortcut(QKeySequence("Escape"), app, activated=lambda: sys.exit(0))

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

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
