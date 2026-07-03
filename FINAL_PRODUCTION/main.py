"""
Dream Memory Hybrid Overlay - Main Application
Works with Ollama (local) OR Gemini (cloud) - Auto-detects available backend
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
    STATUS_WAITING,
    STATUS_READY,
    STATUS_OLLAMA,
    STATUS_GEMINI,
    ERR_NO_AI,
    GEOMETRY_REFRESH_MS
)
from window_tracker import WindowTracker
from game_area import GameAreaDetector
from capture import ScreenCapture
from request_watcher import RequestWatcher
from hybrid_analyzer import HybridAnalyzer  # NEW: Hybrid analyzer
from overlay import OverlayManager


class DreamMemoryApp:
    """Main application with auto-detection of AI backend."""

    def __init__(self):
        self.running = True

        # Components
        self.window_tracker = WindowTracker()
        self.game_area = GameAreaDetector()
        self.capture = ScreenCapture()
        
        # Hybrid AI - auto-detects Ollama or Gemini
        self.analyzer = HybridAnalyzer()
        
        # Update status with selected backend
        backend = self.analyzer.get_backend_name()
        if backend == "ollama":
            self._update_overlay_status(STATUS_OLLAMA)
        elif backend == "gemini":
            self._update_overlay_status(STATUS_GEMINI)
        else:
            print("=" * 50)
            print("ERROR: NO AI BACKEND AVAILABLE")
            print("=" * 50)
            print("Options:")
            print("1. Install Ollama: https://ollama.com")
            print("   Then: ollama pull qwen2.5vl:3b")
            print("   Then: ollama serve")
            print("")
            print("2. Set GEMINI_API_KEY environment variable")
            print("   Get key from: https://aistudio.google.com/app/apikey")
            print("=" * 50)
        
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
        """Run the vision analysis using available backend."""
        try:
            # Capture images
            game_rect = self.capture.game_rect
            if game_rect is None:
                return

            full_img = self.capture.capture_rect(game_rect)
            if full_img is None:
                return

            # Crop areas
            request_bar = self.capture.crop_request_bar(full_img)
            scene = self.capture.crop_scene(full_img)

            # Encode
            request_bar_b64 = self.capture.encode_jpeg_base64(request_bar)
            scene_b64 = self.capture.encode_jpeg_base64(scene)

            # Analyze with hybrid backend (auto-selects Ollama or Gemini)
            result = self.analyzer.analyze_screen(request_bar_b64, scene_b64)

            # Check if stale
            if self.watcher.is_stale(self.wave_id):
                return

            self.current_result = result

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

        game_rect = self.game_area.detect(client_rect)

        if game_rect is None:
            self._update_overlay_status(STATUS_NO_WINDOW)
            return

        self.capture.game_rect = game_rect

        if self.overlay_manager is None:
            x, y, width, height = game_rect
            self.overlay_manager = OverlayManager(x, y, width, height)
            self.overlay_manager.create_overlay()
            self.overlay_manager.show()
            self._update_overlay_status(STATUS_READY)
        else:
            x, y, width, height = game_rect
            self.overlay_manager.move_overlay(x, y, width, height)

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
                self.overlay_manager.update_status(STATUS_READY)
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

        self._update_overlay_status(STATUS_WAITING)

        print("=" * 60)
        print("Dream Memory Ollama Overlay (Local AI)")
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
    print("=" * 60)
    print("Dream Memory Hybrid Overlay")
    print("Auto-detects: Ollama (local) OR Gemini (cloud)")
    print("=" * 60)

    # Create Qt application
    app = QApplication(sys.argv)

    # Create and run app
    dream_app = DreamMemoryApp()
    dream_app.run()

    # Setup hotkeys
    from PyQt6.QtWidgets import QShortcut
    from PyQt6.QtGui import QKeySequence

    QShortcut(QKeySequence(Qt.Key.Key_Escape), app).activated.connect(lambda: sys.exit(0))
    QShortcut(QKeySequence("F8"), app).activated.connect(dream_app.toggle_overlay)
    QShortcut(QKeySequence("F9"), app).activated.connect(lambda: dream_app.toggle_monitoring())
    QShortcut(QKeySequence("F10"), app).activated.connect(dream_app.force_analyze)

    # Timer for cleanup
    app.aboutToQuit.connect(dream_app.stop)

    # Run Qt event loop
    exit_code = app.exec()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
