"""阿里云百炼 通义千问 VL 服务（识图）

用于「拍照识药」：接收药盒照片 → 提取药品名/用法/规格/厂家/适应症等。
申请 Key：https://bailian.console.aliyun.com/
"""
from __future__ import annotations

import base64
import json
from typing import Any

import dashscope
from dashscope import MultiModalConversation

from app.core.config import settings
from app.models.medicine import MedicineInfo

# 显式设置 Key（dashscope SDK 也会自动读环境变量，显式设置更稳）
dashscope.api_key = settings.dashscope_api_key

# 提示词模板 —— 强制 JSON 输出，便于解析
_VL_PROMPT = """你是一名资深药师。请仔细观察这张药品包装照片，
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

如果图片不是药品包装（如风景、人物、动物），请返回：{"error": "非药品图片"}"""


async def recognize_medicine(image_bytes: bytes, content_type: str = "image/jpeg") -> MedicineInfo | None:
    """调通义千问 VL 识别药盒图片，返回结构化药品信息

    Args:
        image_bytes: 图片二进制
        content_type: MIME 类型

    Returns:
        MedicineInfo 识别结果；识别失败返回 None
    """
    if not settings.dashscope_api_key:
        raise ValueError("DASHSCOPE_API_KEY 未配置，请在 backend/.env 中填写")

    # 转为 base64 data URI
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_uri = f"data:{content_type};base64,{b64}"

    # 调用 DashScope 多模态对话
    response = MultiModalConversation.call(
        model=settings.qwen_vl_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"image": data_uri},
                    {"text": _VL_PROMPT},
                ],
            }
        ],
        result_format="message",
    )

    if response.status_code != 200:
        raise RuntimeError(f"VL 调用失败: {response.code} - {response.message}")

    # 提取模型输出
    try:
        content: str = response.output.choices[0].message.content[0]["text"]
    except (AttributeError, IndexError, KeyError, TypeError) as e:
        raise RuntimeError(f"VL 返回结构异常: {e}")

    # 解析 JSON（模型偶发会包 markdown ``` ```，先剥掉）
    parsed: dict[str, Any] = _safe_json_parse(content)
    if "error" in parsed:
        return None

    return MedicineInfo(
        name=parsed.get("name", ""),
        spec=parsed.get("spec"),
        manufacturer=parsed.get("manufacturer"),
        usage=parsed.get("usage"),
        indications=parsed.get("indications"),
        contraindications=parsed.get("contraindications"),
        remarks=parsed.get("remarks"),
        source="vl",
    )


def _safe_json_parse(text: str) -> dict:
    """尝试从模型输出里抠出 JSON（容忍 ```json 包裹、前后杂物）"""
    text = text.strip()

    # 去掉代码块围栏
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(
            line for line in lines if not line.strip().startswith("```")
        )

    # 直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 从第一个 { 到最后一个 } 截取再试
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    return {"error": "JSON 解析失败", "raw": text}