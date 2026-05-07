# Hybrid Search Implementation Summary

## Overview
Implemented three-source concurrent hybrid search (方案 B: Enhance researcher_node) that executes parallel searches across Web, RAG, and Elasticsearch sources.

## Implementation Date
January 13, 2026

## Architecture Decision
**Selected Approach:** 方案 B (Enhance researcher_node)
- Maintains original Graph structure unchanged
- Intercepts execution flow within researcher_node
- Executes concurrent Web/RAG/ES searches
- Aggregates results and injects into context

## Files Modified

### 1. Core Implementation Files

#### New File: `src/graph/hybrid_search.py`
**Purpose:** Concurrent multi-source search module

**Key Components:**
- `HybridSearchResult`: Container for aggregated search results
- `parallel_search()`: Main function executing concurrent searches
- `_search_web()`: Async web search execution
- `_search_rag()`: Async RAG search execution  
- `_search_elasticsearch()`: Async Elasticsearch search execution

**Features:**
- Uses `asyncio.gather()` for true parallelism
- Handles exceptions gracefully with `return_exceptions=True`
- Formats results from each source consistently
- Aggregates all results into unified context string
- **Force execution:** Searches always run regardless of resources parameter

#### Modified File: `src/graph/nodes_2.py`
**Changes to `researcher_node()`:**

**Note:** The system uses `nodes_2.py` (not `nodes.py`) as confirmed by the import in `builder.py`:
```python
from .nodes_2 import (
    analyst_node,
    background_investigation_node,
    coordinator_node,
    researcher_node,
    ...
)
```

1. **Hybrid Search Integration (Lines ~1180-1220)**
   - Imports `parallel_search` from hybrid_search module
   - Extracts current step from plan
   - Builds query from step title and description
   - Executes parallel search before agent invocation

2. **Context Injection (Lines ~1220-1240)**
   - Creates HumanMessage with aggregated context
   - Injects context into state messages
   - Adds explanatory prompt about context source
   - Preserves original researcher flow

3. **Logging Enhancements**
   - Added detailed logging for hybrid search execution
   - Tracks context length and source results
   - Logs errors with full tracebacks

### 2. Backup Files
**Location:** `archive/backup_before_hybrid_v1/`

Backed up files:
- `nodes.py` (not used, but backed up for safety)
- `nodes_2.py` (actual file being used)
- `builder.py`
- `search.py`
- `retriever.py`

## Key Design Decisions

### 1. No @ Symbol Detection
**Removed:** Logic that checks for `@` symbols in messages
**Reason:** Hybrid search should execute automatically, not require user tags

### 2. Force Search Execution
**Implementation:** `parallel_search()` always executes enabled searches
**Behavior:** Ignores empty resources parameter - searches run unconditionally

### 3. Context Injection Strategy
**Method:** Inject as HumanMessage before agent execution
**Advantage:** 
- Agent sees context naturally in conversation flow
- Can still use tools for additional searches
- Maintains backward compatibility

### 4. Error Handling
**Strategy:** Graceful degradation
- Individual search failures don't block others
- Exceptions captured and logged
- Partial results still usable

## Search Source Configuration

### Web Search
- **Tool:** Configured via `get_web_search_tool()`
- **Engines:** Tavily, DuckDuckGo, Serper, etc.
- **Default Results:** Configurable via `max_search_results`

### RAG Search
- **Tool:** `get_retriever_tool()`
- **Providers:** RAGFlow, Dify, VikingDB, etc.
- **Behavior:** Searches across configured knowledge bases

### Elasticsearch Search
- **Provider:** `ElasticsearchProvider`
- **Mode:** Unified global search
- **Indices:** Configurable via `ELASTICSEARCH_TARGET_INDICES`
- **Default Indices:**
  - `2_cn_news_library`
  - `2_cn_post_library`
  - `3_cn_targetmap_*`
  - `2_cn_comment_library`
  - `2_cn_forum_library`
  - `2_cn_interactive_library`

## Usage Example

### Automatic Execution
```python
# In researcher_node, hybrid search executes automatically:
query = f"{current_step.title} {current_step.description}"

hybrid_result = await parallel_search(
    query=query,
    resources=state.get("resources", []),
    enable_web=True,
    enable_rag=True,
    enable_es=True,
    max_web_results=5
)

context = hybrid_result.get_aggregated_context()
```

### Manual Testing
```bash
# Run test script
cd deer-flow_pre/deer-flow
python test_hybrid_search.py
```

## Context Format

The aggregated context is formatted as:

```
=== Web Search Results ===
[Web search content]

=== Knowledge Base (RAG) Results ===
[RAG search content]

=== Database (Elasticsearch) Results ===
[Elasticsearch search content]
```

## Configuration

### Enable/Disable Sources
```python
parallel_search(
    query="your query",
    enable_web=True,   # Enable web search
    enable_rag=True,   # Enable RAG search
    enable_es=True,    # Enable Elasticsearch
    max_web_results=5  # Max web results
)
```

### Environment Variables
Required for Elasticsearch:
- `ELASTICSEARCH_HOST`
- `ELASTICSEARCH_USER`
- `ELASTICSEARCH_PASSWORD`
- `ELASTICSEARCH_TARGET_INDICES` (optional)

## Testing

### Test Script: `test_hybrid_search.py`

**Test Cases:**
1. **Basic Search:** No resources, Web + ES only
2. **With Resources:** Explicit ES resource provided
3. **Selective Sources:** Web search only

**Run Tests:**
```bash
python test_hybrid_search.py
```

## Performance Considerations

### Parallelism
- All enabled searches execute concurrently
- No sequential blocking
- Total time ≈ slowest individual search

### Timeouts
- Web search: Depends on provider
- RAG search: Depends on vector DB
- Elasticsearch: 30 seconds (configurable)

### Result Limits
- Web: Configurable (default 5)
- RAG: Top 10 documents
- Elasticsearch: Top 30 hits (top 10 returned)

## Logging

### Log Levels
- `INFO`: Search execution, results summary
- `DEBUG`: Detailed execution flow
- `WARNING`: Missing results, fallbacks
- `ERROR`: Search failures, exceptions

### Key Log Messages
```
[Hybrid Search] Starting parallel search for query: {query}
[Hybrid Search] Enabled sources - Web: True, RAG: True, ES: True
[Hybrid Search] Launching 3 concurrent searches
[Hybrid Search] Web search completed: 1234 chars
[Hybrid Search] Parallel search completed
[Hybrid Search] Context injected into state messages
```

## Future Enhancements

### Potential Improvements
1. **Caching:** Cache search results to avoid redundant queries
2. **Ranking:** Implement cross-source result ranking
3. **Deduplication:** Remove duplicate content across sources
4. **Streaming:** Stream results as they arrive
5. **Adaptive Search:** Adjust sources based on query type
6. **Result Fusion:** Intelligent merging of overlapping results

### Configuration Options
1. **Per-Source Timeouts:** Individual timeout controls
2. **Result Limits:** Per-source result count limits
3. **Priority Ordering:** Configure source priority
4. **Conditional Execution:** Rules for when to enable each source

## Troubleshooting

### No Results Returned
**Check:**
1. Environment variables configured correctly
2. Search providers accessible
3. Log messages for specific errors
4. Network connectivity

### Elasticsearch Connection Issues
**Solutions:**
1. Verify `ELASTICSEARCH_HOST` format
2. Check credentials
3. Ensure HTTP (not HTTPS) if configured
4. Review firewall rules

### RAG Search Not Working
**Solutions:**
1. Verify RAG provider configured
2. Check resource URIs format
3. Ensure knowledge base indexed
4. Review provider-specific logs

## Rollback Procedure

If issues occur, restore from backup:

```bash
cd deer-flow_pre/deer-flow
cp archive/backup_before_hybrid_v1/nodes_2.py src/graph/
cp archive/backup_before_hybrid_v1/builder.py src/graph/
cp archive/backup_before_hybrid_v1/search.py src/tools/
cp archive/backup_before_hybrid_v1/retriever.py src/tools/
```

**Important:** The system uses `nodes_2.py`, not `nodes.py`.

## Verification

### Verify Implementation
1. Check backup files exist
2. Verify `hybrid_search.py` created
3. Confirm `researcher_node` modified
4. Run test script
5. Check logs for hybrid search messages

### Success Criteria
- ✅ Backup completed
- ✅ `hybrid_search.py` created with all functions
- ✅ `researcher_node` calls `parallel_search()`
- ✅ Context injected into state messages
- ✅ Test script runs without errors
- ✅ Logs show parallel execution

## Contact & Support

For issues or questions about this implementation:
1. Check logs in `deer-flow_pre/deer-flow/logs/`
2. Review test output from `test_hybrid_search.py`
3. Examine backup files for comparison
4. Consult design document: `.kiro/specs/parallel-hybrid-search/design.md`
