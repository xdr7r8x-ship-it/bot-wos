"""
Dream Memory Live Overlay Assistant
Main entry point with keyboard shortcuts and application lifecycle.
"""

import os
import sys
import signal

# Check API key BEFORE importing PyQt6 (which takes time)
API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not API_KEY:
    print("=" * 60)
    print("ERROR: OPENAI_API_KEY environment variable is not set!")
    print("=" * 60)
    print("Please set your OpenAI API key:")
    print("  Windows PowerShell: $env:OPENAI_API_KEY='your-key-here'")
    print("  Windows CMD: set OPENAI_API_KEY=your-key-here")
    print("=" * 60)
    sys.exit(1)

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QKeySequence

from config import STATUS_STOPPED, STATUS_LIVE, STATUS_ANALYZING, STATUS_API_ERROR, STATUS_NO_MARKS
from capture import ScreenCapture
from analyzer import VisionAnalyzer
from watcher import Watcher
from overlay import OverlayManager


class DreamMemoryApp:
    """Main application class."""

    def __init__(self):
        self.api_key = API_KEY

        # Initialize Qt Application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Dream Memory Overlay")
        self.app.setQuitOnLastWindowClosed(False)

        # Setup keyboard interrupt handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Initialize components
        self.capture = ScreenCapture()
        self.analyzer = VisionAnalyzer(self.api_key)

        # Get screen dimensions
        self.screen_width, self.screen_height = self.capture.get_screen_dimensions()

        # Initialize overlay manager
        self.overlay_manager = OverlayManager(self.screen_width, self.screen_height)
        self.overlay = self.overlay_manager.create_overlay()

        # Initialize watcher
        self.watcher = Watcher(
            capture=self.capture,
            analyzer=self.analyzer,
            on_analysis_complete=self._on_analysis_complete,
            on_status_change=self._on_status_change
        )

        # Setup keyboard shortcuts
        self._setup_shortcuts()

        # Status tracking
        self.current_marks = []

    def _setup_shortcuts(self):
        """Setup global keyboard shortcuts."""
        # F8 - Toggle overlay visibility
        toggle_seq = QKeySequence(Qt.KeyboardModifier.NoModifier + Qt.Key.Key_F8)
        self.toggle_overlay_action = QKeySequence(toggle_seq)
        
        # F9 - Start/Stop monitoring
        self.monitor_seq = QKeySequence(Qt.KeyboardModifier.NoModifier + Qt.Key.Key_F9)
        
        # F10 - Force analysis
        self.analyze_seq = QKeySequence(Qt.KeyboardModifier.NoModifier + Qt.Key.Key_F10)
        
        # ESC - Exit
        self.exit_seq = QKeySequence(Qt.Key.Key_Escape)

        # Install event filter for key handling
        self.app.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handle keyboard events for shortcuts."""
        try:
            from PyQt6.QtGui import QKeyEvent
            if event.type() == QKeyEvent.Type.KeyPress:
                key = event.key()
                modifiers = event.modifiers()

                # F8 - Toggle overlay
                if key == Qt.Key.Key_F8 and modifiers == Qt.KeyboardModifier.NoModifier:
                    self._toggle_overlay()
                    return True

                # F9 - Toggle monitoring
                if key == Qt.Key.Key_F9 and modifiers == Qt.KeyboardModifier.NoModifier:
                    self._toggle_monitoring()
                    return True

                # F10 - Force analysis
                if key == Qt.Key.Key_F10 and modifiers == Qt.KeyboardModifier.NoModifier:
                    self._force_analysis()
                    return True

                # ESC - Exit
                if key == Qt.Key.Key_Escape and modifiers == Qt.KeyboardModifier.NoModifier:
                    self._exit_app()
                    return True

        except Exception as e:
            print(f"[MAIN] Event filter error: {e}")

        return super().eventFilter(obj, event)

    def _toggle_overlay(self):
        """Toggle overlay visibility."""
        visible = self.overlay_manager.toggle_overlay()
        state = "visible" if visible else "hidden"
        print(f"[MAIN] Overlay {state}")

    def _toggle_monitoring(self):
        """Toggle monitoring on/off."""
        is_active = self.watcher.toggle_monitoring()
        state = "started" if is_active else "stopped"
        print(f"[MAIN] Monitoring {state}")

    def _force_analysis(self):
        """Force immediate analysis."""
        print("[MAIN] Force analysis triggered")
        self.watcher.force_analysis()

    def _on_analysis_complete(self, result: dict):
        """Handle analysis completion."""
        try:
            marks = result.get("marks", [])
            self.current_marks = marks
            self.overlay_manager.update_marks(marks)

            if marks:
                print(f"[MAIN] Analysis complete: {len(marks)} objects found")
            else:
                print("[MAIN] Analysis complete: no objects found")

        except Exception as e:
            print(f"[MAIN] Analysis callback error: {e}")

    def _on_status_change(self, status: str):
        """Handle status changes."""
        self.overlay_manager.update_status(status)
        print(f"[MAIN] Status: {status}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\n[MAIN] Shutdown signal received")
        self._exit_app()

    def _exit_app(self):
        """Clean exit."""
        print("[MAIN] Exiting...")
        self.watcher.stop()
        self.overlay_manager.close()
        self.capture.close()
        self.app.quit()
        sys.exit(0)

    def run(self):
        """Start the application."""
        print("=" * 60)
        print("Dream Memory Live Overlay Assistant")
        print("=" * 60)
        print(f"Screen: {self.screen_width}x{self.screen_height}")
        print("STATUS: AUTO-RUNNING (Press ESC to exit)")
        print("=" * 60)

        # Show overlay
        self.overlay_manager.show()

        # Start watcher
        self.watcher.start()

        # Auto-start monitoring IMMEDIATELY
        self.watcher.start_monitoring()
        print("[MAIN] ✓ Monitoring started automatically")

        # Force first analysis immediately
        print("[MAIN] ✓ Starting initial analysis...")
        self.watcher.force_analysis()

        # Run Qt event loop
        return self.app.exec()


def main():
    """Entry point."""
    try:
        app = DreamMemoryApp()
        exit_code = app.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[MAIN] Interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"[MAIN] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
