# Game area detector for Dream Memory
import config


class GameAreaDetector:
    """Detect game area in BlueStacks window."""

    def __init__(self):
        self.request_bar_height = 0

    def get_request_bar_region(self, window_height: int) -> tuple:
        """Get request bar region (top portion)."""
        height = int(window_height * config.REQUEST_BAR_HEIGHT_RATIO)
        return (0, 0, 0, height)  # x, y, width, height

    def get_scene_region(self, window_height: int) -> tuple:
        """Get game scene region (below request bar)."""
        bar_height = int(window_height * config.REQUEST_BAR_HEIGHT_RATIO)
        return (0, bar_height, 0, window_height)

    def is_in_request_bar(self, y: int, window_height: int) -> bool:
        """Check if y coordinate is in request bar."""
        bar_height = int(window_height * config.REQUEST_BAR_HEIGHT_RATIO)
        return y < bar_height
