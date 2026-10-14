# 智药通 - 一键推送到 GitHub / Gitee
# 路径：scripts\push_to_github.ps1
# 用法：在 zhijiayaotong/ 根目录右键 → 用 PowerShell 运行

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\zhijiayaotong")

Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  智药通 - 推送到 GitHub / Gitee" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 前置检查
$branch = git rev-parse --abbrev-ref HEAD
$commitCount = (git log --oneline | Measure-Object).Count
$tag = git tag --points-at HEAD
Write-Host "[OK] 当前分支: $branch  提交数: $commitCount  当前 tag: $($tag -join ', ')" -ForegroundColor Green
Write-Host ""

# --- 路径 1: 优先用 GitHub CLI（gh）---
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    Write-Host "[检测] 发现 GitHub CLI (gh): $($gh.Version)" -ForegroundColor Yellow
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "未登录。先执行：gh auth login  （按提示走完）" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] gh 已登录" -ForegroundColor Green

    $repoName = Read-Host "仓库名 (默认: zhiyaotong)"
    if ([string]::IsNullOrWhiteSpace($repoName)) { $repoName = "zhiyaotong" }
    $visibility = Read-Host "可见性 [public/private] (默认: public)"
    if ([string]::IsNullOrWhiteSpace($visibility)) { $visibility = "public" }
    $desc = "智药通 - AI 老年人用药安全助手 (传智杯 AI 创新应用挑战赛)"

    # 已存在则只 push；不存在则 create + push
    $remote = git remote get-url origin 2>$null
    if ($remote) {
        git push -u origin $branch
        git push origin $tag
    } else {
        gh repo create $repoName --$visibility --source=. --remote=origin --description $desc
    }
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ 推送完成" -ForegroundColor Green
    Write-Host "  仓库地址: $remote" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    exit 0
}

# --- 路径 2: HTTPS + Personal Access Token（通用）---
Write-Host "[未检测到 gh CLI] 使用 HTTPS + Token 方式" -ForegroundColor Yellow
Write-Host ""
Write-Host "首次使用需要：" -ForegroundColor Cyan
Write-Host "  1. 在 GitHub/Gitee 网页上创建一个**空仓库**（不要勾选 README/.gitignore）"
Write-Host "  2. 生成 Personal Access Token（PAT）："
Write-Host "     - GitHub: https://github.com/settings/tokens  (勾选 repo 权限)"
Write-Host "     - Gitee:  https://gitee.com/profile/personal_access_tokens"
Write-Host ""

$choice = Read-Host "选择平台 [1=GitHub / 2=Gitee] (默认: 1)"
if ($choice -eq "2") { $defaultHost = "gitee.com" } else { $defaultHost = "github.com" }

$user = Read-Host "你的用户名"
$repoName = Read-Host "仓库名 (默认: zhiyaotong)"
if ([string]::IsNullOrWhiteSpace($repoName)) { $repoName = "zhiyaotong" }

$url = "https://$defaultHost/$user/$repoName.git"
$confirmed = Read-Host "确认推送到 $url ? [y/n]"
if ($confirmed -ne "y") { Write-Host "已取消"; exit 0 }

# 配 remote + push
git remote remove origin 2>$null
git remote add origin $url
git remote set-url origin $url  # 显式写一次，防止 Bash 路径转换

# 第一次 push 会要求输入 username + token（PAT 当密码粘贴）
Write-Host ""
Write-Host "即将执行：git push -u origin $branch" -ForegroundColor Cyan
Write-Host "  username: $user" -ForegroundColor Gray
Write-Host "  password: **粘贴你的 PAT (GitHub Token 或 Gitee 私人令牌)**" -ForegroundColor Gray
Write-Host "  （密码输入时光标不会动，粘贴后回车即可）" -ForegroundColor DarkGray
Write-Host ""
git push -u origin $branch
if ($LASTEXITCODE -eq 0 -and $tag) {
    git push origin $tag
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 推送完成" -ForegroundColor Green
Write-Host "  仓库地址: https://$defaultHost/$user/$repoName" -ForegroundColor Green
Write-Host "  下一步：去网页确认 Public 状态 + 在 Settings → Public 开启" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
