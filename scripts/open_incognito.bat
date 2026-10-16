@echo off
title ZhiYaoTong - Incognito Open

set "EDGE=C:/Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE%" set "EDGE=C:/Program Files\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE%" set "EDGE=C:/Program Files\Google\Chrome\Application\chrome.exe"

echo Opening in incognito window (no cache, no extensions) ...
start "" "%EDGE%" --inprivate "http://localhost:8000"

echo.
echo If nothing opened, start the app first:
echo   double-click "ZhiYaoTong-Start2.bat"
echo.
timeout /t 3 /nobreak >nul
