#!/bin/bash

# 快速重启 DeerFlow 开发服务的脚本

echo "正在停止现有的 DeerFlow 服务..."

# 停止所有 bootstrap.sh --dev 相关进程
pkill -f "bootstrap.sh --dev"
pkill -f "server.py --reload --port 8088"
pkill -f "pnpm dev"

echo "等待进程完全停止..."
sleep 3

# 检查端口是否已释放
if netstat -tlnp 2>/dev/null | grep -q ":3033\|:8088"; then
    echo "警告: 端口仍被占用，尝试强制停止..."
    fuser -k 3033/tcp 2>/dev/null
    fuser -k 8088/tcp 2>/dev/null
    sleep 2
fi

echo "正在启动 DeerFlow 开发服务..."
echo "前端: http://localhost:3033"
echo "后端: http://localhost:8088"
echo ""
echo "按 Ctrl+C 停止服务"
echo "================================"

# 启动服务
./bootstrap.sh --dev
