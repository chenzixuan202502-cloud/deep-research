# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Hybrid Search Module - Concurrent Multi-Source Search
Implements parallel search across Web, RAG, and Elasticsearch sources.
"""

import asyncio
import logging
from typing import List, Optional

from src.rag import Resource
from src.rag.elasticsearch import ElasticsearchProvider
from src.tools.retriever import get_retriever_tool
from src.tools.search import get_web_search_tool

logger = logging.getLogger(__name__)


class HybridSearchResult:
    """Container for aggregated search results from multiple sources."""
    
    def __init__(self):
        self.web_results: str = ""
        self.rag_results: str = ""
        self.es_results: str = ""
        self.has_results: bool = False
    
    def get_aggregated_context(self) -> str:
        """
        Aggregate all search results into a single context string.
        
        Returns:
            Formatted string containing all search results
        """
        sections = []
        
        if self.web_results:
            sections.append(f"=== Web Search Results ===\n{self.web_results}")
        
        if self.rag_results:
            sections.append(f"=== Knowledge Base (RAG) Results ===\n{self.rag_results}")
        
        if self.es_results:
            sections.append(f"=== Database (Elasticsearch) Results ===\n{self.es_results}")
        
        if not sections:
            return ""
        
        self.has_results = True
        return "\n\n".join(sections)


async def _search_web(query: str, max_results: int = 5) -> str:
    """
    Execute web search asynchronously.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        Formatted web search results as string
    """
    try:
        logger.info(f"[Hybrid Search] Starting web search for: {query}")
        web_tool = get_web_search_tool(max_results)
        
        # Execute search (convert sync to async if needed)
        result = await asyncio.to_thread(web_tool.invoke, {"query": query})
        
        if result:
            logger.info(f"[Hybrid Search] Web search completed: {len(str(result))} chars")
            return str(result)
        else:
            logger.warning("[Hybrid Search] Web search returned no results")
            return ""
            
    except Exception as e:
        logger.error(f"[Hybrid Search] Web search failed: {e}")
        return f"Web search error: {str(e)}"


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
        if not resources or len(resources) == 0:
            logger.info(f"[Hybrid Search] Starting RAG search (global knowledge base) for: {query}")
        else:
            logger.info(f"[Hybrid Search] Starting RAG search ({len(resources)} resources) for: {query}")
        
        # Get retriever tool - will work even with empty resources
        # It will search the global knowledge base if no specific resources provided
        retriever_tool = get_retriever_tool(resources if resources else [])
        
        if not retriever_tool:
            logger.warning("[Hybrid Search] No RAG retriever available - check RAG_PROVIDER configuration")
            return ""
        
        # Execute search
        result = await asyncio.to_thread(retriever_tool.invoke, {"keywords": query})
        
        if result and result != "No results found from the local knowledge base.":
            # Format document results
            if isinstance(result, list):
                formatted_results = []
                for doc in result[:10]:  # Limit to top 10
                    if isinstance(doc, dict):
                        title = doc.get("title", "Untitled")
                        chunks = doc.get("chunks", [])
                        if chunks:
                            content = chunks[0].get("content", "")[:500]  # First 500 chars
                            formatted_results.append(f"**{title}**\n{content}")
                
                if formatted_results:
                    logger.info(f"[Hybrid Search] RAG search completed: {len(formatted_results)} documents from global knowledge base")
                    return "\n\n".join(formatted_results)
            
            logger.info(f"[Hybrid Search] RAG search completed: {len(str(result))} chars")
            return str(result)
        else:
            logger.warning("[Hybrid Search] RAG search returned no results")
            return ""
            
    except Exception as e:
        logger.error(f"[Hybrid Search] RAG search failed: {e}")
        import traceback
        traceback.print_exc()
        return f"RAG search error: {str(e)}"



async def _search_elasticsearch(query: str) -> str:
    """
    Execute Elasticsearch search asynchronously.
    
    Args:
        query: Search query string
        
    Returns:
        Formatted Elasticsearch results as string
    """
    try:
        logger.info(f"[Hybrid Search] Starting Elasticsearch search for: {query}")
        
        es_provider = ElasticsearchProvider()
        
        # Execute unified search
        documents = await asyncio.to_thread(
            es_provider.query_relevant_documents,
            query,
            []  # Empty resources for unified search
        )
        
        if documents:
            # Format results
            formatted_results = []
            for doc in documents[:10]:  # Limit to top 10
                title = doc.title or "Untitled"
                content = ""
                if doc.chunks:
                    content = doc.chunks[0].content[:500]  # First 500 chars
                formatted_results.append(f"**{title}**\n{content}")
            
            logger.info(f"[Hybrid Search] Elasticsearch completed: {len(documents)} documents")
            return "\n\n".join(formatted_results)
        else:
            logger.warning("[Hybrid Search] Elasticsearch returned no results")
            return ""
            
    except Exception as e:
        logger.error(f"[Hybrid Search] Elasticsearch search failed: {e}")
        return f"Elasticsearch error: {str(e)}"


async def parallel_search(
    query: str,
    resources: List[Resource] = None,
    enable_web: bool = True,
    enable_rag: bool = True,
    enable_es: bool = True,
    max_web_results: int = 5
) -> HybridSearchResult:
    """
    Execute parallel search across Web, RAG, and Elasticsearch sources.
    
    This function launches concurrent searches and aggregates results,
    regardless of whether resources are provided. This ensures that
    searches are always executed when called.
    
    Args:
        query: Search query string
        resources: Optional list of resources (ignored for forced search)
        enable_web: Enable web search (default: True)
        enable_rag: Enable RAG search (default: True)
        enable_es: Enable Elasticsearch search (default: True)
        max_web_results: Maximum web search results (default: 5)
        
    Returns:
        HybridSearchResult containing aggregated results from all sources
    """
    logger.info(f"[Hybrid Search] Starting parallel search for query: {query}")
    logger.info(f"[Hybrid Search] Enabled sources - Web: {enable_web}, RAG: {enable_rag}, ES: {enable_es}")
    
    result = HybridSearchResult()
    
    # Build list of search tasks
    tasks = []
    
    if enable_web:
        tasks.append(_search_web(query, max_web_results))
    
    if enable_rag:
        tasks.append(_search_rag(query, resources))
    
    if enable_es:
        tasks.append(_search_elasticsearch(query))
    
    if not tasks:
        logger.warning("[Hybrid Search] No search sources enabled")
        return result
    
    # Execute all searches concurrently
    logger.info(f"[Hybrid Search] Launching {len(tasks)} concurrent searches")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Assign results to appropriate fields
    result_index = 0
    
    if enable_web:
        if isinstance(results[result_index], Exception):
            logger.error(f"[Hybrid Search] Web search exception: {results[result_index]}")
            result.web_results = f"Web search error: {str(results[result_index])}"
        else:
            result.web_results = results[result_index]
        result_index += 1
    
    if enable_rag:
        if isinstance(results[result_index], Exception):
            logger.error(f"[Hybrid Search] RAG search exception: {results[result_index]}")
            result.rag_results = f"RAG search error: {str(results[result_index])}"
        else:
            result.rag_results = results[result_index]
        result_index += 1
    
    if enable_es:
        if isinstance(results[result_index], Exception):
            logger.error(f"[Hybrid Search] ES search exception: {results[result_index]}")
            result.es_results = f"Elasticsearch error: {str(results[result_index])}"
        else:
            result.es_results = results[result_index]
        result_index += 1
    
    logger.info("[Hybrid Search] Parallel search completed")
    logger.info(f"[Hybrid Search] Results - Web: {len(result.web_results)} chars, "
                f"RAG: {len(result.rag_results)} chars, ES: {len(result.es_results)} chars")
    
    return result
