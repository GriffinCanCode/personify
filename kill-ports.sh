#!/bin/bash

# Kill processes on ports used by backend and frontend
# Backend: 8000, Frontend: 3000

echo "🔍 Checking for processes on ports 8000 and 3000..."

# Function to kill process on a specific port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    
    if [ -n "$pid" ]; then
        echo "  ⚠️  Found process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null
        echo "  ✓ Killed process on port $port"
    else
        echo "  ✓ Port $port is free"
    fi
}

# Kill backend port (8000)
kill_port 8000

# Kill frontend port (3000)
kill_port 3000

echo "✅ Port cleanup complete!"

