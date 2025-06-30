# Polymarket Agents - Available Commands

This document provides a comprehensive overview of all available commands and ways to run the Polymarket Agents project.

## Prerequisites

Before running any commands, ensure you have:

1. Python 3.9 installed
2. Set up a virtual environment (recommended)
3. Installed dependencies via `pip install -r requirements.txt` or `./scripts/bash/install.sh`
4. Configured your `.env` file with required API keys (see `.env.example` for reference)

## CLI Commands

The project provides a command-line interface (CLI) with various commands for interacting with Polymarket. Use the `run_cli.sh` script to execute these commands.

### Basic Usage

```bash
./run_cli.sh [command] [options]
```

### Available CLI Commands

> **Important**: CLI commands use hyphens (-) instead of underscores (_). For example, use `get-all-markets` instead of `get_all_markets`.

| Command | Description | Example |
|---------|-------------|--------|
| `get-all-markets` | Retrieve all markets from Polymarket | `./run_cli.sh get-all-markets --limit 5 --sort-by spread` |
| `get-all-events` | Retrieve all events from Polymarket | `./run_cli.sh get-all-events --limit 3` |
| `get-relevant-news` | Get news relevant to Polymarket events | `./run_cli.sh get-relevant-news` |
| `create-local-markets-rag` | Create a local RAG database for markets | `./run_cli.sh create-local-markets-rag` |
| `query-local-markets-rag` | Query the local markets RAG database | `./run_cli.sh query-local-markets-rag "US election"` |
| `ask-superforecaster` | Ask a question to the superforecaster | `./run_cli.sh ask-superforecaster "Will Bitcoin reach $100k in 2024?"` |
| `create-market` | Create a new market on Polymarket | `./run_cli.sh create-market` |
| `ask-llm` | Ask a general question to the LLM | `./run_cli.sh ask-llm "What are prediction markets?"` |
| `ask-polymarket-llm` | Ask a Polymarket-specific question to the LLM | `./run_cli.sh ask-polymarket-llm "What are the top political markets?"` |
| `run-autonomous-trader` | Run the autonomous trading system | `./run_cli.sh run-autonomous-trader` |

### CLI Help

To see all available commands and options:

```bash
./run_cli.sh --help
```

To see help for a specific command:

```bash
./run_cli.sh [command] --help
```

## Continuous Monitoring

The project includes scripts for continuously monitoring markets without executing trades.

### Basic Monitoring

```bash
./run_monitor.sh
```

This will run market analysis every hour until stopped with Ctrl+C.

### Monitoring Options

| Option | Description | Example |
|--------|-------------|--------|
| `--interval` | Set interval between checks (seconds) | `./run_monitor.sh --interval 1800` |
| `--once` | Run analysis once and exit | `./run_monitor.sh --once` |

### Background Monitoring

```bash
./run_monitor_background.sh
```

This runs the monitor as a background process that continues after terminal close.

To check status and view logs:

```bash
./check_monitor.sh
```

To stop the background monitor:

```bash
./stop_monitor.sh
```

For more details on monitoring, see `docs/MONITORING.md`.

## Web Server

The project includes a FastAPI web server.

### Starting the Web Server

```bash
./scripts/bash/start-dev.sh
```

This runs `python setup.py` and starts the FastAPI development server.

### Available Endpoints

- `/` - Root endpoint
- `/items/{item_id}` - Get item by ID
- `/trades/{trade_id}` - Get trade by ID
- `/markets/{market_id}` - Get market by ID

## Docker Deployment

The project can be run in a Docker container.

### Building the Docker Image

```bash
./scripts/bash/build-docker.sh
```

### Running the Docker Container

```bash
./scripts/bash/run-docker.sh
```

This runs the container in interactive mode and removes it upon exit.

### Development Docker Container

```bash
./scripts/bash/run-docker-dev.sh
```

## Environment Variables

The following environment variables are required in your `.env` file:

- `POLYGON_WALLET_PRIVATE_KEY` - Your Polygon wallet private key
- `OPENAI_API_KEY` - Your OpenAI API key
- `TAVILY_API_KEY` - Your Tavily API key
- `NEWSAPI_API_KEY` - Your News API key

## Additional Resources

- For more details on the project, see `README.md`
- For contribution guidelines, see `CONTRIBUTING.md`
- For examples, see `docs/EXAMPLE.md`