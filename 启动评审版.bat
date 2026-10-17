@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo    ZhiYaoTong - One-click startup for reviewers
echo    No API Key required (auto demo mode)
echo ============================================================
echo.

cd /d "%~dp0"
echo WorkDir: %CD%
echo.

REM ---------- locate python ----------
set "PY="
where python >nul 2>&1
if %errorlevel%==0 set "PY=python"
if defined PY goto :foundpy
where py >nul 2>&1
if %errorlevel%==0 set "PY=py"
if defined PY goto :foundpy
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if defined PY goto :foundpy
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if defined PY goto :foundpy
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if defined PY goto :foundpy
if exist "C:/Python312/python.exe" set "PY=C:/Python312/python.exe"
if defined PY goto :foundpy
echo [ERROR] Python 3.10+ not found.
echo Please install from https://www.python.org/downloads/
echo IMPORTANT: check "Add Python to PATH" while installing.
echo.
pause
exit /b 1

:foundpy
echo [OK] Python found:
%PY% --version
echo.

REM ---------- venv ----------
echo [1/3] Preparing virtual environment ...
if not exist "backend\venv\Scripts\python.exe" %PY% -m venv backend\venv
set "VPY=%CD%\backend\venv\Scripts\python.exe"
if not exist "%VPY%" set "VPY=%PY%"
echo Using: %VPY%
echo.

REM ---------- deps ----------
echo [2/3] Installing dependencies (first run: 3-5 minutes, needs internet) ...
"%VPY%" -m pip install --upgrade pip -q
"%VPY%" -m pip install -r backend\requirements-cloud.txt
if %errorlevel% neq 0 echo [WARN] Some packages failed to install. Trying to start anyway ...
echo.

REM ---------- run ----------
echo [3/3] Starting server at http://localhost:8000
echo Browser will open automatically in a few seconds.
echo Keep this window OPEN, closing it stops the server.
echo.
start "ZhiYaoTongBrowser" /min %ComSpec% /c "timeout /t 8 /nobreak >nul & start http://localhost:8000"

cd backend
"%VPY%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000

echo.
echo Server stopped.
pause
