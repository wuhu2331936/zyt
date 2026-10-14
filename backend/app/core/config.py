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
    qwen_vl_model: str = "qwen-vl-plus"

    # ====== Edge-TTS ======
    edge_tts_voice: str = "zh-CN-XiaoxiaoNeural"
    edge_tts_rate: str = "+0%"

    # ====== 服务 ======
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True

    # ====== 向量库 ======
    chroma_persist_dir: str = str(BACKEND_DIR / "app" / "data" / "chroma")
    embedding_model: str = "BAAI/bge-small-zh"

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