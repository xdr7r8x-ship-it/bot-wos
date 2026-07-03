"""
Dream Memory Ollama Overlay - Configuration
Local AI - No API needed, No internet needed, No limits!
"""

# Ollama Settings (Local AI)
OLLAMA_HOST = "http://localhost:11434"
MODEL = "llava:7b"  # Vision model for local AI
FALLBACK_MODEL = "llama3.2-vision:11b"  # Alternative vision model

# Timing (milliseconds)
WATCH_INTERVAL_MS = 150
GEOMETRY_REFRESH_MS = 300
API_COOLDOWN_MS = 500
REQUEST_DEBOUNCE_MS = 250
ANALYSIS_TIMEOUT_SECONDS = 30  # Local AI needs more time

# Image processing
JPEG_QUALITY = 30
MAX_WIDTH = 1024

# Detection
MAX_REQUESTS = 20
CONFIDENCE_MIN = 10

# Game area detection
REQUEST_BAR_HEIGHT_RATIO = 0.24
REQUEST_CHANGE_THRESHOLD = 8

# Window target
WINDOW_TITLE_KEYWORDS = ["BlueStacks App Player", "BlueStacks"]

# Overlay appearance
OVERLAY_CIRCLE_RADIUS = 22
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
STATUS_NO_OLLAMA = "NO OLLAMA"
STATUS_READY = "READY"

# Vision prompt for Ollama
VISION_PROMPT = """Analyze this Dream Memory hidden-object game wave.

You receive two images:
1. request_bar: the bottom bar showing the current requested objects
2. scene: the main hidden-object scene

The user has no templates, no dataset, and no item samples.

The game works in waves:
- The request bar shows only the currently requested objects
- The number of visible requests is dynamic
- After current requests are found, the request bar changes

Task:
1. Read every currently visible request from request_bar image
2. Find only those requested objects inside scene image
3. Return one approximate bounding box for each found object

Output rules:
- bbox coordinates normalized from 0 to 1000
- Use short Arabic labels when readable
- confidence must be 0 to 100
- No explanation, only JSON

Return ONLY valid JSON:
{
  "wave_id": "auto",
  "requests": ["item1", "item2"],
  "marks": [
    {
      "label": "item1",
      "bbox": {"x1": 0, "y1": 0, "x2": 1000, "y2": 1000},
      "confidence": 85
    }
  ]
}

If no items found: {"wave_id": "auto", "requests": [], "marks": []}
"""
