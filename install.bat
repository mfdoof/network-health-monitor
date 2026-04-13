@echo off
title Network Monitor - Installer
echo ============================================
echo  NETWORK MONITOR - INSTALL
echo ============================================
echo.

REM --- CHECK PYTHON ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download it from https://python.org
    echo.
    pause
    exit /b 1
)
echo [OK] Python found.

REM --- SET EXECUTION POLICY ---
echo [..] Setting PowerShell execution policy...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
if %errorlevel% neq 0 (
    echo [WARN] Could not set execution policy. Venv activation may fail.
) else (
    echo [OK] Execution policy set.
)

REM --- CREATE VENV ---
echo [..] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment created.

REM --- ACTIVATE VENV ---
echo [..] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated.

REM --- INSTALL DEPENDENCIES ---
echo [..] Installing dependencies...
pip install -r api\requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies installed.

REM --- CHECK OLLAMA ---
echo [..] Checking Ollama...
curl -s http://localhost:11434 >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Ollama is not running.
    echo        Start Ollama manually before running the app.
    echo        Then run: ollama pull llama3.2
) else (
    echo [OK] Ollama is running.
)

echo.
echo ============================================
echo  INSTALL COMPLETE
echo  Run the app with: run.bat
echo ============================================
echo.
pause