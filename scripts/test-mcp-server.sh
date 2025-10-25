#!/bin/bash
#
# Test MCP Server
# Run various tests against the deployed MCP server
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get MCP server URL from Terraform output
MCP_URL=$(cd ../terraform && terraform output -raw mcp_server_url 2>/dev/null)

if [ -z "$MCP_URL" ]; then
    echo "Error: Could not get MCP server URL from Terraform"
    echo "Make sure the infrastructure is deployed first"
    exit 1
fi

echo "Testing MCP Server at: $MCP_URL"
echo ""

# Test 1: Health check
echo -e "${BLUE}Test 1: Health Check${NC}"
curl -s "${MCP_URL}/health" | jq '.'
echo ""

# Test 2: List tools
echo -e "${BLUE}Test 2: List Available Tools${NC}"
curl -s "${MCP_URL}/tools" | jq '.tools[] | {name, description}'
echo ""

# Test 3: Addition
echo -e "${BLUE}Test 3: Addition (5 + 3)${NC}"
curl -s -X POST "${MCP_URL}/tools/add" \
    -H "Content-Type: application/json" \
    -d '{"arguments": {"a": 5, "b": 3}}' | jq '.'
echo ""

# Test 4: Multiplication
echo -e "${BLUE}Test 4: Multiplication (12 × 4)${NC}"
curl -s -X POST "${MCP_URL}/tools/multiply" \
    -H "Content-Type: application/json" \
    -d '{"arguments": {"a": 12, "b": 4}}' | jq '.'
echo ""

# Test 5: Percentage
echo -e "${BLUE}Test 5: Percentage (15% of 100)${NC}"
curl -s -X POST "${MCP_URL}/tools/percentage" \
    -H "Content-Type: application/json" \
    -d '{"arguments": {"number": 100, "percent": 15}}' | jq '.'
echo ""

# Test 6: Division
echo -e "${BLUE}Test 6: Division (100 ÷ 4)${NC}"
curl -s -X POST "${MCP_URL}/tools/divide" \
    -H "Content-Type: application/json" \
    -d '{"arguments": {"a": 100, "b": 4}}' | jq '.'
echo ""

# Test 7: Square root
echo -e "${BLUE}Test 7: Square Root (√64)${NC}"
curl -s -X POST "${MCP_URL}/tools/sqrt" \
    -H "Content-Type: application/json" \
    -d '{"arguments": {"number": 64}}' | jq '.'
echo ""

# Test 8: Error handling - division by zero
echo -e "${BLUE}Test 8: Error Handling (Division by Zero)${NC}"
curl -s -X POST "${MCP_URL}/tools/divide" \
    -H "Content-Type: application/json" \
    -d '{"arguments": {"a": 10, "b": 0}}' | jq '.'
echo ""

echo -e "${GREEN}All tests completed!${NC}"
