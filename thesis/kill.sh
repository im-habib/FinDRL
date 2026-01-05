#!/bin/bash

# Define the port to check
PORT=8000

# Check if a process is using the port
if lsof -i :$PORT > /dev/null; then
    # Get the PID of the process using the port
    PID=$(lsof -t -i :$PORT)
    echo "Found process on port $PORT (PID: $PID)"
    echo "Killing process..."
    kill -9 $PID
    sleep 1  # Wait briefly to ensure the port is released
    echo "Process killed."
else
    echo "No process found on port $PORT"
fi