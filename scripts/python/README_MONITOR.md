# Market Monitor Script

## Overview

The `monitor.py` script provides functionality to analyze Polymarket markets without executing trades. It uses the same analysis logic as the trading functionality but skips the final step of executing trades.

## Features

- Retrieves all tradeable events from Polymarket
- Filters events using RAG (Retrieval-Augmented Generation)
- Maps filtered events to markets
- Filters markets for trading opportunities
- Calculates the best trade for the top market
- Displays what would be traded (without executing)

## Usage

The script can be run directly, but it's recommended to use the convenience scripts in the project root:

```bash
# Run with default settings (continuous monitoring with 1-hour interval)
./run_monitor.sh

# Run with custom interval (e.g., 30 minutes)
./run_monitor.sh --interval 1800

# Run once and exit
./run_monitor.sh --once

# Run in background
./run_monitor_background.sh
```

## Command-line Arguments

- `--interval SECONDS`: Set the interval between market checks in seconds (default: 3600)
- `--once`: Run the monitor only once instead of continuously

## Implementation Details

The script defines a `Monitor` class with the following methods:

- `__init__(interval_seconds=3600)`: Initializes the monitor with a Trader instance
- `monitor_markets()`: Performs market analysis without executing trades
- `start_continuous_monitoring()`: Runs the monitor in a loop with the specified interval

## Error Handling

The script includes error handling to:

- Handle cases where no events are found
- Handle cases where no events pass filtering
- Handle cases where no markets are found
- Catch and display exceptions that occur during analysis
- Allow graceful termination with Ctrl+C

## Customization

To customize the monitoring behavior, you can modify the `monitor.py` script. Some possible customizations include:

- Changing the filtering criteria
- Adjusting the number of markets to analyze
- Adding additional analysis steps
- Implementing notifications for promising trade opportunities

For more information, see the main documentation in `/docs/MONITORING.md`.