@echo off
title Dream Memory Overlay - Setup
color 0A
echo.
echo  ================================================
echo     Dream Memory Overlay - Setup
echo  ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python 3.11+ from:
    echo https://www.python.org/downloads/
    echo.
    echo After installing, run this setup again.
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Install dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo.
    echo Try running this file AS ADMINISTRATOR:
    echo Right-click on SETUP.bat ^> Run as administrator
    pause
    exit /b 1
)

echo.
echo ================================================
echo  Setup Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Open START.bat to run the app
echo 2. Make sure BlueStacks is running
echo 3. Enter your OpenAI API key when prompted
echo.
echo Press any key to exit...
pause >nul
