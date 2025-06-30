#!/bin/bash

# Script to check the status of the background monitor process and view logs

PID_FILE="logs/monitor.pid"

# Check if the monitor is running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
        echo "Monitor is running with PID: $PID"
        
        # Find the most recent log file
        LATEST_LOG=$(ls -t logs/monitor_*.log 2>/dev/null | head -n 1)
        
        if [ -n "$LATEST_LOG" ]; then
            echo "Latest log file: $LATEST_LOG"
            echo ""
            echo "=== Last 20 lines of log ==="
            tail -n 20 "$LATEST_LOG"
            echo ""
            echo "To view the full log, run: less $LATEST_LOG"
        else
            echo "No log files found."
        fi
    else
        echo "Monitor process with PID $PID is not running (stale PID file)."
        echo "You can remove the stale PID file with: rm $PID_FILE"
    fi
else
    echo "Monitor is not running. No PID file found."
    
    # Check if there are any log files
    LATEST_LOG=$(ls -t logs/monitor_*.log 2>/dev/null | head -n 1)
    if [ -n "$LATEST_LOG" ]; then
        echo "Latest log file from previous run: $LATEST_LOG"
        echo "To view the log, run: less $LATEST_LOG"
    fi
fi