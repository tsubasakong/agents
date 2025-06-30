# Migration Guide: Requirements.txt → UV

This guide helps you migrate from the old `pip` + `requirements.txt` setup to the modern `uv` dependency management system.

## 🎯 Why UV?

- **⚡ Faster**: 10-100x faster dependency resolution and installation
- **🔒 Reproducible**: Lockfile ensures consistent environments
- **🧹 Clean**: Single tool for dependency management, virtual environments, and Python versions
- **🚀 Modern**: Built in Rust, designed for modern Python development

## 📦 Migration Steps

### 1. Install UV

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (if needed)
export PATH="$HOME/.cargo/bin:$PATH"
```

### 2. Remove Old Environment

```bash
# Deactivate old virtual environment
deactivate

# Remove old virtual environments
rm -rf .venv .venv_enhanced

# Clean up old pip cache (optional)
pip cache purge
```

### 3. Set Up UV Environment

```bash
# Run the new UV setup script
./setup_uv.sh

# This will:
# - Create UV virtual environment
# - Install all dependencies from pyproject.toml
# - Create .env template
# - Verify installation
```

### 4. Update Your Workflow

#### Old Workflow (pip):
```bash
# Old way
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/python/cli.py
```

#### New Workflow (UV):
```bash
# New way - much simpler!
uv run python scripts/python/cli.py

# Or use the UV scripts
./run_cli_uv.sh
./run_enhanced_trader_uv.sh
```

## 🔄 Command Mapping

| Old Command | New UV Command |
|-------------|----------------|
| `pip install -r requirements.txt` | `uv sync` |
| `source .venv/bin/activate` | Not needed with `uv run` |
| `python script.py` | `uv run python script.py` |
| `pip install package` | `uv add package` |
| `pip uninstall package` | `uv remove package` |
| `pip freeze > requirements.txt` | `uv export > requirements.txt` |

## 📋 File Changes

### Added Files:
- ✅ `pyproject.toml` - Modern dependency specification
- ✅ `uv.lock` - Lockfile for reproducible installs
- ✅ `.python-version` - Python version specification
- ✅ `setup_uv.sh` - UV-based setup script
- ✅ `run_cli_uv.sh` - UV CLI runner
- ✅ `run_enhanced_trader_uv.sh` - Enhanced trader runner

### Modified Files:
- 🔄 `polymarket_agents/__init__.py` - Added version info
- 🔄 `scripts/python/cli.py` - Fixed import paths
- 🔄 `polymarket_agents/application/trade.py` - Enhanced-only logic

### Legacy Files (can be removed after migration):
- ❓ `requirements.txt` - Replaced by `pyproject.toml`
- ❓ `setup_enhanced.sh` - Replaced by `setup_uv.sh`
- ❓ `run_cli.sh` - Replaced by `run_cli_uv.sh`

## 🚀 Enhanced Features

### 1. Enhanced Analysis is Now Primary

The trader now uses **ONLY** the enhanced MCP analysis:

```bash
# Run enhanced autonomous trader
./run_enhanced_trader_uv.sh

# Or manually
uv run python scripts/python/cli.py run-autonomous-trader
```

### 2. New CLI Commands

```bash
# Enhanced market analysis
uv run python scripts/python/cli.py enhanced-analysis

# Specific market analysis
uv run python scripts/python/cli.py enhanced-analysis --market-id 123456
```

### 3. Development Tools

```bash
# Install development dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Code formatting
uv run black .

# Type checking
uv run mypy polymarket_agents
```

## 🔧 Configuration

### Environment Variables

Your `.env` file remains the same:

```env
OPENAI_API_KEY="your_key_here"
POLYGON_WALLET_PRIVATE_KEY="your_private_key"
MCP_REMOTE_ENDPOINT="your_mcp_endpoint"
MCP_API_KEY="your_mcp_key"
```

### Python Version

UV automatically manages Python versions:

```bash
# UV will use Python 3.11 (specified in .python-version)
# Or install it if not available
uv python install 3.11
```

## 🐛 Troubleshooting

### UV Not Found
```bash
# Reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
```

### Import Errors
```bash
# Ensure all dependencies are installed
uv sync --all-extras

# Check installation
uv run python -c "import polymarket_agents; print('OK')"
```

### MCP Connection Issues
```bash
# Verify MCP endpoint in .env
echo $MCP_REMOTE_ENDPOINT

# Test enhanced analysis
uv run python example_enhanced_analysis.py
```

### Legacy Import Errors
- Old imports (`agents.`) have been updated to (`polymarket_agents.`)
- If you have custom code, update import paths accordingly

## 📚 Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [Python Packaging Guide](https://packaging.python.org/en/latest/)
- [Polymarket Agents Documentation](docs/)

## 🎉 Benefits After Migration

- ⚡ **Faster installs**: Dependencies install 10-100x faster
- 🔒 **Reproducible builds**: Lockfile ensures consistent environments
- 🧹 **Simplified commands**: Single `uv run` command for everything
- 🛡️ **Better isolation**: No need to manage virtual environments manually
- 📦 **Modern tooling**: Automatic Python version management
- 🚀 **Enhanced focus**: Trading logic uses ONLY advanced MCP analysis

Ready to trade smarter with UV + Enhanced MCP Analysis! 🤖📈 