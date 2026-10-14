#!/usr/bin/env bash
# 启动脚本：自动构建向量库（首次）→ 启动 gunicorn
set -e

echo "=== 智药通 Backend 启动 ==="
echo "时区: $(date)"
echo "Python: $(python --version)"

# 首次启动时向量库不存在，自动构建一次
if [ ! -d "./app/data/chroma" ] || [ -z "$(ls -A ./app/data/chroma 2>/dev/null)" ]; then
    echo ">>> 首次启动，构建向量库（需要下载 BAAI/bge-small-zh 模型，约 180MB）"
    python scripts/build_vector_db.py || echo "向量库构建失败，将使用 LLM 兜底模式"
fi

# 启动 gunicorn：2 worker + uvicorn worker class（异步 FastAPI）
# 端口从环境变量读（Render 用 PORT，Railway 同；本地用 APP_PORT）
PORT=${PORT:-${APP_PORT:-8000}}
WORKERS=${WEB_CONCURRENCY:-2}

echo ">>> 启动 gunicorn，监听 0.0.0.0:${PORT}，workers=${WORKERS}"
exec gunicorn app.main:app \
    --bind "0.0.0.0:${PORT}" \
    --workers ${WORKERS} \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --graceful-timeout 30 \
    --access-logfile - \
    --error-logfile -
