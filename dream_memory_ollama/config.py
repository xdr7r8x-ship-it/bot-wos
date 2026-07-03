# Dream Memory - Ollama Vision Config
# No API keys required

# Vision backend (Ollama only)
VISION_BACKEND = "ollama"
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Ollama model
OLLAMA_MODEL = "qwen2.5vl:3b"

# Timing
GEOMETRY_REFRESH_MS = 1000
ANALYSIS_TIMEOUT_SECONDS = 60

# Image
JPEG_QUALITY = 25
MAX_WIDTH = 640

# Limits
MAX_REQUESTS = 20
CONFIDENCE_MIN = 10

# Request bar (at BOTTOM of screen)
REQUEST_BAR_HEIGHT_RATIO = 0.24

# Viewport detection mode: "auto", "center_portrait", "manual"
VIEWPORT_MODE = "auto"

# Viewport aspect ratio (portrait)
VIEWPORT_ASPECT = 9 / 16

# Manual viewport override (used when VIEWPORT_MODE="manual")
MANUAL_VIEWPORT_X = None
MANUAL_VIEWPORT_Y = None
MANUAL_VIEWPORT_W = None
MANUAL_VIEWPORT_H = None

# Margin ignores for center_portrait fallback
RIGHT_TOOLBAR_IGNORE_PX = 60
LEFT_IGNORE_PX = 0
TOP_IGNORE_PX = 0
BOTTOM_IGNORE_PX = 0

# Debug
DEBUG_VIEWPORT_BORDER = True

# Startup behavior - DISABLED BY DEFAULT
AUTO_ANALYZE_ON_START = False
AUTO_WATCH_REQUEST_BAR = False

# Status values
STATUS_LIVE = "LIVE"
STATUS_ANALYZING = "ANALYZING..."
STATUS_NO_MARKS = "NO MARKS"
STATUS_API_ERROR = "API ERROR"
STATUS_WAITING = "WAITING..."
STATUS_READY = "READY"
STATUS_STOPPED = "STOPPED"
STATUS_NO_WINDOW = "NO WINDOW"

# Error messages
ERR_NO_AI = "NO AI BACKEND"
ERR_NO_WINDOW = "NO WINDOW"
