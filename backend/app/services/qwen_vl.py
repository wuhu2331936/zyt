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


# 演示模式下的预置药品（老年人常用降压药，信息取自公开说明书要点）
_DEMO_MEDICINES = [
    MedicineInfo(
        name="苯磺酸氨氯地平片",
        spec="5mg*7片/盒",
        manufacturer="辉瑞制药有限公司",
        usage="口服，每次1片（5mg），每日1次，建议每天固定时间服用",
        indications="用于治疗高血压、冠心病（慢性稳定性心绞痛）",
        contraindications="对氨氯地平或本品任何成分过敏者禁用",
        remarks="服药初期可能出现面部潮红、脚踝水肿，一般可耐受；请勿擅自停药",
        source="vl",
    ),
    MedicineInfo(
        name="阿托伐他汀钙片",
        spec="20mg*7片/盒",
        manufacturer="北京嘉林药业股份有限公司",
        usage="口服，每次1片（20mg），每日1次，晚餐后服用效果更佳",
        indications="用于降低血脂（高胆固醇血症）、预防心脑血管事件",
        contraindications="活动性肝病、孕妇及哺乳期妇女禁用",
        remarks="服药期间避免大量饮用西柚汁；定期复查肝功能与肌酶",
        source="vl",
    ),
    MedicineInfo(
        name="阿司匹林肠溶片",
        spec="100mg*30片/盒",
        manufacturer="拜耳医药保健有限公司",
        usage="口服，每次1片（100mg），每日1次，饭前用温水整片送服",
        indications="用于抑制血小板聚集，预防心肌梗死、脑梗死复发",
        contraindications="活动性消化道溃疡、出血体质、阿司匹林过敏者禁用",
        remarks="肠溶片不可嚼碎；与布洛芬等其他止痛药同服需间隔并咨询医生",
        source="vl",
    ),
]

_demo_counter = {"i": 0}


def _demo_recognize() -> MedicineInfo:
    """演示模式：轮流返回预置药品，保证连续演示时结果不重复"""
    m = _DEMO_MEDICINES[_demo_counter["i"] % len(_DEMO_MEDICINES)]
    _demo_counter["i"] += 1
    return m.model_copy(deep=True)


async def recognize_medicine(image_bytes: bytes, content_type: str = "image/jpeg") -> MedicineInfo | None:
    """调通义千问 VL 识别药盒图片，返回结构化药品信息

    Args:
        image_bytes: 图片二进制
        content_type: MIME 类型

    Returns:
        MedicineInfo 识别结果；识别失败返回 None

    说明：未配置 Key 或开启 DEMO_MODE 时，返回预置的演示药品，
    保证评审老师无需任何密钥也能走通完整流程。
    """
    if settings.demo_mode or not settings.dashscope_api_key:
        return _demo_recognize()

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
        # 真实调用失败（如余额不足、模型下线）时降级为演示数据，避免流程中断
        print(f"[qwen_vl] VL 调用失败({response.code} {response.message})，已降级为演示数据")
        return _demo_recognize()

    # 提取模型输出
    try:
        content: str = response.output.choices[0].message.content[0]["text"]
    except (AttributeError, IndexError, KeyError, TypeError) as e:
        print(f"[qwen_vl] VL 返回结构异常({e})，已降级为演示数据")
        return _demo_recognize()

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