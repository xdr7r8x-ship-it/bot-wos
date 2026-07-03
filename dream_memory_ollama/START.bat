@echo off
echo.
echo ================================================
echo  Dream Memory - Ollama Vision
echo ================================================
echo.

echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Starting application...
echo.

python main.py

pause
