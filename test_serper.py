# 正确的包装方式
import asyncio
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import GoogleSerperRun

# 需要在运行前设置环境变量
import os
os.environ["SERPER_API_KEY"] = "eb62ba04c6fd015e96c23b2a4a73d5f600002aec"

search = GoogleSerperAPIWrapper()
tool = GoogleSerperRun(api_wrapper=search)

# 创建一个简单的测试
async def test_serper_tool():
    from langchain_community.tools import GoogleSerperRun
    from langchain_community.utilities import GoogleSerperAPIWrapper
    
    # LoggedSerperSearch = create_logged_tool(GoogleSerperRun)

    search = GoogleSerperAPIWrapper()
    tool = GoogleSerperRun(api_wrapper=search)
    
    # 测试直接调用
    result = await tool.arun("埃菲尔铁塔高度")
    print(f"Result: {result}")

async def test_langgraph_style():
    """模拟LangGraph调用方式"""
    search_wrapper = GoogleSerperAPIWrapper()
    tool = GoogleSerperRun(api_wrapper=search_wrapper)
    
    # 测试不同的调用方式
    print("测试方式1: 直接字符串")
    try:
        result = await tool.arun("埃菲尔铁塔高度")
        print(f"Result_1: {result}")
        print("✅ 方式1成功")
    except Exception as e:
        print(f"❌ 方式1失败: {e}")
    
    print("\n测试方式2: 字典参数")
    try:
        # 模拟可能的LangGraph调用
        result = await tool.arun({"query": "埃菲尔铁塔高度"})
        print(f"Result_2: {result}")
        print("✅ 方式2成功")
    except Exception as e:
        print(f"❌ 方式2失败: {e}")
    
    print("\n测试方式3: ainvoke方法")
    try:
        result = await tool.ainvoke({"query": "埃菲尔铁塔高度"})
        print(f"Result_3: {result}")
        print("✅ 方式3成功")
    except Exception as e:
        print(f"❌ 方式3失败: {e}")

if __name__ == "__main__":
    # asyncio.run(test_serper_tool())
    asyncio.run(test_langgraph_style())