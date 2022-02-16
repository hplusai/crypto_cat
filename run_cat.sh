#!/usr/bin/bash
if pgrep -f "cat.py" &>/dev/null; then
    echo "it is already running"
    exit
else
    python3 cat.py
fi