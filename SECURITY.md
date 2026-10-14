# Security Policy

## 支持的版本

| 版本 | 支持 |
|---|---|
| 0.3.x | ✅ 当前活跃 |
| 0.2.x | ⚠️ 仅严重安全问题 |
| < 0.2 | ❌ 不再维护 |

## 报告漏洞

**请勿在公开 issue 中报告安全问题**，通过邮件发送：

📧 security@[your-domain].local

我们会在 48 小时内确认，并在 7 天内处理。

## 安全设计要点

### 1. API Key 管理
- 所有 API Key 放在环境变量（`.env`）
- `.env` 已加入 `.gitignore`，绝不会入仓
- 仓库提供 `.env.example` 占位
- 部署时通过 Render / Vercel / Railway 的 Secret 注入

### 2. CORS 收紧
- 后端通过 `FRONTEND_URL` 环境变量精确控制允许的源
- **绝不**使用 `allow_origins=["*"]`（生产模式）

### 3. 用户隐私
- 用药清单存本地 `localStorage`，不上传
- 药品识别图片上传后后端立即销毁（不持久化）
- 不收集用户的身份信息

### 4. 输入校验
- 所有 API 入参用 Pydantic 严格校验
- 文件上传限制大小（5MB）+ 验证 Content-Type
- 后端有错误捕获，不会把堆栈泄露给前端

### 5. 依赖安全
- 依赖固定版本（避免供应链攻击）
- 三个月一次升级 `pip install --upgrade`

### 6. 医疗免责声明
- 应用首屏显示"本应用仅供学习交流"
- 任何风险提示都附加"以药品说明书为准"
- 不支持用于急救场景
- App 内置"立即拨打 120"按钮

## ⚠️ 已知风险

| 风险 | 说明 | 缓解 |
|---|---|---|
| AI 误识 | VL 识别药品可能错误 | 强制显示说明书原文建议 |
| AI 模型密钥泄露 | Key 提交到 git | .gitignore + 预提交钩子 |
| 后端误调 | CORS 不当可能误调 | FRONTEND_URL 精确域名 |

## 安全更新

安全更新会通过 GitHub Security Advisories 发布。
