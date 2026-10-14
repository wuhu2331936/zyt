@echo off
REM ZhiYaoTong - API Key setup launcher
chcp 65001 >nul

REM Prepend common Git install paths (script does .env safety check via git)
if exist "C:\Program Files\Git\bin\git.exe" set "PATH=C:\Program Files\Git\bin;%PATH%"
if exist "C:\Program Files\Git\cmd\git.exe" set "PATH=C:\Program Files\Git\cmd;%PATH%"
if exist "C:\Program Files (x86)\Git\bin\git.exe" set "PATH=C:\Program Files (x86)\Git\bin;%PATH%"
if exist "C:\Users\wuhu\.workbuddy\binaries\PortableGit\versions\1.2.0\mingw64\bin\git.exe" set "PATH=C:\Users\wuhu\.workbuddy\binaries\PortableGit\versions\1.2.0\mingw64\bin;%PATH%"

cd /d "%~dp0\.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0\setup_api_keys.ps1"
if errorlevel 1 pause & exit /b 1
pause