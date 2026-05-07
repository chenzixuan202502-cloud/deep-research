# Quick Start - Hybrid Search

## 快速验证

### 1. 检查实施状态
```bash
cd deer-flow_pre/deer-flow
./verify_hybrid_implementation.sh
```

预期输出：`✓ All checks passed! Implementation verified.`

### 2. 运行测试
```bash
python3 test_hybrid_search.py
```

### 3. 启动应用
```bash
# 确保环境变量已配置
export ELASTICSEARCH_HOST=http://your-host:9200
export ELASTICSEARCH_USER=your-username
export ELASTICSEARCH_PASSWORD=your-password

# 启动后端
python3 -m src.server.app
```

### 4. 观察日志
查找以下日志消息确认混合搜索正在运行：
```
[Hybrid Search] Starting parallel search for query: ...
[Hybrid Search] Launching 3 concurrent searches
[Hybrid Search] Parallel search completed
[Hybrid Search] Context injected into state messages
```

## 核心文件

### 新增文件
- `src/graph/hybrid_search.py` - 并发搜索模块
- `test_hybrid_search.py` - 测试脚本
- `verify_hybrid_implementation.sh` - 验证脚本

### 修改文件
- `src/graph/nodes.py` - researcher_node 增强

### 备份文件
- `archive/backup_before_hybrid_v1/` - 所有备份

## 配置要点

### 必需环境变量
```bash
ELASTICSEARCH_HOST=http://host:port
ELASTICSEARCH_USER=username
ELASTICSEARCH_PASSWORD=password
```

### 可选环境变量
```bash
ELASTICSEARCH_TARGET_INDICES=index1,index2,index3
```

## 功能开关

在 `researcher_node` 中调整：
```python
hybrid_result = await parallel_search(
    query=query,
    enable_web=True,   # Web 搜索
    enable_rag=True,   # RAG 搜索
    enable_es=True,    # ES 搜索
    max_web_results=5  # Web 结果数
)
```

## 故障排查

### 问题：验证脚本失败
**解决：** 检查文件是否存在，Python 语法是否正确

### 问题：测试脚本报错
**解决：** 检查环境变量，确保搜索服务可访问

### 问题：应用启动失败
**解决：** 检查依赖安装，查看完整错误日志

### 问题：无搜索结果
**解决：** 检查日志中的 `[Hybrid Search]` 消息，确认各数据源状态

## 回滚

如需回滚到实施前状态：
```bash
cd deer-flow_pre/deer-flow
cp archive/backup_before_hybrid_v1/*.py src/graph/
cp archive/backup_before_hybrid_v1/search.py src/tools/
cp archive/backup_before_hybrid_v1/retriever.py src/tools/
```

## 文档

- `HYBRID_SEARCH_IMPLEMENTATION.md` - 完整实施文档（英文）
- `实施总结_三源并发混合搜索.md` - 实施总结（中文）
- `.kiro/specs/parallel-hybrid-search/` - 需求和设计文档

## 支持

遇到问题请：
1. 查看日志文件
2. 运行验证脚本
3. 检查环境变量配置
4. 参考完整实施文档
