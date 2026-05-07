#!/bin/bash

echo "=========================================="
echo "验证 Locale SSOT 重构"
echo "=========================================="
echo ""

# 检查修改的文件
echo "1. 检查修改的文件..."
echo ""

files=(
    "src/prompts/planner_model.py"
    "src/graph/nodes.py"
    "src/prompts/planner.md"
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

# 检查 planner_model.py 是否移除了 locale 字段
if ! grep -q 'locale: str = Field' src/prompts/planner_model.py; then
    echo "✅ planner_model.py: locale 字段已从 Plan 类中移除"
else
    echo "❌ planner_model.py: locale 字段仍然存在于 Plan 类中"
fi

# 检查是否添加了注释说明
if grep -q 'locale field removed' src/prompts/planner_model.py; then
    echo "✅ planner_model.py: 已添加 locale 移除的注释说明"
else
    echo "⚠️  planner_model.py: 未找到 locale 移除的注释说明"
fi

echo ""

# 检查 nodes.py 是否移除了 locale 覆盖逻辑
if ! grep -q 'if new_plan.get("locale"):' src/graph/nodes.py; then
    echo "✅ nodes.py: locale 覆盖逻辑已移除"
else
    echo "❌ nodes.py: locale 覆盖逻辑仍然存在"
fi

# 检查是否添加了 SSOT 注释
if grep -q 'Locale SSOT' src/graph/nodes.py; then
    echo "✅ nodes.py: 已添加 Locale SSOT 注释说明"
else
    echo "⚠️  nodes.py: 未找到 Locale SSOT 注释说明"
fi

echo ""

# 检查 planner.md 是否移除了 locale 字段要求
if ! grep -q 'locale, has_enough_context, thought, title, and steps' src/prompts/planner.md; then
    echo "✅ planner.md: 已从必需字段列表中移除 locale"
else
    echo "❌ planner.md: locale 仍在必需字段列表中"
fi

# 检查 Plan 接口定义是否移除了 locale
if ! grep -q 'locale: string;' src/prompts/planner.md; then
    echo "✅ planner.md: Plan 接口定义中已移除 locale 字段"
else
    echo "❌ planner.md: Plan 接口定义中仍包含 locale 字段"
fi

# 检查示例输出是否移除了 locale
if ! grep -q '"locale": "en-US"' src/prompts/planner.md; then
    echo "✅ planner.md: 示例输出中已移除 locale"
else
    echo "❌ planner.md: 示例输出中仍包含 locale"
fi

# 检查是否添加了系统上下文说明
if grep -q 'Language selection is handled by the system context' src/prompts/planner.md; then
    echo "✅ planner.md: 已添加系统上下文语言选择说明"
else
    echo "⚠️  planner.md: 未找到系统上下文语言选择说明"
fi

echo ""
echo "=========================================="
echo "验证完成！"
echo "=========================================="
echo ""
echo "如果所有检查都通过，说明 Locale SSOT 重构已成功应用。"
echo ""
echo "下一步："
echo "1. 运行应用并测试实际功能"
echo "2. 验证 Plan 生成不包含 locale 字段"
echo "3. 确认 locale 在整个工作流中保持不变"
echo "4. 检查 token 使用是否减少"
echo ""
