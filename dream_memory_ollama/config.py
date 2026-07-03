"""
Dream Memory Hybrid Overlay - Configuration
Supports both Ollama (local) and Gemini (cloud) with auto-fallback
"""

# =============================================================================
# AI BACKEND SELECTION
# =============================================================================
# Priority order: 1. Ollama (local, free), 2. Gemini (cloud, fallback)
# Set VISION_BACKEND to: "ollama", "gemini", or "auto" (auto-detect)
VISION_BACKEND = "auto"  # "auto" = try Ollama first, fallback to Gemini

# =============================================================================
# OLLAMA SETTINGS (Local AI - Recommended, Free, Unlimited)
# =============================================================================
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5vl:3b"  # Fast vision model
OLLAMA_STRONG_MODEL = "qwen2.5vl:7b"  # Optional stronger model

# =============================================================================
# GEMINI SETTINGS (Cloud AI - Fallback when Ollama unavailable)
# =============================================================================
# Get key from: https://aistudio.google.com/app/apikey
# Gemini has FREE tier: 15 requests/minute
GEMINI_API_KEY = ""  # Set via environment or enter here
GEMINI_MODEL = "gemini-2.0-flash"  # Fast free model
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# =============================================================================
# TIMING (milliseconds)
# =============================================================================
WATCH_INTERVAL_MS = 150
GEOMETRY_REFRESH_MS = 300
API_COOLDOWN_MS = 500
REQUEST_DEBOUNCE_MS = 250
ANALYSIS_TIMEOUT_SECONDS = 20  # Ollama
GEMINI_TIMEOUT_SECONDS = 30  # Gemini

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
STATUS_READY = "READY"
STATUS_OLLAMA = "OLLAMA"
STATUS_GEMINI = "GEMINI"

# Error messages
ERR_NO_AI = "NO AI AVAILABLE"
ERR_NO_OLLAMA = "OLLAMA NOT RUNNING"
ERR_NO_MODEL = "MODEL NOT FOUND"
ERR_NO_GEMINI = "GEMINI KEY MISSING"

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
