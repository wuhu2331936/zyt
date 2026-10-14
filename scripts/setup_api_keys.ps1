# ZhiYaoTong - API Key setup helper
# Path: scripts\setup_api_keys.ps1
# Usage: double-click scripts\setup_api_keys.bat (recommended)
#         OR right-click this .ps1 -> Run with PowerShell
#
# IMPORTANT: Do NOT add Chinese comments above a `$var = '...'` line.
# Windows PowerShell 5.1 has a parser bug where a UTF-8 comment with
# certain symbol sequences silently swallows the next variable assignment.
# All inline notes below are English-only.

$ErrorActionPreference = "Stop"

# Auto-detect common Git install paths (script does .env safety check via git)
$gitCandidates = @(
    'C:\Program Files\Git\bin',
    'C:\Program Files\Git\cmd',
    'C:\Program Files (x86)\Git\bin',
    "$env:LOCALAPPDATA\Programs\Git\bin",
    'C:\Users\wuhu\.workbuddy\binaries\PortableGit\versions\1.2.0\mingw64\bin'
)
foreach ($p in $gitCandidates) {
    if ((Test-Path (Join-Path $p 'git.exe')) -and ($env:Path -notlike "*$p*")) {
        $env:Path = "$p;$env:Path"
    }
}

$backendDir = Resolve-Path (Join-Path $PSScriptRoot "..\backend")
$envFile = Join-Path $backendDir ".env"
$example = Join-Path $backendDir ".env.example"

Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ZhiYaoTong - API Key Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $example)) {
    Write-Host "[FATAL] backend\.env.example not found" -ForegroundColor Red
    Write-Host "  Make sure you run this from zhijiayaotong\ root" -ForegroundColor Red
    pause
    exit 1
}

# 1. Copy .env.example -> .env if missing
if (-not (Test-Path $envFile)) {
    Copy-Item $example $envFile
    Write-Host "[OK] Created backend\.env (from .env.example)" -ForegroundColor Green
} else {
    Write-Host "[skip] backend\.env already exists" -ForegroundColor Yellow
    $overwrite = Read-Host "  Overwrite it? [y/n]"
    if ($overwrite -eq "y") {
        Copy-Item $example $envFile -Force
        Write-Host "[OK] Overwrote backend\.env" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Get 2 API Keys (free tier, takes ~5 min):" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Alibaba Bailian (Qwen-VL, for image recognition)" -ForegroundColor White
Write-Host "     https://bailian.console.aliyun.com/" -ForegroundColor Cyan
Write-Host "     Steps: login -> enable model service -> create API-Key -> copy" -ForegroundColor Gray
Write-Host "     Format: sk-xxxxxxxxxxxxxxxxxxxxxxxx" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. DeepSeek (chat + JSON analysis)" -ForegroundColor White
Write-Host "     https://platform.deepseek.com/" -ForegroundColor Cyan
Write-Host "     Steps: login -> API Keys -> create -> copy" -ForegroundColor Gray
Write-Host "     Format: sk-xxxxxxxxxxxxxxxxxxxxxxxx" -ForegroundColor Gray
Write-Host ""
Write-Host "About to open Notepad to edit .env - replace both sk-xxx placeholders" -ForegroundColor Cyan
Write-Host "Save and close Notepad to continue..." -ForegroundColor Cyan
$null = Read-Host "Press Enter to open Notepad"

Start-Process notepad.exe -ArgumentList "`"$envFile`"" -Wait

# 2. Validate
Write-Host ""
Write-Host "[validate] Checking the file..." -ForegroundColor Cyan
try {
    $content = Get-Content $envFile -Raw -Encoding UTF8
} catch {
    Write-Host "[FATAL] Cannot read $envFile : $($_.Exception.Message)" -ForegroundColor Red
    pause
    exit 1
}
$issues = @()

if ($content -match 'DASHSCOPE_API_KEY=sk-xxxxx') {
    $issues += "DASHSCOPE_API_KEY still has placeholder sk-xxxxx"
}
if ($content -match 'DASHSCOPE_API_KEY=""') {
    $issues += "DASHSCOPE_API_KEY is empty string"
}
if ($content -match 'DEEPSEEK_API_KEY=sk-xxxxx') {
    $issues += "DEEPSEEK_API_KEY still has placeholder sk-xxxxx"
}
if ($content -match 'DEEPSEEK_API_KEY=""') {
    $issues += "DEEPSEEK_API_KEY is empty string"
}

if ($issues.Count -gt 0) {
    Write-Host ""
    Write-Host "Issues found:" -ForegroundColor Red
    $issues | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "Re-run this script to edit again" -ForegroundColor Yellow
    pause
    exit 1
} else {
    Write-Host "[OK] API Keys are filled in" -ForegroundColor Green
}

# 3. Remind about FRONTEND_URL
if ($content -match 'FRONTEND_URL=.*localhost') {
    Write-Host ""
    Write-Host "[note] FRONTEND_URL is still localhost" -ForegroundColor Yellow
    Write-Host "  Fine for local dev. After deploying to Vercel, change to https://<your-domain>.vercel.app" -ForegroundColor Gray
}

# 4. Safety: confirm .env is NOT tracked by git
Write-Host ""
Write-Host "[safety] Confirming .env is NOT tracked by git..." -ForegroundColor Cyan
$projectRoot = (Get-Item $backendDir).Parent.FullName
Set-Location $projectRoot
try {
    $tracked = git ls-files backend/.env 2> $null
} catch {
    $tracked = $null
}
if ($tracked) {
    Write-Host "  [WARNING] .env IS tracked by git! Run immediately:" -ForegroundColor Red
    Write-Host "     git rm --cached backend/.env" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] .env is NOT tracked, safe" -ForegroundColor Green
}

# 5. Next steps
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup complete" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Local test (do NOT push .env):" -ForegroundColor Cyan
Write-Host "  cd zhijiayaotong\backend" -ForegroundColor White
Write-Host "  venv\Scripts\activate" -ForegroundColor White
Write-Host "  python scripts\test_models.py tts   # test TTS (no key needed)" -ForegroundColor Gray
Write-Host "  python scripts\test_models.py llm   # test DeepSeek chat" -ForegroundColor Gray
Write-Host "  python scripts\test_models.py vl    # test Qwen-VL image recognition" -ForegroundColor Gray
Write-Host "  uvicorn app.main:app --reload       # start backend" -ForegroundColor Gray
Write-Host ""
pause