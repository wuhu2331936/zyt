@echo off
REM 智药通 - 申请并填入 API Key 一键启动器
chcp 65001 >nul
cd /d "%~dp0\.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0\setup_api_keys.ps1"
pause
