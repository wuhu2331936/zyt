@echo off
title ZhiYaoTong - One Server

set "ROOT=C:/Users/wuhu/WorkBuddy/2026-10-14-20-41-43/zhijiayaotong"

echo ============================================
echo   ZhiYaoTong - AI Medicine Safety Assistant
echo ============================================
echo.
echo Starting server (single port 8000) ...
echo It serves BOTH the web page and the API.
echo.

start "ZhiYaoTong-Server" /D "%ROOT%\backend" "%ComSpec%" /k "venv\Scripts\uvicorn.exe" app.main:app --host 0.0.0.0 --port 8000

echo Waiting 8 seconds, browser will open ...
timeout /t 8 /nobreak >nul
start "" http://localhost:8000

echo.
echo --------------------------------------------
echo  Open in PC browser : http://localhost:8000
echo  Open in phone      : http://192.168.0.2:8000
echo  API docs           : http://localhost:8000/docs
echo.
echo  Close app: close the black window
echo --------------------------------------------
echo.
pause
