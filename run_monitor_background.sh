#!/bin/bash

# Run the monitor script in the background with nohup
# This allows the monitoring to continue even after you close the terminal
#
# Usage examples:
#   ./run_monitor_background.sh                 # Run with default settings
#   ./run_monitor_background.sh --interval 1800 # Run with 30-minute interval

# Create logs directory if it doesn't exist
mkdir -p logs

# Get current timestamp for log file name
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/monitor_${TIMESTAMP}.log"

# Run the monitor script with nohup
export PYTHONPATH="."
nohup python scripts/python/monitor.py "$@" > "$LOG_FILE" 2>&1 &

# Get the process ID
PID=$!

# Save the PID to a file for later reference
echo $PID > logs/monitor.pid

echo "Monitor started in background with PID: $PID"
echo "Logs are being written to: $LOG_FILE"
echo "To stop the monitor, run: kill $(cat logs/monitor.pid)"