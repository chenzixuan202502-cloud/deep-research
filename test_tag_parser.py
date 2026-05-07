#!/usr/bin/env python3
"""
测试数据库标签解析功能

测试 @Elasticsearch 和 @RAG 标签是否能正确转换为 Resource 对象
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.rag.retriever import Resource


def parse_database_tags(text: str) -> list:
    """
    Parse database tags from user input and convert them to Resource objects.
    
    Supported tags:
    - @Elasticsearch or @ES -> Elasticsearch全库搜索
    - @RAG or @RAGFlow -> RAGFlow数据库
    """
    import re
    resources = []
    
    # Pattern to match @Elasticsearch, @ES, @RAG, @RAGFlow (case-insensitive)
    elasticsearch_pattern = r'@(?:Elasticsearch|ES)\b'
    rag_pattern = r'@(?:RAG|RAGFlow)\b'
    
    # Check for Elasticsearch tags
    if re.search(elasticsearch_pattern, text, re.IGNORECASE):
        resources.append(Resource(
            uri="elasticsearch://es_global_search",
            title="Elasticsearch 全库搜索",
            description="搜索包含新闻、帖子、实体等在内的所有Elasticsearch数据库"
        ))
        print("✅ Detected @Elasticsearch tag")
    
    # Check for RAG tags
    if re.search(rag_pattern, text, re.IGNORECASE):
        resources.append(Resource(
            uri="rag://dataset/default",
            title="RAGFlow 知识库",
            description="RAGFlow向量数据库知识库"
        ))
        print("✅ Detected @RAG tag")
    
    return resources


def test_elasticsearch_tag():
    """测试 @Elasticsearch 标签"""
    print("\n" + "="*60)
    print("测试1: @Elasticsearch 标签")
    print("="*60)
    
    test_cases = [
        "@Elasticsearch 帮我查询新闻数据",
        "使用 @elasticsearch 搜索相关信息",
        "@ES 查询实体信息",
        "@es 搜索",
    ]
    
    for text in test_cases:
        print(f"\n输入: {text}")
        resources = parse_database_tags(text)
        if resources:
            for r in resources:
                print(f"  资源: {r.title}")
                print(f"  URI: {r.uri}")
        else:
            print("  ❌ 未检测到资源")


def test_rag_tag():
    """测试 @RAG 标签"""
    print("\n" + "="*60)
    print("测试2: @RAG 标签")
    print("="*60)
    
    test_cases = [
        "@RAG 查询知识库",
        "使用 @rag 搜索文档",
        "@RAGFlow 检索信息",
        "@ragflow 查询",
    ]
    
    for text in test_cases:
        print(f"\n输入: {text}")
        resources = parse_database_tags(text)
        if resources:
            for r in resources:
                print(f"  资源: {r.title}")
                print(f"  URI: {r.uri}")
        else:
            print("  ❌ 未检测到资源")


def test_both_tags():
    """测试同时使用两个标签"""
    print("\n" + "="*60)
    print("测试3: 同时使用 @Elasticsearch 和 @RAG")
    print("="*60)
    
    text = "@Elasticsearch @RAG 同时查询两个数据库"
    print(f"\n输入: {text}")
    resources = parse_database_tags(text)
    
    if len(resources) == 2:
        print("✅ 正确检测到2个资源")
        for r in resources:
            print(f"  - {r.title} ({r.uri})")
    else:
        print(f"❌ 错误：应该检测到2个资源，但检测到{len(resources)}个")


def test_no_tags():
    """测试没有标签的情况"""
    print("\n" + "="*60)
    print("测试4: 没有数据库标签")
    print("="*60)
    
    text = "普通的查询请求，没有任何标签"
    print(f"\n输入: {text}")
    resources = parse_database_tags(text)
    
    if len(resources) == 0:
        print("✅ 正确：没有检测到资源")
    else:
        print(f"❌ 错误：不应该检测到资源，但检测到{len(resources)}个")


def test_partial_match():
    """测试部分匹配（应该不匹配）"""
    print("\n" + "="*60)
    print("测试5: 部分匹配测试")
    print("="*60)
    
    test_cases = [
        "Elasticsearch 没有@符号",  # 应该不匹配
        "这是一个@test标签",  # 应该不匹配
        "@RAGFlowExtra 额外字符",  # 应该不匹配（因为有额外字符）
    ]
    
    for text in test_cases:
        print(f"\n输入: {text}")
        resources = parse_database_tags(text)
        if len(resources) == 0:
            print("  ✅ 正确：没有检测到资源")
        else:
            print(f"  ⚠️  检测到{len(resources)}个资源（可能是误匹配）")
            for r in resources:
                print(f"    - {r.title}")


def test_mixed_content():
    """测试混合内容"""
    print("\n" + "="*60)
    print("测试6: 混合内容测试")
    print("="*60)
    
    text = """
    请帮我查询以下信息：
    1. 使用 @Elasticsearch 搜索新闻数据
    2. 然后用 @RAG 查询知识库
    3. 最后综合分析结果
    """
    
    print(f"\n输入: {text}")
    resources = parse_database_tags(text)
    
    if len(resources) == 2:
        print("✅ 正确检测到2个资源")
        for r in resources:
            print(f"  - {r.title} ({r.uri})")
    else:
        print(f"❌ 错误：应该检测到2个资源，但检测到{len(resources)}个")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("数据库标签解析功能测试")
    print("="*60)
    
    try:
        test_elasticsearch_tag()
        test_rag_tag()
        test_both_tags()
        test_no_tags()
        test_partial_match()
        test_mixed_content()
        
        print("\n" + "="*60)
        print("测试完成！")
        print("="*60)
        print("\n使用说明：")
        print("- 在用户输入中使用 @Elasticsearch 或 @ES 来引用Elasticsearch数据库")
        print("- 使用 @RAG 或 @RAGFlow 来引用RAGFlow知识库")
        print("- 标签不区分大小写")
        print("- 可以在同一个查询中使用多个标签")
        print()
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
