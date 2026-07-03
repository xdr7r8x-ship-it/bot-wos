@echo off
title Dream Memory Setup
echo.
echo Downloading...
curl -L "https://github.com/xdr7r8x-ship-it/bot-wos/archive/refs/heads/FINAL.zip" -o project.zip
echo.
echo Extracting...
powershell -command "Expand-Archive -Path project.zip -DestinationPath . -Force"
echo.
echo Installing packages...
cd bot-wos-FINAL\VISUAL_VERSION
pip install opencv-python pillow PyQt6 pywin32 numpy -q
echo.
echo Starting...
start cmd /k "python main.py"
cd ..
del project.zip >nul 2>&1
echo Done!
pause