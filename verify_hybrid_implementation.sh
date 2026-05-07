#!/bin/bash
# Verification script for hybrid search implementation

echo "=========================================="
echo "Hybrid Search Implementation Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} File exists: $1"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} File missing: $1"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Function to check content in file
check_content() {
    if grep -q "$2" "$1"; then
        echo -e "${GREEN}✓${NC} Found in $1: $2"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} Not found in $1: $2"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Function to check Python syntax
check_syntax() {
    if python3 -m py_compile "$1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python syntax valid: $1"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} Python syntax error: $1"
        ((CHECKS_FAILED++))
        return 1
    fi
}

echo "1. Checking backup files..."
echo "----------------------------"
check_file "archive/backup_before_hybrid_v1/nodes.py"
check_file "archive/backup_before_hybrid_v1/builder.py"
check_file "archive/backup_before_hybrid_v1/search.py"
check_file "archive/backup_before_hybrid_v1/retriever.py"
echo ""

echo "2. Checking new implementation files..."
echo "----------------------------------------"
check_file "src/graph/hybrid_search.py"
check_file "test_hybrid_search.py"
check_file "HYBRID_SEARCH_IMPLEMENTATION.md"
echo ""

echo "3. Checking Python syntax..."
echo "----------------------------"
check_syntax "src/graph/hybrid_search.py"
check_syntax "src/graph/nodes_2.py"
check_syntax "test_hybrid_search.py"
echo ""

echo "4. Checking hybrid_search.py content..."
echo "----------------------------------------"
check_content "src/graph/hybrid_search.py" "class HybridSearchResult"
check_content "src/graph/hybrid_search.py" "async def parallel_search"
check_content "src/graph/hybrid_search.py" "async def _search_web"
check_content "src/graph/hybrid_search.py" "async def _search_rag"
check_content "src/graph/hybrid_search.py" "async def _search_elasticsearch"
check_content "src/graph/hybrid_search.py" "asyncio.gather"
echo ""

echo "5. Checking researcher_node modifications..."
echo "---------------------------------------------"
check_content "src/graph/nodes_2.py" "from src.graph.hybrid_search import parallel_search"
check_content "src/graph/nodes_2.py" "hybrid_result = await parallel_search"
check_content "src/graph/hybrid_search.py" "get_aggregated_context"
check_content "src/graph/nodes_2.py" "HYBRID SEARCH INTEGRATION"
check_content "src/graph/nodes_2.py" "hybrid_search_context"
echo ""

echo "6. Checking key implementation features..."
echo "-------------------------------------------"
check_content "src/graph/hybrid_search.py" "enable_web"
check_content "src/graph/hybrid_search.py" "enable_rag"
check_content "src/graph/hybrid_search.py" "enable_es"
check_content "src/graph/hybrid_search.py" "ElasticsearchProvider"
check_content "src/graph/hybrid_search.py" "get_web_search_tool"
check_content "src/graph/hybrid_search.py" "get_retriever_tool"
echo ""

echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "Checks passed: ${GREEN}${CHECKS_PASSED}${NC}"
echo -e "Checks failed: ${RED}${CHECKS_FAILED}${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Implementation verified.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run test script: python3 test_hybrid_search.py"
    echo "2. Start the application and test with real queries"
    echo "3. Monitor logs for '[Hybrid Search]' messages"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the implementation.${NC}"
    exit 1
fi
