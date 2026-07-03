# Request bar watcher for Dream Memory
# DISABLED BY DEFAULT - For future use
# Set AUTO_WATCH_REQUEST_BAR = True in config.py to enable

import time
import hashlib
from typing import Callable
from PyQt6.QtCore import QTimer

import config


class RequestWatcher:
    """Watch request bar for changes.
    
    DISABLED BY DEFAULT.
    Enable by setting AUTO_WATCH_REQUEST_BAR = True in config.py
    """

    def __init__(self, capture, on_change: Callable):
        self.capture = capture
        self.on_change = on_change
        self.last_bar_hash = None
        self.last_change_time = 0
        self._analyzing = False
        self._last_api_time = 0
        self.enabled = config.AUTO_WATCH_REQUEST_BAR
        
        # Timer for polling
        self.timer = QTimer()
        self.timer.timeout.connect(self._check)

    def start(self):
        """Start watching (only if enabled)."""
        if self.enabled:
            self.timer.start(config.WATCH_INTERVAL_MS)

    def stop(self):
        """Stop watching."""
        self.timer.stop()

    def trigger_analysis(self):
        """Manually trigger analysis."""
        if not self.enabled:
            return
        self._analyzing = True
        self._last_api_time = time.time()
        self.on_change()

    def is_analyzing(self) -> bool:
        """Check if analysis is in progress."""
        return self._analyzing

    def analysis_complete(self):
        """Mark analysis as complete."""
        self._analyzing = False

    def _check(self):
        """Check for request bar changes (only if enabled)."""
        if not self.enabled:
            return
            
        if self._analyzing:
            return  # Don't trigger while analyzing

        # Check cooldown
        now = time.time()
        if now - self._last_api_time < config.API_COOLDOWN_MS / 1000:
            return

        # Capture request bar
        bar = self.capture.capture_request_bar()
        if bar is None:
            return

        # Hash the bar image
        bar_bytes = bar.tobytes()
        bar_hash = hashlib.md5(bar_bytes).hexdigest()

        # Check for change
        if self.last_bar_hash is None:
            self.last_bar_hash = bar_hash
            return

        if bar_hash != self.last_bar_hash:
            # Debounce
            if now - self.last_change_time < config.REQUEST_DEBOUNCE_MS / 1000:
                return

            self.last_bar_hash = bar_hash
            self.last_change_time = now
            self._analyzing = True
            self._last_api_time = now
            self.on_change()
