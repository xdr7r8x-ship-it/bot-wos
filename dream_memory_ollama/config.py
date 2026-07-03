"""
Dream Memory Ollama Overlay - Configuration
Local AI - No API needed, No internet needed, No limits!
"""

# Ollama Settings (Local AI)
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5vl:3b"  # Fast vision model
OLLAMA_STRONG_MODEL = "qwen2.5vl:7b"  # Optional stronger model

# Timing (milliseconds)
WATCH_INTERVAL_MS = 150
GEOMETRY_REFRESH_MS = 300
API_COOLDOWN_MS = 500
REQUEST_DEBOUNCE_MS = 250
ANALYSIS_TIMEOUT_SECONDS = 20

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
STATUS_NO_OLLAMA = "OLLAMA NOT RUNNING"
STATUS_MODEL_MISSING = "MODEL NOT FOUND"
STATUS_READY = "READY"

# Vision prompt for Ollama Qwen2.5-VL
VISION_PROMPT = """You receive two images:
1. request_bar: the bottom bar showing the current requested objects
2. scene: the main hidden-object scene

This is a Dream Memory hidden-object game. The user has no templates.

Task:
1. Read every currently visible request from request_bar image
2. Find only those requested objects inside scene image
3. Return one approximate bounding box for each found object

Rules:
- Ignore request bar icons and UI elements
- Ignore emulator UI and buttons
- Ignore completed or future requests
- Focus only on currently visible requested objects in the scene

Output: Return ONLY valid JSON, no explanation, no markdown.
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
