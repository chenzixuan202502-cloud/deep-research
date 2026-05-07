#!/usr/bin/env python3
"""
测试 GLM 模型是否支持 Tool Calling
"""

import os

# 从配置文件读取配置
def get_config():
    """从 conf.yaml 读取配置"""
    config_path = os.path.join(os.path.dirname(__file__), "conf.yaml")
    
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 解析 BASIC_MODEL 配置
    basic_model = {}
    in_basic_model = False
    
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("BASIC_MODEL:"):
            in_basic_model = True
            continue
        if line and not line.startswith("#") and not line.startswith("-"):
            if ":" in line and not in_basic_model:
                in_basic_model = False
            elif "base_url:" in line and in_basic_model:
                basic_model["base_url"] = line.split(":", 1)[1].strip().strip('"')
            elif "model:" in line and in_basic_model:
                basic_model["model"] = line.split(":", 1)[1].strip().strip('"')
            elif "api_key:" in line and in_basic_model:
                basic_model["api_key"] = line.split(":", 1)[1].strip().strip('"')
    
    return basic_model


def main():
    from langchain_openai import ChatOpenAI
    from langchain_core.tools import tool
    
    # 读取配置
    config = get_config()
    print(f"配置: base_url={config.get('base_url')}, model={config.get('model')}")
    
    # 定义测试工具
    @tool
    def get_weather(city: str) -> str:
        """获取城市天气"""
        return f"{city}天气：晴，25°C"
    
    # 创建 LLM
    llm = ChatOpenAI(
        model=config.get("model"),
        base_url=config.get("base_url"),
        api_key=config.get("api_key"),
        temperature=0,
    )
    
    # 绑定工具并调用
    
    llm_with_tools = llm.bind_tools([get_weather])
    
    print("\n" + "=" * 50)
    print("🧪 测试 Tool Calling")
    print("=" * 50)
    
    # 测试 1: 天气查询
    print("\n📍 测试: 北京天气如何？")
    response = llm_with_tools.invoke("北京天气如何？")
    
    if response.tool_calls:
        print(f"✅ 成功! 工具调用: {response.tool_calls}")
    else:
        print(f"❌ 失败! 仅返回文本: {response.content}")
    
    # 测试 2: 强制调用
    print("\n🔧 测试: 强制调用工具")
    response = llm_with_tools.invoke([
        {"role": "system", "content": "You MUST call the tool. DO NOT answer directly."},
        {"role": "user", "content": "上海天气如何？"}
    ])
    
    if response.tool_calls:
        print(f"✅ 成功! 工具调用: {response.tool_calls}")
    else:
        print(f"❌ 失败! 仅返回文本: {response.content}")
    
    print("\n" + "=" * 50)
    print("📝 结论")
    print("=" * 50)


if __name__ == "__main__":
    main()
