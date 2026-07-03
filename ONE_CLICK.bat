@echo off
chcp 65001 >nul
title Dream Memory - One Click!
echo.
echo ================================================
echo  Dream Memory - التثبيت التلقائي
echo ================================================
echo.

:: تحميل
echo [1/4] Downloading...
bitsadmin /transfer mydownload https://github.com/xdr7r8x-ship-it/bot-wos/archive/refs/heads/FINAL.zip %CD%\final.zip

:: فك الضغط
echo.
echo [2/4] Extracting...
powershell -command "Expand-Archive -Path final.zip -DestinationPath . -Force"

:: تثبيت
echo.
echo [3/4] Installing packages...
pip install opencv-python pillow PyQt6 pywin32 -q

:: تشغيل
echo.
echo [4/4] Starting...
cd bot-wos-FINAL\INSTANT_VERSION
start "" cmd /k "title Dream Memory && python main.py"

:: تنظيف
del final.zip >nul 2>&1

echo.
echo ================================================
echo  Done! App is starting!
echo ================================================
pause
