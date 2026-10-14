"""智药通 FastAPI 入口

阶段 2：挂载 4 个业务路由（识药 / 相互作用 / 语音问答 / TTS）
阶段 1 验证：health 接口保留
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import medicine, interaction, voice

app = FastAPI(
    title="智药通 API",
    description="AI 老年人用药安全助手",
    version="0.2.0",
)

# 允许前端跨域调用（PWA 在开发期间需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请收紧到具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """根路径"""
    return {"message": "智药通 API is running", "version": "0.2.0"}


@app.get("/api/health")
def health():
    """健康检查"""
    return {"status": "ok"}


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