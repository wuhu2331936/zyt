"""药品知识补全服务（拍照识药的第二阶段）

第一阶段（qwen_vl）只负责"看图识字"——把药盒上印的内容读出来，
很多药盒并不印适应症、不良反应、禁忌等，字段会是空的。

本模块做第二阶段：把识别到的真实药名交给 DeepSeek，
按通用名补一份**说明书级别的结构化解读**（成分/适应症/不良反应/
禁忌/老年人注意/相互作用/漏服处理/储存 + 大白话总结），
让"拍一张照"得到的信息量接近用药说明书，而不只是药盒印刷内容。

安全边界：只做科普，不开处方、不建议停药，急症引导就医。
"""
from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings
from app.models.medicine import MedicineInfo

_SYSTEM_PROMPT = """你是面向中国老年人的临床药师。用户给你一个药品名称（可能还有药盒上的规格/厂家），
请你输出该药品的**结构化用药说明**，要求：

1. 只返回 JSON，不要 markdown 代码块，不要任何解释文字。
2. 面向老年人：语言通俗，句子短，能不用术语就不用；必须说明"什么时候要去看医生"。
3. 不确定的内容写 null，**绝对不要编造具体剂量**；剂量上只复述常规用法并强调"以药盒和医生为准"。
4. 不开处方、不建议自行停药或加药；涉及急症请提示立即拨打 120。

JSON 字段（全部字符串或 null）：
{
  "ingredients": "主要成分（通用名 + 常见商品名举例）",
  "indications": "这个药治什么（通俗说法）",
  "usage": "一般怎么吃（常规用法，并注明以药盒/医嘱为准）",
  "adverse_reactions": "可能出现的不良反应",
  "contraindications": "什么人不能吃/要慎用",
  "elderly_notes": "老年人特别注意（肝肾功能、体位性低血压、跌倒风险等）",
  "interactions": "与常见慢性病药物（降压药、阿司匹林、降糖药等）的相互作用提醒",
  "missed_dose": "漏服了怎么办",
  "storage": "怎么保存",
  "summary": "一段 120 字以内的大白话总结，像药师当面叮嘱那样说话"
}"""

_USER_TMPL = """药品名称：{name}
规格：{spec}
生产厂家：{manufacturer}

请按系统要求输出该药品的结构化用药说明 JSON。"""


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )


def _safe_json(text: str) -> dict[str, Any]:
    """从模型输出里抠出 JSON（容忍 ``` 包裹和前后废话）"""
    t = text.strip()
    if t.startswith("```"):
        t = "\n".join(l for l in t.splitlines() if not l.strip().startswith("```"))
    for candidate in (t,):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    start, end = t.find("{"), t.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(t[start : end + 1])
        except json.JSONDecodeError:
            pass
    return {}


async def enrich_medicine(med: MedicineInfo) -> MedicineInfo:
    """用药名向 DeepSeek 补全说明书级信息（原地补充，不覆盖药盒上的真实字段）

    药盒上真实读到的 spec / manufacturer / usage 优先级最高，只在为空时才用
    模型补全的内容填上。调用失败时静默返回原对象，保证识药流程不受影响。
    """
    if not settings.deepseek_api_key or not med.name:
        return med

    try:
        client = _client()
        resp = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _USER_TMPL.format(
                        name=med.name,
                        spec=med.spec or "未知",
                        manufacturer=med.manufacturer or "未知",
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=1200,
        )
        content = resp.choices[0].message.content or ""
    except Exception as e:
        print(f"[medicine_knowledge] 知识补全失败({e})，保留药盒识别结果")
        return med

    data = _safe_json(content)
    if not data:
        print(f"[medicine_knowledge] JSON 解析失败，原始输出: {content[:200]}")
        return med

    def pick(key: str) -> str | None:
        v = data.get(key)
        if isinstance(v, str) and v.strip() and v.strip().lower() != "null":
            return v.strip()
        return None

    # 药盒真实数据优先：为空才补
    med.ingredients = med.ingredients or pick("ingredients")
    med.indications = med.indications or pick("indications")
    med.usage = med.usage or pick("usage")
    med.contraindications = med.contraindications or pick("contraindications")

    # 药盒上通常没有的字段，直接补
    med.adverse_reactions = pick("adverse_reactions")
    med.elderly_notes = pick("elderly_notes")
    med.interactions = pick("interactions")
    med.missed_dose = pick("missed_dose")
    med.storage = pick("storage")
    med.summary = pick("summary")

    return med
