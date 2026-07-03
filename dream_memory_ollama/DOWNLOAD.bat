@echo off
powershell -Command "Invoke-WebRequest -Uri https://github.com/xdr7r8x-ship-it/bot-wos/archive/refs/heads/FINAL.zip -OutFile project.zip"
powershell -Command "Expand-Archive -Path project.zip -DestinationPath . -Force"
cd bot-wos-FINAL\dream_memory_ollama
pip install -r requirements.txt -q
python main.py
cd ..
del project.zip
pause
