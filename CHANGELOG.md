# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/) 规范。

## [Unreleased]

### 阶段 6 - 比赛材料准备
- 撰写最终版 README.md（含 logo + 功能演示 + 快速开始 + 评分对应）
- 完善演示视频脚本（5-8 分钟分镜 + 对白 + 字幕 + 镜头语言）
- 新增 SCORING.md（比赛评分点逐项对应）
- 新增 CHANGELOG.md / LICENSE / docs/PRD.md

## [0.3.0] - 2026-10-14

### 阶段 5 - PWA + 一键部署配置
### ✨ Features
- 集成 `vite-plugin-pwa`（autoUpdate + Workbox runtimeCaching 三层缓存）
- 新增 PWA manifest + 3 张图标（192/512/maskable）
- 新增一键部署配置：vercel.json / netlify.toml / render.yaml / railway.json
- 新增 Dockerfile + start.sh（首次启动自动 build 向量库）
- 后端 CORS 用 `FRONTEND_URL` 环境变量收紧；启动 banner

### 📚 Docs
- 新增 DEPLOY.md（架构图 + 5 步部署 + 常见问题）
- 新增 `scripts/generate_pwa_icons.py`（cairosvg 优先 + Pillow 降级）

## [0.2.0] - 2026-10-14

### 阶段 4 - RAG + AI 集成
### ✨ Features
- 新增 ChromaDB 构建脚本 `scripts/build_vector_db.py`
- 新增 30 种老年常用药数据集 `scripts/data/medicines.json`
- 升级 `app/services/rag.py`：延迟加载向量库 + DeepSeek 兜底
- 升级 `app/services/deepseek.py`：抽出 `_complete_json` 通用方法
- 新增 Edge-TTS 5 种声音对比脚本 `scripts/preview_tts.py`
- 新增模型连通性测试脚本 `scripts/test_models.py`

### 📚 Docs
- 新增 3 份 AI Prompt 快照：
  - `docs/ai-prompts/vl-recognition.md`（通义千问 VL）
  - `docs/ai-prompts/rag-interaction.md`（DeepSeek + RAG）
  - `docs/ai-prompts/voice-qa.md`（语音问答）

## [0.2.0] - 2026-10-14

### 阶段 3 - 前端 5 个页面
### ✨ Features
- 21 个新文件：3 API 封装 + 3 utils + 3 Pinia stores + 路由 + 3 组件 + 5 视图
- Vant 按需注册 26 个组件
- 适配移动端（safe-area-inset、padding-bottom）
- Pinia 持久化到 localStorage（带 zhiyaotong: 前缀）

## [0.2.0] - 2026-10-14

### 阶段 2 - 后端 4 个核心 API
### ✨ Features
- `POST /api/medicine/recognize` — 通义千问 VL 拍照识药（强制 JSON 输出 + markdown 围栏剥离）
- `POST /api/interaction/check` — DeepSeek 药物相互作用分析
- `POST /api/voice/chat` — DeepSeek 语音问答（老年人友好 system prompt）
- `POST /api/voice/tts` — Edge-TTS 文字转语音（5 种中文声音）
- `GET /api/voice/voices` — TTS 声音列表

## [0.1.0] - 2026-10-14

### 阶段 1 - 项目初始化
### ✨ Features
- 前端：Vue3 + Vite + Vant + vite-plugin-pwa 初始化（247 个依赖）
- 后端：FastAPI 骨架（29 个核心依赖）
- 根目录 `.gitignore` + `README.md` + `docs/`
- 健康检查端点 `GET /api/health`
