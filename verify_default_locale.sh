#!/bin/bash

echo "=========================================="
echo "默认 Locale 设置验证"
echo "=========================================="
echo ""

SUCCESS=0
TOTAL=5

echo "1. 检查 State 类型定义中的默认 locale..."
if grep -q 'locale: str = "zh-CN"' src/graph/types.py; then
    echo "   ✅ State.locale = \"zh-CN\""
    SUCCESS=$((SUCCESS + 1))
else
    echo "   ❌ State.locale 不是 \"zh-CN\""
    grep "locale:" src/graph/types.py | head -1
fi

echo ""
echo "2. 检查 ChatRequest 中的默认 locale..."
if grep -A 1 'locale: Optional\[str\] = Field' src/server/chat_request.py | grep -q '"zh-CN"'; then
    echo "   ✅ ChatRequest.locale = \"zh-CN\""
    SUCCESS=$((SUCCESS + 1))
else
    echo "   ❌ ChatRequest.locale 不是 \"zh-CN\""
    grep -A 1 'locale: Optional\[str\] = Field' src/server/chat_request.py | head -2
fi

echo ""
echo "3. 检查 GeneratePPTRequest 中的默认 locale..."
if grep -A 1 'class GeneratePPTRequest' src/server/chat_request.py | grep -A 5 'locale' | grep -q '"zh-CN"'; then
    echo "   ✅ GeneratePPTRequest.locale = \"zh-CN\""
    SUCCESS=$((SUCCESS + 1))
else
    echo "   ❌ GeneratePPTRequest.locale 不是 \"zh-CN\""
fi

echo ""
echo "4. 检查 nodes.py 中 preserve_state_meta_fields 的默认 locale..."
if grep -A 10 'def preserve_state_meta_fields' src/graph/nodes.py | grep -q '"locale": state.get("locale", "zh-CN")'; then
    echo "   ✅ nodes.py preserve_state_meta_fields locale = \"zh-CN\""
    SUCCESS=$((SUCCESS + 1))
else
    echo "   ❌ nodes.py preserve_state_meta_fields locale 不是 \"zh-CN\""
fi

echo ""
echo "5. 检查 nodes_2.py 中 preserve_state_meta_fields 的默认 locale..."
if grep -A 10 'def preserve_state_meta_fields' src/graph/nodes_2.py | grep -q '"locale": state.get("locale", "zh-CN")'; then
    echo "   ✅ nodes_2.py preserve_state_meta_fields locale = \"zh-CN\""
    SUCCESS=$((SUCCESS + 1))
else
    echo "   ❌ nodes_2.py preserve_state_meta_fields locale 不是 \"zh-CN\""
fi

echo ""
echo "=========================================="
echo "验证结果"
echo "=========================================="
echo "通过: $SUCCESS/$TOTAL"
echo ""

if [ $SUCCESS -eq $TOTAL ]; then
    echo "✅✅✅ 所有默认 locale 已设置为中文！✅✅✅"
    echo ""
    echo "默认 locale 设置："
    echo "  ✅ State.locale = \"zh-CN\""
    echo "  ✅ ChatRequest.locale = \"zh-CN\""
    echo "  ✅ GeneratePPTRequest.locale = \"zh-CN\""
    echo "  ✅ nodes.py preserve_state_meta_fields = \"zh-CN\""
    echo "  ✅ nodes_2.py preserve_state_meta_fields = \"zh-CN\""
    echo ""
    echo "现在 Web 界面默认应该使用中文！"
    echo ""
    exit 0
else
    echo "❌ 验证失败！有 $((TOTAL - SUCCESS)) 个位置的默认 locale 不是中文。"
    echo ""
    echo "请检查上述错误的位置。"
    exit 1
fi
