@echo off
echo Starting TikTok-Sayer...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.6 or higher.
    echo Visit https://www.python.org/downloads/ to download Python.
    pause
    exit /b 1
)

:: Check if requirements are installed
echo Checking requirements...
pip install -r requirements.txt

:: Run the application
echo Launching TikTok-Sayer...
python tiktok_sayer.py

pause