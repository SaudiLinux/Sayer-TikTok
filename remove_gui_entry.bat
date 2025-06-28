@echo off
echo Removing TikTok-Sayer GUI entry point...

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please right-click and select "Run as administrator".
    pause
    exit /b 1
)

REM Delete the GUI entry point script
if exist "%LOCALAPPDATA%\Programs\Python\Python311\Scripts\tiktok-sayer-gui-script.pyw" (
    del /f "%LOCALAPPDATA%\Programs\Python\Python311\Scripts\tiktok-sayer-gui-script.pyw"
    echo GUI entry point script removed successfully.
) else (
    echo GUI entry point script not found.
)

REM Delete the GUI entry point executable if it exists
if exist "%LOCALAPPDATA%\Programs\Python\Python311\Scripts\tiktok-sayer-gui.exe" (
    del /f "%LOCALAPPDATA%\Programs\Python\Python311\Scripts\tiktok-sayer-gui.exe"
    echo GUI entry point executable removed successfully.
) else (
    echo GUI entry point executable not found.
)

echo Done.
pause