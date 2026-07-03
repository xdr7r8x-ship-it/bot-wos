@echo off
title Dream Memory - Auto Install
echo.
echo ================================================
echo  Dream Memory - Auto Install
echo ================================================
echo.

echo Step 1/4: Downloading...
curl -L "https://github.com/xdr7r8x-ship-it/bot-wos/archive/refs/heads/FINAL.zip" -o final.zip

echo.
echo Step 2/4: Extracting...
powershell -command "Expand-Archive -Path final.zip -DestinationPath . -Force"

echo.
echo Step 3/4: Installing packages...
pip install opencv-python pillow PyQt6 pywin32 keyboard numpy -q

echo.
echo Step 4/4: Starting...
cd bot-wos-FINAL\INSTANT_VERSION
start cmd /k "python main.py"

del final.zip >nul 2>&1

echo.
echo ================================================
echo  DONE! App is starting!
echo ================================================
pause
