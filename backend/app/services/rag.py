"""RAG 服务（阶段 2 用 DeepSeek 兜底，阶段 4 接 ChromaDB）

阶段 4 会：
1. 读取国家药监局公开药品说明书 PDF/JSON；
2. 切分 + Embedding（BAAI/bge-small-zh）；
3. 写入 ChromaDB 持久化；
4. 检索时返回 Top-K 段落，再交给 DeepSeek 总结。

阶段 2 先用 LLM 内置知识做兜底，确保端到端可跑通。
"""
from __future__ import annotations

from app.services import deepseek


async def check_interactions(medicines: list[str]) -> dict:
    """检查药品相互作用

    阶段 2：直接调 DeepSeek 分析（基于其内置医学知识）
    阶段 4：先 ChromaDB 检索说明书 → 把相关段落塞进 Prompt → DeepSeek 总结
    """
    if len(medicines) < 2:
        return {
            "has_risk": False,
            "risks": [],
            "summary": "只用了一种药，暂时无法评估相互作用。",
        }
    return await deepseek.analyze_interactions(medicines)