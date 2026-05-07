# Hybrid Search 移除说明

## 修改日期
2026-01-15

## 修改原因

当前系统存在双重搜索问题：
1. **researcher_node** 强制执行 `parallel_search` (Hybrid Search)
2. **Agent** 基于 Plan 主动调用 `local_search_tool`

由于我们已经实现了"虚拟资源注入 (Virtual Resource Injection)"，Agent 已经能够自主、智能地调用检索工具。强制的 Hybrid Search 现在造成了：
- ❌ 不必要的性能开销
- ❌ Token 浪费
- ❌ Elasticsearch 请求量翻倍

## 修改内容

### 文件：`src/graph/nodes_2.py`

在 `researcher_node` 函数中：
- ✅ 注释掉 `from src.graph.hybrid_search import parallel_search` 导入
- ✅ 注释掉整个 Hybrid Search 执行逻辑
- ✅ 注释掉 Context 注入逻辑
- ✅ 保留正常的 Agent 初始化和工具配置

### 修改位置
- 行号：约 1368-1440
- 函数：`async def researcher_node()`

## 预期效果

### 性能优化
- ✅ Elasticsearch 请求量减少约 50%
- ✅ Token 消耗显著降低
- ✅ 响应速度提升

### 功能保持
- ✅ Agent 仍可通过 `local_search_tool` 按需检索
- ✅ Virtual Resource Injection 确保工具可用性
- ✅ Web 搜索功能完全保留
- ✅ RAGFlow 和 Elasticsearch 仍可通过工具访问

## 验证方法

运行验证脚本：
```bash
python3 verify_hybrid_search_removal.py
```

所有检查项应显示 ✅ PASS。

## 回滚方法

如需恢复 Hybrid Search，取消注释以下代码块：
1. `from src.graph.hybrid_search import parallel_search`
2. Hybrid Search 执行逻辑（约 70 行）
3. Context 注入逻辑

## 相关文档
- `HYBRID_SEARCH_IMPLEMENTATION.md` - 原始实现文档
- `混合搜索实施说明.md` - 中文实施说明
- `实施总结_三源并发混合搜索.md` - 实施总结

## 技术决策

### 为什么移除而不是优化？
1. **架构冗余**：Virtual Resource Injection 已提供更优雅的解决方案
2. **智能调度**：Agent 基于 Plan 的按需检索比强制搜索更高效
3. **成本考虑**：减少不必要的 API 调用和 Token 消耗

### Agent 如何访问数据库？
- Agent 通过 `local_search_tool` 主动调用
- Planner 在生成 Plan 时会考虑 `resources` 字段
- Virtual Resource Injection 确保 "全局知识库" 始终可见
- Agent 根据任务需求智能决定是否搜索

## 监控建议

建议监控以下指标以验证改进：
1. Elasticsearch 请求频率
2. 平均 Token 消耗
3. 端到端响应时间
4. Agent 工具调用模式

---

**修改者**: Kiro AI Assistant  
**审核状态**: 待测试验证
