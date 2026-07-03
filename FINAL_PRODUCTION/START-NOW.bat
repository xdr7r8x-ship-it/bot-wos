@echo off
chcp 65001 >nul
title Dream Memory - Auto Installer
color 0A
echo.
echo  ╔═══════════════════════════════════════════════════╗
echo  ║      Dream Memory - التثبيت التلقائي          ║
echo  ╚═══════════════════════════════════════════════════╝
echo.

:: ============================================
:: 1. Check Python
:: ============================================
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [✗] Python غير موجود!
    echo.
    echo يجب تثبيت Python أولاً:
    echo 1. اذهب إلى: https://www.python.org/downloads/
    echo 2. حمل أحدث إصدار
    echo 3. فعّل "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo [✓] Python موجود

:: ============================================
:: 2. Install Packages
:: ============================================
echo.
echo [⏳] تثبيت المكتبات...
pip install mss pillow PyQt6 pywin32 requests -q
if %errorlevel% neq 0 (
    echo [✗] فشل تثبيت المكتبات!
    pause
    exit /b 1
)
echo [✓] تم تثبيت المكتبات

:: ============================================
:: 3. Check/Install Ollama
:: ============================================
echo.
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo [⏳] Ollama غير موجود، جاري التحميل...
    echo هذا يستغرق 2-5 دقائق...
    start https://ollama.com/download
    echo.
    echo [i] بعد تحميل Ollama:
    echo     1. تثبيت Ollama
    echo     2. أعد تشغيل هذا السكربت
    echo.
    set /p choice=هل تريد تشغيل بدون Ollama باستخدام Gemini API? (Y/N):
    if /i "%choice%"=="N" goto :end
)

:: Start Ollama if not running
curl -s http://localhost:11434 >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [⏳] بدء Ollama...
    start "" cmd /c "ollama serve"
    timeout /t 5 /nobreak >nul
)

:: Pull model if needed
ollama list | findstr "qwen2.5vl" >nul
if %errorlevel% neq 0 (
    echo.
    echo [⏳] تحميل نموذج الرؤية (مرة واحدة فقط)...
    echo قد يستغرق 5-10 دقائق حسب سرعتك
    ollama pull qwen2.5vl:3b
)

:: ============================================
:: 4. Run Application
:: ============================================
:start_app
cls
echo.
echo  ╔═══════════════════════════════════════════════════╗
echo  ║         Dream Memory - البدء                    ║
echo  ╚═══════════════════════════════════════════════════╝
echo.
echo الأزرار:
echo   F8  - إظهار/إخفاء Overlay
echo   F9  - تشغيل/إيقاف المراقبة
echo   F10 - تحليل يدوي
echo   ESC - خروج
echo.
echo [⏳] جاري بدء التطبيق...
python main.py

:end
pause
