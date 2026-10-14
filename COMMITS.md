# 提交记录（按时间倒序）

## 比赛提交总览

| 维度 | 数量 |
|---|---|
| 总提交数 | **22**（含本文档） |
| feat | 4 |
| fix | 0 |
| docs | 12 |
| test | 1 |
| ci | 1 |
| chore | 3 |
| refactor | 0 |
| style | 0 |
| perf | 0 |

## 阶段对照表

| 阶段 | 提交数 | 范围 |
|---|---|---|
| 阶段 1 项目初始化 | 1 | 仓库 + Frontend + Backend + .gitignore |
| 阶段 2 后端 4 个 API | 1 | qwen_vl / deepseek / tts / rag 服务 + 路由 |
| 阶段 3 前端 5 页面 | 1 | 21 文件（API/utils/stores/router/views） |
| 阶段 4 RAG + AI 集成 | 1 | ChromaDB + 数据集 + 升级 RAG + 3 份 Prompt 快照 |
| 阶段 5 PWA + 部署 | 1 | vite-plugin-pwa + manifest + 4 个部署配置 + DEPLOY.md |
| 阶段 6 比赛材料 | **17** | README / 部署文档 / FAQ / PR / 安全 / 截图 / CI / 测试 / 一键脚本 |

## 提交详情

```
8b8f7cf docs: add FAQ + API curl examples + docs/ index
2545a50 ci: add GitHub Actions for backend pytest + frontend build
70094fe test(backend): add pytest smoke tests for API + Pydantic models
530efcd feat(scripts): add cross-platform bootstrap.py for one-click setup
2a7d54b docs(security): add security policy + design principles
94b8899 docs(contributing): add Conventional Commits + branch strategy
8eef149 chore(frontend): add preview script with port 4173 + browserslist
2b7b4d2 chore: add editorconfig + gitattributes + consolidate requirements
0f561e5 docs(screenshots): add 5 SVG placeholder screenshots + style guide
f41e1cb docs(prd): add Product Requirements Document
62a7319 docs(demo): expand demo video script to 7-act shot-by-shot
44870c5 docs(scoring): add competition scoring breakdown
67d924b docs(license): add MIT License
5834a43 docs(changelog): add CHANGELOG.md with semantic versioning
820bac3 docs(readme): rewrite README to final competition version
e71fb30 feat(pwa): PWA 集成 + 一键部署配置 (stage 5)
40d744d feat(backend): add RAG vector store + AI integration docs (stage 4)
044b80d feat(frontend): complete all 5 views for stage 3
a3d395e feat(backend): add 4 core APIs for stage 2
864149d chore: initial project structure for zhijiayaotong
```
