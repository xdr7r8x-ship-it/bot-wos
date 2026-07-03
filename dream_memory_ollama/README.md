# Dream Memory Ollama Overlay (Local AI)

## 🎯 The Ultimate Solution - 100% Free, No Limits!

A Windows visual overlay assistant for **Dream Memory** hidden-object event in Whiteout Survival.

### Why Ollama?

| Feature | Gemini API | Ollama (Local) |
|---------|-----------|----------------|
| Cost | Limited free tier | **FREE** |
| Internet | Required | **Not needed** |
| Limits | 15 req/min | **No limits** |
| Speed | Depends on API | **Fast (GPU)** |
| Privacy | Data to Google | **100% Local** |

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
- No API calls to external servers
- No item library required
- No sample images required

## Installation

### Step 1: Install Ollama (One-time setup)

1. Download from: https://ollama.com/download
2. Install Ollama on your Windows PC
3. Open PowerShell and run:

```powershell
# Download the vision model (about 4GB)
ollama pull llava:7b
```

Or use the newer vision model:
```powershell
ollama pull llama3.2-vision:11b
```

### Step 2: Start Ollama

```powershell
ollama serve
```

Keep this window open while using the app!

### Step 3: Install Python Dependencies

```powershell
cd C:\path\to\dream_memory_ollama
pip install -r requirements.txt
```

### Step 4: Run the App

```powershell
python main.py
```

## Running

```powershell
# 1. Start Ollama (keep running)
ollama serve

# 2. Run the app
cd dream_memory_ollama
python main.py
```

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

### Ollama Not Connected

```powershell
# Check Ollama status
ollama list

# If empty, download model
ollama pull llava:7b
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

- **RAM**: 8GB minimum (16GB recommended)
- **GPU**: Optional but recommended (NVIDIA for best performance)
- **Storage**: 5GB for Ollama model

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

1. **GPU Acceleration**: Ollama automatically uses GPU if available
2. **Close Background Apps**: Improves performance
3. **Model Choice**: `llava:7b` is faster, `llama3.2-vision:11b` is more accurate
4. **Resolution**: Lower JPEG quality = faster processing

## License

For personal use only.
