# Polymarket Monitoring

This document explains how to use the monitoring functionality to continuously analyze Polymarket markets without executing trades.

## Overview

The monitoring script allows you to:

1. Analyze Polymarket events and markets
2. Calculate potential trades
3. View trade recommendations
4. All without actually executing any trades

This is useful for:
- Testing the trading algorithm
- Learning about market opportunities
- Monitoring market conditions
- Developing and refining trading strategies

## Usage

### Basic Usage

To start continuous monitoring with the default 1-hour interval:

```bash
./run_monitor.sh
```

This will run the market analysis every hour until you stop it with Ctrl+C.

### Custom Interval

To change the interval between market checks (e.g., every 30 minutes):

```bash
./run_monitor.sh --interval 1800
```

The interval is specified in seconds.

### Single Run

To run the market analysis just once and then exit:

```bash
./run_monitor.sh --once
```

You can also combine options:

```bash
./run_monitor.sh --interval 60 --once
```

### Background Monitoring

To run the monitor in the background (continues running after you close the terminal):

```bash
./run_monitor_background.sh
```

This will:
1. Start the monitor process in the background
2. Save the process ID to `logs/monitor.pid`
3. Write output to a timestamped log file in the `logs` directory

To check the status of the background monitor and view recent logs:

```bash
./check_monitor.sh
```

To stop the background monitor:

```bash
./stop_monitor.sh
```

## Output

The monitoring script will output:

1. Number of events found
2. Filtered events
3. Markets associated with those events
4. Filtered markets
5. Calculated trade recommendations

Example output:

```
Starting continuous market monitoring (interval: 3600 seconds)
Press Ctrl+C to stop

==================================================
Market analysis at 2023-07-01 12:00:00
==================================================
1. FOUND 27 EVENTS
2. FILTERED 4 EVENTS

3. FOUND 6 MARKETS

4. FILTERED 4 MARKETS
5. CALCULATED TRADE BUY 100 shares of YES at 0.65
6. WOULD TRADE 65 USDC (Trading disabled)

Sleeping for 3600 seconds...
```

## How It Works

The monitoring script uses the same analysis logic as the trading functionality but skips the final step of executing trades. It:

1. Retrieves all tradeable events from Polymarket
2. Filters events using RAG (Retrieval-Augmented Generation)
3. Maps filtered events to markets
4. Filters markets for trading opportunities
5. Calculates the best trade for the top market
6. Displays what would be traded (without executing)

## Customization

You can modify the `monitor.py` script to customize the monitoring behavior, such as:

- Changing the filtering criteria
- Adjusting the number of markets to analyze
- Adding additional analysis steps
- Implementing notifications for promising trade opportunities

## Troubleshooting

If you encounter issues:

1. Ensure your environment variables are properly set in `.env`
2. Check that you have the required API keys
3. Verify your internet connection
4. Look for specific error messages in the output

### No Events Found

If you see "No events found. Skipping further analysis." this could be due to:

1. API connectivity issues
2. No active tradeable events on Polymarket at the moment
3. Authentication issues with your API keys

Check your `.env` file to ensure all required API keys are correctly set.