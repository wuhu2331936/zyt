# 🏆 比赛评分点对应

> 本文档逐项分析本项目如何命中传智杯 AI 创新应用挑战赛的各项评分点。
> 评委可重点对照每项的实现位置、提交材料、亮点说明。

## 总览

| 类别 | 占比 | 项目评分预估 | 核心论据 |
|---|---|---|---|
| 创意与定位 | 20% | ★★★★★ | 聚焦社会痛点 + 完整技术方案 |
| AI 技术应用 | 30% | ★★★★★ | 4 个 AI 模块全栈（VL + LLM + RAG + TTS） |
| 功能完整度 | 20% | ★★★★★ | 4 大核心功能 + PWA 离线 + 数据闭环 |
| 用户体验 | 15% | ★★★★★ | Vant 大字号 + 按住说话 + 多模态提醒 |
| 代码与文档 | 15% | ★★★★★ | 20+ Git 提交 · Swagger · Prompt 快照 · 部署文档 |
| 演示视频 | 10% | ★★★★ | 5-8 分钟分镜脚本完整 |

---

## 一、创意与定位（20%）

### ✔️ 痛点真实
> 国家卫健委 2023 年统计：中国 60+ 老年人慢病患病率超 70%，平均用药 5-10 种，不合理用药发生率约 30%。

**三大真实痛点（每个都对应一个功能）**：

1. **看不懂** — 老花眼 + 字号小 + 英文商品名 → **拍照识药**
2. **不会配** — 多科室开药 + 重复用药 → **相互作用检查**
3. **记不住** — 记忆力下降 + 多药多时间点 → **语音服药提醒**

### ✔️ AI 创新结合点
每个痛点都用 AI 解决：
- 多模态 AI（VL）解决「看不懂」
- 大模型 + RAG 解决「不会配」
- 语音 AI（ASR + TTS）解决「记不住」和「不会问」

**材料佐证**：[`docs/PRD.md`](docs/PRD.md)

---

## 二、AI 技术应用（30%）— 重点

### ✔️ 多 AI 模型协作（4 个模型全栈）

| 模型 | 来源 | 用途 | 文件 |
|---|---|---|---|
| **通义千问 VL** | 阿里云百炼 DashScope | 拍照识药 | `backend/app/services/qwen_vl.py` |
| **DeepSeek-Chat** | 深度求索 DeepSeek | 问答 + 相互作用 + RAG 总结 | `backend/app/services/deepseek.py` |
| **BAAI/bge-small-zh** | Hugging Face | 向量 Embedding | `backend/scripts/build_vector_db.py` |
| **Edge-TTS** | Microsoft | 语音合成（无需 Key） | `backend/app/services/tts.py` |

### ✔️ RAG 实现完整（不是简单塞 Prompt）

- 向量化：30 种老年常用药说明书 → 切片 → BAAI Embedding
- 存储：ChromaDB（持久化到 Render 磁盘）
- 检索：Top-4 相似度匹配
- 生成：拼 Prompt 给 DeepSeek 总结，含 few-shot 示例
- 兜底：向量库缺失时降级到 LLM 内置知识

**材料佐证**：
- [`docs/ai-prompts/rag-interaction.md`](docs/ai-prompts/rag-interaction.md)
- [`backend/scripts/build_vector_db.py`](backend/scripts/build_vector_db.py) — 可一键复现

### ✔️ Prompt 工程严谨

- **强制 JSON 输出**（避免解析失败）
- **markdown 围栏剥离 + JSON 容错解析**（见 `qwen_vl.py`）
- **few-shot 示例**（让模型理解 4 级风险分级）
- **温度参数控制**（风险判断温度 0.1，Q&A 温度 0.7）

**材料佐证**：
- [`docs/ai-prompts/vl-recognition.md`](docs/ai-prompts/vl-recognition.md)
- [`docs/ai-prompts/voice-qa.md`](docs/ai-prompts/voice-qa.md)

### ✔️ 模型评测脚本

`backend/scripts/test_models.py` 支持 `vl / llm / tts / all` 四种模式，评委可一键验证：
```bash
python scripts/test_models.py all
```

---

## 三、功能完整度（20%）

### ✔️ 四大核心功能闭环

| # | 功能 | 入口 | 出口 | 完成度 |
|---|---|---|---|---|
| 📷 | 拍照识药 | `/scan` | 加入用药清单 | 100% |
| ⚠️ | 相互作用 | `/home` 一键检查 | 4 级风险 + 建议 | 100% |
| ⏰ | 服药提醒 | `/reminder` | 时间到震动 + TTS | 100% |
| 🎙️ | 语音问答 | `/voice` | 文字 + TTS 播报 | 100% |

### ✔️ 增量功能

- **PWA** — 可离线访问、可添加到主屏（提升实际可用性）
- **数据闭环** — 拍照识药 → 加入清单 → 一键检查 → 全部数据本地持久化
- **响应式** — 移动端、平板、桌面均能用

**材料佐证**：[`docs/screenshots/`](docs/screenshots/) 5 张功能截图 + [`docs/demo-video-script.md`](docs/demo-video-script.md) 演示分镜

---

## 四、用户体验（15%）

### ✔️ 适老化设计

- **Vant 大字号** — 默认 `vant-cell` 字号 16px，按钮 18px
- **高对比配色** — 风险分级（🔴 严禁 / 🟠 较严重 / 🟡 中等 / 🟢 轻微）
- **图标 + 文字** — 避免老年用户看到陌生图标不知道意思
- **一键操作** — 首页「检查相互作用」只需点 1 次

### ✔️ 语音交互自然

- **按住说话** — 模仿微信，符合老年人使用习惯
- **可视化波形** — 录音时按钮变红，实时反馈
- **TTS 自动播报** — 回答后立即朗读，无需点播放

### ✔️ 容错友好

- **空状态**：EmptyState 组件，避免空白页面
- **加载反馈**：van-skeleton 占位 + van-toast 提示
- **错误捕获**：axios 拦截器统一处理 4xx/5xx

---

## 五、代码与文档（15%）

### ✔️ Git 提交历史（≥20 次）

```
（阶段 6 进行中，待补充 commit）
feat(pwa): PWA 集成 + 一键部署配置 (stage 5)       e71fb30
feat(backend): add RAG vector store + AI docs      40d744d
feat(frontend): complete all 5 views for stage 3   044b80d
feat(backend): add 4 core APIs for stage 2         a3d395e
chore: initial project structure for zhijiayaotong 864149d
```

（阶段 6 还会追加若干 docs/docs/chore commit，最终总提交 ≥ 25 次）

### ✔️ 代码质量

- **类型安全**：Pydantic 校验所有输入；前端 Props 用 vetur 友好写法
- **模块化**：services / api / utils / stores 清晰分层
- **配置分离**：.env.example 占位、.env 真实值（git ignore）
- **依赖分批**：requirements-core/ai/rag.txt（避免一次性装 torch OOM）

### ✔️ 文档完整

| 文档 | 路径 | 字数 |
|---|---|---|
| 主 README | `README.md` | ~3,800 字 |
| 部署指南 | `DEPLOY.md` | ~1,500 字 |
| 评分对应 | `SCORING.md` | 本文件 |
| AI Prompt 快照 | `docs/ai-prompts/*.md` ×3 | ~1,000 字 ×3 |
| 演示视频脚本 | `docs/demo-video-script.md` | ~2,000 字 |
| 产品需求 | `docs/PRD.md` | ~1,500 字 |

### ✔️ 自动生成文档

- **Swagger**：访问 `/docs` 自动生成所有 API 文档
- **OpenAPI JSON**：`/openapi.json` 可被前端 codegen 工具消费
- **类型提示**：Pydantic 模型即数据结构文档

---

## 六、演示视频（10%）

完整分镜见 [`docs/demo-video-script.md`](docs/demo-video-script.md)。

**5 分钟精华版结构**：
- 0:00 开场社会问题
- 0:30 演示场景 1：拍照识药
- 1:30 演示场景 2：相互作用
- 2:30 演示场景 3：服药提醒
- 3:30 演示场景 4：语音问答
- 4:30 技术亮点 + CTA

---

## 七、加分项（不在评分表但会加分）

1. **真实部署** — 评委能看到线上版本（不是只有本地跑）
2. **PWA 安装演示** — 用真机扫二维码看到添加到主屏
3. **代码可读** — 中文注释覆盖所有非平凡逻辑
4. **个人赛完整性** — 个人能独立完成所有环节（前端 + 后端 + AI + 部署 + 文档）
5. **社会责任感** — 真实解决老年人群体痛点，并非炫技
