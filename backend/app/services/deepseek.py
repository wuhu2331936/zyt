"""DeepSeek 对话服务（语音问答 + 通用 RAG 兜底）

DeepSeek 兼容 OpenAI SDK，申请：https://platform.deepseek.com/
"""
from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings


def _get_client() -> AsyncOpenAI:
    """获取异步 OpenAI 客户端（指向 DeepSeek）"""
    if not settings.deepseek_api_key:
        raise ValueError("DEEPSEEK_API_KEY 未配置，请在 backend/.env 中填写")
    return AsyncOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )


# 系统提示词 —— 让模型语气更适合老年人（简洁、温和、有耐心）
SYSTEM_PROMPT = """你是一名耐心的社区医院药师，正在和一位老年患者对话。
回答要求：
1. 用通俗易懂的中文，**避免专业医学术语**（必要时用比喻解释）；
2. 每次回答控制在 150 字以内，分点列出更清晰；
3. 涉及具体用药建议时，加一句「具体请咨询您的主治医生」；
4. 不要编造药品说明书内容；如果你不知道，就诚实说不知道；
5. 称呼对方用「您」。

你的职责范围：
- 解释用法用量、不良反应、注意事项；
- 提醒常见药物相互作用风险；
- 回答一般性用药疑问。

你的禁区：
- 不能替代医生诊断；
- 不能开处方；
- 不能建议停用处方药；
- 涉及急症请建议立即拨打 120。"""


async def chat(
    question: str,
    medicine_context: list[str] | None = None,
    history: list[dict[str, str]] | None = None,
) -> str:
    """与 DeepSeek 对话

    Args:
        question: 用户问题
        medicine_context: 当前用户的药品清单（注入上下文）
        history: 对话历史 [{"role":"user/assistant","content":"..."}]

    Returns:
        模型回答文本
    """
    client = _get_client()

    # 构造 messages
    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # 注入用户当前药品上下文
    if medicine_context:
        ctx = "、".join(medicine_context)
        messages.append(
            {
                "role": "system",
                "content": f"【用户当前用药清单】{ctx}。回答时请考虑这些药物之间的相互影响。",
            }
        )

    # 注入历史
    if history:
        # 只取最近 6 条避免超长
        for h in history[-6:]:
            if "role" in h and "content" in h:
                messages.append({"role": h["role"], "content": h["content"]})

    messages.append({"role": "user", "content": question})

    response = await client.chat.completions.create(
        model=settings.deepseek_model,
        messages=messages,
        temperature=0.3,
        max_tokens=600,
    )

    return response.choices[0].message.content or ""


def _safe_json_loads(text: str) -> dict:
    """从模型输出里稳健抠出 JSON（容忍 ```json 围栏）"""
    import json
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(line for line in lines if not line.strip().startswith("```"))
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return {}


async def _complete_json(
    system: str,
    user: str,
    temperature: float = 0.2,
    max_tokens: int = 1200,
) -> dict:
    """通用 JSON 模式调用：返回 dict（自动剥离 markdown 围栏）"""
    client = _get_client()
    response = await client.chat.completions.create(
        model=settings.deepseek_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    text = response.choices[0].message.content or "{}"
    parsed = _safe_json_loads(text)
    return parsed or {"has_risk": False, "risks": [], "summary": "模型返回解析失败"}


async def analyze_interactions(medicines: list[str]) -> dict:
    """让 DeepSeek 直接分析药品相互作用（阶段 2 简化方案）

    阶段 4 会替换为 ChromaDB RAG 检索 + LLM 总结的更精准方案。
    这里先用 LLM 的内置知识做兜底，确保阶段 2 可跑通。
    """
    prompt = f"""请分析以下药物组合之间是否存在相互作用风险，并按以下 **严格 JSON 格式** 返回（不要任何多余文字、不要 markdown 代码块）：

药品列表：{chr(10).join(f"- {m}" for m in medicines)}

JSON Schema:
{{
  "has_risk": true/false,
  "risks": [
    {{
      "pair": ["药品A", "药品B"],
      "level": "critical|major|moderate|minor",
      "level_cn": "严禁/较严重/中等/轻微",
      "description": "作用机制简述",
      "suggestion": "建议措施"
    }}
  ],
  "summary": "整体概述，1-2句话，友好提示"
}}

若不存在明显相互作用，has_risk 设为 false，risks 为空数组。"""
    return await _complete_json(
        system="你是资深药师，擅长分析药物相互作用。请严格按照 JSON 格式输出。",
        user=prompt,
        temperature=0.1,
        max_tokens=1000,
    )