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
REQUEST_BAR_HEIGHT_RATIO = 0.22  # Bottom bar height as ratio of screen height

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

# Vision prompt
VISION_PROMPT = """Analyze this hidden-object game screenshot in emergency wave mode.

The player has a 15-second target time.

The game works in waves:
- The bottom bar shows the currently requested objects.
- The number of visible requests is not fixed.
- It can be 3, 4, 5, 6, 8, 10, or more.
- After current requests are completed, the bottom bar changes and new objects may be added into the same scene.

Task:
1. Read all currently visible requested objects in the bottom request bar.
2. Count them dynamically.
3. Find only those currently requested objects inside the main scene.
4. Return one approximate center point for each found object.
5. Ignore completed objects.
6. Ignore future objects.
7. Never mark objects inside the bottom request bar.
8. Prioritize speed and useful approximate centers over perfect certainty.

Rules:
- Coordinates normalized from 0 to 1000.
- x=0 is left edge, x=1000 is right edge.
- y=0 is top edge, y=1000 is bottom edge.
- Return up to 20 current requested objects.
- Use short labels (1-3 words max).
- If Arabic is readable, use Arabic labels.
- If unclear, use short English labels.
- No explanation text outside the JSON.
- Return ONLY valid JSON in this exact format:
{
  "requests": ["item1", "item2", ...],
  "marks": [
    {"label": "item1", "x": 123, "y": 456, "confidence": 87},
    {"label": "item2", "x": 789, "y": 321, "confidence": 92}
  ]
}
"""
