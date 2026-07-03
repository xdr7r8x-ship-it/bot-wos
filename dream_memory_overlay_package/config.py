"""
Dream Memory Live Overlay Assistant - Configuration
All runtime constants and settings.
"""

# OpenAI Model
MODEL = "gpt-4o-mini"

# Timing (milliseconds)
WATCH_INTERVAL_MS = 200       # How often to check for request bar changes
API_COOLDOWN_MS = 700        # Minimum time between API calls

# Image processing
JPEG_QUALITY = 35            # Compression quality for API (0-100)
MAX_WIDTH = 900              # Max width before sending to API
MAX_HEIGHT = 1600            # Max height before sending to API

# Detection
MAX_REQUESTS = 20             # Maximum visible requests to track
CONFIDENCE_MIN = 12           # Minimum confidence threshold (0-100)
REQUEST_BAR_HEIGHT_RATIO = 0.20  # Bottom bar height as ratio of screen height (game UI area)

# Window target (for BlueStacks/emulators)
WINDOW_TITLE_KEYWORDS = ["BlueStacks", "bluestacks", "Nox", "LDPlayer", "LDPlayer", "GameLoop", "MEmu"]
DEFAULT_WINDOW_TITLE = "BlueStacks"

# Overlay appearance
OVERLAY_CIRCLE_RADIUS = 25    # Circle radius in pixels
OVERLAY_CIRCLE_COLOR = (0, 255, 0, 255)  # Green RGBA
OVERLAY_TEXT_COLOR = (255, 255, 255, 255)  # White RGBA
OVERLAY_FONT_SIZE = 14
OVERLAY_LINE_WIDTH = 3

# Status texts
STATUS_LIVE = "LIVE"
STATUS_ANALYZING = "ANALYZING"
STATUS_NO_MARKS = "NO MARKS"
STATUS_API_ERROR = "API ERROR"
STATUS_PARSE_ERROR = "PARSE ERROR"
STATUS_STOPPED = "STOPPED"
STATUS_NO_WINDOW = "NO WINDOW"

# Vision prompt - Optimized for Dream Memory game
VISION_PROMPT = """You are analyzing a hidden-object game called "Dream Memory" from Whiteout Survival.

The game shows requested items in a BOTTOM BAR at the bottom 15-20% of the screen.
The MAIN SCENE is the area above the bottom bar.

TASK:
1. First, identify ALL items shown in the BOTTOM REQUEST BAR (the items you need to find)
2. Then, locate EACH of those items in the MAIN SCENE area (NOT in the bottom bar)
3. Return ONE center point for each found item in the main scene

IMPORTANT RULES:
- The bottom bar shows icons/sprites of items to find (3-5 items typically)
- Find the matching items HIDDEN in the main scene above the bottom bar
- Ignore the bottom bar when marking item locations
- Coordinates must point to the ITEM in the main scene, not the request bar
- x=0 is LEFT edge, x=1000 is RIGHT edge
- y=0 is TOP edge, y=1000 is BOTTOM edge
- Focus on the MAIN SCENE only for item locations

Return ONLY valid JSON:
{
  "requests": ["item1", "item2", "item3"],
  "marks": [
    {"label": "item1", "x": 500, "y": 400, "confidence": 90},
    {"label": "item2", "x": 200, "y": 300, "confidence": 85}
  ]
}

If no items are found, return:
{"requests": [], "marks": []}
"""
