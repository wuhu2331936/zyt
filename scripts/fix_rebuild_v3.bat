@echo off
title ZhiYaoTong - Force Fix v3

set "NODED=C:/Users/wuhu/.workbuddy/binaries/node/versions/22.22.2"

if exist "%NODED%\npm.cmd" set "PATH=%NODED%;%PATH%"
if exist "C:/Program Files/nodejs" set "PATH=C:/Program Files\nodejs;%PATH%"

cd /d "C:/Users/wuhu/WorkBuddy/2026-10-14-20-41-43/zhijiayaotong/frontend"

echo [1/4] Force-deleting broken package folders ...
rd /s /q "node_modules\@rollup\pluginutils"
rd /s /q "node_modules\@rollup\plugin-node-resolve"
rd /s /q "node_modules\.vite"

echo [2/4] Explicitly installing the two broken packages ...
call npm install @rollup/pluginutils@5.0.5 @rollup/plugin-node-resolve@15.3.0 --no-save --no-audit --no-fund

echo [3/4] Verifying ...
set BROKEN=0
if not exist "node_modules\@rollup\pluginutils\dist\cjs\index.js" set BROKEN=1
if not exist "node_modules\@rollup\plugin-node-resolve\dist\cjs\index.js" set BROKEN=1
if not exist "node_modules\@rollup\plugin-babel\dist\index.js" set BROKEN=1
if "%BROKEN%"=="1" (
  echo   [FAIL] some package still broken - do NOT close, screenshot this window
) else (
  echo   [OK] all packages fixed
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
