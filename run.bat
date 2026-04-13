@echo off
title Network Monitor
echo ============================================
echo  NETWORK MONITOR - STARTING
echo ============================================
echo.

REM --- CHECK VENV ---
if not exist venv\Scripts\activate.bat (
    echo [ERROR] Virtual environment not found.
    echo         Run install.bat first.
    echo.
    pause
    exit /b 1
)

REM --- ACTIVATE VENV ---
echo [..] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated.

REM --- CHECK OLLAMA ---
echo [..] Checking Ollama...
curl -s http://localhost:11434 >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Ollama is not running.
    echo        AI analysis will be unavailable until Ollama is started.
    echo.
) else (
    echo [OK] Ollama is running.
)

REM --- START SERVER ---
echo [..] Starting Network Monitor...
echo.
echo  Open http://localhost:8000/static/index.html in your browser
echo.
echo  Press CTRL+C to stop the server
echo.
echo ============================================
echo.
uvicorn api.main:app --reload