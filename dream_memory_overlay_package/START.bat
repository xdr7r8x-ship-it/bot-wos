@echo off
title Dream Memory Overlay Assistant
color 0A
echo.
echo  ================================================
echo     Dream Memory Overlay Assistant
echo     For Whiteout Survival - Dream Memory
echo  ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.11+ from:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if OPENAI_API_KEY is set
if "%OPENAI_API_KEY%"=="" (
    echo [WARNING] OPENAI_API_KEY is not set!
    echo.
    echo Please enter your OpenAI API Key:
    set /p API_KEY="API Key: "
    setx OPENAI_API_KEY "%API_KEY%"
    set OPENAI_API_KEY=%API_KEY%
    echo [OK] API Key saved to environment
    echo.
)

REM Check and install dependencies
echo [INFO] Checking dependencies...
pip show openai >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        echo Try running as Administrator
        pause
        exit /b 1
    )
)
echo [OK] Dependencies installed
echo.

REM Start the application
echo ================================================
echo  Starting Dream Memory Overlay...
echo  Make sure BlueStacks is running!
echo  Press ESC to exit
echo ================================================
echo.
python main.py

pause
