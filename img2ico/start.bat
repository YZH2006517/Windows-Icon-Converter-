@echo off
echo ==========================================
echo    Image to Icon Converter
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found. Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install Pillow windnd -q

echo [2/3] Starting application...
echo [3/3] Loading...
echo.

python img2ico_gui.py

pause
