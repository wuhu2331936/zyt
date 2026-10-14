"""Edge-TTS 5 种中文声音对比脚本

为比赛演示视频挑选合适的语音角色：

运行：
    cd backend
    python scripts/preview_tts.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))


SAMPLES = {
    "zh-CN-XiaoxiaoNeural": "您好，我是晓晓。今天该吃阿司匹林了，请记得餐前半小时服用哦。",
    "zh-CN-YunxiNeural": "您好，我是云希。现在是晚上八点，请服用硝苯地平控制片。",
    "zh-CN-YunyangNeural": "服药提醒：华法林钠片，每日一片，请固定时间服用。",
    "zh-CN-XiaoyiNeural": "亲爱的奶奶，该吃药啦，我来帮您读一下今天的用药清单。",
    "zh-CN-XiaomengNeural": "嗨，今天的药盒已经扫描好啦，您真棒！",
}


async def main():
    import edge_tts

    out_dir = BACKEND_DIR / "scripts" / "test_data" / "tts_samples"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"🎙️  生成 5 种声音样本到 {out_dir}\n")

    for voice, text in SAMPLES.items():
        out = out_dir / f"{voice}.mp3"
        comm = edge_tts.Communicate(text=text, voice=voice)
        with open(out, "wb") as f:
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
        size = out.stat().st_size
        print(f"  ✅ {voice:30s} -> {out.name} ({size} B)")
        print(f"     「{text}」\n")

    print("=" * 60)
    print("📌 推荐：老年用户用晓晓（zh-CN-XiaoxiaoNeural）温柔亲切")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())