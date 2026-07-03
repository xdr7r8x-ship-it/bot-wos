# Dream Memory - Ollama Vision Config
# No API keys required

# Vision backend (Ollama only)
VISION_BACKEND = "ollama"
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Ollama model
OLLAMA_MODEL = "qwen2.5vl:3b"

# Live mode settings
AUTO_LIVE_MODE = True
AUTO_ANALYZE_ON_START = True
AUTO_WATCH_REQUEST_BAR = True

# Viewport mode: "manual", "auto", "center_portrait"
VIEWPORT_MODE = "manual"

# Manual viewport (BlueStacks 5.2 portrait game)
MANUAL_VIEWPORT_X = 604
MANUAL_VIEWPORT_Y = 39
MANUAL_VIEWPORT_W = 549
MANUAL_VIEWPORT_H = 980

# Debug
DEBUG_VIEWPORT_BORDER = True

# Timing
WATCH_INTERVAL_MS = 200
REQUEST_DEBOUNCE_MS = 250
API_COOLDOWN_MS = 1500
ANALYSIS_TIMEOUT_SECONDS = 45

# Image
JPEG_QUALITY = 25
MAX_WIDTH = 640

# Limits
MAX_REQUESTS = 20
CONFIDENCE_MIN = 10

# Request bar (at BOTTOM of screen)
REQUEST_BAR_HEIGHT_RATIO = 0.24

# Status values
STATUS_READY = "READY"
STATUS_WATCHING = "WATCHING"
STATUS_ANALYZING = "ANALYZING..."
STATUS_LIVE = "LIVE"
STATUS_NO_MARKS = "NO MARKS"
STATUS_TIMEOUT = "TIMEOUT"
STATUS_API_ERROR = "API ERROR"
STATUS_WAITING = "WAITING..."
STATUS_NO_WINDOW = "NO WINDOW"
