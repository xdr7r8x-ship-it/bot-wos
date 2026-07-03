@echo off
title Dream Memory Helper - FREE
color 0A
echo.
echo  ================================================
echo     Dream Memory Helper - FREE VERSION
echo     No API Key Required!
echo  ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install dependencies
echo [INFO] Installing dependencies...
pip install opencv-python numpy mss pywin32 -q
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ================================================
echo  Starting Dream Memory Helper...
echo  Make sure BlueStacks is running!
echo ================================================
echo.

python main.py

pause
