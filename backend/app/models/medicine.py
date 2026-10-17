"""Pydantic 数据模型（阶段 2）"""
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ========== 识药（拍照识药 / 药品详情） ==========

class MedicineInfo(BaseModel):
    """单条药品信息（VL 识别结果 或 用户录入）"""
    name: str = Field(..., description="药品通用名，如'阿司匹林肠溶片'")
    spec: Optional[str] = Field(None, description="规格，如'100mg*30片'")
    manufacturer: Optional[str] = Field(None, description="生产厂家")
    usage: Optional[str] = Field(None, description="用法用量，如'口服，每次1片，每日3次'")
    indications: Optional[str] = Field(None, description="适应症")
    contraindications: Optional[str] = Field(None, description="禁忌")
    remarks: Optional[str] = Field(None, description="备注/警告")
    source: Literal["vl", "manual", "search", "demo"] = Field(
        "vl",
        description="数据来源：vl=拍照识别(真实调用成功), manual=手动添加, search=搜索, "
        "demo=演示/兜底示例数据（未配 Key 或真实调用失败，界面须明确标注，不可冒充 vl）",
    )


class RecognizeResponse(BaseModel):
    """识药接口返回"""
    success: bool
    medicine: Optional[MedicineInfo] = None
    raw_text: Optional[str] = Field(None, description="VL 模型原始输出，便于调试")
    error: Optional[str] = None


# ========== 药物相互作用 ==========

class InteractionRequest(BaseModel):
    """相互作用检查请求"""
    medicines: list[str] = Field(..., min_length=1, description="药品通用名列表")


class InteractionRisk(BaseModel):
    """单条风险项"""
    pair: list[str] = Field(..., description="互相作用的两药")
    level: Literal["critical", "major", "moderate", "minor"] = Field(
        ..., description="风险等级"
    )
    description: str = Field(..., description="风险描述")
    suggestion: str = Field(..., description="建议措施")


class InteractionResponse(BaseModel):
    """相互作用检查返回"""
    has_risk: bool
    risks: list[InteractionRisk] = []
    summary: str = Field("", description="整体概述（给老年人看的友好提示）")


# ========== 语音问答 / TTS ==========

class ChatRequest(BaseModel):
    """语音问答请求（已由前端 ASR 转文字）"""
    question: str = Field(..., min_length=1, max_length=500, description="用户问题")
    medicine_context: list[str] = Field(
        default_factory=list, description="当前用户的药品清单（用于上下文）"
    )
    history: list[dict] = Field(
        default_factory=list, description="对话历史 [{role, content}]"
    )


class ChatResponse(BaseModel):
    """语音问答返回"""
    answer: str = Field(..., description="模型回答（已优化为老年人友好的语气）")
    is_demo: bool = Field(
        False,
        description="True 表示 AI 不可用（未配 Key / 调用失败），当前是预置兜底回答，界面须标注",
    )


class TTSRequest(BaseModel):
    """TTS 请求"""
    text: str = Field(..., min_length=1, max_length=1000, description="要合成的文本")
    voice: Optional[str] = Field(None, description="Edge-TTS 声音，默认 zh-CN-XiaoxiaoNeural")
    rate: Optional[str] = Field(None, description="语速，如 '+10%'")