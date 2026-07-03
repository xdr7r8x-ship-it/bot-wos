# Dream Memory PRO - Configuration
# Optimized for performance and stability

# Screen regions (relative to game window)
SCREEN_TOP = 0
SCREEN_BOTTOM = 675
BAR_TOP = 675
BAR_BOTTOM = 888

# Detection settings
DETECTION_MODE = "color"  # color, template, hybrid
COLOR_THRESHOLD = 50
SCAN_INTERVAL_MS = 300
MIN_OBJECT_SIZE = 50

# Overlay settings
OVERLAY_OPACITY = 0.3
CIRCLE_RADIUS = 12
LINE_WIDTH = 3
FONT_SIZE = 11

# Colors (BGR for OpenCV)
COLOR_GOLD = (0, 215, 255)
COLOR_RED = (0, 0, 255)
COLOR_BLUE = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_PURPLE = (255, 0, 255)
COLOR_ORANGE = (0, 165, 255)

# Known game item colors (RGB)
GAME_COLORS = {
    "gold": ([255, 215, 0], 40),
    "coin": ([255, 200, 0], 35),
    "gem_red": ([255, 0, 0], 30),
    "gem_blue": ([0, 0, 255], 30),
    "gem_green": ([0, 255, 0], 30),
    "gem_purple": ([128, 0, 128], 35),
    "chest": ([139, 69, 19], 45),
    "key": ([255, 215, 0], 25),
    "star": ([255, 255, 0], 30),
    "heart": ([255, 0, 0], 25),
    "crystal": ([200, 100, 255], 35),
    "diamond": ([100, 200, 255], 30),
}
