@echo off
title Dream Memory Overlay
color 0A
echo.
echo  ================================================
echo     Dream Memory Overlay - Ready to Run!
echo  ================================================
echo.

REM Set your API Key here (ask for it if needed)
if "%OPENAI_API_KEY%"=="" (
    echo [ERROR] Please set OPENAI_API_KEY environment variable first!
    echo.
    echo Run API_KEY.bat to set your key, or set it manually:
    echo   setx OPENAI_API_KEY "your-key-here"
    pause
    exit /b 1
)

REM Start the app
echo [OK] Starting Dream Memory Overlay...
echo [OK] Target: BlueStacks
echo.
python main.py

echo.
echo ================================================
echo  App Closed
echo ================================================
pause
