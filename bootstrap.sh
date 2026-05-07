#!/bin/bash

# ===============================
# Bootstrap script for DeerFlow
# ===============================

# 确保遇到错误就停止
set -e

# 默认端口（可通过环境变量覆盖）
BACKEND_PORT=${BACKEND_PORT:-8088}
FRONTEND_PORT=${FRONTEND_PORT:-3039}

# 检查是否为开发模式
if [ "$1" = "--dev" ] || [ "$1" = "-d" ] || [ "$1" = "dev" ] || [ "$1" = "development" ]; then
  MODE="DEVELOPMENT"
else
  MODE="PRODUCTION"
fi

echo -e "Starting DeerFlow in [$MODE] mode..."
echo "Backend Port: $BACKEND_PORT"
echo "Frontend Port: $FRONTEND_PORT"

# 启动后端
uv run server.py $( [ "$MODE" = "DEVELOPMENT" ] && echo "--reload" ) --host 0.0.0.0 --port $BACKEND_PORT &
SERVER_PID=$!

# 启动前端
cd web
if [ "$MODE" = "DEVELOPMENT" ]; then
  PORT=$FRONTEND_PORT HOSTNAME=0.0.0.0 pnpm dev &
else
  PORT=$FRONTEND_PORT HOSTNAME=0.0.0.0 pnpm start &
fi
WEB_PID=$!

# 捕获退出信号，优雅停止
trap "echo 'Stopping DeerFlow...'; kill $SERVER_PID $WEB_PID; exit 0" SIGINT SIGTERM

# 等待子进程结束
wait