"""
Dream Memory Live Overlay Assistant
Main entry point with keyboard shortcuts and application lifecycle.
Optimized for BlueStacks and Android emulators.
"""

import os
import sys
import signal
import platform

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

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QKeyEvent

from config import STATUS_STOPPED, STATUS_NO_WINDOW
from analyzer import VisionAnalyzer
from watcher import Watcher
from overlay import OverlayManager

# Import capture based on platform
if platform.system() == "Windows":
    from capture import ScreenCapture


class KeyMonitor(QTimer):
    """Keyboard monitoring using timer-based polling."""
    
    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self.callback = callback
        self.keys = {}
        self.setInterval(50)  # Check every 50ms
        self.timeout.connect(self._check_keys)
        
    def _check_keys(self):
        from PyQt6.QtGui import QGuiApplication
        try:
            self.callback()
        except:
            pass


class DreamMemoryApp:
    """Main application class."""

    def __init__(self):
        self.api_key = API_KEY
        self.platform = platform.system()

        # Initialize Qt Application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Dream Memory Overlay")
        self.app.setQuitOnLastWindowClosed(False)

        # Setup keyboard interrupt handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Initialize capture (Windows only)
        if self.platform == "Windows":
            # Get target window from env or use default
            window_title = os.environ.get("TARGET_WINDOW", "BlueStacks")
            self.capture = ScreenCapture(window_title)
            print(f"[MAIN] Target window: {window_title}")
        else:
            print("[MAIN] Warning: Non-Windows platform - screen capture may not work")
            self.capture = None

        # Initialize analyzer
        self.analyzer = VisionAnalyzer(self.api_key)

        # Get window dimensions
        if self.capture:
            self.screen_width, self.screen_height = self.capture.get_screen_dimensions()
        else:
            self.screen_width, self.screen_height = 1920, 1080

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

        # Setup keyboard monitoring
        self._setup_keyboard()
        
        # Status tracking
        self.current_marks = []
        self._last_f8 = False
        self._last_f9 = False
        self._last_f10 = False
        self._last_esc = False

    def _setup_keyboard(self):
        """Setup keyboard monitoring."""
        self.key_timer = QTimer(self.app)
        self.key_timer.setInterval(50)
        self.key_timer.timeout.connect(self._check_keyboard)
        self.key_timer.start()

    def _check_keyboard(self):
        """Check for key presses."""
        try:
            from ctypes import windll
            user32 = windll.user32
            
            # Virtual key codes
            VK_F8 = 0x77
            VK_F9 = 0x78
            VK_F10 = 0x79
            VK_ESCAPE = 0x1B
            
            # Check key states (0x8000 = pressed)
            f8_pressed = user32.GetAsyncKeyState(VK_F8) & 0x8000
            f9_pressed = user32.GetAsyncKeyState(VK_F9) & 0x8000
            f10_pressed = user32.GetAsyncKeyState(VK_F10) & 0x8000
            esc_pressed = user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000
            
            # F8
            if f8_pressed and not self._last_f8:
                self._toggle_overlay()
            self._last_f8 = f8_pressed
            
            # F9
            if f9_pressed and not self._last_f9:
                self._toggle_monitoring()
            self._last_f9 = f9_pressed
            
            # F10
            if f10_pressed and not self._last_f10:
                self._force_analysis()
            self._last_f10 = f10_pressed
            
            # ESC
            if esc_pressed and not self._last_esc:
                self._exit_app()
            self._last_esc = esc_pressed
            
        except Exception as e:
            pass  # Silently ignore errors in keyboard checking

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
        if hasattr(self, 'key_timer'):
            self.key_timer.stop()
        self.watcher.stop()
        self.overlay_manager.close()
        if self.capture:
            self.capture.close()
        self.app.quit()
        sys.exit(0)

    def run(self):
        """Start the application."""
        print("=" * 60)
        print("Dream Memory Live Overlay Assistant")
        print("=" * 60)
        print(f"Platform: {self.platform}")
        print(f"Target: BlueStacks/Emulator")
        print(f"Window Size: {self.screen_width}x{self.screen_height}")
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
