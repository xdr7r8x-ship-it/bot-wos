# Dream Memory Hybrid Overlay

## 🎯 Works Automatically - Ollama OR Gemini!

A Windows visual overlay assistant for **Dream Memory** hidden-object event in Whiteout Survival.

### Auto-Detection: No Setup Hassles!

The app automatically detects what's available:

| Backend | Cost | Quotas | Setup |
|---------|------|--------|-------|
| **Ollama (Local)** | FREE | Unlimited | Install once |
| **Gemini (Cloud)** | FREE Tier | 15/min | Set API key |

**Works out-of-box with ZERO configuration!**

## What This App Does

- Detects the BlueStacks App Player window automatically
- Creates a transparent click-through overlay over the game viewport
- Captures only the game area (not full desktop)
- Uses **Local AI (Ollama)** for object detection
- Reads visible requests from the request bar
- Locates requested objects in the main scene
- Draws circles, numbers, and labels over found objects
- Monitors request bar continuously
- Triggers new analysis when requests change

## What This App Does NOT Do

- No auto-clicking
- No mouse movement to the game
- No keyboard input to the game
- No bot behavior
- No API calls to external servers (after setup)
- No item library required
- No sample images required

## Installation

### Option 1: Ollama (Recommended - Unlimited, Local)

```powershell
# 1. Install Ollama
https://ollama.com/download

# 2. Pull vision model (one-time)
ollama pull qwen2.5vl:3b

# 3. Start Ollama server (keep running)
ollama serve

# 4. Install Python deps
pip install mss pillow PyQt6 pywin32 requests

# 5. Run
python main.py
```

### Option 2: Gemini API (Cloud - Fallback)

```powershell
# 1. Get free API key
# https://aistudio.google.com/app/apikey

# 2. Set API key
$env:GEMINI_API_KEY="your-key-here"

# 3. Install Python deps
pip install mss pillow PyQt6 pywin32 requests

# 4. Run (no Ollama needed!)
python main.py
```

### Option 3: Zero Setup (Auto-Detect)

```powershell
# Just install Python deps and run!
pip install mss pillow PyQt6 pywin32 requests
python main.py
```

The app will automatically use:
- **Ollama** if installed and running
- **Gemini** if API key is set
- Shows helpful errors if neither is available

## Recommended BlueStacks Settings

1. **Window Mode**: Use Windowed (not fullscreen)
2. **Layout**: Portrait orientation
3. **Resolution**: 497x888 (portrait)
4. **Avoid**: Exclusive fullscreen mode

## Hotkeys

| Key | Action |
|-----|--------|
| F8 | Toggle overlay visibility |
| F9 | Toggle monitoring on/off |
| F10 | Force analyze current wave |
| ESC | Exit application |

## Status Indicators

| Status | Meaning |
|--------|---------|
| READY | System ready |
| LIVE | Objects found and marked |
| ANALYZING | AI processing image |
| NO MARKS | No objects found |
| API ERROR | Ollama connection error |
| NO OLLAMA | Ollama not running |
| WAITING FOR BLUESTACKS | Window not found |

## Troubleshooting

### Ollama Not Running

```powershell
# Check Ollama status
ollama list

# If empty, download model
ollama pull qwen2.5vl:3b

# Start server
ollama serve
```

### Model Not Found

```powershell
ollama pull qwen2.5vl:3b
```

### Overlay Not Aligned

- Ensure BlueStacks is in windowed mode
- Try resizing BlueStacks slightly

### BlueStacks Not Detected

- Ensure BlueStacks App Player window title contains "BlueStacks"
- Try running as administrator

### Slow Analysis

- Ollama uses CPU by default
- For faster performance, use a GPU
- Close other applications

### No Objects Found

- Make sure the game is visible
- Check request bar is showing objects
- Press F10 to force analysis

## System Requirements

- **RAM**: 6GB minimum for qwen2.5vl:3b (8GB recommended)
- **RAM**: 12GB minimum for qwen2.5vl:7b
- **GPU**: Optional but recommended (NVIDIA CUDA for best performance)
- **Storage**: 2-6GB for Ollama model

## How It Works

```
BlueStacks Window
       ↓
Screen Capture (mss)
       ↓
Crop: Scene + Request Bar
       ↓
Send to Ollama (Local AI)
       ↓
Parse JSON Response
       ↓
Draw Circles on Overlay
```

## Files

```
dream_memory_ollama/
├── main.py              # Main application
├── config.py            # Configuration
├── window_tracker.py    # BlueStacks detection
├── game_area.py         # Game area detection
├── capture.py           # Screen capture
├── request_watcher.py   # Request bar monitoring
├── analyzer.py          # Ollama AI integration
├── overlay.py           # Transparent overlay
├── models.py            # Data structures
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Performance Tips

1. **GPU Acceleration**: Ollama automatically uses GPU if available (NVIDIA CUDA)
2. **Close Background Apps**: Improves performance
3. **Model Choice**: `qwen2.5vl:3b` is faster, `qwen2.5vl:7b` is more accurate
4. **Resolution**: Lower JPEG quality = faster processing

## License

For personal use only.
