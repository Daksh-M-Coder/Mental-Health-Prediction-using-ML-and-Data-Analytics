@echo off
setlocal

:: Open in KEEP mode — window stays open even on error
:: Run by double-clicking start.bat

title MindBridge AI - Startup

echo.
echo ============================================================
echo   MINDBRIDGE AI  -  STARTUP
echo ============================================================
echo.
echo   ROOT : %~dp0
echo.
pause

:: ============================================================
echo ============================================================
echo  STEP 1  Checking Python
echo ============================================================
python --version
if errorlevel 1 (
    echo.
    echo [FAIL] Python not found in PATH.
    echo        Install Python 3.10+ from https://python.org
    echo        Tick the "Add to PATH" checkbox during install.
    pause
    exit /b 1
)
echo [OK] Python found.
echo.
pause

:: ============================================================
echo ============================================================
echo  STEP 2  Checking Node.js
echo ============================================================
node --version
if errorlevel 1 (
    echo [FAIL] Node.js not found. Install from https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node found.
echo.

echo Checking npm...
call npm --version
if errorlevel 1 (
    echo [FAIL] npm not found.
    pause
    exit /b 1
)
echo [OK] npm found.
echo.
pause

:: ============================================================
echo ============================================================
echo  STEP 3  Python Virtual Environment
echo ============================================================
echo Checking: %~dp0backend\venv\Scripts\python.exe
if exist "%~dp0backend\venv\Scripts\python.exe" (
    echo [OK] Venv already exists.
) else (
    echo [INFO] Creating venv - this takes ~30 seconds...
    python -m venv "%~dp0backend\venv"
    if errorlevel 1 (
        echo [FAIL] Could not create venv.
        pause
        exit /b 1
    )
    echo [OK] Venv created.
)
echo.
pause

:: ============================================================
echo ============================================================
echo  STEP 4  Installing Python dependencies
echo ============================================================
echo.
echo [INFO] Upgrading pip...
"%~dp0backend\venv\Scripts\pip.exe" install --upgrade pip
echo.
echo [INFO] Installing from requirements.txt...
"%~dp0backend\venv\Scripts\pip.exe" install -r "%~dp0backend\requirements.txt"
if errorlevel 1 (
    echo.
    echo [FAIL] pip install failed. See errors above.
    pause
    exit /b 1
)
echo.
echo [OK] Python deps installed.
echo.
pause

:: ============================================================
echo ============================================================
echo  STEP 5  Node.js dependencies
echo ============================================================
if exist "%~dp0node_modules" (
    echo [OK] node_modules exists - skipping npm install.
) else (
    echo [INFO] Running npm install - may take 1-2 minutes...
    echo.
    pushd "%~dp0"
    call npm install
    popd
    if errorlevel 1 (
        echo [FAIL] npm install failed.
        pause
        exit /b 1
    )
    echo [OK] npm install done.
)
echo.
pause

:: ============================================================
echo ============================================================
echo  STEP 6  Ollama check
echo ============================================================
curl -s --max-time 3 http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARN] Ollama not detected on localhost:11434
    echo        AI Interview needs ollama running.
    echo        Start with:   ollama serve
    echo        Pull model:   ollama pull deepseek-r1:7b
    echo        Manual Form works fine without Ollama.
) else (
    echo [OK] Ollama running.
)
echo.
pause

:: ============================================================
echo ============================================================
echo  STEP 7  Starting Python backend in new window
echo ============================================================

:: Write temp launcher to avoid nested-quote path issues
echo @echo off                                              > "%TEMP%\mb_start.bat"
echo title MindBridge Backend port 5002                   >> "%TEMP%\mb_start.bat"
echo echo.                                                 >> "%TEMP%\mb_start.bat"
echo echo  MindBridge Backend starting...                  >> "%TEMP%\mb_start.bat"
echo echo  URL: http://localhost:5002                      >> "%TEMP%\mb_start.bat"
echo echo  API: http://localhost:5002/docs                 >> "%TEMP%\mb_start.bat"
echo echo.                                                 >> "%TEMP%\mb_start.bat"
echo cd /d "%~dp0backend"                                  >> "%TEMP%\mb_start.bat"
echo call venv\Scripts\activate.bat                        >> "%TEMP%\mb_start.bat"
echo echo [Venv activated]                                 >> "%TEMP%\mb_start.bat"
echo python -u main.py                                     >> "%TEMP%\mb_start.bat"
echo echo.                                                 >> "%TEMP%\mb_start.bat"
echo echo Backend stopped.                                 >> "%TEMP%\mb_start.bat"
echo pause                                                 >> "%TEMP%\mb_start.bat"

start "MindBridge Backend" cmd /k "%TEMP%\mb_start.bat"
echo [OK] Backend window opened.
echo [INFO] Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo [INFO] Health check:
curl -s --max-time 5 http://localhost:5002/health
echo.
echo.
pause

:: ============================================================
echo ============================================================
echo  STEP 8  Starting Next.js frontend (this window)
echo ============================================================
echo.
echo ============================================================
echo.
echo   OPEN IN BROWSER:
echo     http://localhost:3000
echo.
echo   Backend: http://localhost:5002/docs
echo.
echo   Press Ctrl+C to stop. Close backend window separately.
echo ============================================================
echo.

pushd "%~dp0"
call npm run dev
popd

echo.
echo [Frontend stopped]
pause
