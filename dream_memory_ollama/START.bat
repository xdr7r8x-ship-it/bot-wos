@echo off
cd /d "%~dp0"

echo.
echo ================================================
echo  Dream Memory - LIVE AUTO MODE
echo ================================================
echo.

echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Cleaning old files...
del /q "__pycache__" 2>nul
for /d %%i in ("__pycache__") do rmdir /s /q "%%i"

echo.
echo Starting application...
echo.
echo Auto analysis enabled - no F10 needed!
echo.

python main.py

pause
