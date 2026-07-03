@echo off
title Dream Memory - Installing
echo.
echo ================================================
echo  Dream Memory - Auto Install
echo ================================================
echo.

echo Step 1/5: Downloading...
curl -L "https://github.com/xdr7r8x-ship-it/bot-wos/archive/refs/heads/FINAL.zip" -o project.zip

echo.
echo Step 2/5: Extracting...
powershell -command "Expand-Archive -Path project.zip -DestinationPath . -Force"

echo.
echo Step 3/5: Installing packages...
cd bot-wos-FINAL\VISUAL_VERSION
pip install opencv-python pillow PyQt6 pywin32 numpy -q

echo.
echo Step 4/5: Ready to start...
echo Make sure BlueStacks is running first!

echo.
echo Step 5/5: Starting application...
start cmd /k "python main.py"

cd ..
del project.zip >nul 2>&1

echo.
echo ================================================
echo  DONE! Check for BlueStacks window
echo ================================================
pause
