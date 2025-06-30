#!/bin/bash

# Polymarket Agents - Enhanced Autonomous Trader (UV)
# Runs the autonomous trader using ONLY enhanced MCP analysis

set -e

echo "🤖 Enhanced Polymarket Autonomous Trader"
echo "========================================"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ UV not found. Please run ./setup_uv.sh first"
    exit 1
fi

# Check if .env exists and has required variables
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run ./setup_uv.sh first"
    exit 1
fi

# Source .env to check variables
source .env

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY not configured in .env"
    exit 1
fi

if [ -z "$MCP_REMOTE_ENDPOINT" ] || [ "$MCP_REMOTE_ENDPOINT" = "your_mcp_server_endpoint_here" ]; then
    echo "⚠️  MCP_REMOTE_ENDPOINT not configured - enhanced analysis may fail"
    echo "   Please set MCP_REMOTE_ENDPOINT in .env for full functionality"
fi

if [ -z "$POLYGON_WALLET_PRIVATE_KEY" ] || [ "$POLYGON_WALLET_PRIVATE_KEY" = "your_private_key_here" ]; then
    echo "⚠️  POLYGON_WALLET_PRIVATE_KEY not configured - trade execution disabled"
fi

echo "🚀 Starting enhanced autonomous trader..."
echo "📊 Using MCP server: $MCP_REMOTE_ENDPOINT"
echo "🛡️  Trade execution: DISABLED (safety mode)"
echo ""

# Run the enhanced trader
uv run python scripts/python/cli.py run-autonomous-trader 