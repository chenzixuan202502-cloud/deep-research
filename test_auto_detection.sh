#!/bin/bash

# 测试自动 API 检测功能

echo "================================"
echo "测试自动 API 检测功能"
echo "================================"
echo ""

echo "1. 检查后端服务状态..."
if netstat -tlnp 2>/dev/null | grep -q ":8088"; then
    echo "✅ 后端服务正在运行 (端口 8088)"
    netstat -tlnp 2>/dev/null | grep ":8088"
else
    echo "❌ 后端服务未运行"
    echo "请先启动后端服务: ./bootstrap.sh --dev"
    exit 1
fi

echo ""
echo "2. 检查前端服务状态..."
if netstat -tlnp 2>/dev/null | grep -q ":3033"; then
    echo "✅ 前端服务正在运行 (端口 3033)"
    netstat -tlnp 2>/dev/null | grep ":3033"
else
    echo "❌ 前端服务未运行"
    echo "请先启动前端服务: ./bootstrap.sh --dev"
    exit 1
fi

echo ""
echo "3. 测试本地 API 访问..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8088/api/config)
if [ "$response" = "200" ]; then
    echo "✅ 本地后端 API 可访问 (http://localhost:8088/api)"
else
    echo "❌ 本地后端 API 无法访问 (HTTP $response)"
fi

echo ""
echo "4. 测试本地前端访问..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3033/)
if [ "$response" = "200" ]; then
    echo "✅ 本地前端可访问 (http://localhost:3033)"
else
    echo "❌ 本地前端无法访问 (HTTP $response)"
fi

echo ""
echo "================================"
echo "测试完成！"
echo "================================"
echo ""
echo "现在你可以："
echo "1. 本地访问: http://localhost:3033"
echo "   → 自动连接到 http://localhost:8088/api"
echo ""
echo "2. 远程访问: http://39.98.109.195:58032"
echo "   → 自动连接到 http://39.98.109.195:58031/api"
echo ""
echo "打开浏览器开发者工具（F12）查看 Console，"
echo "你会看到 [API] 日志显示使用的 API URL。"
echo ""
