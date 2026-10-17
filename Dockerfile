# 通用云部署镜像：后端 FastAPI + 已构建的前端 dist（单端口 8000）
# 适用平台：Zeabur / Koyeb / Northflank / Render(Docker) / Fly.io
# 注意：故意用 requirements-cloud.txt（不含 torch/chromadb），
#       因为免费云主机只有 256~512MB 内存，装 RAG 三件套必然 OOM。

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    SERVE_FRONTEND=1

WORKDIR /app

# 依赖单独一层，改代码时不必重装依赖（构建更快）
COPY backend/requirements-cloud.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# 后端代码 + 前端构建产物
COPY backend/ ./backend/
COPY frontend/dist/ ./frontend/dist/

EXPOSE 8000

# Zeabur / Koyeb / Render 都会注入 PORT 环境变量
CMD cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
