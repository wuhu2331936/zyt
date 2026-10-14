"""智药通 FastAPI 入口

阶段 2：挂载 4 个业务路由（识药 / 相互作用 / 语音问答 / TTS）
阶段 5：生产化（CORS 收紧 + 启动横幅）
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import medicine, interaction, voice

app = FastAPI(
    title="智药通 API",
    description="AI 老年人用药安全助手",
    version="0.3.0",
)


def _build_cors_origins() -> list[str]:
    """从 FRONTEND_URL 环境变量解析允许的跨域源（逗号分隔）

    开发环境默认值 "http://localhost:5173,http://127.0.0.1:5173"
    生产环境填前端 Vercel/Netlify 域名，例如：
      FRONTEND_URL=https://zhijiayaotong.vercel.app
    """
    raw = settings.frontend_url.strip()
    if not raw or raw == "*":
        return ["*"]
    return [url.strip() for url in raw.split(",") if url.strip()]


# CORS：生产环境根据 FRONTEND_URL 收紧；开发环境允许所有
app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup_banner():
    """启动时打印一行，便于排查"""
    print(
        f"\n🚀 智药通 API v{app.version} 已启动\n"
        f"   CORS 允许来源: {settings.frontend_url}\n"
        f"   Swagger UI:    http://{settings.app_host}:{settings.app_port}/docs\n"
        f"   ChromaDB 目录: {settings.chroma_persist_dir}\n"
    )


@app.get("/")
def root():
    """根路径"""
    return {
        "message": "智药通 API is running",
        "version": app.version,
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    """健康检查（Render / Railway 用这个做存活探针）"""
    return {"status": "ok", "version": app.version}


# 业务路由
app.include_router(
    medicine.router,
    prefix="/api/medicine",
    tags=["药品识别"],
)
app.include_router(
    interaction.router,
    prefix="/api/interaction",
    tags=["相互作用"],
)
app.include_router(
    voice.router,
    prefix="/api/voice",
    tags=["语音问答 & TTS"],
)
