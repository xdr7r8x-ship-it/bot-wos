"""
Dream Memory Zero-Data Overlay - Request Watcher
Monitors request bar for changes and triggers analysis.
"""

import time
import threading

from config import (
    WATCH_INTERVAL_MS,
    REQUEST_CHANGE_THRESHOLD,
    REQUEST_DEBOUNCE_MS,
    API_COOLDOWN_MS
)


class RequestWatcher:
    """
    Monitors the request bar for changes.
    Uses fingerprint-based change detection with debouncing.
    """

    def __init__(self, capture, on_analyze_trigger):
        self.capture = capture
        self.on_analyze_trigger = on_analyze_trigger

        self._running = False
        self._thread = None
        self._last_fingerprint = None
        self._last_api_time = 0
        self._analyzing = False
        self._stale_count = 0
        self._wave_id = 0

    def start(self):
        """Start watching."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop watching."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        self._thread = None

    def trigger_analysis(self):
        """Manually trigger analysis."""
        self._wave_id += 1
        self.on_analyze_trigger(self._wave_id)

    def _can_call_api(self):
        """Check if API can be called."""
        current_time = time.time() * 1000
        return (current_time - self._last_api_time) >= API_COOLDOWN_MS

    def _watch_loop(self):
        """Main watch loop."""
        last_check = 0
        debounce_time = 0

        while self._running:
            try:
                current_time = time.time() * 1000

                # Check at WATCH_INTERVAL_MS
                if current_time - last_check < WATCH_INTERVAL_MS:
                    time.sleep(0.01)
                    continue

                last_check = current_time

                # Capture request bar for fingerprint
                game_rect = self.capture.game_rect if hasattr(self.capture, 'game_rect') else None
                if game_rect is None:
                    continue

                # We need to capture the full area and crop the bar
                full_img = self.capture.capture_rect(game_rect)
                if full_img is None:
                    continue

                request_bar = self.capture.crop_request_bar(full_img)
                if request_bar is None:
                    continue

                # Compute fingerprint
                fingerprint = self.capture.image_fingerprint(request_bar)

                if self._last_fingerprint is None:
                    self._last_fingerprint = fingerprint
                    # Trigger initial analysis
                    if self._can_call_api():
                        self.trigger_analysis()
                    continue

                # Check for meaningful change
                diff = abs(fingerprint - self._last_fingerprint)

                if diff > REQUEST_CHANGE_THRESHOLD:
                    # Debounce
                    if current_time - debounce_time >= REQUEST_DEBOUNCE_MS:
                        self._last_fingerprint = fingerprint
                        debounce_time = current_time

                        # Trigger if not already analyzing
                        if self._can_call_api():
                            self.trigger_analysis()

            except Exception as e:
                print(f"[WATCHER] Error: {e}")

            time.sleep(0.01)

    def mark_analysis_started(self):
        """Mark that analysis has started."""
        self._analyzing = True
        self._stale_count += 1

    def mark_analysis_complete(self):
        """Mark that analysis is complete."""
        self._analyzing = False
        self._last_api_time = time.time() * 1000

    def is_stale(self, wave_id):
        """Check if a wave_id result is stale."""
        return wave_id < self._wave_id

    @property
    def is_running(self):
        return self._running
