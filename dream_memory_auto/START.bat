@echo off
title Dream Memory AUTO - No API Needed!
color 0A
echo.
echo ================================================
echo  Dream Memory Helper - AUTOMATIC VERSION
echo  No API Key - 100%% FREE!
echo ================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Install Python from python.org
    pause
    exit /b
)

echo [INFO] Installing dependencies...
pip install opencv-python numpy mss pywin32 -q

echo.
echo [READY] Starting...
echo Make sure BlueStacks is running!
echo.
python main.py

pause
