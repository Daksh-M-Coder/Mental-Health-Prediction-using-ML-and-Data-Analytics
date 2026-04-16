@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: ENV_SETUP\setup_windows.bat
:: Mental Health Risk Prediction System - Windows Setup Script
:: Live logging: all output visible AND saved to log file
:: ============================================================

set LOG_FILE=setup_log_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set LOG_FILE=%LOG_FILE: =0%
set VENV_DIR=venv
set REQUIREMENTS=requirements.txt

call :log "============================================================"
call :log "  Mental Health Risk Prediction System - Windows Setup"
call :log "  Started: %date% %time%"
call :log "============================================================"
echo.

:: ── STEP 1: Check Python ────────────────────────────────────
call :header "STEP 1/5 - Checking Python installation"
python --version >nul 2>&1
if errorlevel 1 (
    call :error "Python not found! Please install Python 3.9+ from https://python.org"
    call :error "Make sure to check 'Add Python to PATH' during installation."
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do (
    call :success "Found: %%v"
)

:: ── STEP 2: Create Virtual Environment ──────────────────────
call :header "STEP 2/5 - Creating virtual environment"
if exist "%VENV_DIR%" (
    call :warn "Virtual environment already exists at '%VENV_DIR%\' — skipping creation."
    call :warn "Delete '%VENV_DIR%\' folder manually if you want a fresh install."
) else (
    call :log "Running: python -m venv %VENV_DIR%"
    python -m venv %VENV_DIR% 2>&1 | call :pipe
    if errorlevel 1 (
        call :error "Failed to create virtual environment."
        pause
        exit /b 1
    )
    call :success "Virtual environment created at '%VENV_DIR%\'"
)

:: ── STEP 3: Activate ────────────────────────────────────────
call :header "STEP 3/5 - Activating virtual environment"
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    call :error "Failed to activate virtual environment."
    pause
    exit /b 1
)
call :success "Virtual environment activated."

:: ── STEP 4: Upgrade pip ─────────────────────────────────────
call :header "STEP 4/5 - Upgrading pip (all output shown live)"
call :log "Running: python -m pip install --upgrade pip"
python -m pip install --upgrade pip 2>&1
if errorlevel 1 (
    call :warn "pip upgrade had issues — continuing anyway."
) else (
    call :success "pip upgraded successfully."
)

:: ── STEP 5: Install Requirements ────────────────────────────
call :header "STEP 5/5 - Installing requirements (all output shown live)"
if exist "%REQUIREMENTS%" (
    call :log "Found %REQUIREMENTS% — installing all packages..."
    call :log "Running: pip install -r %REQUIREMENTS%"
    echo.
    pip install -r %REQUIREMENTS% 2>&1
    if errorlevel 1 (
        call :error "Some packages failed to install. Check output above."
    ) else (
        call :success "All packages installed successfully."
    )
) else (
    call :warn "%REQUIREMENTS% not found. Skipping package installation."
    call :warn "Add a requirements.txt to the project root and re-run this script."
)

:: ── DONE ────────────────────────────────────────────────────
echo.
call :log "============================================================"
call :log "  Setup Complete — %date% %time%"
call :log "  Log saved to: %LOG_FILE%"
call :log "============================================================"
echo.
echo To activate venv manually later, run:
echo   %VENV_DIR%\Scripts\activate.bat
echo.
echo To start the app:
echo   python mental_health_ml_system.py
echo.
pause
endlocal
exit /b 0

:: ── HELPER FUNCTIONS ────────────────────────────────────────
:log
    echo %~1
    echo %~1 >> "%LOG_FILE%"
    exit /b 0

:header
    echo.
    echo [----] %~1
    echo [----] %~1 >> "%LOG_FILE%"
    echo.
    exit /b 0

:success
    echo [ OK ] %~1
    echo [ OK ] %~1 >> "%LOG_FILE%"
    exit /b 0

:warn
    echo [WARN] %~1
    echo [WARN] %~1 >> "%LOG_FILE%"
    exit /b 0

:error
    echo [FAIL] %~1
    echo [FAIL] %~1 >> "%LOG_FILE%"
    exit /b 0

:pipe
    setlocal
    set "line="
    set /p line=
    echo        %line%
    echo        %line% >> "%LOG_FILE%"
    endlocal
    exit /b 0
