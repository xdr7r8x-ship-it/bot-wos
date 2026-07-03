# Dream Memory Ollama Overlay (Qwen2.5-VL)

## 🎯 Local AI Solution - No API Keys, No Quotas!

A Windows visual overlay assistant for **Dream Memory** hidden-object event in Whiteout Survival.

### Why Ollama + Qwen2.5-VL?

| Feature | Cloud API | Ollama (Local) |
|---------|-----------|----------------|
| Cost | Limited/Paid | **FREE** |
| Quotas | Yes (rate limits) | **No quotas** |
| Speed | Depends on internet | **Local CPU/GPU** |
| Privacy | Data to cloud | **100% Local** |
| Internet | Always required | **Only for setup** |

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

### Step 1: Install Ollama

1. Download from: https://ollama.com/download
2. Install Ollama on your Windows PC

### Step 2: Pull the Vision Model

Open PowerShell and run:

```powershell
# Fast model (recommended for most systems)
ollama pull qwen2.5vl:3b

# Optional: Stronger model (requires more RAM)
ollama pull qwen2.5vl:7b
```

### Step 3: Start Ollama Server

```powershell
ollama serve
```

Keep this window open while using the app!

### Step 4: Install Python Dependencies

```powershell
cd C:\path\to\dream_memory_ollama
pip install -r requirements.txt
```

### Step 5: Run the App

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
