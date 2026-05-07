#!/usr/bin/env python3
"""
测试选择性数据库搜索功能

测试场景：
1. 引用RAGFlow数据库 - 应该只使用RAGFlowProvider
2. 引用Elasticsearch数据库 - 应该只使用ElasticsearchProvider
3. 不引用数据库 - 不应该创建retriever tool
4. 同时引用两种数据库 - 应该使用CompositeRetriever
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.rag.retriever import Resource
from src.rag.builder import build_retriever
from src.tools.retriever import get_retriever_tool


def test_ragflow_only():
    """测试场景1: 只引用RAGFlow数据库"""
    print("\n" + "="*60)
    print("测试场景1: 只引用RAGFlow数据库")
    print("="*60)
    
    resources = [
        Resource(
            uri="rag://dataset/test123",
            title="测试RAGFlow数据集",
            description="这是一个测试数据集"
        )
    ]
    
    retriever = build_retriever(resources)
    
    if retriever:
        print(f"✅ 成功创建retriever: {retriever.__class__.__name__}")
        if retriever.__class__.__name__ == "RAGFlowProvider":
            print("✅ 正确：只使用了RAGFlowProvider")
        else:
            print(f"❌ 错误：应该使用RAGFlowProvider，但使用了{retriever.__class__.__name__}")
    else:
        print("❌ 错误：应该创建retriever但返回了None")


def test_elasticsearch_only():
    """测试场景2: 只引用Elasticsearch数据库"""
    print("\n" + "="*60)
    print("测试场景2: 只引用Elasticsearch数据库")
    print("="*60)
    
    resources = [
        Resource(
            uri="elasticsearch://es_global_search",
            title="Elasticsearch全库搜索",
            description="搜索所有Elasticsearch索引"
        )
    ]
    
    retriever = build_retriever(resources)
    
    if retriever:
        print(f"✅ 成功创建retriever: {retriever.__class__.__name__}")
        if retriever.__class__.__name__ == "ElasticsearchProvider":
            print("✅ 正确：只使用了ElasticsearchProvider")
        else:
            print(f"❌ 错误：应该使用ElasticsearchProvider，但使用了{retriever.__class__.__name__}")
    else:
        print("❌ 错误：应该创建retriever但返回了None")


def test_no_resources():
    """测试场景3: 不引用任何数据库"""
    print("\n" + "="*60)
    print("测试场景3: 不引用任何数据库")
    print("="*60)
    
    resources = []
    
    tool = get_retriever_tool(resources)
    
    if tool is None:
        print("✅ 正确：没有资源时不创建retriever tool")
    else:
        print(f"❌ 错误：没有资源时不应该创建retriever tool，但创建了{tool}")


def test_both_databases():
    """测试场景4: 同时引用两种数据库"""
    print("\n" + "="*60)
    print("测试场景4: 同时引用两种数据库")
    print("="*60)
    
    resources = [
        Resource(
            uri="rag://dataset/test123",
            title="测试RAGFlow数据集",
            description="这是一个测试数据集"
        ),
        Resource(
            uri="elasticsearch://es_global_search",
            title="Elasticsearch全库搜索",
            description="搜索所有Elasticsearch索引"
        )
    ]
    
    retriever = build_retriever(resources)
    
    if retriever:
        print(f"✅ 成功创建retriever: {retriever.__class__.__name__}")
        if retriever.__class__.__name__ == "CompositeRetriever":
            print("✅ 正确：同时引用两种数据库时使用CompositeRetriever")
        else:
            print(f"⚠️  警告：同时引用两种数据库时应该使用CompositeRetriever，但使用了{retriever.__class__.__name__}")
    else:
        print("❌ 错误：应该创建retriever但返回了None")


def test_unknown_resource():
    """测试场景5: 引用未知类型的资源"""
    print("\n" + "="*60)
    print("测试场景5: 引用未知类型的资源")
    print("="*60)
    
    resources = [
        Resource(
            uri="unknown://some/resource",
            title="未知资源",
            description="这是一个未知类型的资源"
        )
    ]
    
    retriever = build_retriever(resources)
    
    if retriever is None:
        print("✅ 正确：未知资源类型时不创建retriever")
    else:
        print(f"⚠️  警告：未知资源类型时应该返回None，但创建了{retriever.__class__.__name__}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("选择性数据库搜索功能测试")
    print("="*60)
    
    # 检查环境变量
    rag_provider = os.getenv("RAG_PROVIDER")
    print(f"\n当前RAG_PROVIDER配置: {rag_provider}")
    
    if not rag_provider:
        print("❌ 错误：RAG_PROVIDER环境变量未设置")
        print("请在.env文件中设置: RAG_PROVIDER=ragflow,elasticsearch")
        sys.exit(1)
    
    # 运行测试
    try:
        test_ragflow_only()
        test_elasticsearch_only()
        test_no_resources()
        test_both_databases()
        test_unknown_resource()
        
        print("\n" + "="*60)
        print("测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
