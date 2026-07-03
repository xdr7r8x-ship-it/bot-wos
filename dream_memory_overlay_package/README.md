# Dream Memory Live Overlay Assistant

A Windows desktop application that provides **real-time visual guidance** for the "Dream Memory" hidden-object mini-game in Whiteout Survival. The app captures the BlueStacks/emulator window, analyzes it using OpenAI Vision, and draws visual markers over requested objects.

## 🎮 Game: ذاكرة الأحلام (Dream Memory)

- **Event**: Whiteout Survival Anniversary Event
- **Objective**: Find hidden objects before time runs out (20 seconds per wave)
- **Strategy**: Use this overlay to locate items faster and complete waves with time to spare

## What It Does

- ✅ **Window Capture**: Captures BlueStacks/emulator window specifically
- ✅ **Request Bar Detection**: Detects when bottom bar changes
- ✅ **AI Vision Analysis**: Uses OpenAI GPT-4o-mini to find objects
- ✅ **Visual Overlay**: Draws circles, numbers, and labels over found objects
- ✅ **Click-Through**: Does NOT interfere with mouse clicks on the game
- ✅ **Auto-Start**: Starts monitoring automatically on launch

## What It Does NOT Do

- ❌ No auto-clicking
- ❌ No mouse movement
- ❌ No keyboard input
- ❌ No bot behavior

## Requirements

- Windows 10/11
- Python 3.11+
- BlueStacks (or other Android emulator)
- OpenAI API key

## Installation

### 1. Install Python Dependencies

```powershell
cd dream_memory_overlay
pip install -r requirements.txt
```

### 2. Set Your OpenAI API Key

**Quick (PowerShell)**:
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

**Permanent (PowerShell Admin)**:
```powershell
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-your-api-key-here", "User")
```

### 3. BlueStacks Settings

1. Open **BlueStacks Settings**
2. Go to **Display** → Set to **1920x1080** or **1280x720**
3. Set mode to **Windowed** or **Borderless**
4. Make sure BlueStacks window title contains "BlueStacks"

### 4. Find BlueStacks Window Title (if needed)

The app looks for windows with "BlueStacks" in the title by default. If your title is different:

```powershell
$env:TARGET_WINDOW="Your Window Title"
```

## How to Run

```powershell
# Set API key first
$env:OPENAI_API_KEY="sk-your-api-key-here"

# Run the app
cd dream_memory_overlay
python main.py
```

## Supported Emulators

| Emulator | Window Title Contains |
|----------|----------------------|
| BlueStacks 5 | "BlueStacks" |
| BlueStacks 4 | "BlueStacks" |
| LDPlayer | "LDPlayer" |
| NOX | "Nox" |
| MEmu | "MEmu" |
| GameLoop | "GameLoop" |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **F8** | Toggle overlay visibility |
| **F9** | Start/Stop monitoring |
| **F10** | Force analysis |
| **ESC** | Exit app |

## Status Indicators

| Status | Meaning |
|--------|---------|
| `LIVE` | Monitoring active ✅ |
| `ANALYZING` | AI processing 🔄 |
| `NO MARKS` | No objects found |
| `API ERROR` | OpenAI error |
| `STOPPED` | Monitoring paused |
| `NO WINDOW` | Window not found |

## Troubleshooting

### "NO WINDOW" Status
- Check BlueStacks is running
- Verify window title: `Get-Process | Where-Object {$_.MainWindowTitle -like "*Blue*"}`
- Set correct window title: `$env:TARGET_WINDOW="Your Title"`

### Overlay Behind Game
- Press **F8** to toggle
- Set BlueStacks to windowed mode
- Run as Administrator

### Wrong Circle Positions
- The AI analyzes the entire window
- Coordinates are relative to the captured area
- Try pressing **F10** to refresh

### API Errors
- Check your API key is valid
- Check internet connection
- Wait 60 seconds (rate limit recovery)

## Performance

- **Watch Loop**: 200ms interval
- **API Calls**: Only when request bar changes
- **Cooldown**: 700ms between API calls
- **Bandwidth**: ~50KB per image (compressed JPEG)

## Project Structure

```
dream_memory_overlay/
├── main.py         # Entry point + app lifecycle
├── config.py       # Settings + vision prompt
├── capture.py      # Window/screen capture
├── analyzer.py     # OpenAI Vision API
├── watcher.py      # Monitoring loop
├── overlay.py      # Click-through UI
├── requirements.txt
└── README.md
```

## How It Works

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   BlueStacks    │────▶│   Capture    │────▶│   Watcher   │
│   Window        │     │   (200ms)    │     │   Loop       │
└─────────────────┘     └──────────────┘     └──────┬──────┘
                                                     │
                              ┌──────────────────────┘
                              ▼
                    ┌─────────────────┐     ┌─────────────┐
                    │  Change         │────▶│   OpenAI    │
                    │  Detected?      │ Yes │   Vision    │
                    └─────────────────┘     └──────┬──────┘
                              │ No                   │
                              ▼                      ▼
                    ┌─────────────────┐     ┌─────────────┐
                    │  Wait 200ms      │     │   Draw      │
                    │  Check Again     │     │   Circles   │
                    └─────────────────┘     └─────────────┘
```

## Disclaimer

For educational purposes only. Use at your own risk. Follow Whiteout Survival's Terms of Service.
