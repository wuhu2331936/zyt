@echo off
REM ZhiYaoTong - One-click push launcher
chcp 65001 >nul

REM Prepend common Git install paths so PowerShell can find git.exe
if exist "C:\Program Files\Git\bin\git.exe" set "PATH=C:\Program Files\Git\bin;%PATH%"
if exist "C:\Program Files\Git\cmd\git.exe" set "PATH=C:\Program Files\Git\cmd;%PATH%"
if exist "C:\Program Files (x86)\Git\bin\git.exe" set "PATH=C:\Program Files (x86)\Git\bin;%PATH%"
if exist "C:\Users\wuhu\.workbuddy\binaries\PortableGit\versions\1.2.0\mingw64\bin\git.exe" set "PATH=C:\Users\wuhu\.workbuddy\binaries\PortableGit\versions\1.2.0\mingw64\bin;%PATH%"

cd /d "%~dp0\.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0\push_to_github.ps1"
if errorlevel 1 pause & exit /b 1
pause