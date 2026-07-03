@echo off
title Dream Memory PRO - Installing
echo.
echo ================================================
echo  Dream Memory PRO - Auto Install
echo ================================================

echo.
echo [1/4] Downloading project...
curl -L "https://github.com/xdr7r8x-ship-it/bot-wos/archive/refs/heads/FINAL.zip" -o project.zip

echo.
echo [2/4] Extracting...
powershell -command "Expand-Archive -Path project.zip -DestinationPath . -Force"

echo.
echo [3/4] Installing packages...
cd bot-wos-FINAL\PRO_VERSION
pip install opencv-python pillow PyQt6 pywin32 numpy -q

echo.
echo [4/4] Starting application...
start cmd /k "python main.py"

cd ..
del project.zip >nul 2>&1

echo.
echo ================================================
echo  Installation complete!
echo ================================================
pause
