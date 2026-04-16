@echo off
:: Backend launcher — called by start.bat
:: Do NOT run this directly unless backend\venv exists

title MindBridge Backend - http://localhost:5002

echo.
echo ============================================================
echo   MINDBRIDGE BACKEND SERVER
echo   http://localhost:5002
echo   http://localhost:5002/docs  (interactive API docs)
echo ============================================================
echo.

cd /d "%~dp0"

echo [INFO] Activating venv...
call venv\Scripts\activate.bat

echo [INFO] Starting FastAPI server...
echo.
python -u main.py

echo.
echo [BACKEND STOPPED]
pause
