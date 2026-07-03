# Dream Memory Zero-Data Overlay

## What This App Does

A Windows visual overlay assistant for the **Dream Memory** hidden-object event in Whiteout Survival, running inside BlueStacks.

- Detects the BlueStacks App Player window automatically
- Creates a transparent click-through overlay over the game viewport
- Captures only the game area (not full desktop)
- Splits capture into: main scene + request bar
- Sends images to Google Gemini Vision API for zero-data object detection
- Reads visible requests from the request bar
- Locates requested objects in the main scene
- Draws circles, numbers, and labels over found objects
- Monitors request bar continuously
- Triggers new analysis when requests change
- Keeps old marks visible while analyzing new wave
- Replaces marks only after fresh valid result arrives

## What This App Does NOT Do

- No auto-clicking
- No mouse movement to the game
- No keyboard input to the game
- No bot behavior
- No training pipeline
- No item library required
- No sample images required
- No template matching

## Important Limitation

**Zero-data vision mode is the fastest setup with no images or training, but it cannot guarantee 100% accuracy or zero delay.** Response time depends on Gemini API latency.

## Installation

### 1. Install Python 3.11+

Download from: https://www.python.org/downloads/

### 2. Install Dependencies

Open PowerShell and run:

```powershell
cd C:\path\to\dream_memory_zero_data
pip install -r requirements.txt
```

### 3. Set Up Gemini API Key (FREE!)

Get your free key from: https://aistudio.google.com/app/apikey

Set it before running:

```powershell
$env:GEMINI_API_KEY="your-key-here"
```

## Running the App

```powershell
cd C:\path\to\dream_memory_zero_data
$env:GEMINI_API_KEY="your-key-here"
python main.py
```

Or use the environment variable persistently:

```powershell
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-key-here", "User")
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
|--------|--------|
| LIVE | Overlay active, marks visible |
| ANALYZING | API call in progress |
| NO MARKS | No objects found |
| API ERROR | API call failed |
| PARSE ERROR | Invalid response from API |
| STALE IGNORED | Old result discarded |
| WAITING FOR BLUESTACKS | Window not found |
| STOPPED | Monitoring disabled |

## Troubleshooting

### Overlay Not Aligned

The overlay should attach to BlueStacks automatically. If it's misaligned:
- Ensure BlueStacks is in windowed mode
- Try resizing BlueStacks slightly

### BlueStacks Not Detected

- Ensure BlueStacks App Player window title contains "BlueStacks"
- Try running as administrator

### Slow Analysis

- Check your internet connection
- The API has built-in 8-second timeout
- Press F10 to retry

### Wrong Circles / False Positives

Zero-data mode relies on AI interpretation. Accuracy depends on:
- Image clarity
- Request bar visibility
- AI model response quality

### Request Bar Not Detected

- Ensure game is in portrait orientation
- Check BlueStacks resolution settings

### Overlay Hidden

- Press F8 to toggle visibility
- Check that BlueStacks window is visible

## Files

```
dream_memory_zero_data/
├── main.py              # Main application entry
├── config.py            # Configuration settings
├── window_tracker.py    # BlueStacks window detection
├── game_area.py         # Game area detection
├── capture.py           # Screen capture
├── request_watcher.py   # Request bar monitoring
├── analyzer.py          # Gemini Vision API
├── overlay.py           # Transparent overlay window
├── models.py            # Data structures
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Technical Details

- **Capture**: Uses mss for fast screen capture
- **Overlay**: PyQt6 frameless transparent window
- **Analysis**: Google Gemini 2.5 Flash with JSON output
- **Change Detection**: Image fingerprint + debounce
- **Single-flight**: Only one API call at a time; stale results ignored

## Cost

Uses **Google Gemini API** (FREE tier available):
- Gemini 2.5 Flash: Generous free tier
- Very low cost for personal use

## License

For personal use only.
