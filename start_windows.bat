@echo off
:: Mental Health Prediction System - Windows Startup Script
:: Automatically installs dependencies and launches the application

title Mental Health Prediction System - Windows Launcher

echo ======================================================
echo 🧠 MENTAL HEALTH RISK PREDICTION SYSTEM
echo ======================================================
echo Starting Windows Setup and Launch Process...
echo.

:: Check if Python is installed
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

:: Check if pip is available
echo 🔍 Checking pip installation...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip not found. Please reinstall Python with pip.
    pause
    exit /b 1
)
echo ✅ pip is available

:: Check if requirements.txt exists
echo 🔍 Checking requirements file...
if not exist "requirements.txt" (
    echo ❌ requirements.txt not found in current directory.
    echo Please ensure you're in the correct project folder.
    pause
    exit /b 1
)
echo ✅ requirements.txt found

:: Check if main application file exists
echo 🔍 Checking main application file...
if not exist "mental_health_ml_system.py" (
    echo ❌ mental_health_ml_system.py not found in current directory.
    echo Please ensure you're in the correct project folder.
    pause
    exit /b 1
)
echo ✅ Main application file found

:: Create virtual environment (optional but recommended)
echo 🔧 Setting up Python environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment.
        echo Continuing without virtual environment...
    ) else (
        echo ✅ Virtual environment created
        call venv\Scripts\activate.bat
        if %errorlevel% neq 0 (
            echo ⚠️  Could not activate virtual environment, continuing...
        ) else (
            echo ✅ Virtual environment activated
        )
    )
) else (
    echo ✅ Virtual environment already exists
    call venv\Scripts\activate.bat >nul 2>&1
)

:: Upgrade pip
echo 🔧 Upgrading pip...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo ⚠️  Failed to upgrade pip, continuing...
) else (
    echo ✅ pip upgraded successfully
)

:: Install required packages
echo 🔧 Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ❌ Failed to install required packages.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo ✅ All dependencies installed successfully

:: Check for Gradio installation specifically
echo 🔍 Verifying Gradio installation...
python -c "import gradio" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Gradio not properly installed, attempting reinstallation...
    pip install gradio --quiet
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Gradio.
        pause
        exit /b 1
    )
)
echo ✅ Gradio verified

:: Check for scikit-learn installation
echo 🔍 Verifying scikit-learn installation...
python -c "import sklearn" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  scikit-learn not properly installed, attempting reinstallation...
    pip install scikit-learn --quiet
    if %errorlevel% neq 0 (
        echo ❌ Failed to install scikit-learn.
        pause
        exit /b 1
    )
)
echo ✅ scikit-learn verified

:: Final system check
echo 🔍 Performing final system check...
python -c "import pandas, numpy, colorama" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Some dependencies may be missing, attempting to install all...
    pip install pandas numpy colorama --quiet
)
echo ✅ System check completed

:: Launch the application
echo ======================================================
echo 🚀 LAUNCHING MENTAL HEALTH PREDICTION SYSTEM
echo ======================================================
echo.
echo The application will be available at: http://127.0.0.1:7860
echo Press Ctrl+C to stop the application
echo.
echo Starting server...
echo.

:: Run the main application
python mental_health_ml_system.py

:: Handle application exit
if %errorlevel% neq 0 (
    echo.
    echo ❌ Application encountered an error.
    echo Error code: %errorlevel%
    echo Please check the console output above for details.
    echo.
    echo Common solutions:
    echo 1. Ensure all dependencies are installed
    echo 2. Check if port 7860 is available
    echo 3. Verify the mental_health_ml_system.py file exists
    echo.
) else (
    echo.
    echo ✅ Application closed successfully.
)

echo.
echo Press any key to exit...
pause >nul