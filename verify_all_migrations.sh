#!/bin/bash

echo "=========================================="
echo "nodes_2.py 完整迁移验证脚本"
echo "=========================================="
echo ""

SUCCESS_COUNT=0
TOTAL_CHECKS=0

# 辅助函数
check_pass() {
    echo "   ✅ $1"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
}

check_fail() {
    echo "   ❌ 错误: $1"
}

# ============================================================
# 第一部分：标签解析器迁移验证
# ============================================================
echo "【第一部分】标签解析器迁移验证"
echo "=========================================="
echo ""

echo "1. 检查 nodes.py 中是否已移除标签解析器..."
TOTAL_CHECKS=$((TOTAL_CHECKS + 5))

if grep -q "def parse_database_tags" src/graph/nodes.py; then
    check_fail "nodes.py 中仍然存在 parse_database_tags 函数"
else
    check_pass "nodes.py 中已移除 parse_database_tags 函数"
fi

if grep -q "def extract_user_message_content" src/graph/nodes.py; then
    check_fail "nodes.py 中仍然存在 extract_user_message_content 函数"
else
    check_pass "nodes.py 中已移除 extract_user_message_content 函数"
fi

if grep -q "TAG PARSER" src/graph/nodes.py; then
    check_fail "nodes.py 中仍然存在 TAG PARSER 代码块"
else
    check_pass "nodes.py 中已移除 TAG PARSER 代码块"
fi

if grep -q "^import re$" src/graph/nodes.py; then
    check_fail "nodes.py 中仍然导入 re 模块"
else
    check_pass "nodes.py 中已移除 re 模块导入"
fi

if grep -q "from src.rag.retriever import Resource" src/graph/nodes.py; then
    check_fail "nodes.py 中仍然导入 Resource"
else
    check_pass "nodes.py 中已移除 Resource 导入"
fi

echo ""
echo "2. 检查 nodes_2.py 中是否包含标签解析器..."
TOTAL_CHECKS=$((TOTAL_CHECKS + 5))

if grep -q "def parse_database_tags" src/graph/nodes_2.py; then
    check_pass "nodes_2.py 中包含 parse_database_tags 函数"
else
    check_fail "nodes_2.py 中缺少 parse_database_tags 函数"
fi

if grep -q "def extract_user_message_content" src/graph/nodes_2.py; then
    check_pass "nodes_2.py 中包含 extract_user_message_content 函数"
else
    check_fail "nodes_2.py 中缺少 extract_user_message_content 函数"
fi

if grep -q "TAG PARSER" src/graph/nodes_2.py; then
    check_pass "nodes_2.py 中包含 TAG PARSER 代码块"
else
    check_fail "nodes_2.py 中缺少 TAG PARSER 代码块"
fi

if grep -q "^import re$" src/graph/nodes_2.py; then
    check_pass "nodes_2.py 中导入了 re 模块"
else
    check_fail "nodes_2.py 中缺少 re 模块导入"
fi

if grep -q "from src.rag.retriever import Resource" src/graph/nodes_2.py; then
    check_pass "nodes_2.py 中导入了 Resource"
else
    check_fail "nodes_2.py 中缺少 Resource 导入"
fi

# ============================================================
# 第二部分：Locale SSOT 迁移验证
# ============================================================
echo ""
echo "【第二部分】Locale SSOT 迁移验证"
echo "=========================================="
echo ""

echo "3. 检查 nodes.py 中的 Locale SSOT 实现..."
TOTAL_CHECKS=$((TOTAL_CHECKS + 2))

if grep -q "NOTE: Locale SSOT" src/graph/nodes.py; then
    check_pass "nodes.py 中包含 Locale SSOT 注释"
else
    check_fail "nodes.py 中缺少 Locale SSOT 注释"
fi

if grep -q "REMOVED: Locale override logic" src/graph/nodes.py; then
    check_pass "nodes.py 中包含 locale 覆盖移除说明"
else
    check_fail "nodes.py 中缺少 locale 覆盖移除说明"
fi

echo ""
echo "4. 检查 nodes_2.py 中的 Locale SSOT 实现..."
TOTAL_CHECKS=$((TOTAL_CHECKS + 3))

if grep -q "NOTE: Locale SSOT" src/graph/nodes_2.py; then
    check_pass "nodes_2.py 中包含 Locale SSOT 注释"
else
    check_fail "nodes_2.py 中缺少 Locale SSOT 注释"
fi

if grep -q "REMOVED: Locale override logic" src/graph/nodes_2.py; then
    check_pass "nodes_2.py 中包含 locale 覆盖移除说明"
else
    check_fail "nodes_2.py 中缺少 locale 覆盖移除说明"
fi

# 检查是否移除了错误的 locale 覆盖代码
if grep -q 'if new_plan.get("locale"):' src/graph/nodes_2.py; then
    check_fail "nodes_2.py 中仍然存在 locale 覆盖逻辑"
else
    check_pass "nodes_2.py 中已移除 locale 覆盖逻辑"
fi

# ============================================================
# 第三部分：编译检查
# ============================================================
echo ""
echo "【第三部分】编译检查"
echo "=========================================="
echo ""

echo "5. Python 语法检查..."
TOTAL_CHECKS=$((TOTAL_CHECKS + 2))

if python3 -m py_compile src/graph/nodes.py 2>/dev/null; then
    check_pass "nodes.py 编译成功"
else
    check_fail "nodes.py 编译失败"
fi

if python3 -m py_compile src/graph/nodes_2.py 2>/dev/null; then
    check_pass "nodes_2.py 编译成功"
else
    check_fail "nodes_2.py 编译失败"
fi

# ============================================================
# 第四部分：一致性检查
# ============================================================
echo ""
echo "【第四部分】nodes.py 与 nodes_2.py 一致性检查"
echo "=========================================="
echo ""

echo "6. 检查两个文件的 Locale SSOT 实现是否一致..."
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# 提取两个文件中的 Locale SSOT 相关代码
NODES_LOCALE=$(grep -A 5 "NOTE: Locale SSOT" src/graph/nodes.py 2>/dev/null | head -6)
NODES2_LOCALE=$(grep -A 5 "NOTE: Locale SSOT" src/graph/nodes_2.py 2>/dev/null | head -6)

if [ "$NODES_LOCALE" = "$NODES2_LOCALE" ]; then
    check_pass "两个文件的 Locale SSOT 实现一致"
else
    check_fail "两个文件的 Locale SSOT 实现不一致"
fi

# ============================================================
# 总结
# ============================================================
echo ""
echo "=========================================="
echo "验证总结"
echo "=========================================="
echo ""
echo "总检查项: $TOTAL_CHECKS"
echo "通过项: $SUCCESS_COUNT"
echo "失败项: $((TOTAL_CHECKS - SUCCESS_COUNT))"
echo ""

if [ $SUCCESS_COUNT -eq $TOTAL_CHECKS ]; then
    echo "✅✅✅ 所有验证通过！✅✅✅"
    echo ""
    echo "迁移完成的功能："
    echo "  1. ✅ 标签解析器（Tag Parser）"
    echo "  2. ✅ Locale SSOT 重构"
    echo ""
    echo "nodes_2.py 现在包含："
    echo "  • parse_database_tags() 函数"
    echo "  • extract_user_message_content() 函数"
    echo "  • TAG PARSER 代码块"
    echo "  • Locale SSOT 实现"
    echo "  • 与 nodes.py 保持一致的架构"
    echo ""
    exit 0
else
    echo "❌ 验证失败！请检查上述错误。"
    echo ""
    exit 1
fi
