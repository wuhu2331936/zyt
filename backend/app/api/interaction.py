"""药物相互作用检查路由"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.medicine import (
    InteractionRequest,
    InteractionResponse,
    InteractionRisk,
)
from app.services import rag

router = APIRouter()


@router.post("/check", response_model=InteractionResponse, summary="检查多种药物相互作用")
async def check_interaction(req: InteractionRequest):
    """接收药品列表 → RAG/LLM 分析 → 返回风险列表

    前端调用：用户添加多种药品到清单后，前端调用此接口展示风险卡片。
    """
    if not req.medicines:
        raise HTTPException(status_code=400, detail="药品列表不能为空")

    # 去重 + 去掉空字符串
    unique = [m.strip() for m in req.medicines if m and m.strip()]
    if not unique:
        raise HTTPException(status_code=400, detail="药品列表为空")

    try:
        result = await rag.check_interactions(unique)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"相互作用分析失败: {e}")

    # 把字典转换为 InteractionRisk 对象
    risks: list[InteractionRisk] = []
    for r in result.get("risks", []):
        try:
            risks.append(
                InteractionRisk(
                    pair=r.get("pair", []),
                    level=r.get("level", "moderate"),
                    description=r.get("description", ""),
                    suggestion=r.get("suggestion", ""),
                )
            )
        except Exception:
            # 跳过解析失败的项
            continue

    return InteractionResponse(
        has_risk=result.get("has_risk", len(risks) > 0),
        risks=risks,
        summary=result.get("summary", ""),
    )