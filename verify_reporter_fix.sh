#!/bin/bash

echo "=========================================="
echo "Reporter 语言强制约束修复验证"
echo "=========================================="
echo ""

SUCCESS=0
TOTAL=4

echo "1. 检查 reporter.md 是否包含语言强制约束..."
if grep -q "CRITICAL LANGUAGE REQUIREMENT" src/prompts/reporter.md; then
    echo "   ✅ reporter.md 包含 CRITICAL LANGUAGE REQUIREMENT"
    SUCCESS=$((SUCCESS + 1))
else
    echo "   ❌ reporter.md 缺少 CRITICAL LANGUAGE REQUIREMENT"
fi

echo ""
echo "2. 检查 reporter.zh_CN.md 是否包含语言强制约束..."
if grep -q "关键语言要求" src/prompts/reporter.zh_CN.md; then
    echo "   ✅ reporter.zh_CN.md 包含关键语言要求"
    SUCCESS=$((SUCCESS + 1))
else
    echo "   ❌ reporter.zh_CN.md 缺少关键语言要求"
fi

echo ""
echo "3. 检查是否包含'语料惯性'说明..."
if grep -q "语料惯性" src/prompts/reporter.md; then
    echo "   ✅ reporter.md 包含语料惯性说明"
    SUCCESS=$((SUCCESS + 1))
else
    echo "   ❌ reporter.md 缺少语料惯性说明"
fi

echo ""
echo "4. 检查是否包含验证清单..."
if grep -q "Verification Checklist" src/prompts/reporter.md; then
    echo "   ✅ reporter.md 包含验证清单"
    SUCCESS=$((SUCCESS + 1))
else
    echo "   ❌ reporter.md 缺少验证清单"
fi

echo ""
echo "=========================================="
echo "验证结果"
echo "=========================================="
echo "通过: $SUCCESS/$TOTAL"
echo ""

if [ $SUCCESS -eq $TOTAL ]; then
    echo "✅✅✅ 所有验证通过！✅✅✅"
    echo ""
    echo "Reporter 语言强制约束已成功添加："
    echo "  • 强力语言约束（CRITICAL, 死命令）"
    echo "  • 语料惯性问题说明和应对策略"
    echo "  • 正确/错误示例对比"
    echo "  • 提交前验证清单"
    echo "  • 角色定位和最后警告"
    echo ""
    echo "预期效果："
    echo "  🎯 消除语言混杂问题"
    echo "  📈 提高报告质量"
    echo "  🛡️ 防止语料惯性错误"
    echo ""
    exit 0
else
    echo "❌ 验证失败！请检查上述错误。"
    exit 1
fi
