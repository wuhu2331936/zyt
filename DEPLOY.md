# =============================================================================
# 部署指南
# =============================================================================

> 本文档说明如何把智药通部署到生产环境。
> 比赛演示地址示例：`https://zhijiayaotong.vercel.app` + `https://zhijiayaotong-api.onrender.com`

## 一、整体架构

```
┌──────────────────────────┐         ┌──────────────────────────┐
│   前端 (Vercel/Netlify)  │  HTTPS  │   后端 (Render/Railway)  │
│   Vue3 + Vite + PWA      │ ──────► │   FastAPI + ChromaDB     │
│   zhijiayaotong.vercel.app│        │   zhijiayaotong-api.     │
└──────────────────────────┘         │   onrender.com           │
        │                            └──────────────────────────┘
        │                                       │
        ▼                                       ▼
   PWA 安装到手机                           DeepSeek API
   离线也能看清单                            通义千问 VL
                                            Edge-TTS（自带）
```

## 二、推荐路线：Render + Vercel（两平台都免费起步）

### 步骤 1：把代码推到 GitHub

```bash
cd zhijiayaotong
git remote add origin https://github.com/<your-username>/zhijiayaotong.git
git push -u origin main
```

> **比赛建议**：在 GitHub 仓库设置 → About → 勾选 "Releases" 让评委能下载提交包。

### 步骤 2：部署后端到 Render

1. 打开 https://render.com → Sign up with GitHub
2. 点击 **New +** → **Blueprint**
3. 选你的 `zhijiayaotong` 仓库 → Render 会自动识别根目录的 `render.yaml`
4. 点击 **Apply** → 开始部署
5. 等部署完成（约 5–8 分钟，包含构建向量库）
6. 进入服务 → **Environment** → 手动添加两个 Key：
   - `DASHSCOPE_API_KEY`：阿里云百炼控制台 → https://bailian.console.aliyun.com/ → API-Key 管理
   - `DEEPSEEK_API_KEY`：https://platform.deepseek.com/ → API Keys
7. 添加后服务自动重启。访问 `https://zhijiayaotong-api.onrender.com/api/health` 应返回 `{"status":"ok"}`

> **注意**：Render 免费版会休眠（15 分钟无请求），首次访问慢约 30 秒。比赛演示前手动访问一次热身即可。

### 步骤 3：部署前端到 Vercel

1. 打开 https://vercel.com → Sign up with GitHub
2. 点击 **Add New** → **Project** → 选 `zhijiayaotong` 仓库
3. Framework Preset 自动识别为 Vite
4. **Root Directory** 改成 `frontend`
5. **Environment Variables** 添加：
   - `VITE_API_BASE_URL` = `https://zhijiayaotong-api.onrender.com/api`
6. 点击 **Deploy** → 约 1 分钟完成
7. 访问 Vercel 给你的域名（默认 `<仓库名>.vercel.app`）

### 步骤 4：把前端地址告知后端（CORS）

回到 Render 后端服务 → Environment → 添加：
- `FRONTEND_URL` = `https://zhijiayaotong.vercel.app`

然后 `app/main.py` 里我可以读到它作为 CORS allow origin（生产模式），避免任何域都能调用。

### 步骤 5：PWA 测试

1. 浏览器（Chrome/Edge）打开前端域名 → 右上角会出现 "📲 安装智药通" 按钮
2. iOS Safari → 分享 → 添加到主屏幕
3. 安装后图标是 `public/pwa-icons/icon.svg` 渲染的胶囊图案
4. 离线状态（断网）应能打开首页看到用药清单

## 三、备选部署方案

### A. Railway（更简单但要绑卡）

1. https://railway.app → New Project → Deploy from GitHub
2. 选 `zhijiayaotong` 仓库 → Root Directory 填 `backend`
3. Railway 自动读 `backend/railway.json`
4. Variables 加 `DASHSCOPE_API_KEY` + `DEEPSEEK_API_KEY`
5. Settings → Generate Domain → 得到 `xxx.up.railway.app`

### B. Netlify（前端）

1. https://netlify.com → Add new site → Import from Git
2. 选 `zhijiayaotong` 仓库
3. Build command: `cd frontend && npm run build`
4. Publish directory: `frontend/dist`
5. Environment Variables 加 `VITE_API_BASE_URL`

### C. 自有云服务器（Docker Compose）

```yaml
# docker-compose.yml（生产用）
version: "3.9"
services:
  backend:
    build: ./backend
    ports:
      - "8000:10000"
    env_file: ./backend/.env
    volumes:
      - ./backend/app/data/chroma:/app/app/data/chroma
    restart: unless-stopped
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./dist:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend
```

> 比赛一般不需要，D 步骤的免费方案已经够用。

## 四、环境变量清单

### 后端（必须设置在 Render/Railway Environment）

| 变量名 | 说明 | 获取 |
|---|---|---|
| `DASHSCOPE_API_KEY` | 阿里云百炼 | bailian.console.aliyun.com |
| `DEEPSEEK_API_KEY` | DeepSeek 对话 | platform.deepseek.com |
| `DEEPSEEK_BASE_URL` | （默认即可）| https://api.deepseek.com |
| `QWEN_VL_MODEL` | （默认 qwen-vl-plus）| 阿里云百炼模型市场 |
| `EMBEDDING_MODEL` | （默认 BAAI/bge-small-zh）| HuggingFace |

### 前端（必须设置在 Vercel/Netlify Environment）

| 变量名 | 说明 | 示例 |
|---|---|---|
| `VITE_API_BASE_URL` | 后端 API 完整路径 | `https://xxx.onrender.com/api` |

## 五、部署后的演示流程

1. 评委扫码 → 进入前端 URL
2. 首页看到空清单（首次访问）
3. 点 "拍照识药" → 上传一张常见药盒图 → 2–5 秒返回药品信息
4. 把识别出的药加入清单 → 再添加一个 → 首页点 "检查相互作用"
5. 进 "语音问答" → 按住说话 → 松手 → 听 Edge-TTS 播报回答
6. 关闭网络 → 离线模式仍能看清单（PWA 命中 Service Worker 缓存）

## 六、常见问题

### Q1. Render 部署失败 "pip install timeout"
A: 升级到 starter plan（$7/月），512MB 以下内存装 torch 会 OOM。

### Q2. 后端 `/api/medicine/recognize` 返回 500
A: 大概率是没填 `DASHSCOPE_API_KEY`，去 Render → Environment 加上重启。

### Q3. PWA 安装按钮不出现
A: 必须是 HTTPS。Vercel/Netlify 部署后默认 HTTPS，本地 `http://localhost:5173` 也能用。

### Q4. 离线打开页面是空白
A: PWA 首次安装后必须联网一次，让 Service Worker 完成预缓存。等看到 Console 提示 "PWA registered" 再断网。
