"""
Dream Memory Zero-Data Overlay - Configuration
"""

# Gemini Model
MODEL = "gemini-2.5-flash"

# Timing (milliseconds)
WATCH_INTERVAL_MS = 150
GEOMETRY_REFRESH_MS = 300
API_COOLDOWN_MS = 600
REQUEST_DEBOUNCE_MS = 250
ANALYSIS_TIMEOUT_SECONDS = 8

# Image processing
JPEG_QUALITY = 32
MAX_WIDTH = 850

# Detection
MAX_REQUESTS = 20
CONFIDENCE_MIN = 10

# Game area detection
REQUEST_BAR_HEIGHT_RATIO = 0.24
REQUEST_CHANGE_THRESHOLD = 8

# Window target
WINDOW_TITLE_KEYWORDS = ["BlueStacks App Player", "BlueStacks"]

# Overlay appearance
OVERLAY_CIRCLE_RADIUS = 20
OVERLAY_CIRCLE_COLOR = (0, 255, 0, 255)
OVERLAY_TEXT_COLOR = (255, 255, 255, 255)
OVERLAY_FONT_SIZE = 11
OVERLAY_LINE_WIDTH = 2

# Status texts
STATUS_LIVE = "LIVE"
STATUS_ANALYZING = "ANALYZING"
STATUS_NO_MARKS = "NO MARKS"
STATUS_API_ERROR = "API ERROR"
STATUS_PARSE_ERROR = "PARSE ERROR"
STATUS_WAITING = "WAITING FOR BLUESTACKS"
STATUS_STALE = "STALE IGNORED"
STATUS_STOPPED = "STOPPED"
STATUS_NO_WINDOW = "NO WINDOW"

# Vision prompt
VISION_PROMPT = """Analyze this Dream Memory hidden-object game wave.

You receive two images:
1. request_bar_image: the bottom bar showing the current requested objects.
2. scene_image: the main hidden-object scene.

The user has no templates, no dataset, and no item samples.
This is zero-data emergency vision mode.

The game works in waves:
- The request bar shows only the currently requested objects.
- The number of visible requests is dynamic.
- After current requests are found, the request bar changes.
- New objects may appear in the same scene.

Task:
1. Read every currently visible request from request_bar_image.
2. Count all current visible requests dynamically.
3. Find only those requested objects inside scene_image.
4. Return one approximate bounding box for each found object.
5. Use useful approximate boxes when exact boundaries are unclear.
6. Prioritize speed and practical guidance.
7. Ignore completed objects.
8. Ignore future objects.
9. Ignore UI buttons, rewards, bars, emulator controls, and request icons.
10. Return JSON only.

Output rules:
- bbox coordinates normalized from 0 to 1000.
- Use short Arabic labels when readable.
- If Arabic is unclear, use short English labels.
- confidence must be 0 to 100.
- No explanation.
- No markdown.
- JSON only.

Return ONLY valid JSON:
{
  "wave_id": "string",
  "requests": ["string"],
  "marks": [
    {
      "label": "string",
      "bbox": {"x1": 0, "y1": 0, "x2": 1000, "y2": 1000},
      "confidence": 0
    }
  ]
}

If no items found, return:
{"wave_id": "auto", "requests": [], "marks": []}
"""
