#!/bin/bash

# Polymarket Agents - UV Setup Script
# This script sets up the project using uv for modern Python dependency management

set -e

echo "🚀 Setting up Polymarket Agents with UV"
echo "======================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo "✅ UV installed successfully"
else
    echo "✅ UV is already installed"
fi

# Check UV version
echo "📦 UV version: $(uv --version)"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example template"
    else
        echo "❌ .env.example template not found. Creating basic template..."
        cat > .env << 'EOF'
# Polymarket Agents Configuration
# Please see .env.example for the complete configuration template

# Required: OpenAI API Key
OPENAI_API_KEY="your_openai_api_key_here"

# Required: Polygon wallet private key (for trading)
POLYGON_WALLET_PRIVATE_KEY="your_private_key_here"

# Required: MCP Configuration
MCP_REMOTE_ENDPOINT="your_mcp_server_endpoint_here"
MCP_API_KEY="your_mcp_api_key_here"
EOF
        echo "✅ Created basic .env file - please copy from .env.example for full configuration"
    fi
else
    echo "✅ .env file already exists"
fi

# Initialize UV project and install dependencies
echo "📦 Installing dependencies with UV..."
uv sync --all-extras

echo "🎯 Verifying installation..."
uv run python -c "import polymarket_agents; print(f'✅ Polymarket Agents v{polymarket_agents.__version__} installed successfully')"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - OPENAI_API_KEY (required)"
echo "   - POLYGON_WALLET_PRIVATE_KEY (for trading)"
echo "   - MCP_REMOTE_ENDPOINT & MCP_API_KEY (required for MCP functionality)"
echo "   - See .env.example for complete configuration options"
echo ""
echo "2. Test the enhanced analysis:"
echo "   uv run python examples/example_enhanced_analysis.py"
echo ""
echo "3. Use the CLI:"
echo "   uv run python scripts/python/cli.py --help"
echo ""
echo "4. Run autonomous trader:"
echo "   uv run python scripts/python/cli.py run-autonomous-trader"
echo ""
echo "🔗 For MCP integration setup, see: docs/COMMANDS.md" 