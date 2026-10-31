# 版本发布说明

## v0.4.1 — 语音输入服务端化（2026-10-31）

**核心修复：手机端「按住说话」不再失效。**

此前依赖浏览器原生 `webkitSpeechRecognition`，在国内手机上基本不可用：

| 运行环境 | 实际情况 |
| --- | --- |
| Android Chrome / Edge | API 存在但录音需送 Google 服务器，国内连不通 → `error=network` |
| 微信 / QQ / UC 内置浏览器 | 无此 API |
| iOS App 内置 WKWebView | 同样不可用 |

由于能力检测仍返回 `true`，按钮会正常显示、点击后却始终没有结果，长期被误判为代码缺陷。

改造内容：

- 新增 `backend/app/services/asr.py` + `POST /api/voice/asr`，由服务端调用阿里云百炼 Paraformer 转写，
  模型三级回退 + OpenAI 兼容接口兜底，**复用现有 DashScope Key，无需新增环境变量**
- 前端改用 Web Audio 采集 PCM → 降采样 16kHz → 封装 WAV 上传
  （统一 WAV 是因为云端镜像无 ffmpeg，无法转码 iOS 的 aac / Android 的 opus）
- 修复 `AudioContext` 创建顺序：必须先 `getUserMedia()` 再 `new AudioContext()`，
  顺序颠倒时 `onaudioprocess` 一次都不触发（实测 3 秒：0 帧 → 11 帧）
- 新增 `unlockAudio` / `unlockSpeech`：iOS 音频需在用户手势同步栈内解锁，否则回答语音也放不出来
- 健壮性：静音早退提示「没听到声音」、30 秒录音上限（约 480KB，避开网关 body 限制）、
  权限被拒与非 HTTPS 分别给出针对性提示、演示模式返回预置问句

## v0.4.0 — 云端部署与评审材料（2026-10-17）

- 后端版本号对齐；部署至腾讯云 CloudBase 云托管
- 修复 TTS 500：`edge-tts` 升级至 7.3.1（微软签名变更导致 403），不可用时返回 204 静默降级浏览器语音
- 新增省赛版长视频录制脚本 `scripts/record_long_video.py`
- 作品介绍文档配图更换为线上真机截图

---

# 🎉 比赛版本完成（v0.3.0）

> 本文件作为项目交付封档说明。
> 阶段 1-6 全部完成，可提交比赛。

## 交付清单

### 代码（production-ready）

- **前端**：Vue3 + Vite + Vant + Pinia + vite-plugin-pwa
  - 5 个页面（首页/拍照/详情/提醒/语音问答）
  - 3 个通用组件 + 3 个 Pinia stores + 3 个 API 封装
  - PWA 离线可用 + Service Worker 缓存

- **后端**：FastAPI + Pydantic + httpx + asyncio
  - 4 个核心 API（识药 / 相互作用 / 语音问答 / TTS）
  - 4 个 AI 服务模块（VL / LLM / Edge-TTS / RAG）
  - ChromaDB 向量库 + BAAI/bge-small-zh Embedding
  - 生产化 Dockerfile + gunicorn + startup banner + CORS 收紧

### 部署

- 前端：Vercel / Netlify（vercel.json + netlify.toml 一键）
- 后端：Render Blueprint（render.yaml + Docker）
- 备选：Railway（railway.json 自动识别）

### 文档（11 份）

| 类型 | 文件 |
|---|---|
| **用户** | README.md（最终版，含 logo）|
| **运维** | DEPLOY.md / SECURITY.md / CONTRIBUTING.md |
| **产品** | docs/PRD.md / docs/FAQ.md |
| **演示** | docs/demo-video-script.md（7 幕分镜）|
| **AI Prompt** | docs/ai-prompts/{vl-recognition,rag-interaction,voice-qa}.md |
| **API** | docs/API_EXAMPLES.md（curl 完整示例）|
| **评分** | SCORING.md（评分点逐项对应）|
| **变更** | CHANGELOG.md / COMMITS.md |
| **许可证** | LICENSE（MIT）|

### 评测

- Git 提交：**21 次**（含本次）
- 自动化：GitHub Actions × 2（pytest + frontend build）
- 单元测试：pytest 7 个测试用例
- 生产构建：`npm run build` 384 模块成功
- 端到端验证：5 个 API 在 Swagger 全部 200

### 一键脚本

- `scripts/bootstrap.py`：从克隆到跑通一气呵成
- `scripts/build_vector_db.py`：构建 ChromaDB
- `scripts/test_models.py`：验证 VL/LLM/TTS 连通性
- `scripts/preview_tts.py`：5 种声音对比
- `scripts/generate_pwa_icons.py`：PWA 图标自动生成

## 接下来的工作（比赛期间）

1. ✅ 填 `backend/.env` 的真实 Key
2. ⏳ 执行 `python scripts/build_vector_db.py` 构建向量库
3. ⏳ 部署后端到 Render → 前端到 Vercel
4. ⏳ 按 [`docs/demo-video-script.md`](docs/demo-video-script.md) 录演示视频
5. ⏳ 替换 `docs/screenshots/*.svg` 为真实截图
6. ⏳ 把 README 顶部的部署地址回填
7. ⏳ 提交比赛

---

> Made with ❤️ for elderly users, with ☕ and AI assistance.

— 智药通开发团队 · 2026-10-14 · v0.3.0
