"""Edge-TTS 服务（语音合成，无需 API Key）

用于「服药提醒」和「语音问答」播报。
Edge-TTS 利用微软 Edge 浏览器的 TTS 能力，免费、无需 Key。
文档：https://github.com/rany2/edge-tts
"""
from __future__ import annotations

import io
import tempfile
from pathlib import Path

import edge_tts

from app.core.config import settings


async def synthesize_speech(
    text: str,
    voice: str | None = None,
    rate: str | None = None,
) -> bytes:
    """把文字转成 mp3 音频

    Args:
        text: 要合成的文字
        voice: 声音，默认 zh-CN-XiaoxiaoNeural（女声，温柔）
        rate: 语速，默认配置值

    Returns:
        mp3 字节流
    """
    voice = voice or settings.edge_tts_voice
    rate = rate or settings.edge_tts_rate

    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)

    # 收集流式音频块到内存
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])

    return buf.getvalue()


async def synthesize_to_file(text: str, output: str | Path) -> Path:
    """合成并写入文件（适合本地调试 / 大文本）"""
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    audio = await synthesize_speech(text)
    path.write_bytes(audio)
    return path


# 可选声音清单（供前端 UI 选择）
AVAILABLE_VOICES = [
    {"id": "zh-CN-XiaoxiaoNeural", "label": "晓晓（女声温柔，推荐）"},
    {"id": "zh-CN-YunxiNeural", "label": "云希（男声稳重）"},
    {"id": "zh-CN-YunyangNeural", "label": "云扬（男声播报）"},
    {"id": "zh-CN-XiaoyiNeural", "label": "晓伊（女声亲切）"},
    {"id": "zh-CN-XiaomengNeural", "label": "晓梦（女声活泼）"},
]