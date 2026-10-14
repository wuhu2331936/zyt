# 智药通 — 常见问题解答（FAQ）

> 评委 / 队友 / 用户在评审或使用中可能问到的问题。

---

## 关于项目

### Q1. 为什么做这个？
我妈妈今年 67 岁，每天要吃 5 种药。她找不到 / 看不清药盒说明，每次打电话问我，最后我做了这个。

### Q2. 为什么不直接用 ChatGPT 或文心一言？
- 通用 LLM 没有「药物说明书 RAG 检索」，容易给出错误信息
- 我们有 30 种老年常用药说明书向量库，每条风险都能追溯
- 适老化 UI（大字号 / 语音交互）通用 App 没有

### Q3. 数据隐私？
- 用药清单存 localStorage，不上云
- 拍照图片上传阿里云百炼识图，后端立即销毁
- 后端日志只记录必要 audit 信息，不存图

### Q4. 数据集为什么只有 30 种药？
- MVP 阶段验证技术路线足够
- 真实部署时可换成国家药监局公开数据（~17000 个药品）
- 替换方法见 [`docs/PRD.md`](PRD.md) §7

### Q5. AI 误识别怎么办？
- 强制显示"以药品说明书为准"
- 每条风险都可点击查看原文出处
- 风险分级（如 🔴 严禁）比单一开关更直观

---

## 关于技术

### Q6. 为什么用 FastAPI 而不是 Flask/Django？
- 异步性能 + 自动 OpenAPI + 类型安全
- 选 Vue3 是因为 Vant 移动端组件库成熟

### Q7. 为什么不用 GPT-4V 识图？
- 价格 5x + 网络稳定性差
- 通义千问 VL 中文药品包装识别率更高

### Q8. Edge-TTS 为什么免费？
- 微软官方公开的 Edge 浏览器 TTS 接口
- 不限量 / 不限速 / 6+ 种中文声音
- 唯一限制是商用要标注"由 Microsoft 提供"

### Q9. RAG 检索不到怎么办？
- 自动降级到 LLM 内置知识（llm_analyze 模式）
- 服务对此做了 try/except，自动选最优路径

---

## 关于部署

### Q10. 没有 API Key 能跑起来吗？
- 部分能：TTS、Swagger、/api/health 都可访问
- 识药 / 语音问答 / 相互作用必须填 API Key
- 评分时建议在演示视频中放真实交互演示

### Q11. Render 免费版够用吗？
- Starter $7/月起步，建议至少 starter（512MB 装 torch）
- 免费版会休眠，演示前手动热身

### Q12. PWA 装不上？
- 必须是 HTTPS（Vercel/Netlify 自动提供）
- 用户首次访问必须联网一次（Service Worker 预缓存）
- iOS Safari → 分享 → 添加到主屏

---

## 演示相关

### Q13. 演示视频太短 / 没做完？
- 看 [`docs/demo-video-script.md`](demo-video-script.md) 完整分镜
- 即使只有 5 分钟精华版也够比赛评分

### Q14. 评委想本地复现怎么办？
- 一次性脚本：`python scripts/bootstrap.py`
- 或按 `README.md` 步骤手动复现

### Q15. 真实部署地址？
- 见 README 顶部的 `🎬 在线演示`
- 比赛提交后回填

---

## 关于评分

### Q16. AI Prompt 快照在哪里？
- [`docs/ai-prompts/`](ai-prompts/) 三份：
  - `vl-recognition.md`（VL 识图）
  - `rag-interaction.md`（RAG 风险分析）
  - `voice-qa.md`（语音问答）

### Q17. 评分点对应？
- 见 [`SCORING.md`](../SCORING.md)

### Q18. 代码可以商用吗？
- MIT License（见 [LICENSE](../LICENSE)）
- 但 Edge-TTS 商用需注明"Microsoft 提供"
