# AI 协同开发全过程记录（Prompt 链快照）

> 本文档记录智药通开发过程中，3 个核心功能迭代时与 AI 的**完整交互链**：
> 我的原始提问 → AI 的实现/修改建议 → 我如何引导 AI 修复 Bug。
> 配套的单点提示词设计细节见同目录 `vl-recognition.md` / `rag-interaction.md` / `voice-qa.md`。

---

## 链条一：拍照识药 —— 让通义千问 VL 输出稳定 JSON

### 第 1 轮：我的提问（功能落地）

> 我用 FastAPI 写了一个拍照识药接口，接收药盒图片后调用阿里云百炼的通义千问 VL。请帮我写 qwen_vl.py 服务：
> 1. 图片转 base64 传入，用 OpenAI 兼容模式调用；
> 2. 让模型识别药品名、规格、用法用量、注意事项，**返回严格 JSON**，字段固定为 name/brand/specification/indication/dosage/frequency/precautions/confidence；
> 3. 异步实现，加中文注释。

**AI 产出**：完整的 `app/services/qwen_vl.py`，含 base64 编码、messages 构造、JSON 提示词模板。commit：`feat(backend): add 4 core APIs for stage 2`。

### 第 2 轮：发现 Bug（AI 自查建议）

我实测 3 张药盒照片，其中 2 张解析失败。把报错贴回给 AI：

> 调用返回的文本是 ```json\n{...}\n``` 这样带 markdown 围栏的，我直接 json.loads 就抛 JSONDecodeError。怎么修？

**AI 修改建议**：① 在提示词末尾追加硬约束"不要任何多余文字、不要 markdown 代码块"；② 增加 `_safe_json_parse` 容错函数——先剥 ``` 围栏，再正则提取首个 `{...}` 块，仍失败返回 None。

**我的引导追问**：

> 兜底返回 None 的话前端会白屏。改成返回一个结构相同的降级对象（name 为空 + error 字段），让前端能提示"识别失败请重试"。

**AI 产出**：降级结构 `{"name": "", "confidence": 0, "error": "parse_failed"}`，接口 HTTP 恒为 200。

### 第 3 轮：边界情况（置信度）

> 低置信度时我不想直接展示错误信息误导老人。让模型多返回一个 confidence 字段（0-100），低于 60 我在前端提示"请手动确认信息"。

**结果**：提示词追加置信度定义与评分标准；前端 ScanView 增加黄色确认条。此链对应仓库 commit `a3d395e`。

---

## 链条二：药物相互作用 —— RAG 检索的"抗噪"设计

### 第 1 轮：我的提问（RAG 升级）

> 阶段 2 的相互作用检查是直接问 DeepSeek， hallucination 风险高。我已用 ChromaDB + bge-small-zh 建了 30 种老年常用药说明书向量库。请重写 rag.py：检索 Top-4 相关说明书片段，拼进提示词让 DeepSeek 只依据片段+药学知识输出风险 JSON，格式为 has_risk/risks(pair/level/description/suggestion)/summary。

**AI 产出**：`app/services/rag.py`（延迟加载 ChromaDB、lru_cache 单例、Top-4 检索、Prompt 拼接），并同步修改 `interaction.py` 路由。commit：`feat(backend): add RAG vector store + AI integration docs (stage 4)`。

### 第 2 轮：发现 Bug（检索噪声污染回答）

我测试"氨氯地平+氨糖软骨素"（两者无相互作用），AI 却输出了一条中等级风险。排查发现向量库召回了不相关片段（氨基比林），模型被噪声带偏。我把检索结果和错误回答贴给 AI：

> 召回的第 3 条片段跟查询药品完全无关，模型却把它当成了依据。提示词要怎么改才能忽略无关片段？

**AI 修改建议**：① 提示词显式加一句"若片段与问题中的药品无关，请忽略该片段"；② 每个片段前加【片段N】编号并要求模型引用编号，便于溯源；③ 返回体增加 `source` 字段标注结论来自 "rag" 还是 "model_builtin"。

**我的引导追问**：

> 另外向量库没构建时（比如评委首次部署忘了跑脚本）接口会直接 500。加一个 try/except：加载失败就降级为纯模型分析，source 标 model_builtin，接口永不报错。

**AI 产出**：降级逻辑 + 启动日志提示"向量库未找到，已降级"。修复后"氨氯地平+氨糖软骨素"正确返回 has_risk=false；"华法林+阿司匹林"正确返回严禁级风险。

---

## 链条三：语音问答 —— 修复 Edge-TTS 超时

### 第 1 轮：我的提问（TTS 服务）

> 请写 tts.py：接收文本，用 edge-tts 合成 mp3 直接以 audio/mpeg 响应返回，不要落盘临时文件。音色从环境变量读，默认晓晓。

**AI 产出**：`app/services/tts.py`（异步合成、内存 BytesIO 流式响应）+ `/api/voice/tts` 路由 + 音色列表接口。

### 第 2 轮：发现 Bug（首次调用偶发超时）

演示时首次合成经常 8~10 秒才出声，第二次就快。我让 AI 分析：

> edge-tts 第一次调用很慢、第二次快，是什么原因？怎么把首次延迟降下来？

**AI 修改建议**：首次调用包含 TLS 握手与 WebSocket 连接建立，耗时集中在建连。① 全局复用一个 `Communicator`/连接（模块级单例）；② 加 `asyncio.wait_for` 10 秒超时 + 1 次重试；③ 前端在"按住说话"时就**预请求**一段静音 TTS 预热连接（对用户无感）。

**我的引导追问**：

> 复用连接要小心并发：两个请求同时用同一个连接会串音吗？如果会，用 asyncio.Lock 串行化，或者干脆维护一个小的连接池。

**AI 产出**：`_get_communicator()` 单例 + `asyncio.Lock` 防并发串音 + 超时重试；前端 VoiceQAView 增加页面加载时静音预热。实测首次播报延迟从 ~9s 降到 ~2s。

### 第 3 轮：体验细节（播报清洗）

> 回答里的 markdown 符号（*、#、表格线）会被 TTS 读出来很难听。合成前先清洗文本。

**AI 产出**：`_clean_text_for_speech()` 正则清洗（去 md 符号/表格符/多余空白），TTS 播报自然度显著提升。

---

## 复现提示（评委可验证）

- 上述三条链对应的代码均可在仓库对应 commit diff 中验证；
- 服务层源码注释保留了 `_safe_json_parse`、降级 source 标记、`asyncio.Lock` 等关键决策点；
- 演示视频第 6 幕将现场复现"片段二"的完整交互过程（≥2 分钟）。
