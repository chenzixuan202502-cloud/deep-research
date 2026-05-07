#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Test script for hybrid search implementation.
Tests the parallel search functionality across Web, RAG, and Elasticsearch.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph.hybrid_search import parallel_search
from src.rag import Resource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_basic_search():
    """Test basic parallel search without resources."""
    logger.info("=" * 80)
    logger.info("TEST 1: Basic Parallel Search (No Resources)")
    logger.info("=" * 80)
    
    query = "人工智能的最新发展"
    
    result = await parallel_search(
        query=query,
        resources=[],
        enable_web=True,
        enable_rag=False,  # Disable RAG if no resources
        enable_es=True,
        max_web_results=3
    )
    
    context = result.get_aggregated_context()
    
    logger.info(f"\nQuery: {query}")
    logger.info(f"Has Results: {result.has_results}")
    logger.info(f"Web Results Length: {len(result.web_results)} chars")
    logger.info(f"RAG Results Length: {len(result.rag_results)} chars")
    logger.info(f"ES Results Length: {len(result.es_results)} chars")
    logger.info(f"Total Context Length: {len(context)} chars")
    
    if context:
        logger.info("\n--- Aggregated Context Preview (first 500 chars) ---")
        logger.info(context[:500])
    else:
        logger.warning("No context retrieved!")
    
    return result


async def test_with_resources():
    """Test parallel search with explicit resources."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Parallel Search with Resources")
    logger.info("=" * 80)
    
    query = "新闻数据分析"
    
    # Create test resources
    resources = [
        Resource(
            uri="elasticsearch://es_global_search",
            title="Elasticsearch 全库搜索",
            description="搜索包含新闻、帖子、实体等在内的所有数据库"
        )
    ]
    
    result = await parallel_search(
        query=query,
        resources=resources,
        enable_web=True,
        enable_rag=False,
        enable_es=True,
        max_web_results=3
    )
    
    context = result.get_aggregated_context()
    
    logger.info(f"\nQuery: {query}")
    logger.info(f"Resources: {[r.title for r in resources]}")
    logger.info(f"Has Results: {result.has_results}")
    logger.info(f"Web Results Length: {len(result.web_results)} chars")
    logger.info(f"RAG Results Length: {len(result.rag_results)} chars")
    logger.info(f"ES Results Length: {len(result.es_results)} chars")
    logger.info(f"Total Context Length: {len(context)} chars")
    
    if context:
        logger.info("\n--- Aggregated Context Preview (first 500 chars) ---")
        logger.info(context[:500])
    else:
        logger.warning("No context retrieved!")
    
    return result


async def test_selective_sources():
    """Test with selective source enablement."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Selective Source Search (Web Only)")
    logger.info("=" * 80)
    
    query = "Python programming best practices"
    
    result = await parallel_search(
        query=query,
        resources=[],
        enable_web=True,
        enable_rag=False,
        enable_es=False,
        max_web_results=5
    )
    
    context = result.get_aggregated_context()
    
    logger.info(f"\nQuery: {query}")
    logger.info(f"Enabled Sources: Web only")
    logger.info(f"Has Results: {result.has_results}")
    logger.info(f"Web Results Length: {len(result.web_results)} chars")
    logger.info(f"Total Context Length: {len(context)} chars")
    
    if context:
        logger.info("\n--- Aggregated Context Preview (first 500 chars) ---")
        logger.info(context[:500])
    else:
        logger.warning("No context retrieved!")
    
    return result


async def main():
    """Run all tests."""
    logger.info("Starting Hybrid Search Tests")
    logger.info("=" * 80)
    
    try:
        # Test 1: Basic search
        await test_basic_search()
        
        # Test 2: With resources
        await test_with_resources()
        
        # Test 3: Selective sources
        await test_selective_sources()
        
        logger.info("\n" + "=" * 80)
        logger.info("All tests completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
