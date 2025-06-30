#!/bin/bash

# Polymarket Agents - UV CLI Runner
# Modern replacement for run_cli.sh using uv

set -e

echo "🚀 Polymarket Agents CLI (UV)"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ UV not found. Please run ./setup_uv.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    echo "Please edit .env with your API keys before continuing."
    ./setup_uv.sh
    exit 1
fi

# Run CLI with UV
echo "🎯 Starting enhanced CLI with MCP support..."
uv run python scripts/python/cli.py "$@" 