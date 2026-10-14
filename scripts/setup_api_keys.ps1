# 智药通 - API Key 申请 + 填入 .env 一键脚本
# 路径：scripts\setup_api_keys.ps1
# 用法：在 zhijiayaotong/ 根目录右键 → 用 PowerShell 运行

$ErrorActionPreference = "Stop"
$backendDir = Resolve-Path "$PSScriptRoot\..\backend"
$envFile = Join-Path $backendDir ".env"
$example = Join-Path $backendDir ".env.example"

Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  智药通 - API Key 申请与填入" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 复制 .env.example → .env（如不存在）
if (-not (Test-Path $envFile)) {
    Copy-Item $example $envFile
    Write-Host "[OK] 已创建 backend\.env（基于 .env.example）" -ForegroundColor Green
} else {
    Write-Host "[跳过] backend\.env 已存在" -ForegroundColor Yellow
    $overwrite = Read-Host "  要重新生成吗？[y/n]"
    if ($overwrite -eq "y") {
        Copy-Item $example $envFile -Force
        Write-Host "[OK] 已覆盖 backend\.env" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "请按下方链接申请 2 个 API Key（都有免费额度，5 分钟搞定）：" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. 阿里云百炼（通义千问 VL - 识图用）" -ForegroundColor White
Write-Host "     https://bailian.console.aliyun.com/" -ForegroundColor Cyan
Write-Host "     步骤：登录 → 开通「模型服务」 → 创建 API-Key → 复制" -ForegroundColor Gray
Write-Host "     形如：sk-xxxxxxxxxxxxxxxxxxxxxxxx" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. DeepSeek（对话 + JSON 分析用）" -ForegroundColor White
Write-Host "     https://platform.deepseek.com/" -ForegroundColor Cyan
Write-Host "     步骤：登录 → API Keys → 创建 → 复制" -ForegroundColor Gray
Write-Host "     形如：sk-xxxxxxxxxxxxxxxxxxxxxxxx" -ForegroundColor Gray
Write-Host ""
Write-Host "即将打开 Notepad 编辑 .env，把两个 sk-xxx 替换占位符" -ForegroundColor Cyan
Write-Host "保存后回到此窗口..." -ForegroundColor Cyan
$go = Read-Host "准备好了吗 [回车继续]"
notepad $envFile

# 2. 校验
Write-Host ""
Write-Host "[校验] 检查填写情况..." -ForegroundColor Cyan
$content = Get-Content $envFile -Raw -Encoding UTF8
$issues = @()

if ($content -match 'DASHSCOPE_API_KEY=sk-xxxxx') {
    $issues += "DASHSCOPE_API_KEY 未替换（仍是占位符 sk-xxxxx）"
}
if ($content -match 'DASHSCOPE_API_KEY=""') {
    $issues += "DASHSCOPE_API_KEY 是空字符串"
}
if ($content -match 'DEEPSEEK_API_KEY=sk-xxxxx') {
    $issues += "DEEPSEEK_API_KEY 未替换（仍是占位符 sk-xxxxx）"
}
if ($content -match 'DEEPSEEK_API_KEY=""') {
    $issues += "DEEPSEEK_API_KEY 是空字符串"
}

if ($issues.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ 发现问题：" -ForegroundColor Red
    $issues | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "重新运行此脚本即可再次编辑" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "[OK] API Key 已填写" -ForegroundColor Green
}

# 3. 提醒 FRONTEND_URL
if ($content -match 'FRONTEND_URL=.*localhost') {
    Write-Host ""
    Write-Host "[提示] FRONTEND_URL 还是 localhost" -ForegroundColor Yellow
    Write-Host "  本地开发无需改动；部署到 Vercel 后改成 https://<你的域名>.vercel.app" -ForegroundColor Gray
}

# 4. 安全检查
Write-Host ""
Write-Host "[安全] 确认 .env 未被 git 追踪..." -ForegroundColor Cyan
$envDir = (Get-Item $backendDir).Parent.FullName
Set-Location $envDir
$tracked = git ls-files backend/.env 2>$null
if ($tracked) {
    Write-Host "  ❌ 警告：.env 已被 git 追踪！立即执行：" -ForegroundColor Red
    Write-Host "     git rm --cached backend/.env" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] .env 未被追踪，安全" -ForegroundColor Green
}

# 5. 提示下一步
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 配置完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "现在可以本地测试：" -ForegroundColor Cyan
Write-Host "  cd zhijiayaotong\backend" -ForegroundColor White
Write-Host "  venv\Scripts\activate" -ForegroundColor White
Write-Host "  python scripts\test_models.py tts    " -ForegroundColor White -NoNewline
Write-Host "# 测试 TTS（无需 Key）" -ForegroundColor Gray
Write-Host "  python scripts\test_models.py llm    " -ForegroundColor White -NoNewline
Write-Host "# 测试 DeepSeek 对话" -ForegroundColor Gray
Write-Host "  python scripts\test_models.py vl     " -ForegroundColor White -NoNewline
Write-Host "# 测试通义千问识图（需上传药盒图）" -ForegroundColor Gray
Write-Host ""
Write-Host "  uvicorn app.main:app --reload        " -ForegroundColor White -NoNewline
Write-Host "# 启动后端" -ForegroundColor Gray
