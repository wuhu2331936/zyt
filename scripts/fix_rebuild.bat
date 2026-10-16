@echo off
title ZhiYaoTong - Force Fix and Rebuild

set "ROOT=C:/Users/wuhu/WorkBuddy/2026-10-14-20-41-43/zhijiayaotong"
set "NODED=C:/Users/wuhu/.workbuddy/binaries/node/versions/22.22.2"

if exist "%NODED%\npm.cmd" set "PATH=%NODED%;%PATH%"
if exist "C:/Program Files/nodejs" set "PATH=C:/Program Files\nodejs;%PATH%"

cd /d "%ROOT%\frontend"

echo [1/4] Force-deleting broken package folder ...
rd /s /q "node_modules\@rollup\plugin-babel"
rd /s /q "node_modules\.vite"

echo [2/4] Explicitly installing @rollup/plugin-babel ...
call npm install @rollup/plugin-babel@6.1.0 --no-audit --no-fund

echo [3/4] Verifying ...
if exist "node_modules\@rollup\plugin-babel\dist\index.js" (
  echo   [OK] package fixed
) else (
  echo   [FAIL] package still broken - do NOT close, screenshot this window
)

echo [4/4] Building production bundle ...
call npm run build

echo.
if exist "dist\index.html" (
  echo ============================================
  echo  BUILD SUCCESS
  echo  Now double-click "ZhiYaoTong-Start.bat"
  echo  and open http://localhost:4173
  echo ============================================
) else (
  echo ============================================
  echo  BUILD FAILED - screenshot this window
  echo ============================================
)
echo.
pause
