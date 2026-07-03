"""
Dream Memory - Instant Detection Config
Uses Template Matching + Color Detection - NO AI NEEDED!
"""

import os

# =============================================================================
# DETECTION MODE
# =============================================================================
# Options: "template" (fast), "color" (accurate), "hybrid" (both)
DETECTION_MODE = "hybrid"

# =============================================================================
# TEMPLATE MATCHING SETTINGS
# =============================================================================
TEMPLATE_MATCH_THRESHOLD = 0.7  # 0-1, higher = stricter
TEMPLATE_SCALE_RANGE = (0.8, 1.2)  # Scale range for matching
TEMPLATE_MAX_RESULTS = 10  # Max objects to find

# =============================================================================
# COLOR DETECTION SETTINGS
# =============================================================================
COLOR_THRESHOLD = 50  # Color distance threshold
COLOR_MIN_AREA = 100  # Min pixel area to detect

# =============================================================================
# SCREEN SETTINGS
# =============================================================================
BLUESTACKS_WIDTH = 497
BLUESTACKS_HEIGHT = 888
GAME_TOP = 0
GAME_BOTTOM = 675
BAR_TOP = 675
BAR_BOTTOM = 888

# Window title to detect
WINDOW_TITLE = "BlueStacks"

# =============================================================================
# OVERLAY SETTINGS
# =============================================================================
OVERLAY_OPACITY = 0.7
OVERLAY_COLOR = (0, 255, 0)  # Green
OVERLAY_RADIUS = 15
OVERLAY_LINE_WIDTH = 3

# =============================================================================
# TIMING
# =============================================================================
SCAN_INTERVAL_MS = 200  # How often to scan
CHANGE_DEBOUNCE_MS = 300  # Debounce for request changes

# =============================================================================
# TEMPLATES FOLDER
# =============================================================================
TEMPLATES_FOLDER = "templates"
if not os.path.exists(TEMPLATES_FOLDER):
    os.makedirs(TEMPLATES_FOLDER)
