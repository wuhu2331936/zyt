"""语音问答 + TTS + ASR 路由"""
from __future__ import annotations

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from app.models.medicine import ChatRequest, ChatResponse, TTSRequest
from app.services import asr, deepseek, tts

router = APIRouter()
logger = logging.getLogger(__name__)

# 单次录音上限：16kHz/16bit 单声道约 2 分钟，正常人问一句话远小于此
MAX_ASR_BYTES = 4 * 1024 * 1024  # 4MB


class ASRResponse(BaseModel):
    text: str
    is_demo: bool = False


@router.post("/asr", response_model=ASRResponse, summary="语音转文字（阿里云百炼 Paraformer）")
async def speech_to_text(file: UploadFile = File(...)):
    """接收前端录的音频 → 返回识别文本

    存在的意义：浏览器原生 Web Speech API 在国内手机上不可用
    （Chrome 的识别走 Google 服务器，国内连不通；微信内置浏览器干脆没有这个 API），
    所以语音输入统一走服务端识别。
    """
    data = await file.read()
    if len(data) > MAX_ASR_BYTES:
        raise HTTPException(status_code=413, detail="录音太长，请控制在 2 分钟内")

    try:
        text, is_demo = await asr.transcribe(data, file.filename or "audio.wav")
    except asr.ASRError as e:
        logger.warning("[asr] 识别失败: %s", e)
        raise HTTPException(status_code=503, detail=f"语音识别失败：{e}")

    if not text:
        raise HTTPException(status_code=422, detail="没听清，请再说一次")
    return ASRResponse(text=text, is_demo=is_demo)


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