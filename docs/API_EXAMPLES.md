# API 调用示例（curl）

> 提交比赛时方便评委一行命令验证后端功能。
> 前置：后端已启动（uvicorn） + .env 已填 API Key。

## 健康检查（无需 Key）

```bash
curl http://localhost:8000/api/health
# {"status":"ok","version":"0.3.0"}
```

## 1. 拍照识药（通义千问 VL）

需要真实药盒照片，假设保存在 `./medicine.jpg`：

```bash
curl -X POST http://localhost:8000/api/medicine/recognize \
  -F "image=@./medicine.jpg" \
  -H "Accept: application/json"
```

返回示例：

```json
{
  "success": true,
  "medicine": {
    "name": "氨氯地平片",
    "brand_name": "络活喜",
    "spec": "5mg × 7 片",
    "usage": "口服，每日 1 次 1 片，饭后",
    "warnings": ["可能会出现脚踝水肿", "不可与柚子同服"],
    "confidence": 0.94
  }
}
```

## 2. 药物相互作用（DeepSeek + RAG）

```bash
curl -X POST http://localhost:8000/api/interaction/check \
  -H "Content-Type: application/json" \
  -d '{
    "medicines": ["华法林", "阿司匹林", "氨氯地平"]
  }'
```

返回示例：

```json
{
  "has_risk": true,
  "risks": [
    {
      "pair": ["华法林", "阿司匹林"],
      "level": "critical",
      "level_cn": "严禁",
      "description": "两者均可抑制血小板聚集，叠加使用显著增加胃出血风险。",
      "suggestion": "改用对乙酰氨基酚（泰诺）替代。"
    }
  ],
  "summary": "⚠️ 检测到 1 条严禁同服组合，1 条轻微相互作用。请咨询医生调整用药方案。"
}
```

## 3. 语音问答（DeepSeek）

```bash
curl -X POST http://localhost:8000/api/voice/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "高血压的人能吃布洛芬吗？",
    "context": ["氨氯地平片 5mg"]
  }'
```

返回示例：

```json
{
  "answer": "高血压长期患者服用布洛芬可能影响降压效果，建议改用对乙酰氨基酚。若有不适请立即咨询医生。",
  "tokens": 78,
  "model": "deepseek-chat"
}
```

## 4. Edge-TTS（无需 Key）

```bash
curl -X POST http://localhost:8000/api/voice/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"该吃氨氯地平片了，饭后服用哦","voice":"zh-CN-XiaoxiaoNeural"}' \
  -o tts_output.mp3

# 播放
# macOS: afplay tts_output.mp3
# Windows: start tts_output.mp3
# Linux: mpg123 tts_output.mp3
```

## 5. TTS 声音列表

```bash
curl http://localhost:8000/api/voice/voices
```

返回示例：

```json
{
  "voices": [
    {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓（女·温柔）", "gender": "female"},
    {"id": "zh-CN-YunxiNeural",   "name": "云希（男·青年）", "gender": "male"},
    {"id": "zh-CN-YunyangNeural", "name": "云扬（男·播报）", "gender": "male"},
    {"id": "zh-CN-XiaoyiNeural",  "name": "晓伊（女·儿童）", "gender": "female"},
    {"id": "zh-CN-XiaomengNeural","name": "晓梦（女·老年）", "gender": "female"}
  ]
}
```

## 完整 E2E 测试脚本

```bash
#!/bin/bash
set -e

API=http://localhost:8000

echo "=== 1. 健康检查 ==="
curl -fs $API/api/health && echo

echo "=== 2. TTS（无需 Key） ==="
curl -fs -X POST $API/api/voice/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"你好，智药通为您服务"}' \
  -o /tmp/zhiyaotong.mp3 && echo "  ✓ mp3 大小: $(stat -c%s /tmp/zhiyaotong.mp3) bytes"

echo "=== 3. 声音列表 ==="
curl -fs $API/api/voice/voices | python -m json.tool | head -10

echo "=== 4. 相互作用（需 DASHSCOPE_API_KEY） ==="
curl -fs -X POST $API/api/interaction/check \
  -H "Content-Type: application/json" \
  -d '{"medicines":["华法林","阿司匹林"]}' | python -m json.tool

echo "✅ E2E 测试完成"
```

---

## 移动端调试

iOS Safari:
- 设置 → Safari → 高级 → Web 检查器 → 打开
- Mac 启动 Safari → 开发 → [你的设备] → 选择页面

Android Chrome:
- 桌面 Chrome → chrome://inspect/#devices
- USB 调试开启后即可调试 PWA
