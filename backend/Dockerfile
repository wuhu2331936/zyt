# =============================================================================
# Dockerfile for 智药通 FastAPI Backend
# 适用：Render / Railway / Fly.io / 阿里云容器服务
# =============================================================================

# 阶段 1：构建向量库（在生产镜像里一并构建一次，避免首次请求卡住）
FROM python:3.12-slim AS builder

# 系统依赖（ChromaDB 的 hnswlib 需要编译工具）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# 先 copy requirements 单独一层利用 Docker 缓存
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# 阶段 2：运行时（精简版，无编译器）
FROM python:3.12-slim AS runtime

# 时区设为上海
ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 拷贝已编译好的依赖（不再重新下载/编译）
COPY --from=builder /install /usr/local

# 代码
COPY app ./app
COPY scripts ./scripts

# 启动脚本
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

# 默认端口（Render 必填 10000）
ENV APP_HOST=0.0.0.0 \
    APP_PORT=10000

EXPOSE 10000

CMD ["./start.sh"]
