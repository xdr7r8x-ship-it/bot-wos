@echo off
powershell -Command "Invoke-WebRequest -Uri https://github.com/xdr7r8x-ship-it/bot-wos/archive/refs/heads/FINAL.zip -OutFile project.zip"
powershell -Command "Expand-Archive -Path project.zip -DestinationPath . -Force"
cd bot-wos-FINAL\VISUAL_VERSION
pip install opencv-python pillow PyQt6 pywin32 numpy -q
start cmd /k "python main.py"
cd ..
del project.zip
pause