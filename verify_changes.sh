#!/bin/bash

echo "=========================================="
echo "验证选择性数据库搜索功能修改"
echo "=========================================="
echo ""

# 检查修改的文件
echo "1. 检查修改的文件..."
echo ""

files=(
    "src/rag/builder.py"
    "src/tools/retriever.py"
    "src/prompts/planner.md"
    "src/rag/composite_provider.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
    fi
done

echo ""
echo "2. 检查关键修改..."
echo ""

# 检查 builder.py 是否添加了 resources 参数
if grep -q "def build_retriever(resources: list = None)" src/rag/builder.py; then
    echo "✅ builder.py: build_retriever() 已添加 resources 参数"
else
    echo "❌ builder.py: build_retriever() 未添加 resources 参数"
fi

# 检查是否有资源过滤逻辑
if grep -q "if resources:" src/rag/builder.py; then
    echo "✅ builder.py: 已添加资源过滤逻辑"
else
    echo "❌ builder.py: 未添加资源过滤逻辑"
fi

# 检查是否识别 rag:// 前缀
if grep -q 'uri.startswith("rag://")' src/rag/builder.py; then
    echo "✅ builder.py: 已添加 rag:// 前缀识别"
else
    echo "❌ builder.py: 未添加 rag:// 前缀识别"
fi

# 检查是否识别 elasticsearch:// 前缀
if grep -q 'uri.startswith("elasticsearch://")' src/rag/builder.py; then
    echo "✅ builder.py: 已添加 elasticsearch:// 前缀识别"
else
    echo "❌ builder.py: 未添加 elasticsearch:// 前缀识别"
fi

echo ""

# 检查 retriever.py 是否传递 resources
if grep -q "build_retriever(resources)" src/tools/retriever.py; then
    echo "✅ retriever.py: get_retriever_tool() 已传递 resources 参数"
else
    echo "❌ retriever.py: get_retriever_tool() 未传递 resources 参数"
fi

echo ""

# 检查 planner.md 是否添加了数据库资源处理说明
if grep -q "Database Resource Handling" src/prompts/planner.md; then
    echo "✅ planner.md: 已添加数据库资源处理说明"
else
    echo "❌ planner.md: 未添加数据库资源处理说明"
fi

echo ""

# 检查 composite_provider.py 是否增强了日志
if grep -q "Resources filter:" src/rag/composite_provider.py; then
    echo "✅ composite_provider.py: 已增强日志输出"
else
    echo "❌ composite_provider.py: 未增强日志输出"
fi

echo ""
echo "=========================================="
echo "验证完成！"
echo "=========================================="
echo ""
echo "如果所有检查都通过，说明修改已成功应用。"
echo ""
echo "下一步："
echo "1. 启动应用并测试实际功能"
echo "2. 查看日志验证选择性查询是否生效"
echo "3. 测试不同的资源引用场景"
echo ""
