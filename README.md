<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/polymarket/agents">
    <img src="docs/images/cli.png" alt="Logo" width="466" height="262">
  </a>

<h3 align="center">Polymarket Agents</h3>

  <p align="center">
    Trade autonomously on Polymarket using AI Agents with MCP Integration
    <br />
    <a href="https://github.com/polymarket/agents"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/polymarket/agents">View Demo</a>
    ·
    <a href="https://github.com/polymarket/agents/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/polymarket/agents/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>


<!-- CONTENT -->
# Polymarket Agents

Polymarket Agents is a developer framework and set of utilities for building AI agents for Polymarket with **advanced MCP (Model Context Protocol) integration** for intelligent market analysis and automated trading decisions.

This code is free and publicly available under MIT License open source license ([terms of service](#terms-of-service))!

## ✨ Features

- **🤖 Enhanced AI Agent Integration**: OpenAI Agent pattern with real-time MCP tool integration
- **🔗 MCP Server Support**: Connect to external data sources, news feeds, and market analysis tools
- **📊 Intelligent Market Analysis**: AI-powered trading recommendations with confidence scoring
- **🔍 Real-time Data**: Access to crypto prices, news sentiment, technical indicators via MCP
- **⚡ Async Architecture**: High-performance async execution with retry logic and error handling
- **📈 Advanced Trading Logic**: Sophisticated market analysis with external factor consideration
- **🎯 Trace Integration**: Full OpenAI trace support for debugging and analysis
- **🛠️ Production Ready**: Robust configuration, caching, and monitoring capabilities

## 🚀 Enhanced Agent with MCP Integration

The **Enhanced Executor** (`agents/application/enhanced_executor.py`) provides cutting-edge AI agent capabilities:

### 🔧 Key Components

1. **OpenAI Agent Pattern**: Uses real OpenAI Agent + Runner for advanced reasoning
2. **MCP Server Integration**: Connects to external tools and data sources
3. **Intelligent Analysis**: Combines market data with real-time external information
4. **Smart Recommendations**: BUY/SELL/HOLD decisions with confidence levels

### 💡 How It Works

```python
# The Enhanced Executor uses:
- OpenAI Agent: Advanced reasoning and decision-making
- MCP Tools: Real-time data (crypto prices, news, technical analysis)
- Context Management: Maintains conversation state and market context
- Trace Integration: Full observability and debugging
```

### 📈 Sample Analysis Output

```
📈 Recommendation: BUY
🎯 Confidence: 75%
🔗 MCP Integration: ACTIVE
🤖 Real Agent Used: True

💭 Analysis: Based on MCP tool analysis:
- Current Bitcoin Price: $108,614 (already above target!)
- News Sentiment: 65% positive
- Technical Indicators: Bullish momentum
- Tim Draper Prediction: $120,000 by end of 2024
```

# 🛠️ Getting Started

## 🚀 Modern Setup with UV (Recommended)

We've migrated to **UV** for fast, modern Python dependency management. UV provides 10-100x faster installation and better reproducibility.

### Prerequisites
- **Python 3.10+** (UV will automatically manage Python versions)
- OpenAI API key
- MCP server endpoint (for enhanced features)

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/polymarket/agents.git
   cd agents
   ```

2. **Run the UV setup script**
   ```bash
   ./setup_uv.sh
   ```
   
   This automatically:
   - Installs UV (if needed)
   - Creates virtual environment
   - Installs all dependencies from `pyproject.toml`
   - Creates `.env` template
   - Verifies installation

3. **Configure your environment**
   
   Edit the generated `.env` file:
   ```env
   # Required
   OPENAI_API_KEY="your_openai_api_key"
   POLYGON_WALLET_PRIVATE_KEY="your_private_key"
   
   # Enhanced MCP Features
   MCP_REMOTE_ENDPOINT="your_mcp_server_endpoint"
   MCP_API_KEY="your_mcp_api_key"
   
   # Optional: External APIs
   TAVILY_API_KEY="your_tavily_api_key"
   NEWSAPI_API_KEY="your_newsapi_key"
   ```

4. **Test the setup**
   ```bash
   # Test enhanced analysis
   uv run python examples/example_enhanced_analysis.py
   
   # Run CLI
   ./run_cli_uv.sh
   
   # Or manually
   uv run python scripts/python/cli.py --help
   ```

### 🔧 UV Commands

| Task | UV Command |
|------|------------|
| **Install dependencies** | `uv sync` |
| **Add new package** | `uv add package-name` |
| **Remove package** | `uv remove package-name` |
| **Run script** | `uv run python script.py` |
| **Run CLI** | `uv run python scripts/python/cli.py` |
| **Run tests** | `uv run pytest` |

## 📦 Legacy Setup (Not Recommended)

<details>
<summary>Click to expand legacy pip-based setup (deprecated)</summary>

For those still using the old pip-based workflow:

1. **Create virtual environment**
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run manually**
   ```bash
   PYTHONPATH="." python scripts/python/cli.py
   ```

**⚠️ Warning**: This method is deprecated. Please migrate to UV for better performance and reproducibility.

</details>

## 🔄 Migration from pip to UV

If you're upgrading from the old pip-based setup, see our comprehensive [Migration Guide](MIGRATION_UV.md) for step-by-step instructions.

### 🎯 Using the Enhanced Agent

```python
import asyncio
from agents.application.enhanced_executor import EnhancedExecutor, AgentConfig, MCPServerConfig
from agents.utils.objects import SimpleMarket

async def analyze_market():
    # Configure MCP server
    mcp_config = MCPServerConfig(
        name="Trading MCP Server",
        url="https://your-mcp-endpoint.com/sse",
        api_key="your_mcp_api_key",
        enable_cache=True
    )
    
    # Configure agent
    agent_config = AgentConfig(
        model="gpt-4o",
        temperature=0.1,
        max_tokens=50000,
        timeout=180
    )
    
    # Create enhanced executor
    executor = EnhancedExecutor(
        agent_config=agent_config,
        mcp_config=mcp_config
    )
    
    # Your market data
    market = SimpleMarket(
        id=123456789,
        question="Will Bitcoin exceed $100k by end of 2024?",
        # ... other market fields
    )
    
    try:
        # Initialize MCP connection
        await executor.initialize_mcp_connection()
        
        # Run enhanced analysis with real MCP tools
        result = await executor.enhanced_market_analysis(market)
        
        print(f"Recommendation: {result['recommendation']}")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Trace URL: {result['trace_url']}")
        
    finally:
        await executor.cleanup()

# Run the analysis
asyncio.run(analyze_market())
```

## 🔗 MCP Integration Details

### Available MCP Tools

The enhanced agent can use these MCP tools (depending on your MCP server):

- **`crypto_prices_get_price`**: Get current cryptocurrency prices
- **`crypto_prices_get_historical`**: Historical price data and trends
- **`news_analysis_search_news`**: Search relevant news articles
- **`news_analysis_sentiment`**: Analyze news sentiment
- **`market_data_technical_analysis`**: Technical indicators (RSI, MACD, etc.)

### MCP Configuration

```python
@dataclass
class MCPServerConfig:
    name: str = "Polymarket MCP Server"
    url: str = "https://your-mcp-endpoint.com/sse"
    api_key: Optional[str] = None
    timeout: int = 60
    enable_cache: bool = True
    cache_ttl: int = 3600
```

### Agent Configuration

```python
@dataclass
class AgentConfig:
    model: str = "gpt-4o"  # Production-ready model
    temperature: float = 0.1
    max_tokens: int = 50000
    timeout: int = 120  # Longer timeout for MCP calls
    max_retries: int = 3
```

## 🎯 Modern Architecture Benefits

| Feature | UV-Based Modern Setup | Legacy pip Setup |
|---------|----------------------|------------------|
| **Installation Speed** | 10-100x faster with UV | Slow pip resolution |
| **Dependency Management** | `pyproject.toml` + lockfile | Manual `requirements.txt` |
| **Python Version** | Auto-managed by UV | Manual version management |
| **Virtual Environment** | Automatic with `uv run` | Manual activation required |
| **AI Integration** | OpenAI Agent + MCP tools | Basic OpenAI API calls |
| **Data Sources** | Real-time MCP integration | Static market data only |
| **Analysis Quality** | Multi-tool comprehensive | Basic prompt-based |
| **Reproducibility** | Guaranteed with `uv.lock` | Version conflicts possible |

## 📊 Architecture

The Enhanced Polymarket Agents architecture features:

### 🧠 Enhanced Executor Components

- **`EnhancedExecutor`**: Core class with OpenAI Agent + MCP integration
- **`AgentConfig`**: Configuration for AI model and behavior
- **`MCPServerConfig`**: Configuration for external MCP server connection
- **`BaseExecutor`**: Foundation class with basic trading utilities

### 🔌 MCP Integration Flow

1. **Initialization**: Connect to MCP server and discover available tools
2. **Context Preparation**: Prepare market data and context for analysis
3. **Agent Creation**: Initialize OpenAI Agent with MCP tools and instructions
4. **Tool Execution**: Agent automatically calls relevant MCP tools
5. **Analysis**: Comprehensive reasoning using all available data
6. **Recommendation**: Structured output with confidence scoring

### 📡 APIs and Connectors

- **`Chroma.py`**: Vector database for news and API data
- **`Gamma.py`**: Polymarket Gamma API client for market metadata
- **`Polymarket.py`**: Main Polymarket API interface for trading
- **`Objects.py`**: Pydantic data models for type safety

### 🖥️ Scripts and CLI

The modern CLI uses UV for all operations and focuses on enhanced MCP-powered analysis:

```bash
# Get all markets
uv run python scripts/python/cli.py get-all-markets --limit 10

# Enhanced market analysis with MCP
uv run python scripts/python/cli.py enhanced-analysis --market-id 123456

# Run autonomous trader
uv run python scripts/python/cli.py run-autonomous-trader

# Using the UV CLI script
./run_cli_uv.sh get-all-markets --limit 10
```

## 🔍 Monitoring and Debugging

### OpenAI Traces

Every enhanced analysis generates a trace URL for debugging:

```
🔗 Trace URL: https://platform.openai.com/traces/trace?trace_id=trace_abc123
```

### Logging

Configure logging levels:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # For detailed MCP interaction logs
```

### Error Handling

The enhanced executor includes robust error handling:

- **Retry Logic**: Automatic retries for transient failures
- **Fallback Modes**: Graceful degradation when MCP tools are unavailable
- **Detailed Error Messages**: Clear debugging information

## 🚀 Production Deployment

### Environment Variables

Your `.env` file (auto-generated by `./setup_uv.sh`):

```env
# Required
OPENAI_API_KEY="sk-your-openai-key"
POLYGON_WALLET_PRIVATE_KEY="0x..."

# Enhanced MCP Features
MCP_REMOTE_ENDPOINT="https://your-mcp-server.com/sse"
MCP_API_KEY="your-mcp-key"

# Optional External APIs
TAVILY_API_KEY="your-tavily-key"
NEWSAPI_API_KEY="your-news-api-key"
```

### UV Production Commands

```bash
# Production sync with lockfile
uv sync --frozen

# Run autonomous trader
uv run python scripts/python/cli.py run-autonomous-trader

# Run with monitoring
./run_enhanced_trader_uv.sh
```

### Docker Support

Modern Docker setup with UV:

```bash
# Build with UV and Python 3.11
docker build .

# Run with MCP integration
docker run -e MCP_REMOTE_ENDPOINT="..." polymarket-agents
```

## 📚 Examples

See [`examples/example_enhanced_analysis.py`](examples/example_enhanced_analysis.py) for a complete working example.

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes (Python 3.10+ required)
4. Run the UV setup: `./setup_uv.sh`
5. Run tests and formatting
6. Submit a pull request

### Development Setup

```bash
# Setup with development dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Code formatting
uv run black .

# Type checking
uv run mypy polymarket_agents

# Install pre-commit hooks
uv run pre-commit install
```

## 📖 Related Repos

- [py-clob-client](https://github.com/Polymarket/py-clob-client): Python client for Polymarket CLOB
- [python-order-utils](https://github.com/Polymarket/python-order-utils): Order utilities
- [openai-agents](https://github.com/openai/agents): OpenAI Agent framework
- [MCP](https://modelcontextprotocol.org/): Model Context Protocol specification

## 📚 Further Reading

- [Model Context Protocol (MCP)](https://modelcontextprotocol.org/): Official MCP documentation
- [OpenAI Agents](https://platform.openai.com/docs/agents): OpenAI Agent documentation
- [Prediction Markets Research](https://mirror.xyz/1kx.eth/jnQhA56Kx9p3RODKiGzqzHGGEODpbskivUUNdd7hwh0): Market analysis insights
- [AI + Crypto Applications](https://vitalik.eth.limo/general/2024/01/30/cryptoai.html): Vitalik's perspective

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

## 📞 Contact

For questions or inquiries:
- Email: liam@polymarket.com
- Website: www.greenestreet.xyz

## ⚖️ Terms of Service

[Terms of Service](https://polymarket.com/tos) prohibit US persons and persons from certain other jurisdictions from trading on Polymarket (via UI & API and including agents developed by persons in restricted jurisdictions), although data and information is viewable globally.


<!-- LINKS -->
[contributors-shield]: https://img.shields.io/github/contributors/polymarket/agents?style=for-the-badge
[contributors-url]: https://github.com/polymarket/agents/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/polymarket/agents?style=for-the-badge
[forks-url]: https://github.com/polymarket/agents/network/members
[stars-shield]: https://img.shields.io/github/stars/polymarket/agents?style=for-the-badge
[stars-url]: https://github.com/polymarket/agents/stargazers
[issues-shield]: https://img.shields.io/github/issues/polymarket/agents?style=for-the-badge
[issues-url]: https://github.com/polymarket/agents/issues
[license-shield]: https://img.shields.io/github/license/polymarket/agents?style=for-the-badge
[license-url]: https://github.com/polymarket/agents/blob/master/LICENSE.md