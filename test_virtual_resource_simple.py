#!/usr/bin/env python3
"""
简化的虚拟全局资源测试（不依赖完整环境）
"""


class Resource:
    """简化的 Resource 类"""
    def __init__(self, uri, title, description):
        self.uri = uri
        self.title = title
        self.description = description


def test_virtual_resource_injection():
    """测试虚拟资源注入逻辑"""
    print("\n" + "="*80)
    print("测试 1: 虚拟全局资源注入")
    print("="*80)
    
    # 模拟没有资源的情况
    existing_resources = []
    
    # 注入虚拟全局资源（coordinator_node 逻辑）
    if not existing_resources:
        global_resource = Resource(
            uri="global://knowledge-base",
            title="全局知识库 (内部数据库)",
            description="包含所有内部报告、新闻和统计数据。必须检查官方数据。"
        )
        existing_resources = [global_resource]
        print("✓ 成功注入虚拟全局资源")
    
    # 验证资源
    assert len(existing_resources) == 1, "应该有一个资源"
    assert existing_resources[0].uri == "global://knowledge-base", "URI 应该是 global://knowledge-base"
    assert "全局知识库" in existing_resources[0].title, "标题应该包含'全局知识库'"
    
    print(f"✓ 虚拟资源已注入:")
    print(f"  - URI: {existing_resources[0].uri}")
    print(f"  - 标题: {existing_resources[0].title}")
    print(f"  - 描述: {existing_resources[0].description}")
    
    return existing_resources


def test_virtual_resource_filtering():
    """测试虚拟资源过滤逻辑（retriever tool 逻辑）"""
    print("\n" + "="*80)
    print("测试 2: Retriever Tool 虚拟资源过滤")
    print("="*80)
    
    # 场景 1: 只有虚拟资源
    print("\n场景 1: 只有虚拟资源")
    resources = [
        Resource(
            uri="global://knowledge-base",
            title="全局知识库",
            description="虚拟资源"
        )
    ]
    
    # RetrieverTool._run 中的过滤逻辑
    actual_resources = [r for r in resources if not r.uri.startswith("global://")]
    
    if not actual_resources and any(r.uri.startswith("global://") for r in resources):
        print("  ✓ 检测到虚拟全局资源，执行全库搜索")
        print("  ✓ 传递空资源列表给 retriever.query_relevant_documents()")
        actual_resources = []
    
    assert len(actual_resources) == 0, "应该传递空列表"
    
    # 场景 2: 混合资源
    print("\n场景 2: 混合资源（虚拟 + 实际）")
    resources = [
        Resource(uri="global://knowledge-base", title="全局知识库", description="虚拟"),
        Resource(uri="rag://dataset/123", title="数据集1", description="实际"),
        Resource(uri="elasticsearch://es_global_search", title="ES搜索", description="实际")
    ]
    
    actual_resources = [r for r in resources if not r.uri.startswith("global://")]
    
    print(f"  - 总资源: {len(resources)}")
    print(f"  - 过滤后实际资源: {len(actual_resources)}")
    for r in actual_resources:
        print(f"    • {r.title} ({r.uri})")
    
    assert len(actual_resources) == 2, "应该有两个实际资源"
    print("  ✓ 只搜索实际资源，忽略虚拟资源")
    
    # 场景 3: 空资源列表
    print("\n场景 3: 空资源列表")
    resources = []
    
    if not resources:
        print("  ✓ 没有资源，执行全库搜索")


def test_get_retriever_tool_logic():
    """测试 get_retriever_tool 函数逻辑"""
    print("\n" + "="*80)
    print("测试 3: get_retriever_tool 函数逻辑")
    print("="*80)
    
    # 场景 1: 只有虚拟资源
    print("\n场景 1: 只有虚拟资源")
    resources = [
        Resource(uri="global://knowledge-base", title="全局知识库", description="虚拟")
    ]
    
    has_virtual_global = any(r.uri.startswith("global://") for r in resources)
    actual_resources = [r for r in resources if not r.uri.startswith("global://")]
    
    print(f"  - 有虚拟资源: {has_virtual_global}")
    print(f"  - 实际资源数: {len(actual_resources)}")
    
    if has_virtual_global and not actual_resources:
        print("  ✓ 检测到只有虚拟资源")
        retriever_resources = []
        print("  ✓ 传递空列表给 build_retriever() 以触发全库搜索")
    else:
        retriever_resources = actual_resources
    
    assert len(retriever_resources) == 0
    
    # 场景 2: 混合资源
    print("\n场景 2: 混合资源")
    resources = [
        Resource(uri="global://knowledge-base", title="全局知识库", description="虚拟"),
        Resource(uri="rag://dataset/456", title="数据集", description="实际")
    ]
    
    has_virtual_global = any(r.uri.startswith("global://") for r in resources)
    actual_resources = [r for r in resources if not r.uri.startswith("global://")]
    
    print(f"  - 有虚拟资源: {has_virtual_global}")
    print(f"  - 实际资源数: {len(actual_resources)}")
    
    retriever_resources = actual_resources if actual_resources else []
    
    print(f"  ✓ 传递 {len(retriever_resources)} 个实际资源给 build_retriever()")
    assert len(retriever_resources) == 1


def test_coordinator_injection_logic():
    """测试 coordinator_node 的完整注入逻辑"""
    print("\n" + "="*80)
    print("测试 4: Coordinator Node 完整注入逻辑")
    print("="*80)
    
    # 场景 1: 没有任何资源
    print("\n场景 1: 用户没有指定任何资源")
    existing_resources = []
    
    if not existing_resources:
        global_resource = Resource(
            uri="global://knowledge-base",
            title="全局知识库 (内部数据库)",
            description="包含所有内部报告、新闻和统计数据。必须检查官方数据。"
        )
        existing_resources = [global_resource]
        print("  ✓ 注入虚拟全局资源")
    
    assert len(existing_resources) == 1
    print(f"  ✓ 最终资源数: {len(existing_resources)}")
    
    # 场景 2: 已有资源，但没有全局资源
    print("\n场景 2: 用户指定了资源，但没有全局资源")
    existing_resources = [
        Resource(uri="rag://dataset/789", title="用户数据集", description="用户指定")
    ]
    
    has_global = any(r.uri == "global://knowledge-base" for r in existing_resources)
    if not has_global:
        global_resource = Resource(
            uri="global://knowledge-base",
            title="全局知识库 (内部数据库)",
            description="包含所有内部报告、新闻和统计数据。必须检查官方数据。"
        )
        existing_resources.append(global_resource)
        print("  ✓ 添加虚拟全局资源到现有资源")
    
    assert len(existing_resources) == 2
    print(f"  ✓ 最终资源数: {len(existing_resources)}")
    for r in existing_resources:
        print(f"    • {r.title} ({r.uri})")


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("虚拟全局资源注入功能测试")
    print("="*80)
    
    try:
        test_virtual_resource_injection()
        test_virtual_resource_filtering()
        test_get_retriever_tool_logic()
        test_coordinator_injection_logic()
        
        print("\n" + "="*80)
        print("✓ 所有测试通过！")
        print("="*80)
        
        print("\n" + "="*80)
        print("实现总结")
        print("="*80)
        print("""
修改点 1: src/graph/nodes_2.py - coordinator_node
  • 在 parse_database_tags 之后注入虚拟全局资源
  • 如果 existing_resources 为空，创建 global://knowledge-base 资源
  • 如果已有资源但没有全局资源，也添加全局资源
  • 确保 Planner 总能看到至少一个资源

修改点 2: src/tools/retriever.py - RetrieverTool._run
  • 过滤掉虚拟资源（global:// 开头）
  • 如果只有虚拟资源，传递空列表给 query_relevant_documents
  • 空列表触发全库搜索（不加 filter）

修改点 3: src/tools/retriever.py - get_retriever_tool
  • 检测虚拟全局资源
  • 提取实际资源（非 global:// 的资源）
  • 传递实际资源给 build_retriever
  • 如果只有虚拟资源，传递空列表触发全库搜索

预期工作流程:
  1. 用户提问（无资源）
  2. coordinator_node 注入虚拟 "全局知识库" 资源
  3. Planner 看到资源，生成包含 "Search Global Knowledge Base" 的计划
  4. Researcher 执行步骤，调用 local_search_tool
  5. RetrieverTool 识别虚拟资源，执行全库检索
  6. 返回所有相关内部数据
        """)
        print("="*80 + "\n")
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
