#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Test script for RAG global search functionality.
Tests that RAG search works even without specific resources.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph.hybrid_search import _search_rag
from src.rag import Resource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_rag_with_empty_resources():
    """Test RAG search with empty resources list."""
    logger.info("=" * 80)
    logger.info("TEST 1: RAG Search with Empty Resources (Global Knowledge Base)")
    logger.info("=" * 80)
    
    # Check if RAG_PROVIDER is configured
    rag_provider = os.getenv("RAG_PROVIDER")
    if not rag_provider:
        logger.warning("RAG_PROVIDER not configured. Skipping test.")
        logger.warning("Set RAG_PROVIDER environment variable to test (e.g., RAG_PROVIDER=ragflow)")
        return None
    
    logger.info(f"RAG_PROVIDER configured: {rag_provider}")
    
    query = "人工智能"
    
    # Test with empty resources list
    result = await _search_rag(query, resources=[])
    
    logger.info(f"\nQuery: {query}")
    logger.info(f"Resources: [] (empty - should search global knowledge base)")
    logger.info(f"Result length: {len(result)} chars")
    
    if result:
        logger.info("\n--- RAG Search Result Preview (first 500 chars) ---")
        logger.info(result[:500])
        logger.info("\n✓ SUCCESS: RAG search returned results from global knowledge base")
    else:
        logger.warning("\n⚠ WARNING: RAG search returned no results")
        logger.warning("This could mean:")
        logger.warning("1. Global knowledge base is empty")
        logger.warning("2. Query didn't match any documents")
        logger.warning("3. RAG provider configuration issue")
    
    return result


async def test_rag_with_none_resources():
    """Test RAG search with None resources."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: RAG Search with None Resources")
    logger.info("=" * 80)
    
    # Check if RAG_PROVIDER is configured
    rag_provider = os.getenv("RAG_PROVIDER")
    if not rag_provider:
        logger.warning("RAG_PROVIDER not configured. Skipping test.")
        return None
    
    query = "机器学习"
    
    # Test with None resources
    result = await _search_rag(query, resources=None)
    
    logger.info(f"\nQuery: {query}")
    logger.info(f"Resources: None (should search global knowledge base)")
    logger.info(f"Result length: {len(result)} chars")
    
    if result:
        logger.info("\n--- RAG Search Result Preview (first 500 chars) ---")
        logger.info(result[:500])
        logger.info("\n✓ SUCCESS: RAG search returned results from global knowledge base")
    else:
        logger.warning("\n⚠ WARNING: RAG search returned no results")
    
    return result


async def test_rag_with_specific_resources():
    """Test RAG search with specific resources."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: RAG Search with Specific Resources")
    logger.info("=" * 80)
    
    # Check if RAG_PROVIDER is configured
    rag_provider = os.getenv("RAG_PROVIDER")
    if not rag_provider:
        logger.warning("RAG_PROVIDER not configured. Skipping test.")
        return None
    
    query = "深度学习"
    
    # Create test resources
    resources = [
        Resource(
            uri="rag://dataset/test",
            title="Test Dataset",
            description="Test RAG dataset"
        )
    ]
    
    # Test with specific resources
    result = await _search_rag(query, resources=resources)
    
    logger.info(f"\nQuery: {query}")
    logger.info(f"Resources: {[r.title for r in resources]}")
    logger.info(f"Result length: {len(result)} chars")
    
    if result:
        logger.info("\n--- RAG Search Result Preview (first 500 chars) ---")
        logger.info(result[:500])
        logger.info("\n✓ SUCCESS: RAG search returned results")
    else:
        logger.warning("\n⚠ WARNING: RAG search returned no results")
    
    return result


async def test_retriever_tool_creation():
    """Test retriever tool creation with empty resources."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Retriever Tool Creation with Empty Resources")
    logger.info("=" * 80)
    
    from src.tools.retriever import get_retriever_tool
    
    # Check if RAG_PROVIDER is configured
    rag_provider = os.getenv("RAG_PROVIDER")
    if not rag_provider:
        logger.warning("RAG_PROVIDER not configured. Skipping test.")
        return None
    
    logger.info(f"RAG_PROVIDER configured: {rag_provider}")
    
    # Test with empty resources
    retriever_tool = get_retriever_tool([])
    
    if retriever_tool:
        logger.info(f"✓ SUCCESS: Retriever tool created: {retriever_tool.__class__.__name__}")
        logger.info(f"  Retriever: {retriever_tool.retriever.__class__.__name__}")
        logger.info(f"  Resources: {retriever_tool.resources}")
    else:
        logger.error("✗ FAILED: Retriever tool not created")
        logger.error("Check RAG_PROVIDER configuration and provider initialization")
    
    return retriever_tool


async def main():
    """Run all tests."""
    logger.info("Starting RAG Global Search Tests")
    logger.info("=" * 80)
    
    # Check environment
    rag_provider = os.getenv("RAG_PROVIDER")
    if not rag_provider:
        logger.error("\n" + "!" * 80)
        logger.error("ERROR: RAG_PROVIDER environment variable not set!")
        logger.error("!" * 80)
        logger.error("\nPlease set RAG_PROVIDER to test RAG functionality.")
        logger.error("Examples:")
        logger.error("  export RAG_PROVIDER=ragflow")
        logger.error("  export RAG_PROVIDER=milvus")
        logger.error("  export RAG_PROVIDER=qdrant")
        logger.error("\nAlso ensure provider-specific configuration is set.")
        logger.error("=" * 80)
        sys.exit(1)
    
    try:
        # Test 1: Empty resources
        result1 = await test_rag_with_empty_resources()
        
        # Test 2: None resources
        result2 = await test_rag_with_none_resources()
        
        # Test 3: Specific resources
        result3 = await test_rag_with_specific_resources()
        
        # Test 4: Tool creation
        tool = await test_retriever_tool_creation()
        
        logger.info("\n" + "=" * 80)
        logger.info("Test Summary")
        logger.info("=" * 80)
        logger.info(f"Test 1 (Empty resources): {'✓ PASS' if result1 else '⚠ NO RESULTS'}")
        logger.info(f"Test 2 (None resources): {'✓ PASS' if result2 else '⚠ NO RESULTS'}")
        logger.info(f"Test 3 (Specific resources): {'✓ PASS' if result3 else '⚠ NO RESULTS'}")
        logger.info(f"Test 4 (Tool creation): {'✓ PASS' if tool else '✗ FAIL'}")
        logger.info("=" * 80)
        
        if tool and (result1 or result2):
            logger.info("\n✓ SUCCESS: RAG global search is working!")
            logger.info("The system can now search the global knowledge base even without specific resources.")
        else:
            logger.warning("\n⚠ WARNING: Some tests did not return results.")
            logger.warning("This may be expected if the global knowledge base is empty.")
        
    except Exception as e:
        logger.error(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
