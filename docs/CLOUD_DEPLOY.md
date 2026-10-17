# 智药通 · 公网部署指南（手机随时打开，电脑不用开）

本地跑服务要求电脑一直开着。要让手机在任何地方、任何时候都能打开，必须把服务部署到公网。
本项目的后端已经在同一端口（8000）托管前端构建产物，**所以只需要部署一个服务，就同时有网页和接口**。

## 方案对比（2026-10 实测）

| 方案 | 费用 | 免绑卡 | 国内访问 | 说明 |
|---|---|---|---|---|
| **腾讯云 CloudBase 云托管**（首选） | 按量计费（很小额）+ 实名 | ✅ 微信/QQ 实名即可 | **最快**（境内节点） | 上传 zip 或填公开仓库地址，支持 Dockerfile |
| Leapcell | Hobby 免费（20 个项目） | ✅ GitHub 登录即可 | 较好（日本节点） | GitOps，填 Build/Start 命令即可 |
| Koyeb（备选） | 免费 1 个 Web Service | ✅ | 一般（法兰克福/华盛顿） | 直接吃本仓库根目录 `Dockerfile` |
| Zeabur | ❌ **已停止个人免费** | — | — | 2026-05-15 起关闭共享集群，新建项目必须买服务器（$3/月起） |
| Render | 免费 | ❌ **新账户强制绑信用卡** | 一般 | 有国际卡才可用，配置见 `render.yaml` |
| 腾讯云 CloudBase | 有免费额度 | ✅（需实名） | 快 | 需实名认证 |
| 本地 + 内网穿透 | 免费 | ✅ | 快 | **电脑必须开机**，不符合需求 |

**结论：优先腾讯云 CloudBase 云托管（国内节点、微信实名即可、老师打开最快）；
海外平台（Leapcell / Koyeb）作为备用。**

## 腾讯云 CloudBase 云托管部署步骤（首选，国内最快）

### 第 0 步：准备部署包（已完成）
桌面上的 `zhiyaotong-cloudrun.zip`（0.3MB，51 个文件）就是部署包，
只包含 `Dockerfile` + `backend/app` + `backend/requirements-cloud.txt` + `frontend/dist`，
**不含 `.env`（避免把 API Key 传上去）、不含 venv / node_modules**。

重新生成：
```
python scripts/make_cloudrun_zip.py
```

### 第 1 步：开通云开发 + 充 10 元
1. 打开 https://tcb.cloud.tencent.com/ ，**微信扫码登录**，完成实名认证（身份证 + 人脸）
2. 进腾讯云**费用中心**用微信充值 **10 元**（按量计费要求账户有余额，不需要绑信用卡）
3. 回云开发控制台点 **新建环境** → 名称填 `zhiyaotong` → 计费方式选 **按量计费**

#### 到底要花多少钱

| 配置 | 费用 |
|---|---|
| 最小实例 **0**（按需启动，没人访问不收费） | 老师偶尔打开演示：**几毛 ~ 几元** |
| 最小实例 **1**（常驻秒开） | 0.5 核 / 1GB 约 **¥20–40/月** |

**推荐：最小实例设 0 + 充 10 元**，比赛全程够用。
比完赛把服务/环境删掉就不会再产生费用。

> CloudBase 另有「免费体验版」¥0/月（3000 资源点），需公众号领一次性兑换码，
> 但免费环境**不支持按量付费**，云托管基本跑不起来，所以走按量计费更省事。

### 第 2 步：新建云托管服务
1. 左侧进 **云托管** → **新建服务**
2. 部署方式选 **本地代码**（推荐，避免国内构建机拉 GitHub 失败）
   —— 上传桌面那个 `zhiyaotong-cloudrun.zip`
   （也可以选「Git 仓库」填公开地址 `https://github.com/wuhu2331936/zyt`，公开仓库免授权）
3. 配置照抄：

| 配置项 | 填什么 |
|---|---|
| 服务名称 | `zhiyaotong` |
| 访问类型 | **WEB（公网访问）** |
| Dockerfile 路径 | `Dockerfile`（默认，不用改） |
| 目标目录 | 默认（仓库根目录） |
| 端口 | **8080** |
| CPU / 内存 | `0.5 核 / 1 GB`（最低档就够） |
| 最小实例数 | `0`（按需启动，省钱） |
| 最大实例数 | `1` |

### 第 3 步：填环境变量（关键）
服务建好后 → **服务配置 → 环境变量**，添加：

| 变量名 | 值 |
|---|---|
| `PORT` | `8080` |
| `DASHSCOPE_API_KEY` | 阿里云百炼 Key（拍照识药） |
| `DEEPSEEK_API_KEY` | DeepSeek Key（AI 问答） |
| `QWEN_VL_MODEL` | `qwen3-vl-plus` |
| `RAG_ENABLED` | `0`（云端不装 RAG，省内存） |
| `DEMO_MODE` | **`0`**（填 `1` 会屏蔽真实 AI，识药直接返回假数据，别开） |

> ⚠️ `DEMO_MODE=1` 会让识药/问答**完全跳过真实 API**，只返回预置示例。
> 真实调用失败（余额不足、模型下线）时代码**本来就会自动降级**，
> 所以只要 Key 有效就填 `0`，这样才是真 AI + 失败兜底。

保存后服务会自动重启。用 `/api/health` 验证：`demo_mode` 为 `false` 且两个 Key 都填了，说明真实 AI 已生效。

> **云托管改环境变量的正确姿势**：服务详情页的「环境变量」列表是**只读**的（右侧眼睛图标只控制显示/隐藏）。
> 要修改必须走 **「版本管理 → 新建版本」**，在新建版本表单里会再次出现可视化的环境变量输入框，
> 改完提交部署才生效 —— 光改列表不会重启实例。

### 第 4 步：拿到网址
服务详情页会给出公网域名，形如：
```
https://zhiyaotong-xxx.ap-shanghai.app.tcloudbase.com
```
手机/电脑浏览器直接打开，可「添加到主屏幕」当 App 用。**电脑关机也不影响。**

> 最小实例数设 0 时，第一次打开会冷启动（等 20–40 秒）。
> 演示前先自己打开一次把它唤醒；想秒开就把最小实例数改成 `1`（费用略高）。

> 免费云主机的通病：**15 分钟没人访问会休眠**，下次打开要等 30–50 秒冷启动。
> 比赛演示前先打开一次页面把它唤醒。

## Leapcell 部署步骤（约 5 分钟）

### 第 1 步：先把代码推到 GitHub
见 `docs/PUSH_TO_REMOTE_GUIDE.md`。**必须先推**，Leapcell 是从 GitHub 拉代码的。
当前远端已同步到 `906c3cc`（含 Dockerfile 与演示模式）。

### 第 2 步：创建服务
1. 打开 https://leapcell.io ，点 **Deploy For Free → 用 GitHub 账号登录**
2. 新建 Service → **Git** → 选 `wuhu2331936/zyt` 仓库，分支 `main`
3. 填这四项（其余默认）：

| 配置项 | 填什么 |
|---|---|
| Root Directory | 留空（仓库根目录） |
| Build Command | `pip install -r backend/requirements-cloud.txt` |
| Start Command | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| Port | `8000` |

> 前端不用构建：仓库里已经提交了 `frontend/dist`，后端在同一端口直接托管网页和接口。

4. 区域（Region）选 **Japan**（离国内最近，比美国节点快很多）
5. 点 Deploy，看 Logs 等到出现 `Application startup complete`

### 第 3 步：填环境变量（关键）
服务页面 → **Environment Variables / Variables**，添加：

| 变量名 | 值 |
|---|---|
| `DASHSCOPE_API_KEY` | 阿里云百炼 Key（拍照识药用） |
| `DEEPSEEK_API_KEY` | DeepSeek Key（AI 问答用，余额需 > 0） |

保存后服务会自动重启生效。变量在平台侧加密保存，不会进 GitHub 仓库。

### 第 4 步：拿到网址
部署成功后平台给一个 `xxx.leapcell.dev` 域名。
手机浏览器打开即可，也可以「添加到主屏幕」当 App 用。**电脑关机也不影响。**

## Koyeb 部署步骤（Leapcell 走不通时的备选）

1. 打开 https://app.koyeb.com ，GitHub 登录
2. **Create Web Service → GitHub** → 选 `zyt` 仓库
3. Builder 选 **Dockerfile**（它会自动用仓库根目录那个），端口填 `8080`，并把环境变量 `PORT=8080` 写上
4. 同样添加 `DASHSCOPE_API_KEY`、`DEEPSEEK_API_KEY`
5. 部署完拿到 `xxx.koyeb.app`

## 关于 Zeabur（已弃用）

Zeabur 官方公告：共享集群不再开放新项目，2026-05-15 起个人免费集群彻底关闭。
现在创建项目只能**购买专属服务器**（腾讯云 $3/月起、AWS $14/月起），
所以控制台会直接跳到「购买新服务器」那一页——**不要买**，换 Leapcell 或 Koyeb。

## 为什么云端依赖分成了两个文件

- `backend/requirements.txt`：本地全量版，含 RAG 三件套（chromadb + sentence-transformers + pypdf），会拖进 torch（约 2GB）
- `backend/requirements-cloud.txt`：云端轻量版，**去掉 RAG**（Dockerfile 用的就是这个）

免费云主机只有 256–512MB 内存，装 torch 会直接构建失败或 OOM。
`app/services/rag.py` 里已经写了 `ImportError` 降级：缺这些包时 RAG 自动禁用，
**拍照识药、AI 问答、语音播报、相互作用检查全部照常可用**。

## 修改代码后如何更新

平台关联 GitHub 后会自动监听：本地 commit → push 到 GitHub → 自动重新构建部署。
不需要在面板做任何操作。

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
Render 对新账户强制要求信用卡验证，即使 Free 档也一样。没卡就换 Leapcell / Koyeb。

**Q：CloudBase 构建时 pip 装包失败/超时？**
镜像里装的是 `requirements-cloud.txt`（无 torch）。构建失败先看日志：
如果是拉 GitHub 超时，改回「本地代码」上传 zip；如果是 pip 源慢，在环境变量里加
`PIP_INDEX_URL` = `https://mirrors.tencent.com/pypi/simple/`。

**Q：CloudBase 打开页面白屏/404？**
确认端口填的是 `8080`，且环境变量 `PORT=8080`（Dockerfile 里读的是 `${PORT}`）。

**Q：Zeabur 让我买服务器？**
正常的，它 2026-05 起关掉了个人免费集群。别买，按上面换平台。
