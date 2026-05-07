#!/bin/bash

echo "=========================================="
echo "标签解析器迁移验证脚本"
echo "=========================================="
echo ""

# 检查 nodes.py 中不应该存在的内容
echo "1. 检查 nodes.py 中是否已移除标签解析器..."
if grep -q "def parse_database_tags" src/graph/nodes.py; then
    echo "   ❌ 错误: nodes.py 中仍然存在 parse_database_tags 函数"
    exit 1
else
    echo "   ✅ nodes.py 中已移除 parse_database_tags 函数"
fi

if grep -q "def extract_user_message_content" src/graph/nodes.py; then
    echo "   ❌ 错误: nodes.py 中仍然存在 extract_user_message_content 函数"
    exit 1
else
    echo "   ✅ nodes.py 中已移除 extract_user_message_content 函数"
fi

if grep -q "TAG PARSER" src/graph/nodes.py; then
    echo "   ❌ 错误: nodes.py 中仍然存在 TAG PARSER 代码块"
    exit 1
else
    echo "   ✅ nodes.py 中已移除 TAG PARSER 代码块"
fi

if grep -q "^import re$" src/graph/nodes.py; then
    echo "   ❌ 错误: nodes.py 中仍然导入 re 模块"
    exit 1
else
    echo "   ✅ nodes.py 中已移除 re 模块导入"
fi

if grep -q "from src.rag.retriever import Resource" src/graph/nodes.py; then
    echo "   ❌ 错误: nodes.py 中仍然导入 Resource"
    exit 1
else
    echo "   ✅ nodes.py 中已移除 Resource 导入"
fi

echo ""
echo "2. 检查 nodes_2.py 中是否包含标签解析器..."
if grep -q "def parse_database_tags" src/graph/nodes_2.py; then
    echo "   ✅ nodes_2.py 中包含 parse_database_tags 函数"
else
    echo "   ❌ 错误: nodes_2.py 中缺少 parse_database_tags 函数"
    exit 1
fi

if grep -q "def extract_user_message_content" src/graph/nodes_2.py; then
    echo "   ✅ nodes_2.py 中包含 extract_user_message_content 函数"
else
    echo "   ❌ 错误: nodes_2.py 中缺少 extract_user_message_content 函数"
    exit 1
fi

if grep -q "TAG PARSER" src/graph/nodes_2.py; then
    echo "   ✅ nodes_2.py 中包含 TAG PARSER 代码块"
else
    echo "   ❌ 错误: nodes_2.py 中缺少 TAG PARSER 代码块"
    exit 1
fi

if grep -q "^import re$" src/graph/nodes_2.py; then
    echo "   ✅ nodes_2.py 中导入了 re 模块"
else
    echo "   ❌ 错误: nodes_2.py 中缺少 re 模块导入"
    exit 1
fi

if grep -q "from src.rag.retriever import Resource" src/graph/nodes_2.py; then
    echo "   ✅ nodes_2.py 中导入了 Resource"
else
    echo "   ❌ 错误: nodes_2.py 中缺少 Resource 导入"
    exit 1
fi

echo ""
echo "3. 编译检查..."
if python3 -m py_compile src/graph/nodes.py 2>/dev/null; then
    echo "   ✅ nodes.py 编译成功"
else
    echo "   ❌ 错误: nodes.py 编译失败"
    exit 1
fi

if python3 -m py_compile src/graph/nodes_2.py 2>/dev/null; then
    echo "   ✅ nodes_2.py 编译成功"
else
    echo "   ❌ 错误: nodes_2.py 编译失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 所有验证通过！标签解析器已成功迁移到 nodes_2.py"
echo "=========================================="
