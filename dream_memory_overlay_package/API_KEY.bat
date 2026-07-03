@echo off
title Set API Key
color 0A
echo.
echo  ================================================
echo     Set Your OpenAI API Key
echo  ================================================
echo.
echo Enter your OpenAI API Key:
echo.
set /p API_KEY="API Key: "

if "%API_KEY%"=="" (
    echo.
    echo [ERROR] You must enter an API key!
    pause
    exit /b 1
)

setx OPENAI_API_KEY "%API_KEY%"
echo.
echo ================================================
echo  [OK] API Key saved successfully!
echo ================================================
echo.
echo Now run START.bat to launch the app!
echo.
pause
