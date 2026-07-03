"""
Dream Memory Zero-Data Overlay - Main Application
Transparent overlay assistant for Dream Memory hidden-object game.
"""

import os
import sys
import time
import threading
from typing import Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from config import (
    STATUS_LIVE,
    STATUS_ANALYZING,
    STATUS_NO_MARKS,
    STATUS_API_ERROR,
    STATUS_PARSE_ERROR,
    STATUS_WAITING,
    STATUS_STALE,
    STATUS_STOPPED,
    STATUS_NO_WINDOW,
    GEOMETRY_REFRESH_MS
)
from window_tracker import WindowTracker
from game_area import GameAreaDetector
from capture import ScreenCapture
from request_watcher import RequestWatcher
from analyzer import VisionAnalyzer
from overlay import OverlayManager


class DreamMemoryApp:
    """Main application for Dream Memory overlay."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.running = True

        # Components
        self.window_tracker = WindowTracker()
        self.game_area = GameAreaDetector()
        self.capture = ScreenCapture()
        self.analyzer = VisionAnalyzer(api_key)
        self.overlay_manager: Optional[OverlayManager] = None

        # State
        self.current_marks = []
        self.current_result = None
        self.monitoring = True
        self.wave_id = 0
        self.analysis_in_progress = False

        # Connect capture to game rect
        self.capture.game_rect = None

        # Request watcher
        self.watcher = RequestWatcher(self.capture, self._on_analyze_trigger)

    def _on_analyze_trigger(self, wave_id: int):
        """Called when analysis should be triggered."""
        if wave_id <= self.wave_id:
            # Ignore stale requests
            self._update_overlay_status(STATUS_STALE)
            return

        self.wave_id = wave_id
        self.analysis_in_progress = True
        self._update_overlay_status(STATUS_ANALYZING)
        self.watcher.mark_analysis_started()

        # Start analysis in background thread
        thread = threading.Thread(target=self._run_analysis, daemon=True)
        thread.start()

    def _run_analysis(self):
        """Run the vision analysis."""
        try:
            # Capture images
            game_rect = self.capture.game_rect
            if game_rect is None:
                print("[ANALYSIS] No game rect")
                return

            full_img = self.capture.capture_rect(game_rect)
            if full_img is None:
                print("[ANALYSIS] Failed to capture")
                return

            # Crop areas
            request_bar = self.capture.crop_request_bar(full_img)
            scene = self.capture.crop_scene(full_img)

            # Encode
            request_bar_b64 = self.capture.encode_jpeg_base64(request_bar)
            scene_b64 = self.capture.encode_jpeg_base64(scene)

            # Analyze
            result = self.analyzer.analyze_screen(request_bar_b64, scene_b64)

            # Check if stale
            if self.watcher.is_stale(self.wave_id):
                print("[ANALYSIS] Stale result ignored")
                return

            # Store result
            self.current_result = result

            # Check for errors
            if "error" in result:
                self._update_overlay_status(STATUS_API_ERROR)
                print(f"[ANALYSIS] Error: {result['error']}")
            elif not result.get("marks"):
                self._update_overlay_status(STATUS_NO_MARKS)
                self._update_overlay_marks([])
            else:
                self._update_overlay_status(STATUS_LIVE)
                self._update_overlay_marks(result["marks"])

            self.watcher.mark_analysis_complete()

        except Exception as e:
            print(f"[ANALYSIS] Exception: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.analysis_in_progress = False

    def _update_overlay_status(self, status: str):
        """Update overlay status."""
        if self.overlay_manager:
            self.overlay_manager.update_status(status)

    def _update_overlay_marks(self, marks: list):
        """Update overlay marks."""
        if self.overlay_manager:
            self.overlay_manager.update_marks(marks)

    def _update_geometry(self):
        """Update window geometry."""
        client_rect = self.window_tracker.get_client_rect()

        if client_rect is None:
            self._update_overlay_status(STATUS_NO_WINDOW)
            return

        # Detect game area
        game_rect = self.game_area.detect(client_rect)

        if game_rect is None:
            self._update_overlay_status(STATUS_NO_WINDOW)
            return

        # Update capture
        self.capture.game_rect = game_rect

        # Create or move overlay
        if self.overlay_manager is None:
            x, y, width, height = game_rect
            self.overlay_manager = OverlayManager(x, y, width, height)
            self.overlay_manager.create_overlay()
            self.overlay_manager.show()
        else:
            x, y, width, height = game_rect
            self.overlay_manager.move_overlay(x, y, width, height)

        # Set initial status
        if self.overlay_manager.overlay.status == STATUS_WAITING:
            self.overlay_manager.update_status(STATUS_LIVE)

    def _geometry_loop(self):
        """Periodically update geometry."""
        while self.running:
            try:
                self.window_tracker.update()
                self._update_geometry()
            except Exception as e:
                print(f"[GEOMETRY] Error: {e}")
            time.sleep(GEOMETRY_REFRESH_MS / 1000.0)

    def toggle_monitoring(self):
        """Toggle monitoring on/off."""
        self.monitoring = not self.monitoring
        if self.overlay_manager:
            if self.monitoring:
                self.overlay_manager.update_status(STATUS_LIVE)
            else:
                self.overlay_manager.update_status(STATUS_STOPPED)
        return self.monitoring

    def force_analyze(self):
        """Force analysis of current wave."""
        self.wave_id += 1
        self._on_analyze_trigger(self.wave_id)

    def toggle_overlay(self):
        """Toggle overlay visibility."""
        if self.overlay_manager:
            self.overlay_manager.toggle_overlay()

    def run(self):
        """Run the application."""
        # Start geometry loop
        geometry_thread = threading.Thread(target=self._geometry_loop, daemon=True)
        geometry_thread.start()

        # Start request watcher
        self.watcher.start()

        # Set initial status
        self._update_overlay_status(STATUS_WAITING)

        print("=" * 60)
        print("Dream Memory Zero-Data Overlay")
        print("=" * 60)
        print("Hotkeys:")
        print("  F8 - Toggle overlay visibility")
        print("  F9 - Toggle monitoring on/off")
        print("  F10 - Force analyze current wave")
        print("  ESC - Exit")
        print("=" * 60)

    def stop(self):
        """Stop the application."""
        self.running = False
        self.watcher.stop()
        if self.overlay_manager:
            self.overlay_manager.close()
        self.capture.close()


def main():
    """Main entry point."""
    # Check API key
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("Set it with: $env:OPENAI_API_KEY='your-key'")
        print("Get your key from: https://platform.openai.com/api-keys")
        sys.exit(1)

    # Create Qt application
    app = QApplication(sys.argv)

    # Create and run app
    dream_app = DreamMemoryApp(api_key)
    dream_app.run()

    # Setup hotkeys
    from PyQt6.QtWidgets import QShortcut
    from PyQt6.QtGui import QKeySequence

    shortcuts = {
        QShortcut(QKeySequence(Qt.Key.Key_Escape), app): lambda: sys.exit(0),
        QShortcut(QKeySequence("F8"), app): dream_app.toggle_overlay,
        QShortcut(QKeySequence("F9"), app): lambda: dream_app.toggle_monitoring(),
        QShortcut(QKeySequence("F10"), app): dream_app.force_analyze,
    }

    # Timer for cleanup
    def cleanup():
        dream_app.stop()

    app.aboutToQuit.connect(cleanup)

    # Run Qt event loop
    exit_code = app.exec()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
