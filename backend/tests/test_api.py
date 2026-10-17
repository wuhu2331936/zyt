"""单元测试：API 健康检查 + 模型连通性（不真实调外部 API）

使用：cd backend && pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
import os

# 测试前注入假环境变量（避免 Pydantic 必填报错）
os.environ.setdefault("DASHSCOPE_API_KEY", "sk-fake-test-only")
os.environ.setdefault("DEEPSEEK_API_KEY", "sk-fake-test-only")


@pytest.fixture(scope="module")
def client():
    """复用 FastAPI TestClient"""
    from app.main import app
    return TestClient(app)


def test_root(client):
    """根路径托管前端 SPA（HTML），JSON 元信息改由 /api/root 提供"""
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]

    r2 = client.get("/api/root")
    assert r2.status_code == 200
    data = r2.json()
    assert "message" in data
    assert "version" in data


def test_health(client):
    """健康检查"""
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_demo_mode_fallback(monkeypatch):
    """未配置 API Key 时应降级为演示数据，而不是抛错

    保证评审老师拿到源码、无任何密钥时也能完整走通识药 / 问答 / 相互作用检查。
    """
    import asyncio

    from app.core.config import settings
    from app.services import deepseek, qwen_vl

    monkeypatch.setattr(settings, "dashscope_api_key", "")
    monkeypatch.setattr(settings, "deepseek_api_key", "")

    # 拍照识药：返回预置药品
    med = asyncio.run(qwen_vl.recognize_medicine(b"\x89PNG\r\n\x1a\nfake"))
    assert med is not None and med.name

    # 语音问答：返回预置回答
    answer = asyncio.run(deepseek.chat("这个药怎么吃？"))
    assert isinstance(answer, str) and len(answer) > 0

    # 相互作用：命中预置规则（阿司匹林 + 布洛芬 → 较严重）
    risk = asyncio.run(
        deepseek.analyze_interactions(["阿司匹林肠溶片", "布洛芬缓释胶囊"])
    )
    assert risk["has_risk"] is True
    assert risk["risks"][0]["level"] == "major"


def test_openapi_generated(client):
    """OpenAPI 文档自动生成"""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    # 至少有 4 个核心 API
    paths = spec["paths"]
    expected = {
        "/api/medicine/recognize",
        "/api/interaction/check",
        "/api/voice/chat",
        "/api/voice/tts",
    }
    for path in expected:
        assert path in paths, f"missing {path}"


def test_recognize_empty_body(client):
    """未传图片应该 422 ValidationError"""
    r = client.post("/api/medicine/recognize")
    assert r.status_code in (422, 400)


def test_tts_voices(client):
    """TTS 声音列表无需 AI Key 就能返回"""
    r = client.get("/api/voice/voices")
    assert r.status_code == 200
    data = r.json()
    assert "voices" in data or isinstance(data, list)


def test_settings_load():
    """配置模块可正常导入"""
    from app.core.config import settings
    assert settings.app_port == 8000
    assert settings.embedding_model == "BAAI/bge-small-zh"


def test_pydantic_models():
    """Pydantic 模型序列化可用"""
    from app.models.medicine import (
        MedicineInfo,
        RecognizeResponse,
        InteractionRequest,
        TTSRequest,
    )

    med = MedicineInfo(name="氨氯地平片", spec="5mg")
    assert med.name == "氨氯地平片"
    assert med.spec == "5mg"

    resp = RecognizeResponse(success=True, medicine=med)
    assert resp.success is True

    req = InteractionRequest(medicines=["氨氯地平", "阿司匹林"])
    assert len(req.medicines) == 2

    tts_req = TTSRequest(text="你好")
    assert tts_req.text == "你好"


def test_model_modules_importable():
    """4 个 service 模块能 import（不真实调 API）

    如果 chromadb 还没装（依赖太重），跳过 rag 模块的测试。
    """
    import app.services.qwen_vl as qwen_vl
    import app.services.deepseek as deepseek
    import app.services.tts as tts
    assert hasattr(qwen_vl, "recognize_medicine")
    assert hasattr(deepseek, "chat")
    assert hasattr(tts, "synthesize_speech")

    try:
        import app.services.rag as rag  # noqa: F401

        assert hasattr(rag, "check_interactions")
        assert hasattr(rag, "search_medicine_info")
        # RAG 可选依赖未安装时模块也能导入（优雅降级）
        assert hasattr(rag, "RAG_DEPENDENCIES_AVAILABLE")
    except ModuleNotFoundError as e:
        # 跳过的常见原因：chromadb / sentence-transformers 未装
        if "chromadb" in str(e) or "sentence_transformers" in str(e):
            pytest.skip(f"Skip: 跳过 RAG 模块测试，原因为 {e}")
        raise
