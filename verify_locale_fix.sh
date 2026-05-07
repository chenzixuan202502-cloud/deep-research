#!/bin/bash

echo "=== Locale Fix 验证脚本 ==="
echo ""

# 检查 chat.ts 是否导出了 mapLocaleToBackend
echo "1. 检查 mapLocaleToBackend 函数是否存在..."
if grep -q "export function mapLocaleToBackend" web/src/core/api/chat.ts; then
    echo "   ✓ mapLocaleToBackend 函数已导出"
else
    echo "   ✗ 未找到 mapLocaleToBackend 函数"
    exit 1
fi

# 检查 chatStream 是否接受 locale 参数
echo "2. 检查 chatStream 是否接受 locale 参数..."
if grep -q "locale: string;" web/src/core/api/chat.ts; then
    echo "   ✓ chatStream 接受 locale 参数"
else
    echo "   ✗ chatStream 未接受 locale 参数"
    exit 1
fi

# 检查 store.ts 是否导入了 mapLocaleToBackend
echo "3. 检查 store.ts 是否导入 mapLocaleToBackend..."
if grep -q "mapLocaleToBackend" web/src/core/store/store.ts; then
    echo "   ✓ store.ts 已导入 mapLocaleToBackend"
else
    echo "   ✗ store.ts 未导入 mapLocaleToBackend"
    exit 1
fi

# 检查 sendMessage 是否接受 locale 参数
echo "4. 检查 sendMessage 是否接受 locale 参数..."
if grep -q "locale?: string;" web/src/core/store/store.ts; then
    echo "   ✓ sendMessage 接受 locale 参数"
else
    echo "   ✗ sendMessage 未接受 locale 参数"
    exit 1
fi

# 检查 messages-block.tsx 是否使用 useLocale
echo "5. 检查 messages-block.tsx 是否使用 useLocale..."
if grep -q "useLocale" web/src/app/chat/components/messages-block.tsx; then
    echo "   ✓ messages-block.tsx 使用了 useLocale"
else
    echo "   ✗ messages-block.tsx 未使用 useLocale"
    exit 1
fi

# 检查是否将 locale 传递给 sendMessage
echo "6. 检查是否将 locale 传递给 sendMessage..."
if grep -q "locale," web/src/app/chat/components/messages-block.tsx; then
    echo "   ✓ locale 已传递给 sendMessage"
else
    echo "   ✗ locale 未传递给 sendMessage"
    exit 1
fi

# 检查后端是否接收 locale 参数
echo "7. 检查后端是否接收 locale 参数..."
if grep -q "request.locale" src/server/app.py; then
    echo "   ✓ 后端正确接收 locale 参数"
else
    echo "   ✗ 后端未接收 locale 参数"
    exit 1
fi

echo ""
echo "=== 所有检查通过！ ==="
echo ""
echo "下一步："
echo "1. 清除浏览器 Cookie"
echo "2. 打开应用（默认语言应为中文）"
echo "3. 直接发起对话，检查后端日志确认收到 locale: zh-CN"
echo "4. 验证 Agent 返回中文回复"
