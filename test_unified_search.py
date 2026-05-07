#!/usr/bin/env python3
"""
Test script to demonstrate the Unified Knowledge Base pattern.
Shows how a single resource provides access to all Elasticsearch indices.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.rag.builder import build_retriever


def main():
    print("\n" + "=" * 80)
    print("Elasticsearch Unified Knowledge Base - Demo")
    print("=" * 80 + "\n")
    
    # Build retriever
    print("1. Initializing retriever...")
    retriever = build_retriever()
    
    if not retriever:
        print("✗ Failed to initialize retriever")
        return
    
    print(f"✓ Retriever initialized: {retriever.__class__.__name__}\n")
    
    # List resources - should return only ONE unified resource
    print("2. Listing resources (Unified Mode)...")
    print("-" * 80)
    resources = retriever.list_resources()
    
    print(f"\n✓ Total resources: {len(resources)}")
    print("\nResource Details:")
    for i, resource in enumerate(resources, 1):
        print(f"\n  [{i}] {resource.title}")
        print(f"      URI: {resource.uri}")
        print(f"      Description: {resource.description}")
    
    # Test multiple queries to show cross-index search
    test_queries = [
        "中国 新闻",
        "美国 政治",
        "科技 创新",
    ]
    
    print("\n" + "=" * 80)
    print("3. Testing Unified Cross-Index Search")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 80)
        
        documents = retriever.query_relevant_documents(query)
        
        if not documents:
            print("  No documents found")
            continue
        
        print(f"  ✓ Found {len(documents)} documents across all indices\n")
        
        # Group by index to show cross-index results
        index_groups = {}
        for doc in documents:
            # Extract index name from document ID (format: index_name:doc_id)
            if ":" in doc.id:
                index_name = doc.id.split(":")[0]
            else:
                index_name = "unknown"
            
            if index_name not in index_groups:
                index_groups[index_name] = []
            index_groups[index_name].append(doc)
        
        print("  Results by Index:")
        for index_name, docs in sorted(index_groups.items()):
            print(f"    • {index_name}: {len(docs)} documents")
        
        # Show top 2 results
        print("\n  Top Results:")
        for i, doc in enumerate(documents[:2], 1):
            print(f"\n    [{i}] {doc.title}")
            print(f"        ID: {doc.id}")
            print(f"        Score: {doc.chunks[0].similarity:.2f}")
            content_preview = doc.chunks[0].content[:150].replace("\n", " ")
            print(f"        Preview: {content_preview}...")
    
    print("\n" + "=" * 80)
    print("✓ Unified Search Demo Complete!")
    print("=" * 80)
    print("\nKey Benefits:")
    print("  • Single entry point for all data")
    print("  • Automatic cross-index search")
    print("  • Field-agnostic querying (multi_match)")
    print("  • Results sorted by relevance across all indices")
    print("  • No need to know underlying data structure")
    print()


if __name__ == "__main__":
    main()
