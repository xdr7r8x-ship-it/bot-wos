# Dream Memory Live Overlay Assistant

A Windows desktop application that provides real-time visual guidance for hidden-object games. The app captures your game screen, analyzes it using OpenAI Vision, and draws visual markers over requested objects in the main scene.

## What It Does

- **Live Screen Capture**: Continuously monitors your game screen
- **Request Bar Detection**: Detects when the bottom request bar changes
- **Vision Analysis**: Uses AI to locate requested objects in the game scene
- **Visual Overlay**: Draws circles, numbers, and labels over found objects
- **Click-Through Overlay**: Does not interfere with mouse/keyboard input

## What It Does NOT Do

- ❌ Auto-click or interact with the game
- ❌ Move the mouse
- ❌ Send keyboard input
- ❌ Play the game for you
- ❌ Train machine learning models

## Requirements

- Windows 10/11
- Python 3.11+
- OpenAI API key (GPT-4o-mini model)

## Installation

### 1. Install Python Dependencies

Open PowerShell and run:

```powershell
cd path\to\dream_memory_overlay
pip install -r requirements.txt
```

### 2. Set Your OpenAI API Key

**Option A - PowerShell (Current Session)**:
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

**Option B - PowerShell (Permanent)**:
```powershell
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-your-api-key-here", "User")
```

**Option C - Windows Environment Variables**:
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to Advanced → Environment Variables
3. Add new User variable: `OPENAI_API_KEY` = `sk-your-api-key-here`

## How to Run

```powershell
cd path\to\dream_memory_overlay
python main.py
```

## Game Settings

For best results, run your hidden-object game in:
- **Windowed mode** (recommended)
- **Borderless window mode**

Avoid **exclusive fullscreen** mode as it may prevent the overlay from displaying correctly.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **F8** | Toggle overlay visibility (show/hide) |
| **F9** | Start/Stop monitoring |
| **F10** | Force immediate analysis |
| **ESC** | Exit application |

## Status Indicators

The overlay shows status in the top-left corner:

| Status | Meaning |
|--------|---------|
| `LIVE` | Monitoring active, ready for detection |
| `ANALYZING` | Processing screen with AI |
| `NO MARKS` | AI found no objects |
| `API ERROR` | OpenAI API error occurred |
| `HIDDEN` | Overlay is hidden |
| `STOPPED` | Monitoring is stopped |

## Troubleshooting

### Overlay Not Visible
1. Press **F8** to toggle visibility
2. Check if the game is in exclusive fullscreen (change to windowed)
3. Make sure the overlay isn't behind the game window
4. Try running the app as Administrator

### API Key Missing Error
1. Verify the `OPENAI_API_KEY` environment variable is set
2. Restart your terminal/PowerShell after setting the variable
3. Check for typos in the API key

### Slow Detection
- The app monitors the request bar locally every 200ms
- AI analysis only triggers when the bar changes
- API response time depends on OpenAI servers

### Wrong Circles / No Circles
1. Ensure the game screen shows the request bar at the bottom
2. Make sure requested objects are visible in the main scene
3. Try pressing **F10** to force a new analysis
4. Check that the game hasn't changed modes

### Game in Fullscreen Hides Overlay
1. Switch the game to **windowed** or **borderless window** mode
2. The overlay should appear on top of windowed games

### Application Crashes
1. Check Python version (requires 3.11+)
2. Reinstall dependencies: `pip install --force-reinstall -r requirements.txt`
3. Check console output for error messages

## Performance

- **Monitoring**: Checks every 200ms for changes
- **API Calls**: Only triggered when request bar changes (not every frame)
- **API Cooldown**: 700ms minimum between calls to prevent rate limiting
- **Memory**: Uses efficient mss library for screen capture

## Project Structure

```
dream_memory_overlay/
├── main.py         # Application entry point
├── config.py       # Configuration and constants
├── capture.py      # Screen capture module
├── analyzer.py     # OpenAI Vision API integration
├── watcher.py      # Monitoring loop
├── overlay.py      # Transparent click-through overlay
├── requirements.txt # Python dependencies
└── README.md       # This file
```

## API Usage

The app uses OpenAI's GPT-4o-mini model with Vision capabilities:
- Model: `gpt-4o-mini`
- Image detail: Low (for speed)
- Response format: JSON
- Max tokens: 1024

## License

MIT License - Free for personal and commercial use.

## Disclaimer

This tool is for educational and assistance purposes only. Always follow the game's terms of service regarding third-party tools.
