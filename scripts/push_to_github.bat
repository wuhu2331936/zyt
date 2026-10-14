@echo off
REM 智药通 - 推送到 GitHub/Gitee 一键启动器
chcp 65001 >nul
cd /d "%~dp0\.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0\push_to_github.ps1"
pause
