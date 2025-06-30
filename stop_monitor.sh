#!/bin/bash

# Script to stop the background monitor process

PID_FILE="logs/monitor.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "No monitor process found. PID file does not exist."
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null; then
    echo "Stopping monitor process with PID: $PID"
    kill "$PID"
    rm "$PID_FILE"
    echo "Monitor process stopped successfully."
else
    echo "Monitor process with PID $PID is not running."
    rm "$PID_FILE"
    echo "Removed stale PID file."
fi