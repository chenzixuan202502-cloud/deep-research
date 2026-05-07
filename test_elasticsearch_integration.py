#!/usr/bin/env python3
"""
Test script for Elasticsearch and multi-provider RAG integration.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag.builder import build_retriever

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_retriever():
    """Test the multi-provider retriever setup."""
    
    logger.info("=" * 80)
    logger.info("Testing Multi-Provider RAG Integration")
    logger.info("=" * 80)
    
    try:
        # Build retriever
        logger.info("\n1. Building retriever...")
        retriever = build_retriever()
        
        if retriever is None:
            logger.error("No retriever was built!")
            return False
        
        logger.info(f"✓ Retriever built successfully: {retriever.__class__.__name__}")
        
        # List resources
        logger.info("\n2. Listing resources...")
        resources = retriever.list_resources()
        logger.info(f"✓ Found {len(resources)} resources")
        
        if resources:
            logger.info("\nSample resources:")
            for i, resource in enumerate(resources[:5]):
                logger.info(f"  {i+1}. {resource.title} ({resource.uri})")
        
        # Test query
        logger.info("\n3. Testing query...")
        test_query = "中国 新闻"
        logger.info(f"Query: '{test_query}'")
        
        documents = retriever.query_relevant_documents(test_query, resources[:3] if resources else [])
        logger.info(f"✓ Query returned {len(documents)} documents")
        
        if documents:
            logger.info("\nSample documents:")
            for i, doc in enumerate(documents[:3]):
                logger.info(f"\n  Document {i+1}:")
                logger.info(f"    ID: {doc.id}")
                logger.info(f"    Title: {doc.title}")
                if doc.url:
                    logger.info(f"    URL: {doc.url}")
                if doc.chunks:
                    content_preview = doc.chunks[0].content[:200] + "..." if len(doc.chunks[0].content) > 200 else doc.chunks[0].content
                    logger.info(f"    Content: {content_preview}")
                    logger.info(f"    Similarity: {doc.chunks[0].similarity}")
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ All tests passed!")
        logger.info("=" * 80)
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Test failed with error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_retriever()
    sys.exit(0 if success else 1)
