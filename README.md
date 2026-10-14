# 智药通 — AI 老年人用药安全助手

> 传智杯 AI 创新应用挑战赛参赛作品（个人赛）
> 帮助老年人安全用药的 H5 / PWA 应用

## ✨ 核心功能

- 📷 **拍照识药**：上传药盒照片，AI 自动识别药品名、规格、用法用量
- ⚠️ **相互作用检查**：基于 RAG 检索药品说明书，提示用药风险
- ⏰ **服药提醒**：可设置每日提醒，语音播报
- 🎙️ **语音问答**：按住说话 → 文字转写 → 大模型回答 → TTS 播报
- 📱 **PWA 安装**：可添加到手机桌面，离线访问

## 🛠️ 技术栈

**前端**：Vue3 + Vite + Vant + Pinia + vite-plugin-pwa
**后端**：Python FastAPI + DashScope（通义千问 VL）+ DeepSeek + Edge-TTS + ChromaDB
**部署**：前端 Vercel/Netlify，后端 Render/Railway

## 🚀 快速开始

### 后端
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env  # 填入真实 API Key
uvicorn app.main:app --reload --port 8000
```
后端启动后访问 http://localhost:8000/docs 查看 API 文档。

### 前端
```bash
cd frontend
npm install
npm run dev
```
前端启动后访问 http://localhost:5173 。

## 📁 目录结构

```
zhijiayaotong/
├── frontend/   # Vue3 前端 + PWA
├── backend/    # FastAPI 后端
└── docs/       # 比赛材料（演示视频脚本/Prompt 快照/截图）
```

## 📝 License

MIT