# Dream Memory - Ollama Vision Overlay
# Main application

import sys
import time
import threading
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QApplication

import config
from capture import ScreenCapture
from analyzer import OllamaAnalyzer
from request_watcher import RequestWatcher
from overlay import TransparentOverlay


class DreamMemoryApp:
    """Main application."""

    def __init__(self):
        print("APP STARTED")
        
        self.running = True
        self.monitoring = True
        self.game_rect = None
        self.wave_id = 0
        self.analysis_in_progress = False

        # Components
        self.capture = ScreenCapture()
        self.analyzer = OllamaAnalyzer()

        # Check analyzer
        if not self.analyzer.is_available():
            print("ERROR: Ollama not available")
            if not self.analyzer.model_installed:
                print(f"Run: ollama pull {config.OLLAMA_MODEL}")

        # Watcher
        self.watcher = RequestWatcher(self.capture, self._on_watcher_trigger)

        # Overlay
        self.overlay = TransparentOverlay()

        # Find window
        self._find_game()

        # Show UI
        self.overlay.show_overlay()
        print("OVERLAY STARTED")

        # Start watcher if monitoring enabled
        if self.monitoring:
            self.watcher.start()

    def _find_game(self):
        """Find BlueStacks window."""
        if self.capture.find_window():
            self.game_rect = self.capture.get_geometry()
            if self.game_rect:
                self.overlay.update_geometry(*self.game_rect)

    def _on_watcher_trigger(self):
        """Handle watcher trigger."""
        self.wave_id += 1
        self._run_analysis(self.wave_id)

    def force_analyze(self):
        """Force analysis on F10."""
        if not self.game_rect:
            self._find_game()
            
        if not self.game_rect:
            print("NO WINDOW")
            return
            
        if self.analysis_in_progress:
            return
            
        print("F10 FORCE ANALYZE")
        self.watcher.trigger_analysis()

    def _run_analysis(self, wave_id: int):
        """Run analysis in background."""
        if self.analysis_in_progress:
            return
            
        if not self.analyzer.is_available():
            self.overlay.update_status(config.STATUS_API_ERROR)
            return

        self.analysis_in_progress = True
        self.overlay.update_status(config.STATUS_ANALYZING)

        # Run in thread
        thread = threading.Thread(target=self._analysis_worker, args=(wave_id,), daemon=True)
        thread.start()

    def _analysis_worker(self, wave_id: int):
        """Background analysis worker."""
        try:
            # Capture images
            scene = self.capture.capture_scene()
            if scene is None:
                self._on_analysis_complete(wave_id, [], "CAPTURE FAILED")
                return

            # Encode
            scene_b64 = self.capture.encode_jpeg(scene)
            if scene_b64 is None:
                self._on_analysis_complete(wave_id, [], "ENCODE FAILED")
                return

            import base64
            scene_b64_str = base64.b64encode(scene_b64).decode('utf-8')
            bar_b64_str = ""  # Not needed for vision

            # Analyze
            result = self.analyzer.analyze(bar_b64_str, scene_b64_str)

            # Check if stale
            if wave_id != self.wave_id:
                print("STALE RESULT IGNORED")
                return

            self._on_analysis_complete(wave_id, result.objects, result.error)

        except Exception as e:
            print(f"ANALYSIS ERROR: {e}")
            self._on_analysis_complete(wave_id, [], str(e))

    def _on_analysis_complete(self, wave_id: int, objects, error: str):
        """Handle analysis completion on main thread."""
        if wave_id != self.wave_id:
            return

        self.analysis_in_progress = False
        self.watcher.analysis_complete()

        if error:
            print(f"ANALYSIS ERROR: {error}")
            self.overlay.update_status(config.STATUS_API_ERROR)
        elif not objects:
            print("NO MARKS")
            self.overlay.update_status(config.STATUS_NO_MARKS)
            self.overlay.update_marks([])
        else:
            self.overlay.update_status(config.STATUS_LIVE)
            self.overlay.update_marks(objects)

    def toggle_monitoring(self):
        """Toggle monitoring on/off."""
        self.monitoring = not self.monitoring
        if self.monitoring:
            self.watcher.start()
            self.overlay.update_status(config.STATUS_READY)
        else:
            self.watcher.stop()
            self.overlay.update_status(config.STATUS_STOPPED)

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
        self.watcher.stop()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)

    # Create app
    dream = DreamMemoryApp()

    # Hotkeys
    QShortcut(QKeySequence("F8"), app, activated=dream.toggle_overlay)
    QShortcut(QKeySequence("F9"), app, activated=dream.toggle_monitoring)
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
    print("F9 - Toggle monitoring")
    print("F10 - Force analyze")
    print("ESC - Exit")
    print("=" * 50)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
