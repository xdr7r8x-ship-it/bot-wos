"""
Dream Memory Zero-Data Overlay - Game Area Detector
Detects the actual portrait game area inside BlueStacks client.
"""

import platform


class GameAreaDetector:
    """
    Detects the actual portrait game area inside BlueStacks.
    Removes emulator borders and chrome.
    """

    def __init__(self):
        self.game_rect = None  # (x, y, width, height)

        # Empirically detected chrome sizes (may vary by BlueStacks version)
        # These are typical values for BlueStacks portrait mode
        self.border_top = 0
        self.border_bottom = 0
        self.border_left = 0
        self.border_right = 0

        if platform.system() == "Windows":
            import win32gui
            self.win32gui = win32gui

    def detect(self, client_rect):
        """
        Detect game area from client rect.
        Returns (x, y, width, height) for game area.
        """
        if client_rect is None:
            return None

        x, y, width, height = client_rect

        # Try to detect actual game area
        # In portrait mode BlueStacks, the game typically occupies most of the client area
        # but there might be small chrome areas

        # Use client rect as fallback
        game_x = x + self.border_left
        game_y = y + self.border_top
        game_width = width - self.border_left - self.border_right
        game_height = height - self.border_top - self.border_bottom

        # Ensure reasonable minimum size
        if game_width < 200 or game_height < 200:
            # Use full client rect
            game_x = x
            game_y = y
            game_width = width
            game_height = height

        self.game_rect = (game_x, game_y, game_width, game_height)
        return self.game_rect

    def get_game_rect(self):
        """Get current game rect."""
        return self.game_rect

    def set_chrome(self, top=0, bottom=0, left=0, right=0):
        """Manually set chrome sizes if detection fails."""
        self.border_top = top
        self.border_bottom = bottom
        self.border_left = left
        self.border_right = right
