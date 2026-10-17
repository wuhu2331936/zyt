"""语音问答 + TTS 路由"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.models.medicine import ChatRequest, ChatResponse, TTSRequest
from app.services import deepseek, tts

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse, summary="用药问答（DeepSeek）")
async def voice_chat(req: ChatRequest):
    """接收用户问题 → 返回用药助手回答

    前端流程：按住说话 → Web Speech API / 讯飞 ASR 转文字 → 调此接口 → 用 Edge-TTS 播报
    """
    try:
        answer, is_demo = await deepseek.chat_with_meta(
            question=req.question,
            medicine_context=req.medicine_context,
            history=req.history,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话服务失败: {e}")

    return ChatResponse(answer=answer, is_demo=is_demo)


@router.post("/tts", summary="文字转语音（Edge-TTS）")
async def text_to_speech(req: TTSRequest):
    """接收文本 → 返回 mp3 音频流

    Content-Type: audio/mpeg

    ⚠️ 服务端合成失败（微软接口 403 / 网络受限 / 依赖异常）时**不再返回 500**，
    而是返回 `204 No Content` + `X-TTS-Fallback: browser`，语义是
    「服务端没有音频，请用浏览器内置语音播报」。
    老人端最怕看到「请求失败 500」这种红色报错，静音降级体验更好。
    """
    try:
        audio = await tts.synthesize_speech(
            text=req.text,
            voice=req.voice,
            rate=req.rate,
        )
    except Exception as e:
        logger.warning("Edge-TTS 合成失败，降级为浏览器语音: %s", e)
        return Response(status_code=204, headers={"X-TTS-Fallback": "browser"})

    if not audio:
        logger.warning("Edge-TTS 返回空音频，降级为浏览器语音")
        return Response(status_code=204, headers={"X-TTS-Fallback": "browser"})

    return Response(
        content=audio,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": 'inline; filename="tts.mp3"',
            "Cache-Control": "public, max-age=3600",  # 缓存 1 小时
        },
    )


@router.get("/voices", summary="获取可选 TTS 声音列表")
async def list_voices():
    """供前端「提醒设置页」选择语音"""
    return {"voices": tts.AVAILABLE_VOICES}