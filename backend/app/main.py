"""智药通 FastAPI 入口

阶段 2：挂载 4 个业务路由（识药 / 相互作用 / 语音问答 / TTS）
阶段 5：生产化（CORS 收紧 + 启动横幅）
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.core.config import settings
from app.api import medicine, interaction, voice

# 前端生产构建产物目录（backend/app/main.py -> 项目根/frontend/dist）
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
# 后端直接托管前端：只有一条服务、一个端口、同源，无需 vite 代理和跨域
SERVE_SPA = os.getenv("SERVE_FRONTEND", "1") != "0" and (
    FRONTEND_DIST / "index.html"
).is_file()

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


@app.get("/api/root")
def root():
    """根路径"""
    return {
        "message": "智药通 API is running",
        "version": app.version,
        "docs": "/docs",
        "frontend_served": SERVE_SPA,
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


if SERVE_SPA:
    # SPA 兜底：非 /api、非 /docs 的路径都返回 index.html（前端路由用）
    # 静态资源（/assets/...）存在则直出文件，否则回落到 index.html
    # index_inline.html：CSS 已内嵌的版本（规避个别环境单独拉取 CSS 失败）
    _SPA_INDEX = (
        FRONTEND_DIST / "index_inline.html"
        if (FRONTEND_DIST / "index_inline.html").is_file()
        else FRONTEND_DIST / "index.html"
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def _spa_fallback(full_path: str):
        target = (FRONTEND_DIST / full_path).resolve()
        if (
            target.is_file()
            and FRONTEND_DIST.resolve() in target.parents
        ):
            # sw.js 每次都回源校验，确保客户端 Service Worker 能立即更新
            if target.name == "sw.js":
                return FileResponse(target, headers={"Cache-Control": "no-cache"})
            return FileResponse(target)
        # HTML 入口禁止缓存，避免浏览器拿到旧版无样式页面
        return FileResponse(_SPA_INDEX, headers={"Cache-Control": "no-store"})
