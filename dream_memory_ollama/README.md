# Dream Memory - Ollama Vision Overlay

Official folder: `dream_memory_ollama`

## Features

- **Local AI Only** - Uses Ollama with qwen2.5vl vision model
- **No API Keys** - No Gemini, no OpenAI, no external APIs
- **Transparent Overlay** - Shows detected objects over BlueStacks
- **Hotkeys** - Full keyboard control

## Requirements

1. **Windows 10/11**
2. **Ollama** installed locally
3. **BlueStacks** (or other Android emulator)
4. **Python 3.8+**

## Setup

### 1. Install Ollama

Download from: https://ollama.ai

### 2. Pull Vision Model

```powershell
ollama pull qwen2.5vl:3b
```

### 3. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Start Ollama

Make sure Ollama is running before starting the app:
```powershell
ollama serve
```

## Running

```powershell
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| **F8** | Toggle overlay visibility |
| **F9** | Toggle monitoring on/off |
| **F10** | Force analyze current screen |
| **ESC** | Exit program |

## How It Works

1. Captures BlueStacks window
2. Watches request bar for changes
3. When change detected, analyzes scene with Ollama Vision
4. Draws circles over detected objects

## Speed

- Depends on CPU/GPU/RAM
- qwen2.5vl:3b is optimized for speed
- Typical analysis: 5-15 seconds

## Offline Use

- Runtime internet not required after model download
- All processing done locally

## Troubleshooting

### Ollama Not Running
```
ERROR: Ollama not available
```
Start Ollama: `ollama serve`

### Model Not Found
```
MODEL NOT FOUND
```
Run: `ollama pull qwen2.5vl:3b`

### BlueStacks Not Found
```
WAITING FOR BLUESTACKS
```
Make sure BlueStacks is running in window mode.

## Technical Details

- Backend: Ollama (local)
- Model: qwen2.5vl:3b
- Vision: Built-in Ollama vision support
- Capture: win32gui + PIL
- Overlay: PyQt6 transparent window
