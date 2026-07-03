"""
Dream Memory Live Overlay Assistant - Watcher Module
Monitors screen for changes and triggers analysis.
"""

import time
import threading
from typing import Callable, Optional

from config import WATCH_INTERVAL_MS, API_COOLDOWN_MS


class Watcher:
    """
    Monitors the game screen and triggers analysis when request bar changes.
    Uses a timer-based loop to check for changes without blocking.
    """

    def __init__(
        self,
        capture,
        analyzer,
        on_analysis_complete: Callable[[dict], None],
        on_status_change: Callable[[str], None]
    ):
        self.capture = capture
        self.analyzer = analyzer
        self.on_analysis_complete = on_analysis_complete
        self.on_status_change = on_status_change

        self._running = False
        self._monitoring = False
        self._thread: Optional[threading.Thread] = None
        self._last_api_time = 0
        self._force_analysis = False

    def start(self):
        """Start the watcher thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the watcher thread."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._thread = None

    def start_monitoring(self):
        """Enable active monitoring."""
        self._monitoring = True
        self.on_status_change("LIVE")

    def stop_monitoring(self):
        """Disable active monitoring."""
        self._monitoring = False
        self.on_status_change("STOPPED")

    def toggle_monitoring(self) -> bool:
        """Toggle monitoring state. Returns new state."""
        if self._monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
        return self._monitoring

    def force_analysis(self):
        """Force immediate analysis regardless of change detection."""
        self._force_analysis = True

    def _can_call_api(self) -> bool:
        """Check if enough time has passed since last API call."""
        current_time = time.time() * 1000
        return (current_time - self._last_api_time) >= API_COOLDOWN_MS

    def _run_loop(self):
        """Main watcher loop running in separate thread."""
        consecutive_no_action = 0
        
        while self._running:
            try:
                if self._monitoring:
                    # Check for changes or retries
                    if self._force_analysis or self.capture.should_analyze():
                        if self._can_call_api():
                            self._do_analysis()
                            consecutive_no_action = 0
                        else:
                            consecutive_no_action += 1
                    else:
                        consecutive_no_action += 1
                        
                        # If API is available and we haven't analyzed recently, do periodic check
                        if consecutive_no_action > 10 and self._can_call_api():
                            # Force a check anyway to catch any missed changes
                            if self.capture.should_analyze():
                                self._do_analysis()
                            consecutive_no_action = 0

                # Sleep for watch interval
                time.sleep(WATCH_INTERVAL_MS / 1000.0)

            except Exception as e:
                print(f"[WATCHER] Error in loop: {e}")
                time.sleep(1)  # Back off on error

    def _check_and_analyze(self):
        """Check for changes and trigger analysis if needed."""
        # Force analysis takes priority
        should_analyze = self._force_analysis
        self._force_analysis = False

        # Check for request bar changes
        if not should_analyze:
            should_analyze = self.capture.should_analyze()

        # Only analyze if we can call the API
        if should_analyze:
            if self._can_call_api():
                self._do_analysis()
            # If can't call API yet, will retry on next loop iteration

    def _do_analysis(self):
        """Perform the actual screen analysis."""
        try:
            self.on_status_change("ANALYZING")

            # Get capture data
            image_data, screen_w, screen_h = self.capture.get_capture_for_analysis()

            # Call API
            result = self.analyzer.analyze_screen(
                image_data,
                screen_w,
                screen_h
            )

            # Update last API call time
            self._last_api_time = time.time() * 1000

            # Handle errors
            if "error" in result and not result["marks"]:
                self.on_status_change("API ERROR")
            elif not result.get("marks"):
                self.on_status_change("NO MARKS")
                self.on_analysis_complete({"marks": []})
            else:
                self.on_status_change("LIVE")
                self.on_analysis_complete(result)

        except Exception as e:
            print(f"[WATCHER] Loop error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(2)  # Back off on error

    @property
    def is_running(self) -> bool:
        """Check if watcher thread is running."""
        return self._running

    @property
    def is_monitoring(self) -> bool:
        """Check if active monitoring is enabled."""
        return self._monitoring
