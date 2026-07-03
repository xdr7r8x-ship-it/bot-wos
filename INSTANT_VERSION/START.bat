@echo off
chcp 65001 >nul
title Dream Memory - Zero Setup
color 0A
echo.
echo  ╔════════════════════════════════════════════════════════╗
echo  ║   Dream Memory - Zero Setup Edition              ║
echo  ║   NO AI, NO API, NO WAITING!                    ║
echo  ╚════════════════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found

:: Install packages
echo.
echo [INFO] Installing packages...
pip install opencv-python pillow PyQt6 pywin32 -q

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install packages!
    echo Try running as Administrator.
    pause
    exit /b 1
)

echo [OK] Packages installed

:: Run
echo.
echo ═══════════════════════════════════════════════════════
echo.
echo Starting Dream Memory...
echo.
echo CONTROLS:
echo   F8 - Toggle overlay
echo   F9 - Start/Stop monitoring
echo   ESC - Exit
echo.
echo ═══════════════════════════════════════════════════════
echo.
python main.py

pause
