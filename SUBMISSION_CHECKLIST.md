# 智药通 — 比赛提交材料对照清单

> 对照《作品提交要求》逐项核验。✅=已就绪 ⏳=需你本人操作

---

## 2.1 代码仓库与演进记录

| 要求 | 状态 | 位置 / 操作 |
|---|---|---|
| 托管平台 GitHub/Gitee，Public 或提供访问权限 | ⏳ | **双击 `scripts\push_to_github.bat`**（自动检测 gh CLI，否则走 PAT 方式，全程中文引导） |
| 完整、细粒度 Git 提交历史（禁止一次性 initial commit 含全部功能） | ✅ | 23 次提交，6 阶段演进，`git log --oneline` 可核验；`git bundle` 备份已随包提供 |
| AI 对话历史导出的 Prompt 快照（≥3 个核心功能完整 Prompt 链，含提问→AI建议→修 Bug 过程） | ✅ | `docs/ai-prompts/AI-COLLABORATION-LOG.md`（3 条完整链）+ `vl-recognition.md` / `rag-interaction.md` / `voice-qa.md`（单点提示词设计） |

## 2.2 复现性声明与重现指南（README.md）

| 要求 | 状态 | 位置 |
|---|---|---|
| 10 分钟极速复现指南 | ✅ | 根目录 `README.md`（快速开始 4 步，实测路径） |
| 完整环境配置说明 | ✅ | `README.md` + `backend/.env.example`（全部变量含注释） |
| 依赖清单 | ✅ | `frontend/package.json` + `backend/requirements.txt`（锁定小版本） |
| 环境变量模板 | ✅ | `frontend/.env.example` + `backend/.env.example` |

> **API Key 申请** → 双击 `scripts\setup_api_keys.bat`（自动复制 .env + 打开记事本 + 填完自动校验）

## 2.3 演示视频与技术文档

| 要求 | 状态 | 位置 / 操作 |
|---|---|---|
| 演示视频 5-8 分钟 MP4 1080p | ⏳ | 按 `docs/demo-video-script.md` 八幕分镜录制（含**第六幕 AI 协同复现 2 分 10 秒**，满足赛制硬性要求） |
| 视频含 ≥2 分钟 AI 协同过程复现（现场输入 Prompt 生成核心模块 / 引导 AI 修 Bug） | ✅ 脚本就绪 | 第六幕 6A（Prompt 生成识药模块 50s）+ 6B（引导修复 JSON 解析 Bug 80s） |
| 技术文档 PDF ≤30 页（意图控制策略 / 架构设计 / 可复现性论证） | ✅ | `docs/技术文档.pdf`（9 页，三大重点分别见第 3 / 2 / 7 章） |

---

## 提交前最后 Checklist

- [ ] **双击 `scripts\push_to_github.bat`** → 推送仓库到 GitHub/Gitee 并设 Public
- [ ] **双击 `scripts\setup_api_keys.bat`** → 申请 2 个 Key 并填入 `backend\.env`（脚本会自动确认 .env 未被提交）
- [ ] `README.md` 顶部回填仓库地址 / 演示地址 / 视频链接占位
- [ ] 部署上线（Vercel + Render，见 `DEPLOY.md`），演示视频用线上地址更有说服力
- [ ] 录制演示视频（脚本第八幕前完成），输出 MP4 1080p
- [ ] 核对视频时长 5-8 分钟、AI 协同片段 ≥2 分钟
- [ ] 官网提交：仓库链接 + 视频文件/链接 + 技术文档 PDF

## 随包文件说明

```
zhiyaotong-submission.zip
├── zhijiayaotong/            # 完整源码（不含 node_modules/venv/dist）
│   └── ...（含全部文档、Prompt 快照、技术文档 PDF）
└── zhiyaotong-git-history.bundle   # 完整 Git 历史（评委解包即可核验 22 次提交）
```

解包核验 Git 历史：`git clone zhiyaotong-git-history.bundle -b main 本地目录`
