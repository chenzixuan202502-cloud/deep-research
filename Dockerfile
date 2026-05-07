# 1. 使用 uv 官方镜像作为底座 (Python 3.12)
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# 2. 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 3. 安装系统基础依赖 + Node.js 20
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libpq-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    # === 关键：安装 pnpm ===
    && npm install -g pnpm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 4. 后端依赖缓存层 (利用 Docker 缓存加速构建)
# 复制 uv.lock 和 pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# 5. 前端依赖缓存层
COPY web/package.json web/pnpm-lock.yaml* ./web/
# 使用 pnpm 安装前端依赖
RUN cd web && pnpm install --frozen-lockfile

# 6. 复制剩余所有代码
COPY . /app

# 7. 安装项目本身 (同步环境)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# 8. 暴露端口
EXPOSE 8088 3033

# 9. 赋予脚本执行权限
RUN chmod +x bootstrap.sh

# 10. 启动命令 (直接调用您的脚本)
# 注意：这里默认使用 dev 模式，生产环境可在 docker-compose 里覆盖
CMD ["./bootstrap.sh", "--dev"]