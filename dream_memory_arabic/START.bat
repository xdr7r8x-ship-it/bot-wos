@echo off
title Dream Memory Helper - Arabic
color 0A
echo.
echo ================================================
echo   Dream Memory Helper - Arabic Version
echo ================================================
echo.

pip install opencv-python numpy mss pywin32 -q

echo.
echo Starting...
echo.
python main.py

pause
