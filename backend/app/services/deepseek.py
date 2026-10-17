"""DeepSeek 对话服务（语音问答 + 通用 RAG 兜底）

DeepSeek 兼容 OpenAI SDK，申请：https://platform.deepseek.com/
"""
from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings


def _is_demo() -> bool:
    """是否走演示模式：显式开启 DEMO_MODE，或未配置 DeepSeek Key"""
    return bool(settings.demo_mode) or not settings.deepseek_api_key


def _get_client() -> AsyncOpenAI:
    """获取异步 OpenAI 客户端（指向 DeepSeek）"""
    if not settings.deepseek_api_key:
        raise ValueError("DEEPSEEK_API_KEY 未配置，请在 backend/.env 中填写")
    return AsyncOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )


# ========== 演示模式：预置问答（关键词匹配，语气贴合老年人） ==========
_DEMO_ANSWERS: list[tuple[tuple[str, ...], str]] = [
    (
        ("怎么吃", "用法", "用量", "吃几片", "什么时候吃", "一天几次"),
        "您按说明书来就行：一般是每天固定时间吃一次，用温水整片送服，不要嚼碎。\n"
        "建议您把吃药和每天必做的事绑在一起（比如早饭后），就不容易忘。\n"
        "具体吃多少、吃几次，请以药盒说明和医生嘱咐为准。",
    ),
    (
        ("副作用", "不良反应", "有害", "伤身", "伤肝", "伤肾"),
        "常见的轻微反应有：口干、轻微头晕、胃肠道不舒服，多数人适应几天就好了。\n"
        "如果出现皮疹、明显乏力、尿色变深或持续不适，请马上停药并联系医生。\n"
        "长期服药建议定期复查肝肾功能。",
    ),
    (
        ("一起吃", "同时吃", "相互作用", "冲突", "能不能和", "搭配"),
        "几种药一起吃确实要留意。比如止痛药（布洛芬）和阿司匹林同服会增加胃出血风险；\n"
        "某些降压药和西柚汁也会影响药效。\n"
        "最稳妥的做法：把您所有在吃的药（含保健品）列给医生或药师看一次。",
    ),
    (
        ("忘记", "漏服", "忘了", "少吃", "多吃"),
        "想起来时如果离下次吃药还远，就补吃一次；\n"
        "如果已经快到下一次了，就跳过错过的那次，千万别一次吃两倍的量。\n"
        "经常忘记的话，可以用带闹钟的药盒，或者让家人帮忙提醒。",
    ),
    (
        ("饭前", "饭后", "空腹", "吃饭"),
        "多数药建议饭后吃，能减少对胃的刺激；\n"
        "但有的药（比如某些降压、降糖药）需要饭前空腹吃才吸收好。\n"
        "请以药盒上标注的为准，或者问问开药的医生。",
    ),
    (
        ("忌口", "注意", "不能吃", "饮食", "喝酒"),
        "服药期间尽量少喝酒，酒精会加重肝脏负担、也可能放大药效导致危险。\n"
        "另外西柚（葡萄柚）汁会影响不少药的代谢，服药期间最好别喝。\n"
        "饮食清淡、规律作息，药效会更稳定。",
    ),
]

_DEMO_ANSWER_DEFAULT = (
    "您问的这个问题我记下了。一般原则是：按时按量服药、不自行加减剂量、\n"
    "出现不适及时告诉医生。\n"
    "如果需要针对您个人情况的准确答复，建议带着药盒去咨询您的主治医生或社区药师。"
)


def _demo_answer(question: str) -> str:
    """演示模式：按关键词返回预置回答"""
    for keywords, answer in _DEMO_ANSWERS:
        if any(k in question for k in keywords):
            return answer
    return _DEMO_ANSWER_DEFAULT


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
    if _is_demo():
        return _demo_answer(question)

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

    try:
        response = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=messages,
            temperature=0.3,
            max_tokens=600,
        )
        return response.choices[0].message.content or ""
    except Exception as e:  # 余额不足 / 网络异常 / 模型不可用，均降级保证演示不中断
        print(f"[deepseek] 调用失败({e})，已降级为演示回答")
        return _demo_answer(question)


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


# ========== 演示模式：预置相互作用规则 ==========
_DEMO_RISK_RULES: list[dict] = [
    {
        "a": ("阿司匹林", "氯吡格雷", "华法林", "利伐沙班"),
        "b": ("布洛芬", "萘普生", "双氯芬酸", "洛索洛芬"),
        "level": "major",
        "level_cn": "较严重",
        "description": "抗血小板/抗凝药与非甾体抗炎药同服，会明显增加胃肠道出血风险。",
        "suggestion": "尽量避免合用。确需止痛可改用对乙酰氨基酚，并咨询医生是否需要加用胃黏膜保护剂。",
    },
    {
        "a": ("阿托伐他汀", "瑞舒伐他汀", "辛伐他汀", "他汀"),
        "b": ("红霉素", "克拉霉素", "伊曲康唑", "氟康唑"),
        "level": "major",
        "level_cn": "较严重",
        "description": "部分抗生素/抗真菌药会抑制他汀代谢，使血药浓度升高，增加肌病和横纹肌溶解风险。",
        "suggestion": "合用期间如出现肌肉酸痛、乏力、尿色变深，应立即停药就医；必要时由医生临时调整他汀剂量。",
    },
    {
        "a": ("氨氯地平", "硝苯地平", "非洛地平"),
        "b": ("西地那非", "他达拉非"),
        "level": "moderate",
        "level_cn": "中等",
        "description": "两类药都有扩张血管作用，同服可能导致血压降得过低，出现头晕、乏力。",
        "suggestion": "如需合用请间隔时间并监测血压，起身时动作放缓，避免跌倒。",
    },
    {
        "a": ("氨氯地平", "硝苯地平", "依那普利", "缬沙坦", "美托洛尔"),
        "b": ("螺内酯", "氢氯噻嗪", "呋塞米"),
        "level": "minor",
        "level_cn": "轻微",
        "description": "降压药与利尿剂联用是常见方案，但初期可能降压过猛或引起电解质波动。",
        "suggestion": "按医嘱服用即可，建议定期复查血压与血钾，起床时慢一点防止体位性低血压。",
    },
]


def _demo_interactions(medicines: list[str]) -> dict:
    """演示模式：按预置规则匹配风险，保证多药场景下有可展示的结果"""
    risks: list[dict] = []
    joined = medicines

    for rule in _DEMO_RISK_RULES:
        hits_a = [m for m in joined if any(k in m for k in rule["a"])]
        hits_b = [m for m in joined if any(k in m for k in rule["b"])]
        if hits_a and hits_b:
            risks.append(
                {
                    "pair": [hits_a[0], hits_b[0]],
                    "level": rule["level"],
                    "level_cn": rule["level_cn"],
                    "description": rule["description"],
                    "suggestion": rule["suggestion"],
                }
            )

    if risks:
        worst = min(
            risks,
            key=lambda r: ["critical", "major", "moderate", "minor"].index(r["level"]),
        )
        return {
            "has_risk": True,
            "risks": risks,
            "summary": f"您目前的用药里有 {len(risks)} 处需要留意的组合，"
            f"其中最需要注意的是「{worst['pair'][0]}」和「{worst['pair'][1]}」，"
            f"属于{worst['level_cn']}程度。建议把这张清单给医生或药师看一下。",
        }

    if len(medicines) >= 2:
        return {
            "has_risk": False,
            "risks": [],
            "summary": f"您目前在用的 {len(medicines)} 种药，按预置规则未发现明显相互作用。"
            "不过每个人情况不同，复诊时记得把完整用药清单带给医生。",
        }

    return {
        "has_risk": False,
        "risks": [],
        "summary": "目前只有一种药，暂时不存在药物相互作用问题。记得按时服用。",
    }


async def analyze_interactions(medicines: list[str]) -> dict:
    """让 DeepSeek 直接分析药品相互作用（阶段 2 简化方案）

    阶段 4 会替换为 ChromaDB RAG 检索 + LLM 总结的更精准方案。
    这里先用 LLM 的内置知识做兜底，确保阶段 2 可跑通。
    """
    if _is_demo():
        return _demo_interactions(medicines)

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
    try:
        return await _complete_json(
            system="你是资深药师，擅长分析药物相互作用。请严格按照 JSON 格式输出。",
            user=prompt,
            temperature=0.1,
            max_tokens=1000,
        )
    except Exception as e:  # 余额不足 / 网络异常时降级，避免整个页面报错
        print(f"[deepseek] 相互作用分析失败({e})，已降级为演示数据")
        return _demo_interactions(medicines)