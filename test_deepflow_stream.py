#!/usr/bin/env python3
"""
Test client for DeerFlow SSE endpoint.

Usage:
    python3 test_deepflow_stream.py

Features:
    - Streams and displays all SSE events in real-time
    - Shows message chunks progressively (AI thinking/generation)
    - Displays tool calls and search results with formatting
    - Handles planning stage with optional interruption feedback
    - Shows reasoning content (deep thinking)
"""

import requests
import json
import sys
import time

# 使用 /api/deep-research/stream 端点（自动确认计划，无需手动干预）
URL = "http://localhost:8088/api/deep-research/stream"

# Request payload - 深度研究接口会设置默认参数
payload = {
    "messages": [{"role": "user", "content": "分析一下日本大选后各方的动态以及由此可见的世界局势"}],
    "locale": "zh-CN",
}

# Headers - 后端是内部服务，不需要认证
headers = {
    "Content-Type": "application/json"
}


def format_value(val, max_len=2000):
    """Format value for display, truncate if too long."""
    if isinstance(val, str):
        if len(val) > max_len:
            return val[:max_len] + "..."
        return val
    elif isinstance(val, dict):
        return json.dumps(val, ensure_ascii=False, indent=2)[:max_len]
    else:
        return str(val)[:max_len]


def handle_tool_calls(data):
    """Process tool_calls event (tool invocation)."""
    tool_calls = data.get("tool_calls", [])
    for tc in tool_calls:
        print(f"  [TOOL_CALL] {tc.get('name')} (id: {tc.get('id')})")
        args = tc.get("args", {})
        for k, v in args.items():
            print(f"    {k}: {format_value(v, 100)}")


def handle_tool_call_result(data):
    """Process tool_call_result event (tool output/search results)."""
    tool_id = data.get("tool_call_id", "?")
    content = data.get("content", "")
    print(f"  [TOOL_RESULT] {tool_id}")
    
    # Try to parse as JSON (search results)
    try:
        results = json.loads(content)
        if isinstance(results, list):
            print(f"    Retrieved {len(results)} results:")
            for i, r in enumerate(results[:3], 1):
                if isinstance(r, dict):
                    title = r.get("title", r.get("name", "Unknown"))
                    url = r.get("url", "")
                    print(f"      [{i}] {title}")
                    if url:
                        print(f"          URL: {url[:80]}")
                else:
                    print(f"      [{i}] {str(r)[:100]}")
        else:
            print(f"    {format_value(content, 200)}")
    except Exception:
        # Plain text result
        print(f"    {format_value(content, 200)}")


def handle_interrupt(data):
    """Process interrupt event (waiting for user feedback)."""
    options = data.get("options", [])
    print(f"  [INTERRUPT] Waiting for feedback")
    for opt in options:
        value = opt.get("value", "?")
        label = opt.get("label", value)
        print(f"    - {label} ({value})")
    
    # Return the first acceptable option (usually "accepted")
    default_choice = None
    for opt in options:
        value = opt.get("value", "?")
        if value == "accepted":
            default_choice = value
            break
    
    if default_choice is None and options:
        default_choice = options[0].get("value", "?")
    
    if default_choice:
        print(f"  [AUTO-ACCEPT] Choosing: {default_choice}\n")
        return default_choice
    
    return None


def stream_with_events(payload):
    """Stream from endpoint with real-time printing of incoming data."""
    print(f"Connecting to {URL}...")
    print(f"Query: {payload['messages'][0]['content']}\n")
    
    attempt = 1
    while True:
        try:
            print(f"{'='*60}")
            if attempt == 1:
                print("STREAMING RESPONSE (Real-time)")
            else:
                print(f"STREAMING RESPONSE - Attempt {attempt} (Auto-resume after interrupt)")
            print(f"{'='*60}\n")
            
            with requests.post(URL, json=payload, stream=True, headers=headers, timeout=300) as r:
                r.raise_for_status()
                
                buffer = ""
                last_event_type = None
                in_message_chunk = False
                interrupt_feedback = None
                
                for raw_chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
                    if not raw_chunk:
                        continue
                    
                    buffer += raw_chunk
                    sys.stdout.flush()  # 立即刷新，确保实时输出
                    
                    # Process complete SSE messages (delimited by \n\n)
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
                        except json.JSONDecodeError as e:
                            print(f"\n[ERROR] Failed to parse event data: {e}")
                            print(f"  Raw: {event_data[:100]}")
                            continue
                        
                        # Real-time handling for message_chunk (AI tokens)
                        if event_type == "message_chunk":
                            content = data.get("content", "")
                            
                            # Print event header only once at start or when switching agents
                            agent = data.get("agent", "?")
                            if not in_message_chunk or agent != last_event_type:
                                if in_message_chunk:
                                    print()  # Newline when switching
                                print(f"\n[MESSAGE from {agent}] ", end="", flush=True)
                                in_message_chunk = True
                                last_event_type = agent
                            
                            # Real-time print each token/chunk
                            print(content, end="", flush=True)
                        
                        # Handle interrupt event
                        elif event_type == "interrupt":
                            if in_message_chunk:
                                print()  # Newline before interrupt
                                in_message_chunk = False
                            
                            interrupt_feedback = handle_interrupt(data)
                            # Don't break, continue streaming
                        
                        # Other event types
                        else:
                            if in_message_chunk:
                                print()  # Newline before switching to other events
                                in_message_chunk = False
                            
                            print(f"\n[{event_type.upper()}]", flush=True)
                            
                            if event_type == "tool_calls":
                                handle_tool_calls(data)
                            elif event_type == "tool_call_result":
                                handle_tool_call_result(data)
                            else:
                                # Generic fallback
                                if "content" in data:
                                    print(f"  {format_value(data.get('content'), 150)}")
                                else:
                                    print(f"  {json.dumps(data, ensure_ascii=False)[:150]}")
                            
                            last_event_type = event_type
                
                if in_message_chunk:
                    print()
                
                print("\n" + "="*60)
                print("STREAMING COMPLETE")
                print("="*60)
                
                # If interrupt happened, resume with feedback
                if interrupt_feedback:
                    print(f"\n[RESUMING] Sending feedback: {interrupt_feedback}\n")
                    payload["interrupt_feedback"] = interrupt_feedback
                    attempt += 1
                    time.sleep(0.5)  # Brief pause before retry
                    continue
                
                # If no interrupt, we're done
                break
                
        except requests.exceptions.ConnectionError as e:
            print(f"\n❌ Connection failed: {e}")
            print("   Make sure DeerFlow is running: ./bootstrap.sh or uv run server.py --port 8088")
            sys.exit(1)
        except requests.exceptions.Timeout:
            print("\n❌ Request timeout (300s)")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    stream_with_events(payload)


if __name__ == "__main__":
    main()
