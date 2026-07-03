@echo off
chcp 65001 >nul
title Dream Memory Visual - Auto Install
color 0A
echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   Dream Memory Visual - BlueStacks Edition      ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

echo [1/5] Downloading project...
curl -L "https://github.com/xdr7r8x-ship-it/bot-wos/archive/refs/heads/FINAL.zip" -o project.zip

echo.
echo [2/5] Extracting...
powershell -command "Expand-Archive -Path project.zip -DestinationPath . -Force"

echo.
echo [3/5] Installing packages...
cd bot-wos-FINAL\VISUAL_VERSION
pip install opencv-python pillow PyQt6 pywin32 numpy -q

echo.
echo [4/5] Checking BlueStacks...
echo Please make sure BlueStacks is running!

echo.
echo [5/5] Starting application...
start cmd /k "title Dream Memory && python main.py"

cd ..
del project.zip >nul 2>&1

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   Ready! Overlay should appear over BlueStacks   ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
pause
