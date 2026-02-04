@echo off
cls
echo ========================================
echo 🧠 Mental Health Prediction System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if requirements are installed
echo Checking dependencies...
pip show gradio >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo ✅ All dependencies installed
echo.

REM Launch the application
echo Starting Mental Health Prediction System...
echo.
echo 🌐 Access the application at: http://127.0.0.1:7860
echo 🔧 Check logs in: mental_health_system.log
echo ❌ Press Ctrl+C to stop the server
echo.

python gradio_interface_final.py

pause