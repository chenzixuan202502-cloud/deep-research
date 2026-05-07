#!/usr/bin/env python3
"""
测试 /api/deep-research/stream 接口

功能：
1. 测试接口连接
2. 统计各模块使用时间
3. 仅显示纯内容（无前缀、无阶段标识）
4. 最后统一展示最终报告

Usage:
    python3 test_deep_research.py
"""

import requests
import json
import sys
import time
import os
import yaml
from datetime import datetime
from collections import defaultdict

# 获取配置文件路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONF_FILE = os.path.join(SCRIPT_DIR, "conf.yaml")

# 测试接口地址
URL = "http://localhost:8088/api/deep-research/stream"


def load_config():
    """加载模型配置"""
    try:
        with open(CONF_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        basic_model = config.get("BASIC_MODEL", {})
        base_url = basic_model.get("base_url", "")
        model = basic_model.get("model", "")
        api_key = basic_model.get("api_key", "")

        if not base_url or not model:
            raise ValueError("BASIC_MODEL 配置不完整")

        base_url = base_url.rstrip("/")
        print(f"[配置] 模型: {model}")
        print(f"[配置] API地址: {base_url}")
        
        return base_url, model, api_key
    except FileNotFoundError:
        print(f"[错误] 配置文件不存在: {CONF_FILE}")
        sys.exit(1)
    except Exception as e:
        print(f"[错误] 配置加载失败: {e}")
        sys.exit(1)


# 加载配置
MODEL_BASE_URL, MODEL_NAME, MODEL_API_KEY = load_config()

# 测试请求
payload = {
    "messages": [{"role": "user", "content": "简单介绍一下日本今天的新闻"}],
    "locale": "zh-CN",
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MODEL_API_KEY}"
}


# 状态变量
module_times = defaultdict(float)
module_start_time = {}
current_module = None
event_counts = defaultdict(int)

# 收集最终内容
final_content = {
    "coordinator": "",
    "planner": "",
    "reporter": ""
}

# 工具调用记录
tool_calls_log = []
search_results_log = []


def print_progress(event_type, data):
    """打印进度（显示完整检索结果）"""
    if event_type == "tool_calls":
        tool_calls = data.get("tool_calls", [])
        for tc in tool_calls:
            name = tc.get("name", "?")
            tool_id = tc.get("id", "?")
            tool_calls_log.append({"name": name, "id": tool_id})
            
            if name == "search" or name == "web_search":
                args = tc.get("args", {})
                query = args.get("query", "")
                print(f"🔍 搜索: {query}")
            elif name == "fetch_page":
                args = tc.get("args", {})
                url = args.get("url", "")[:50]
                print(f"📄 获取页面: {url}...")
            else:
                print(f"🔧 工具: {name}")
    
    elif event_type == "tool_call_result":
        tool_id = data.get("tool_call_id", "?")
        content = data.get("content", "")
        
        # 尝试解析为 JSON 显示完整搜索结果
        try:
            results = json.loads(content)
            
            if isinstance(results, list) and len(results) > 0:
                # 搜索结果列表
                search_results_log.append(len(results))
                print(f"✓ 搜索结果: {len(results)}条")
                
                for i, r in enumerate(results):
                    if isinstance(r, dict):
                        title = r.get("title", "无标题")
                        url = r.get("url", "")
                        score = r.get("score", "")
                        
                        print(f"   [{i+1}] {title}")
                        print(f"       📎 {url}")
                        if score:
                            print(f"       ⭐ 相关度: {score:.2f}")
                    else:
                        print(f"   [{i+1}] {str(r)[:100]}")
                        
            elif isinstance(results, dict):
                # 字典类型的搜索结果
                print(f"✓ 工具结果:")
                for k, v in results.items():
                    if k == "results" and isinstance(v, list):
                        search_results_log.append(len(v))
                        print(f"   📊 结果数: {len(v)}条")
                        for i, r in enumerate(v[:3]):
                            title = r.get("title", "无标题") if isinstance(r, dict) else str(r)
                            url = r.get("url", "") if isinstance(r, dict) else ""
                            print(f"       [{i+1}] {title[:50]}")
                            if url:
                                print(f"           📎 {url}")
                    else:
                        print(f"   {k}: {str(v)[:60]}")
            else:
                print(f"✓ 工具完成: {str(results)[:100]}...")
                
        except (json.JSONDecodeError, TypeError):
            # 非 JSON 格式，直接显示内容
            if len(content) > 200:
                print(f"✓ 工具完成: {content[:200]}...")
            else:
                print(f"✓ 工具完成: {content}")


def print_content(content, agent):
    """打印纯内容（无任何前缀）"""
    if content:
        print(content, end="", flush=True)


def test_connection():
    """测试接口连接"""
    print("\n" + "="*60)
    print("步骤1: 测试接口连接")
    print("="*60)
    
    try:
        test_payload = {"messages": [{"role": "user", "content": "你好"}]}
        
        response = requests.post(URL, json=test_payload, headers=headers, 
                                timeout=10, stream=True)
        
        print(f"✅ 连接成功! 状态码: {response.status_code}")
        response.close()
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败")
        print(f"   请确保 DeerFlow 服务器正在运行")
        return False
    except requests.exceptions.Timeout:
        print(f"⚠️ 连接超时，但接口可能正常")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def stream_request():
    """流式请求"""
    global current_module
    
    print("\n" + "="*60)
    print("步骤2: 流式请求")
    print("="*60)
    print(f"问题: {payload['messages'][0]['content']}\n")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        with requests.post(URL, json=payload, stream=True, headers=headers, timeout=600) as r:
            r.raise_for_status()
            
            buffer = ""
            
            for raw_chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
                if not raw_chunk:
                    continue
                
                buffer += raw_chunk
                
                while "\n\n" in buffer:
                    chunk, buffer = buffer.split("\n\n", 1)
                    lines = chunk.strip().split("\n")
                    
                    event_type = None
                    event_data = None
                    
                    for line in lines:
                        if line.startswith("event:"):
                            event_type = line[6:].strip()
                        elif line.startswith("data:"):
                            event_data = line[5:].strip()
                    
                    if not event_type or not event_data:
                        continue
                    
                    try:
                        data = json.loads(event_data)
                    except json.JSONDecodeError:
                        continue
                    
                    # 统计事件
                    event_counts[event_type] += 1
                    
                    # 调试：打印所有事件类型
                    # print(f"[DEBUG] event_type={event_type}, agent={data.get('agent', '?')}, content_len={len(data.get('content', ''))}")
                    
                    # 根据 agent 判断阶段
                    agent = data.get("agent", "")
                    if agent == "coordinator":
                        if current_module != "coordinator":
                            module_start_time["coordinator"] = time.time()
                            current_module = "coordinator"
                            print("\n" + "-" * 60)
                    elif agent == "planner":
                        if current_module != "planner":
                            if current_module and current_module in module_start_time:
                                module_times[current_module] = time.time() - module_start_time[current_module]
                            module_start_time["planner"] = time.time()
                            current_module = "planner"
                            print("\n" + "-" * 60)
                    elif agent == "reporter":
                        if current_module != "reporter":
                            if current_module and current_module in module_start_time:
                                module_times[current_module] = time.time() - module_start_time[current_module]
                            module_start_time["reporter"] = time.time()
                            current_module = "reporter"
                            print("\n" + "-" * 60)
                    
                    # 收集内容
                    content = data.get("content", "")
                    if agent in final_content:
                        final_content[agent] += content
                    
                    # 打印纯内容（无前缀）
                    if event_type == "message_chunk" and content:
                        print_content(content, agent)
                    
                    # 打印进度（不含内容）
                    print_progress(event_type, data)
                    
                    # 处理错误事件
                    if event_type == "error":
                        error_msg = data.get("error", "未知错误")
                        print(f"\n❌ 后端错误: {error_msg}")
                        break
                    
                    # 检查是否正常结束
                    finish_reason = data.get("finish_reason", "")
                    if finish_reason in ["stop", "end_turn", "completed"]:
                        print(f"\n✓ 流正常结束 (finish_reason: {finish_reason})")
            
            # 检查是否有未处理的数据
            if buffer.strip():
                print(f"\n⚠️ 还有未处理的数据: {buffer[:200]}")
            
            # 结束计时
            if current_module and current_module in module_start_time:
                module_times[current_module] = time.time() - module_start_time[current_module]
            
            total_time = time.time() - start_time
            
            print("\n" + "="*60)
            print("执行完成")
            print("="*60)
            
            # 统计信息
            print(f"\n总耗时: {total_time:.2f}秒")
            
            # 打印事件统计（调试用）
            if event_counts:
                print(f"\n事件统计:")
                for evt, cnt in sorted(event_counts.items(), key=lambda x: -x[1]):
                    print(f"  {evt}: {cnt}次")
            
            print(f"\n模块耗时:")
            for module, t in sorted(module_times.items(), key=lambda x: -x[1]):
                percentage = (t / total_time) * 100
                name = {"coordinator": "协调者", "planner": "规划者", "reporter": "报告者"}.get(module, module)
                print(f"  {name}: {t:.2f}秒 ({percentage:.1f}%)")
            
            if tool_calls_log:
                print(f"\n工具调用: {len(tool_calls_log)}次")
            if search_results_log:
                print(f"搜索结果: {sum(search_results_log)}条")
            
            return True
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("DeerFlow 深度研究接口测试")
    print("="*60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"接口: {URL}")
    
    if not test_connection():
        sys.exit(1)
    
    stream_request()


if __name__ == "__main__":
    main()
