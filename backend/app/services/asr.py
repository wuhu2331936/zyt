"""语音识别（ASR）服务 —— 让用户"按住说话"在手机上真的能用

为什么需要它（这是手机端语音失效的真正根因）：
------------------------------------------------------------------
浏览器原生 Web Speech API（webkitSpeechRecognition）在国内手机上基本是废的：

1. Android Chrome / Edge：API 存在（`isASRSupported()` 返回 true，按钮照常显示），
   但它把录音送到 **Google** 的语音服务器。国内网络根本连不上，
   按下去几秒后抛 `error = network`，表现为"按钮转圈然后没反应"。
2. 微信 / QQ / UC 内置浏览器：直接没有这个 API，按钮压根不显示。
3. iOS Safari 的识别走 Apple 服务，在 WKWebView（App 内置浏览器）里同样不可用。

所以这里改为 **前端录音 → 上传 WAV → 后端调阿里云百炼转写**：
只要浏览器能拿到麦克风（HTTPS 下 Chrome/Safari/微信基本都行），语音输入就可用，
与 Google 服务无关。

音频格式为什么固定 WAV：
------------------------------------------------------------------
MediaRecorder 在各平台产出的封装五花八门（Android 是 webm/opus，iOS 是 mp4/aac），
而云上运行的是 python:3.11-slim 镜像，**没有 ffmpeg**，服务端转不动 mp4/aac。
因此前端统一用 Web Audio API 采集 PCM 并封成 16bit WAV 上传，后端零外部依赖。
"""
from __future__ import annotations

import asyncio
import logging
import struct
import tempfile
from pathlib import Path
from typing import Iterable

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# 模块级缓存：dashscope 只在第一次调用时 import（云端没装也不会影响其他接口）
_dashscope_import_error: Exception | None = None

# 演示模式下的预置问句（无 Key 时也能完整走通"说话 → 出回答"的流程）
_DEMO_QUESTIONS = [
    "高血压能吃布洛芬吗",
    "这两种药能一起吃吗",
    "这个药饭后吃还是饭前吃",
    "忘记吃药了要不要补服",
]
_demo_counter = {"i": 0}

# 一句话识别模型（按优先级回退：新模型优先，老 Key 也能用旧的）
_ASR_MODELS: tuple[str, ...] = (
    "paraformer-realtime-v2",
    "paraformer-realtime-v1",
    "paraformer-v1",
)

# OpenAI 兼容接口的兜底模型（DashScope 兼容模式，不依赖 SDK 版本）
_COMPATIBLE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/audio/transcriptions"
_COMPATIBLE_MODELS: tuple[str, ...] = ("qwen3-asr-flash", "qwen-audio-asr")


class ASRError(RuntimeError):
    """ASR 调用失败（调用方据此决定降级策略）"""


def _demo_text() -> str:
    """演示模式：轮流返回预置问句，连续演示时结果不重复"""
    q = _DEMO_QUESTIONS[_demo_counter["i"] % len(_DEMO_QUESTIONS)]
    _demo_counter["i"] += 1
    return q


def parse_wav_info(data: bytes) -> tuple[int, int, int]:
    """从 WAV 头解析 (采样率, 声道数, 位深)

    前端会带上自己认为的采样率，但浏览器未必真的按 16k 采样（Safari 尤甚），
    所以一律以**文件头里的真实值**为准，避免传给服务端的参数与音频不符导致识别错乱。
    解析失败时按 16k/单声道/16bit 兜底。
    """
    if len(data) < 44 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return 16000, 1, 16
    try:
        channels = struct.unpack_from("<H", data, 22)[0]
        sample_rate = struct.unpack_from("<I", data, 24)[0]
        bits = struct.unpack_from("<H", data, 34)[0]
        if sample_rate <= 0 or channels <= 0:
            return 16000, 1, 16
        return sample_rate, channels, bits
    except Exception:  # 头坏了就按默认值，让服务端去判断
        return 16000, 1, 16


def _join_sentences(sentences: Iterable[dict]) -> str:
    """把 Paraformer 返回的分句结果拼成一段文本"""
    parts: list[str] = []
    for s in sentences or []:
        if isinstance(s, dict):
            t = str(s.get("text") or "").strip()
            if t:
                parts.append(t)
    return "".join(parts).strip()


def _recognize_with_sdk(wav_path: str, sample_rate: int) -> str:
    """用 dashscope SDK 做一句话识别（同步阻塞，调用方需放进线程）

    依次尝试 _ASR_MODELS 里的模型：新 Key 用 v2，老 Key 回退到 v1，
    避免"模型不存在"直接把功能打死。
    """
    global _dashscope_import_error
    try:
        import dashscope  # noqa: PLC0415
        from dashscope.audio.asr import Recognition  # noqa: PLC0415
    except Exception as e:  # 云端/最小依赖环境可能没装 dashscope
        _dashscope_import_error = e
        raise ASRError(f"dashscope 未安装: {e}") from e

    # SDK 不读 .env，必须显式塞 Key（和 qwen_vl.py 一致）
    dashscope.api_key = settings.dashscope_api_key

    last_err = "未知错误"
    for model in _ASR_MODELS:
        try:
            # language_hints 只有较新的 SDK/模型支持，老版本传了会 TypeError
            try:
                recog = Recognition(
                    model=model,
                    format="wav",
                    sample_rate=sample_rate,
                    language_hints=["zh", "en"],
                    callback=None,
                )
            except TypeError:
                recog = Recognition(
                    model=model,
                    format="wav",
                    sample_rate=sample_rate,
                    callback=None,
                )

            result = recog.call(wav_path)
            status = getattr(result, "status_code", None)
            if status == 200:
                text = _join_sentences(result.get_sentence())
                if text:
                    return text
                last_err = f"{model}: 识别结果为空（可能是静音或录音太短）"
                logger.warning("[asr] %s", last_err)
            else:
                last_err = f"{model}: {getattr(result, 'code', status)} {getattr(result, 'message', '')}"
                logger.warning("[asr] %s", last_err)
        except Exception as e:
            last_err = f"{model}: {e}"
            logger.warning("[asr] %s 调用异常: %s", model, e)

    raise ASRError(last_err)


async def _recognize_with_compatible_api(wav_bytes: bytes, filename: str) -> str:
    """兜底：走 DashScope 的 OpenAI 兼容接口

    好处是完全不依赖 dashscope SDK 版本（1.20.11 对部分新模型支持不全），
    只要 Key 有权限就能用。
    """
    key = settings.dashscope_api_key
    last_err = "未知错误"
    async with httpx.AsyncClient(timeout=60) as client:
        for model in _COMPATIBLE_MODELS:
            try:
                resp = await client.post(
                    _COMPATIBLE_URL,
                    headers={"Authorization": f"Bearer {key}"},
                    files={"file": (filename, wav_bytes, "audio/wav")},
                    data={"model": model},
                )
                if resp.status_code == 200:
                    text = str((resp.json() or {}).get("text") or "").strip()
                    if text:
                        return text
                    last_err = f"{model}: 返回空文本"
                else:
                    last_err = f"{model}: HTTP {resp.status_code} {resp.text[:200]}"
                    logger.warning("[asr] 兼容接口 %s", last_err)
            except Exception as e:
                last_err = f"{model}: {e!r}"
                logger.warning("[asr] 兼容接口异常: %s", last_err)
    raise ASRError(last_err)


async def transcribe(audio_bytes: bytes, filename: str = "audio.wav") -> tuple[str, bool]:
    """把语音转成文字

    Args:
        audio_bytes: 音频二进制（推荐 WAV；其它格式会尝试原样上传）
        filename: 原始文件名，用于推断 MIME

    Returns:
        (识别文本, 是否演示数据)

    Raises:
        ASRError: 未配置 Key 且非演示模式，或所有识别通道都失败
    """
    if not audio_bytes:
        raise ASRError("没有收到音频数据")

    # 演示模式：返回预置问句，让无 Key 的评审也能走通完整流程
    if settings.demo_mode or not settings.dashscope_api_key:
        return _demo_text(), True

    sample_rate, channels, bits = parse_wav_info(audio_bytes)
    suffix = Path(filename).suffix or ".wav"

    # 排障用：手机端"识别不出来"时，先看是没录到声音还是识别服务的问题
    data_len = max(0, len(audio_bytes) - 44)
    seconds = data_len / (sample_rate * channels * bits / 8) if sample_rate else 0
    logger.info(
        "[asr] 收到音频 %d 字节 / %.2fs（%dHz %dch %dbit）",
        len(audio_bytes),
        seconds,
        sample_rate,
        channels,
        bits,
    )
    # 短于 0.3 秒基本就是静音/误触，直接给出可操作的提示，别白跑一趟接口
    if seconds < 0.3:
        raise ASRError("录音太短，请按住按钮说完整一句话")

    # SDK 只吃文件路径，先落到临时文件
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_path = tmp.name
    try:
        tmp.write(audio_bytes)
        tmp.close()

        try:
            text = await asyncio.to_thread(_recognize_with_sdk, tmp_path, sample_rate)
            return text, False
        except ASRError as e:
            logger.warning("[asr] SDK 通道失败(%s)，改走兼容接口", e)

        # SDK 通道不通（版本过旧 / 模型无权限）→ 兼容接口
        text = await _recognize_with_compatible_api(audio_bytes, f"audio{suffix}")
        return text, False
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass
