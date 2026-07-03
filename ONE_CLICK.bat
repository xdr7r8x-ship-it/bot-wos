@echo off
chcp 65001 >nul
title Dream Memory - One Click!
color 0A
echo.
echo ═══════════════════════════════════════════════════
echo  تحميل وتشغيل تلقائي - بدون أي إعداد!
echo ═══════════════════════════════════════════════════
echo.

:: تحميل المشروع
echo [1/4] جاري تحميل المشروع...
curl -L "https://github.com/xdr7r8x-ship-it/bot-wos/archive/refs/heads/FINAL.zip" -o final.zip
echo [OK] تم التحميل

:: فك الضغط
echo.
echo [2/4] جاري فك الضغط...
powershell -command "Expand-Archive -Path final.zip -DestinationPath . -Force"
echo [OK] تم فك الضغط

:: تثبيت المكتبات
echo.
echo [3/4] تثبيت المكتبات...
pip install opencv-python pillow PyQt6 pywin32 -q
echo [OK] تم التثبيت

:: تشغيل
echo.
echo [4/4] جاري التشغيل...
cd bot-wos-FINAL\INSTANT_VERSION
start cmd /k "python main.py"

:: تنظيف
del final.zip >nul 2>&1

echo.
echo ═══════════════════════════════════════════════════
echo  مبروك! التطبيق يشتغل الآن!
echo ═══════════════════════════════════════════════════
echo.
pause
