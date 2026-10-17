# 智药通 · 公网部署指南（手机随时打开，电脑不用开）

本地跑服务要求电脑一直开着。要让手机在任何地方、任何时候都能打开，必须把服务部署到公网。
本项目的后端已经在同一端口（8000）托管前端构建产物，**所以只需要部署一个服务，就同时有网页和接口**。

## 方案对比（2026-10 实测）

| 方案 | 费用 | 免绑卡 | 国内访问 | 说明 |
|---|---|---|---|---|
| **Zeabur**（推荐） | 免费额度 | ✅ GitHub 登录即可 | **快**（香港/新加坡节点） | 控制台中文，自动识别 Dockerfile |
| Koyeb | 免费额度 $5.5/月 | ✅ | 一般 | 也支持本仓库 Dockerfile |
| Render | 免费 | ❌ **新账户强制绑信用卡** | 一般 | 有国际卡才可用，配置见 `render.yaml` |
| 腾讯云 CloudBase | 有免费额度 | ✅（需实名） | 快 | 需实名认证 |
| 本地 + 内网穿透 | 免费 | ✅ | 快 | **电脑必须开机**，不符合需求 |

**结论：没有国际信用卡就用 Zeabur。**

> 免费云主机的通病：**15 分钟没人访问会休眠**，下次打开要等 30–50 秒冷启动。
> 比赛演示前先打开一次页面把它唤醒。

## Zeabur 部署步骤（约 5 分钟）

### 第 1 步：先把代码推到 GitHub
见 `docs/PUSH_TO_REMOTE_GUIDE.md`。**必须先推**，Zeabur 是从 GitHub 拉代码的。

### 第 2 步：创建项目
1. 打开 https://zeabur.com ，点 **Login → 用 GitHub 账号登录**
2. 点 **New Project**
3. 选 **Deploy from GitHub**，授权后找到 **`zyt`** 仓库点 Deploy
4. Zeabur 会检测到仓库根目录的 `Dockerfile` 并按它构建（不需要你手填命令）

### 第 3 步：填环境变量（关键）
部署后进入服务页面 → **Variables** 标签，添加：

| 变量名 | 值 |
|---|---|
| `DASHSCOPE_API_KEY` | 阿里云百炼 Key（拍照识药用） |
| `DEEPSEEK_API_KEY` | DeepSeek Key（AI 问答用，余额需 > 0） |

保存后服务会自动重启生效。Zeabur 里的变量是加密的，不会进 GitHub 仓库。

### 第 4 步：拿到网址
服务页面会给出一个 `xxx.zeabur.app` 的免费域名。
手机浏览器打开它即可，也可以「添加到主屏幕」当 App 用。**电脑关机也不影响。**

## 为什么云端依赖分成了两个文件

- `backend/requirements.txt`：本地全量版，含 RAG 三件套（chromadb + sentence-transformers + pypdf），会拖进 torch（约 2GB）
- `backend/requirements-cloud.txt`：云端轻量版，**去掉 RAG**（Dockerfile 用的就是这个）

免费云主机只有 256–512MB 内存，装 torch 会直接构建失败或 OOM。
`app/services/rag.py` 里已经写了 `ImportError` 降级：缺这些包时 RAG 自动禁用，
**拍照识药、AI 问答、语音播报、相互作用检查全部照常可用**。

## 修改代码后如何更新

Zeabur 关联 GitHub 后会自动监听：本地 commit → push 到 GitHub → Zeabur 自动重新构建部署。
不需要在 Zeabur 面板做任何操作。

> 注意：前端改了样式/页面，需要本地 `npm run build` 并把 `frontend/dist` 一起提交，
> 因为云端不跑 npm 构建，直接托管仓库里的 `frontend/dist`。

## 常见问题

**Q：打开网址转圈很久？**
免费实例休眠了，等 30–50 秒让它冷启动，之后就快了。

**Q：构建失败，日志里 pip 报错或 OOM？**
确认用的是 `requirements-cloud.txt`（Dockerfile 里已写死），不要换成全量版。

**Q：拍照识药报 "Model not exist"？**
`QWEN_VL_MODEL` 要设为 `qwen3-vl-plus`（旧的 `qwen-vl-plus` 已被百炼下线）。当前代码已改好。

**Q：AI 问答报 402？**
DeepSeek 账户余额为 0，充值 10 元即可。

**Q：Render 一直弹绑卡？**
Render 对新账户强制要求信用卡验证，即使 Free 档也一样。没卡就换 Zeabur。
