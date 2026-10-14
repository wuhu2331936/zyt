# 📷 通义千问 VL 识药 Prompt 快照

> 文件位置：`docs/ai-prompts/vl-recognition.md`
> 生成时间：阶段 4 完稿
> 适用接口：`POST /api/medicine/recognize`
> 模型：`qwen-vl-plus`

---

## 完整 Prompt（系统提示 + 用户输入）

### 系统提示
```
你是一名资深药师。请仔细观察这张药品包装照片，
识别出以下信息并以 **严格的 JSON 格式** 返回（不要任何多余文字、不要 markdown 代码块）：

{
  "name": "药品通用名（如'阿司匹林肠溶片'，必须包含剂型）",
  "spec": "规格（如'100mg*30片'，若看不清写 null）",
  "manufacturer": "生产厂家（若看不清写 null）",
  "usage": "用法用量（如'口服，每次1片，每日3次'，若包装未显示写 null）",
  "indications": "适应症（简明扼要）",
  "contraindications": "禁忌（关键信息）",
  "remarks": "其他注意事项（如'孕妇慎用'等）"
}

如果图片不是药品包装（如风景、人物、动物），请返回：{"error": "非药品图片"}
```

### 用户输入（消息内容）
- **第一项**：`{"image": "data:image/jpeg;base64,<base64编码的药盒照片>"}`
- **第二项**：`{"text": "<上方系统提示>"}`

---

## 典型调用示例

```python
import base64
from dashscope import MultiModalConversation

with open("aspirin.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

response = MultiModalConversation.call(
    model="qwen-vl-plus",
    messages=[{
        "role": "user",
        "content": [
            {"image": f"data:image/jpeg;base64,{image_b64}"},
            {"text": "<上方系统提示>"},
        ],
    }],
    result_format="message",
)
```

---

## 典型输出（成功）

```json
{
  "name": "阿司匹林肠溶片",
  "spec": "100mg*30片",
  "manufacturer": "拜耳医药保健",
  "usage": "口服，每次1片，每日1次",
  "indications": "预防心肌梗死、缺血性卒中",
  "contraindications": "活动性消化道溃疡患者禁用",
  "remarks": "餐前30分钟空腹服用"
}
```

## 典型输出（图片无效）

```json
{"error": "非药品图片"}
```

---

## 设计要点

1. **强制 JSON 输出**：避免后续解析问题
2. **明确字段语义**：每个字段给出例子（如 "name" 强调必须含剂型）
3. **失败兜底**：明确要求非药品返回 `{"error": "..."}`
4. **隐私保护**：图片 base64 内联传输，无需额外存储

## 容错处理（后端 `_safe_json_parse`）

- 自动剥离 markdown 围栏（```json ... ```）
- 从字符串首尾抠出首个 `{...}`
- 三次失败返回 `{"error": "JSON 解析失败"}`

---

## 比赛演示要点

- ✅ 展示上传清晰药盒 → 1-2 秒返回结构化信息
- ✅ 展示上传错误图片（如猫）→ 友好提示
- ✅ 强调"老年人友好"：所有文字放大、可语音播报