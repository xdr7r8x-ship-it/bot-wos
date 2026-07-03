"""
Dream Memory Zero-Data Overlay - Window Tracker
Finds and tracks the BlueStacks App Player window.
"""

import platform
import time

from config import GEOMETRY_REFRESH_MS, WINDOW_TITLE_KEYWORDS


class WindowTracker:
    """Tracks BlueStacks window position and size."""

    def __init__(self):
        self.hwnd = None
        self.rect = None  # (left, top, right, bottom) in screen coordinates
        self.client_rect = None  # (x, y, width, height)
        self.found = False

        if platform.system() == "Windows":
            import win32gui
            import win32con
            self.win32gui = win32gui
            self.win32con = win32con

    def find_window(self):
        """Find BlueStacks App Player window."""
        if platform.system() != "Windows":
            return False

        self.hwnd = None

        def enum_callback(hwnd, ctx):
            if not self.win32gui.IsWindowVisible(hwnd):
                return True

            title = self.win32gui.GetWindowText(hwnd)
            if not title:
                return True

            # Check for BlueStacks in title
            for keyword in WINDOW_TITLE_KEYWORDS:
                if keyword.lower() in title.lower():
                    self.hwnd = hwnd
                    return False

            return True

        self.win32gui.EnumWindows(enum_callback, None)
        return self.hwnd is not None

    def get_client_rect(self):
        """
        Get client rect in screen coordinates.
        Returns (x, y, width, height) or None if not found.
        """
        if not self.hwnd or platform.system() != "Windows":
            return None

        try:
            # Get client rect (relative to window)
            client_rect = self.win32gui.GetClientRect(self.hwnd)

            # Convert to screen coordinates
            top_left = self.win32gui.ClientToScreen(self.hwnd, (client_rect[0], client_rect[1]))
            bottom_right = self.win32gui.ClientToScreen(self.hwnd, (client_rect[2], client_rect[3]))

            x = top_left[0]
            y = top_left[1]
            width = bottom_right[0] - top_left[0]
            height = bottom_right[1] - top_left[1]

            self.client_rect = (x, y, width, height)
            self.found = True
            return self.client_rect

        except Exception as e:
            print(f"[WINDOW] Error getting client rect: {e}")
            self.found = False
            return None

    def update(self):
        """Update window position. Returns client rect or None."""
        if not self.find_window():
            self.found = False
            self.hwnd = None
            return None

        return self.get_client_rect()

    def is_found(self):
        """Check if window is found."""
        return self.found and self.hwnd is not None

    def get_geometry(self):
        """Get current geometry for capture/overlay."""
        return self.update()

    def run_loop(self, callback):
        """Run update loop calling callback with geometry."""
        while True:
            geometry = self.update()
            callback(geometry)
            time.sleep(GEOMETRY_REFRESH_MS / 1000.0)
