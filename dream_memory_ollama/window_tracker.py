# Window tracker for BlueStacks
import win32gui
from typing import Optional, Tuple


class WindowTracker:
    """Track BlueStacks window."""

    def __init__(self):
        self.hwnd = None
        self.rect = None

    def find(self, title: str = "BlueStacks") -> bool:
        """Find BlueStacks window."""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                text = win32gui.GetWindowText(hwnd)
                if title.lower() in text.lower():
                    windows.append(hwnd)
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        if windows:
            self.hwnd = windows[0]
            self._update_rect()
            return True
        return False

    def _update_rect(self):
        """Update window rectangle."""
        if self.hwnd:
            self.rect = win32gui.GetWindowRect(self.hwnd)

    def get_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """Get window rect."""
        self._update_rect()
        return self.rect

    def is_valid(self) -> bool:
        """Check if window is valid."""
        return self.hwnd is not None and self.rect is not None
