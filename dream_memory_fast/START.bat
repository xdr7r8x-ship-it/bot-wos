@echo off
title Dream Memory - ULTRA FAST
color 0A
echo.
echo ================================================
echo  Dream Memory Helper - ULTRA FAST VERSION
echo ================================================
echo.

pip install opencv-python numpy mss pywin32 -q
if errorlevel 1 goto :error

echo [READY]
echo.
python main.py
pause
exit /b

:error
echo [ERROR] Failed to install dependencies
pause
