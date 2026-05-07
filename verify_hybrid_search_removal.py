#!/usr/bin/env python3
"""
Verification script to confirm Hybrid Search has been disabled in researcher_node.

This script checks that:
1. The parallel_search import is commented out
2. The hybrid search execution logic is commented out
3. The context injection logic is commented out
4. The normal researcher flow remains intact
"""

import re
import sys


def verify_hybrid_search_removal():
    """Verify that Hybrid Search has been properly disabled."""
    
    file_path = "src/graph/nodes_2.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: File {file_path} not found")
        return False
    
    # Find the researcher_node function
    researcher_match = re.search(
        r'async def researcher_node\(.*?\n(.*?)(?=\nasync def |\ndef |\Z)',
        content,
        re.DOTALL
    )
    
    if not researcher_match:
        print("❌ Error: researcher_node function not found")
        return False
    
    researcher_code = researcher_match.group(1)
    
    # Check 1: Verify import is commented out
    if re.search(r'^\s*from src\.graph\.hybrid_search import parallel_search', researcher_code, re.MULTILINE):
        print("❌ FAIL: parallel_search import is NOT commented out")
        return False
    
    if re.search(r'^\s*#\s*from src\.graph\.hybrid_search import parallel_search', researcher_code, re.MULTILINE):
        print("✅ PASS: parallel_search import is commented out")
    else:
        print("⚠️  WARNING: parallel_search import not found (may have been removed)")
    
    # Check 2: Verify parallel_search call is commented out
    if re.search(r'^\s*hybrid_result = await parallel_search\(', researcher_code, re.MULTILINE):
        print("❌ FAIL: parallel_search call is NOT commented out")
        return False
    
    if re.search(r'^\s*#.*hybrid_result = await parallel_search\(', researcher_code, re.MULTILINE):
        print("✅ PASS: parallel_search call is commented out")
    else:
        print("⚠️  WARNING: parallel_search call not found (may have been removed)")
    
    # Check 3: Verify context injection is commented out
    if re.search(r'^\s*state = \{.*"messages": current_messages\}', researcher_code, re.MULTILINE):
        print("❌ FAIL: Context injection is NOT commented out")
        return False
    
    if re.search(r'^\s*#.*state = \{.*"messages": current_messages\}', researcher_code, re.MULTILINE):
        print("✅ PASS: Context injection is commented out")
    else:
        print("⚠️  WARNING: Context injection not found (may have been removed)")
    
    # Check 4: Verify normal researcher flow is intact
    if not re.search(r'tools = \[get_web_search_tool\(.*?\), crawl_tool\]', researcher_code):
        print("❌ FAIL: Normal researcher tools initialization is missing")
        return False
    print("✅ PASS: Normal researcher tools initialization is intact")
    
    if not re.search(r'retriever_tool = get_retriever_tool\(state\.get\("resources", \[\]\)\)', researcher_code):
        print("❌ FAIL: Retriever tool initialization is missing")
        return False
    print("✅ PASS: Retriever tool initialization is intact")
    
    if not re.search(r'return await _setup_and_execute_agent_step\(', researcher_code):
        print("❌ FAIL: Agent execution call is missing")
        return False
    print("✅ PASS: Agent execution call is intact")
    
    # Check 5: Verify DISABLED comment is present
    if re.search(r'HYBRID SEARCH INTEGRATION - DISABLED', researcher_code):
        print("✅ PASS: DISABLED marker comment is present")
    else:
        print("⚠️  WARNING: DISABLED marker comment not found")
    
    # Check 6: Verify reason comment is present
    if re.search(r'Virtual Resource Injection', researcher_code):
        print("✅ PASS: Virtual Resource Injection reason is documented")
    else:
        print("⚠️  WARNING: Virtual Resource Injection reason not documented")
    
    print("\n" + "="*60)
    print("✅ SUCCESS: Hybrid Search has been properly disabled!")
    print("="*60)
    print("\nExpected Effects:")
    print("  • researcher_node will NOT automatically trigger parallel_search")
    print("  • Agent will rely on local_search_tool for on-demand retrieval")
    print("  • Elasticsearch request volume should decrease by ~50%")
    print("  • Token consumption will be reduced")
    print("  • Virtual Resource Injection ensures Agent has access to tools")
    
    return True


if __name__ == "__main__":
    success = verify_hybrid_search_removal()
    sys.exit(0 if success else 1)
