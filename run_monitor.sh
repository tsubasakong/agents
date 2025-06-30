#!/bin/bash

# Convenience script to run the market monitor with proper Python path
# 
# Usage examples:
#   ./run_monitor.sh                       # Run continuous monitoring with default 1-hour interval
#   ./run_monitor.sh --interval 1800       # Run continuous monitoring with 30-minute interval
#   ./run_monitor.sh --once                # Run market analysis once and exit
#   ./run_monitor.sh --interval 60 --once  # Run market analysis once with custom settings

export PYTHONPATH="."
python scripts/python/monitor.py "$@"