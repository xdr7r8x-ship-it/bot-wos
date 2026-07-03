"""
Dream Memory Helper - Free Version (No API Required!)
Uses OpenCV template matching instead of AI.
"""

# Template matching settings
CONFIDENCE_THRESHOLD = 0.6  # 60% match confidence
SEARCH_SCALE_MIN = 0.5     # Scale range for matching
SEARCH_SCALE_MAX = 1.5

# Image processing
MAX_MATCHES = 20           # Max objects to mark
CIRCLE_RADIUS = 20
REQUEST_BAR_RATIO = 0.18   # Bottom 18% is UI bar

# Colors (BGR for OpenCV)
CIRCLE_COLOR = (0, 255, 0)  # Green
TEXT_COLOR = (255, 255, 255)  # White
BG_COLOR = (50, 50, 50)  # Dark gray

# Status
STATUS_READY = "READY"
STATUS_SCANNING = "SCANNING"
STATUS_FOUND = "FOUND"
STATUS_NO_MATCH = "NO MATCH"
