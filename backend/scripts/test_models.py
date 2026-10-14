"""模型调用测试脚本（阶段 4）

测试三种 AI 服务：
- 通义千问 VL（识图，需要 DASHSCOPE_API_KEY）
- DeepSeek（对话 + JSON 模式，需要 DEEPSEEK_API_KEY）
- Edge-TTS（无需 Key）

运行：
    cd backend
    python scripts/test_models.py vl       # 测试 VL
    python scripts/test_models.py llm      # 测试 DeepSeek
    python scripts/test_models.py tts     # 测试 TTS
    python scripts/test_models.py all      # 全部
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))


async def test_vl():
    """测试通义千问 VL：用一张公开药品图（请自行准备 ./test_data/aspirin.jpg）"""
    from app.services.qwen_vl import recognize_medicine
    test_image = BACKEND_DIR / "scripts" / "test_data" / "aspirin.jpg"
    if not test_image.exists():
        print(f"⚠️  测试图片不存在: {test_image}")
        print("   请上传一张药盒照片到该路径，再执行测试")
        return
    print(f"📷 测试 VL：{test_image}")
    with open(test_image, "rb") as f:
        image_bytes = f.read()
    result = await recognize_medicine(image_bytes)
    print(f"✅ 识别结果: {result.model_dump_json(indent=2, ensure_ascii=False)}")


async def test_llm():
    """测试 DeepSeek：对话 + JSON"""
    from app.services.deepseek import chat, analyze_interactions

    print("💬 测试 DeepSeek 对话...")
    answer = await chat(
        question="高血压的老人能吃布洛芬吗？",
        medicine_context=["硝苯地平控释片", "布洛芬缓释胶囊"],
    )
    print(f"✅ 回答: {answer}\n")

    print("💊 测试 DeepSeek 相互作用分析...")
    result = await analyze_interactions(["华法林钠片", "阿司匹林肠溶片"])
    print(f"✅ 结果: {result}")


async def test_tts():
    """测试 Edge-TTS：合成一段并保存为 mp3"""
    from app.services.tts import synthesize_to_file
    out = BACKEND_DIR / "scripts" / "test_data" / "tts_test.mp3"
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"🔊 测试 TTS：生成 {out}")
    await synthesize_to_file("您好，请按时服用阿司匹林，每天一片。", out)
    size = out.stat().st_size
    print(f"✅ 已生成: {out} ({size} 字节)")


async def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"

    if arg in ("vl",):
        await test_vl()
    elif arg in ("llm",):
        await test_llm()
    elif arg in ("tts",):
        await test_tts()
    elif arg == "all":
        await test_tts()  # TTS 无需 Key 先跑
        try:
            await test_llm()
        except Exception as e:
            print(f"⚠️ LLM 测试失败: {e}")
        try:
            await test_vl()
        except Exception as e:
            print(f"⚠️ VL 测试失败: {e}")
    else:
        print(f"用法: python {sys.argv[0]} [vl|llm|tts|all]")


if __name__ == "__main__":
    asyncio.run(main())