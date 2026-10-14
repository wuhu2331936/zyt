# ZhiYaoTong - One-click push to GitHub / Gitee
# Path: scripts\push_to_github.ps1
# Usage: double-click scripts\push_to_github.bat (recommended)
#         OR right-click this .ps1 -> Run with PowerShell
#
# IMPORTANT: Do NOT add Chinese comments above a `$var = '...'` line.
# Windows PowerShell 5.1 has a parser bug where a UTF-8 comment with
# certain symbol sequences silently swallows the next variable assignment.
# All inline notes below are English-only.

$ErrorActionPreference = "Stop"

# Auto-detect common Git install paths (PowerShell does NOT inherit Git Bash PATH)
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

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $projectRoot

Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ZhiYaoTong - Push to GitHub / Gitee" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    $branch = git rev-parse --abbrev-ref HEAD
    $commitCount = (git log --oneline | Measure-Object).Count
    $tag = git tag --points-at HEAD
    Write-Host "[OK] branch: $branch  commits: $commitCount  tag: $($tag -join ', ')" -ForegroundColor Green
} catch {
    Write-Host "[FATAL] git not available or not in a git repo" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please confirm:" -ForegroundColor Yellow
    Write-Host "  1. Git for Windows is installed"
    Write-Host "  2. You run this from zhijiayaotong\ root (with .git folder)"
    pause
    exit 1
}
Write-Host ""

# Path 1: GitHub CLI (gh)
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    Write-Host "[detect] GitHub CLI (gh): $($gh.Version)" -ForegroundColor Yellow
    $authOutput = gh auth status 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Not logged in. Run first: gh auth login" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "[OK] gh logged in" -ForegroundColor Green

    $repoName = Read-Host "Repo name (default: zhiyaotong)"
    if ([string]::IsNullOrWhiteSpace($repoName)) { $repoName = "zhiyaotong" }
    $visibility = Read-Host "Visibility [public/private] (default: public)"
    if ([string]::IsNullOrWhiteSpace($visibility)) { $visibility = "public" }
    $desc = "ZhiYaoTong - AI elderly medication safety assistant"

    $remote = git remote get-url origin 2> $null
    if ($remote) {
        git push -u origin $branch
        if ($tag) { git push origin $tag }
    } else {
        gh repo create $repoName --$visibility --source=. --remote=origin --description $desc
    }
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Push complete" -ForegroundColor Green
    Write-Host "  Repo URL: $remote" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    pause
    exit 0
}

# Path 2: HTTPS + Personal Access Token
Write-Host "[no gh CLI] Falling back to HTTPS + Token" -ForegroundColor Yellow
Write-Host ""
Write-Host "Prerequisites:" -ForegroundColor Cyan
Write-Host "  1. Create an empty repo on the web (do NOT tick README/.gitignore)"
Write-Host "  2. Generate a Personal Access Token (PAT):"
Write-Host "     - GitHub: https://github.com/settings/tokens  (scope: repo)"
Write-Host "     - Gitee:  https://gitee.com/profile/personal_access_tokens"
Write-Host ""

$choice = Read-Host "Platform [1=GitHub / 2=Gitee] (default: 1)"
if ($choice -eq "2") { $defaultHost = "gitee.com" } else { $defaultHost = "github.com" }

$user = Read-Host "Your username"
$repoName = Read-Host "Repo name (default: zhiyaotong)"
if ([string]::IsNullOrWhiteSpace($repoName)) { $repoName = "zhiyaotong" }

$url = "https://$defaultHost/$user/$repoName.git"
$confirmed = Read-Host "Push to $url ? [y/n]"
if ($confirmed -ne "y") { Write-Host "Cancelled"; pause; exit 0 }

git remote remove origin 2> $null
git remote add origin $url

Write-Host ""
Write-Host "Running: git push -u origin $branch" -ForegroundColor Cyan
Write-Host "  username: $user" -ForegroundColor Gray
Write-Host "  password: paste your PAT (GitHub Token / Gitee private token)" -ForegroundColor Gray
Write-Host "  (cursor won't move while typing password, just paste + Enter)" -ForegroundColor DarkGray
Write-Host ""
git push -u origin $branch
if ($LASTEXITCODE -eq 0 -and $tag) {
    git push origin $tag
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Push complete" -ForegroundColor Green
Write-Host "  Repo URL: https://$defaultHost/$user/$repoName" -ForegroundColor Green
Write-Host "  Next: confirm Public status on the web" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
pause