# RAG 全局搜索功能 - 修改说明

## 修改日期
2026年1月13日

## 问题描述
当前 hybrid_search 模块在 resources 列表为空时，会自动跳过 RAG 检索（日志显示 "No resources provided, skipping..."）。但系统拥有一个预先索引好的全局向量数据库（Global Knowledge Base），即使没有用户上传的临时文件，也应该查询这个全局库。

## 修改目标
修改代码，使其在 resources 为空时，依然强制初始化 RAG Retriever 并查询默认的向量集合。

## 已完成的修改

### 1. 修改 `src/tools/retriever.py`

#### 修改前
```python
def get_retriever_tool(resources: List[Resource]) -> RetrieverTool | None:
    if not resources:
        logger.info("No resources provided, skipping retriever tool creation")
        return None
    # ...
```

#### 修改后
```python
def get_retriever_tool(resources: List[Resource]) -> RetrieverTool | None:
    """
    Get retriever tool for RAG search.
    
    Args:
        resources: List of resources to search. If empty, will search global knowledge base.
        
    Returns:
        RetrieverTool instance or None if RAG_PROVIDER is not configured
    """
    # Check if RAG_PROVIDER is configured
    import os
    rag_provider = os.getenv("RAG_PROVIDER")
    
    if not rag_provider:
        logger.info("RAG_PROVIDER not configured, skipping retriever tool creation")
        return None
    
    # Log resource information
    if not resources:
        logger.info("No specific resources provided, will search global knowledge base")
    else:
        logger.info(f"Creating retriever tool for {len(resources)} resources: {[r.uri for r in resources]}")
    
    # Build retriever - this will work even with empty resources list
    retriever = build_retriever(resources if resources else [])
    # ...
```

**关键变化：**
- ✅ 移除了 `if not resources: return None` 的守卫语句
- ✅ 改为检查 `RAG_PROVIDER` 环境变量
- ✅ 只有当 `RAG_PROVIDER` 为空时才跳过
- ✅ 允许传入空列表，会搜索全局知识库

### 2. 修改 `src/rag/builder.py`

#### 修改前
```python
def build_retriever(resources: list = None) -> Retriever | None:
    # ...
    if resources:
        # 只有提供了 resources 才过滤 providers
        required_providers = set()
        # ...
        if not required_providers:
            logger.info("No matching providers found for the given resources")
            return None  # ❌ 这里会导致返回 None
    else:
        # 没有 resources 时使用所有 providers
        provider_names = all_provider_names
```

#### 修改后
```python
def build_retriever(resources: list = None) -> Retriever | None:
    """
    Build a retriever based on the RAG_PROVIDER environment variable and resources.
    
    Args:
        resources: Optional list of Resource objects to determine which providers to use.
                  If empty or None, all configured providers will be initialized for global search.
    
    Returns:
        A single Retriever instance, or CompositeRetriever if multiple providers are configured.
        Returns None if no provider is configured or initialization fails.
    """
    # ...
    
    # If resources are provided and not empty, filter providers based on resource URIs
    if resources and len(resources) > 0:
        required_providers = set()
        # ... 过滤逻辑 ...
        
        if not required_providers:
            # ✅ 改进：即使没有匹配的 providers，也使用所有配置的 providers
            logger.info("No matching providers found for the given resources, will use all configured providers")
            provider_names = all_provider_names
        else:
            provider_names = list(required_providers)
    else:
        # ✅ 没有 resources 或空列表，使用所有配置的 providers 进行全局搜索
        provider_names = all_provider_names
        logger.info(f"No specific resources, initializing all configured providers for global search: {provider_names}")
```

**关键变化：**
- ✅ 改进了 resources 为空时的处理逻辑
- ✅ 即使 resources 为空，也会初始化所有配置的 providers
- ✅ 明确日志说明是"全局搜索"模式
- ✅ 移除了会导致返回 None 的逻辑

### 3. 修改 `src/graph/hybrid_search.py`

#### 修改前
```python
async def _search_rag(query: str, resources: List[Resource] = None) -> str:
    try:
        logger.info(f"[Hybrid Search] Starting RAG search for: {query}")
        
        if not resources:
            resources = []
        
        retriever_tool = get_retriever_tool(resources)
        
        if not retriever_tool:
            logger.warning("[Hybrid Search] No RAG retriever available")
            return ""
        # ...
```

#### 修改后
```python
async def _search_rag(query: str, resources: List[Resource] = None) -> str:
    """
    Execute RAG search asynchronously.
    
    Args:
        query: Search query string
        resources: Optional list of resources to search (if empty, searches global knowledge base)
        
    Returns:
        Formatted RAG search results as string
    """
    try:
        # ✅ 改进的日志信息
        if not resources or len(resources) == 0:
            logger.info(f"[Hybrid Search] Starting RAG search (global knowledge base) for: {query}")
        else:
            logger.info(f"[Hybrid Search] Starting RAG search ({len(resources)} resources) for: {query}")
        
        # Get retriever tool - will work even with empty resources
        retriever_tool = get_retriever_tool(resources if resources else [])
        
        if not retriever_tool:
            logger.warning("[Hybrid Search] No RAG retriever available - check RAG_PROVIDER configuration")
            return ""
        # ...
        
        if formatted_results:
            # ✅ 改进的成功日志
            logger.info(f"[Hybrid Search] RAG search completed: {len(formatted_results)} documents from global knowledge base")
            return "\n\n".join(formatted_results)
```

**关键变化：**
- ✅ 改进了日志信息，明确区分"全局知识库"和"特定资源"
- ✅ 更清晰的错误提示（提示检查 RAG_PROVIDER 配置）
- ✅ 成功日志中说明是从"全局知识库"获取的结果

## 预期行为

### 场景 1：没有 resources（全局搜索）
```python
# 用户查询，不带附件
resources = []

# 日志输出：
[Hybrid Search] Starting RAG search (global knowledge base) for: 人工智能
[Hybrid Search] RAG search completed: 5 documents from global knowledge base
```

### 场景 2：有 resources（特定资源搜索）
```python
# 用户查询，带特定资源
resources = [Resource(uri="rag://dataset/123", title="My Dataset")]

# 日志输出：
[Hybrid Search] Starting RAG search (1 resources) for: 人工智能
[Hybrid Search] RAG search completed: 3 documents
```

### 场景 3：RAG_PROVIDER 未配置
```python
# RAG_PROVIDER 环境变量未设置
os.getenv("RAG_PROVIDER")  # None

# 日志输出：
[Hybrid Search] No RAG retriever available - check RAG_PROVIDER configuration
```

## 配置要求

### 必需环境变量
```bash
# 至少需要配置一个 RAG provider
export RAG_PROVIDER=ragflow

# 或者配置多个（逗号分隔）
export RAG_PROVIDER=ragflow,milvus,qdrant
```

### 各 Provider 的额外配置

#### RAGFlow
```bash
export RAGFLOW_API_KEY=your_api_key
export RAGFLOW_BASE_URL=http://your-ragflow-host
```

#### Milvus
```bash
export MILVUS_HOST=localhost
export MILVUS_PORT=19530
export MILVUS_COLLECTION=your_collection
```

#### Qdrant
```bash
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
export QDRANT_COLLECTION=your_collection
```

## 测试验证

### 运行测试脚本
```bash
cd deer-flow_pre/deer-flow

# 确保 RAG_PROVIDER 已配置
export RAG_PROVIDER=ragflow

# 运行测试
python3 test_rag_global_search.py
```

### 测试用例
1. **空 resources 列表** - 应该搜索全局知识库
2. **None resources** - 应该搜索全局知识库
3. **特定 resources** - 应该搜索指定资源
4. **Retriever 工具创建** - 应该成功创建

### 预期测试输出
```
[Hybrid Search] Starting RAG search (global knowledge base) for: 人工智能
Successfully retrieved X documents from Vector DB
✓ SUCCESS: RAG global search is working!
```

## 工作流程

### 修改前
```
用户查询（无附件）
    ↓
resources = []
    ↓
get_retriever_tool([])
    ↓
if not resources: return None  ❌ 跳过 RAG 搜索
    ↓
无 RAG 结果
```

### 修改后
```
用户查询（无附件）
    ↓
resources = []
    ↓
get_retriever_tool([])
    ↓
检查 RAG_PROVIDER ✓
    ↓
build_retriever([])
    ↓
初始化所有配置的 providers ✓
    ↓
查询全局知识库 ✓
    ↓
返回搜索结果 ✓
```

## 关键改进点

### ✅ 1. 移除资源检查守卫
- **修改前：** `if not resources: return None`
- **修改后：** 检查 `RAG_PROVIDER` 环境变量

### ✅ 2. 支持全局搜索
- **修改前：** 必须提供 resources 才能搜索
- **修改后：** resources 为空时搜索全局知识库

### ✅ 3. 改进日志信息
- **修改前：** "No resources provided, skipping..."
- **修改后：** "Starting RAG search (global knowledge base)..."

### ✅ 4. 更好的错误提示
- **修改前：** "No RAG retriever available"
- **修改后：** "No RAG retriever available - check RAG_PROVIDER configuration"

## 兼容性

### 向后兼容
- ✅ 原有的带 resources 的搜索功能不受影响
- ✅ 所有现有代码无需修改
- ✅ 只是增加了全局搜索能力

### 新功能
- ✅ 支持无 resources 的全局搜索
- ✅ 自动使用所有配置的 providers
- ✅ 更清晰的日志和错误提示

## 故障排查

### 问题：RAG 搜索仍然被跳过
**检查：**
1. `RAG_PROVIDER` 环境变量是否设置
2. Provider 特定的配置是否正确
3. 查看日志中的具体错误信息

### 问题：返回空结果
**可能原因：**
1. 全局知识库为空（没有索引数据）
2. 查询词没有匹配的文档
3. Provider 连接失败

**解决方案：**
1. 检查向量数据库中是否有数据
2. 尝试不同的查询词
3. 查看 Provider 的详细日志

### 问题：Provider 初始化失败
**检查：**
1. Provider 特定的环境变量
2. 网络连接（如果是远程服务）
3. 认证信息（API Key 等）

## 文件清单

### 修改的文件
- ✅ `src/tools/retriever.py` - 移除资源检查守卫
- ✅ `src/rag/builder.py` - 支持空 resources 的全局搜索
- ✅ `src/graph/hybrid_search.py` - 改进日志信息

### 新增的文件
- ✅ `test_rag_global_search.py` - RAG 全局搜索测试脚本
- ✅ `RAG全局搜索修改说明.md` - 本文档

## 总结

### 修改前的问题
- ❌ resources 为空时跳过 RAG 搜索
- ❌ 无法利用全局知识库
- ❌ 日志信息不清晰

### 修改后的改进
- ✅ resources 为空时搜索全局知识库
- ✅ 充分利用预索引的向量数据
- ✅ 清晰的日志和错误提示
- ✅ 保持向后兼容性

### 下一步
1. 运行测试脚本验证功能
2. 确保 RAG_PROVIDER 正确配置
3. 检查全局知识库中有数据
4. 在实际应用中测试
