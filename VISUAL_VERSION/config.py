# Dream Memory Visual - BlueStacks Optimized
# Must work on BlueStacks 497x888

# BlueStacks window detection
WINDOW_TITLE = "BlueStacks"
ALT_TITLES = ["BlueStacks 5", "BlueStacks App Player", "BstSharedFolder"]

# Screen regions (BlueStacks 497x888)
GAME_WIDTH = 497
GAME_HEIGHT = 888

# Request bar location (top of screen)
BAR_TOP = 0
BAR_HEIGHT = 60

# Game scene location
SCENE_TOP = 60
SCENE_BOTTOM = 675

# Bottom bar
BOTTOM_TOP = 675
BOTTOM_BOTTOM = 888

# Detection settings
SCAN_INTERVAL_MS = 150  # Fast scan
COLOR_TOLERANCE = 45  # Color matching tolerance
MIN_OBJECT_PIXELS = 30  # Minimum object size in pixels

# Overlay settings
OVERLAY_OPACITY = 0.4
CIRCLE_SIZE = 20
LINE_WIDTH = 4
FONT_SIZE = 12
LABEL_OFFSET_X = 25
LABEL_OFFSET_Y = 5

# Detection colors for Dream Memory game items
# These are approximate RGB values - game items have specific colors
DETECTION_COLORS = {
    # Gold and coins
    "gold_coin": {"rgb": [255, 215, 0], "tol": 40},
    "gold": {"rgb": [255, 200, 50], "tol": 50},
    "coin": {"rgb": [255, 180, 0], "tol": 45},
    
    # Gems
    "red_gem": {"rgb": [220, 50, 50], "tol": 50},
    "blue_gem": {"rgb": [50, 100, 220], "tol": 50},
    "green_gem": {"rgb": [50, 200, 100], "tol": 50},
    "purple_gem": {"rgb": [150, 50, 200], "tol": 50},
    "pink_gem": {"rgb": [220, 100, 180], "tol": 50},
    "yellow_gem": {"rgb": [255, 230, 50], "tol": 50},
    
    # Special items
    "chest": {"rgb": [180, 120, 60], "tol": 55},
    "key": {"rgb": [255, 220, 100], "tol": 40},
    "star": {"rgb": [255, 255, 100], "tol": 45},
    "heart": {"rgb": [255, 80, 100], "tol": 50},
    "crystal": {"rgb": [150, 200, 255], "tol": 45},
    "diamond": {"rgb": [200, 230, 255], "tol": 40},
    "flower": {"rgb": [255, 150, 200], "tol": 50},
    
    # Common in games
    "snowflake": {"rgb": [200, 230, 255], "tol": 45},
    "butterfly": {"rgb": [180, 100, 200], "tol": 50},
    "shell": {"rgb": [255, 220, 200], "tol": 45},
    "feather": {"rgb": [200, 180, 255], "tol": 45},
    
    # Catch-all colors
    "bright_yellow": {"rgb": [255, 255, 100], "tol": 40},
    "bright_red": {"rgb": [255, 100, 100], "tol": 45},
    "bright_blue": {"rgb": [100, 150, 255], "tol": 45},
    "bright_green": {"rgb": [100, 255, 150], "tol": 45},
}

# Colors for visualization (BGR for OpenCV)
DRAW_COLORS = {
    "gold_coin": (0, 215, 255),  # BGR
    "gold": (0, 200, 255),
    "coin": (0, 180, 255),
    "red_gem": (50, 50, 220),
    "blue_gem": (220, 100, 50),
    "green_gem": (100, 200, 50),
    "purple_gem": (200, 50, 150),
    "pink_gem": (180, 100, 220),
    "yellow_gem": (50, 230, 255),
    "chest": (60, 120, 180),
    "key": (100, 220, 255),
    "star": (100, 255, 255),
    "heart": (100, 80, 255),
    "crystal": (255, 200, 150),
    "diamond": (255, 230, 200),
    "flower": (200, 150, 255),
    "snowflake": (255, 230, 200),
    "butterfly": (200, 100, 180),
    "shell": (200, 220, 255),
    "feather": (255, 180, 200),
    "bright_yellow": (100, 255, 255),
    "bright_red": (100, 100, 255),
    "bright_blue": (255, 150, 100),
    "bright_green": (150, 255, 100),
}
