"""应用配置（从环境变量读取 API Key 等敏感信息）"""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# 项目根目录 = backend/ 的父目录
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """统一管理配置项"""

    # ====== 阿里云百炼 ======
    dashscope_api_key: str = ""

    # ====== DeepSeek ======
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # ====== 通义千问 VL ======
    qwen_vl_model: str = "qwen3-vl-plus"

    # ====== Edge-TTS ======
    edge_tts_voice: str = "zh-CN-XiaoxiaoNeural"
    edge_tts_rate: str = "+0%"

    # ====== 服务 ======
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True

    # ====== CORS：前端地址（生产环境填 Vercel/Netlify 给的域名）======
    # 多个用英文逗号分隔；填 * 表示全部允许（仅开发）
    frontend_url: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:4173,http://127.0.0.1:4173,"
        "http://192.168.0.2:4173,http://192.168.0.2:5173"
    )

    # ====== 演示模式 ======
    # 供评审/演示使用：开启后（或无 API Key 时自动降级）返回预置示例数据，
    # 让无任何密钥的人也能完整走通「拍照识药 / 语音问答 / 相互作用检查」流程。
    demo_mode: bool = False

    # ====== 向量库 ======
    chroma_persist_dir: str = str(BACKEND_DIR / "app" / "data" / "chroma")
    embedding_model: str = "BAAI/bge-small-zh"

    # 是否启用 RAG 向量检索。云端通常不装 chromadb/sentence-transformers，
    # 必须显式置 0，否则相互作用检查会尝试加载向量库并直接 500。
    rag_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """缓存配置实例"""
    return Settings()


settings = get_settings()