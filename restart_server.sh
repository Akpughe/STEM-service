#!/bin/bash
# Quick script to restart the server with latest changes

echo "========================================"
echo "Restarting STEM Service with Latest Code"
echo "========================================"
echo ""

# Check if server is running
echo "Checking for running server..."
SERVER_PID=$(pgrep -f "python.*main.py" || pgrep -f "uvicorn.*main:app")

if [ ! -z "$SERVER_PID" ]; then
    echo "Found running server (PID: $SERVER_PID)"
    echo "Stopping server..."
    kill $SERVER_PID
    sleep 2

    # Force kill if still running
    if pgrep -f "python.*main.py" > /dev/null || pgrep -f "uvicorn.*main:app" > /dev/null; then
        echo "Force stopping server..."
        pkill -9 -f "python.*main.py"
        pkill -9 -f "uvicorn.*main:app"
        sleep 1
    fi
    echo "✓ Server stopped"
else
    echo "No running server found"
fi

echo ""
echo "Starting server with updated code..."
python main.py &
echo "✓ Server starting in background"
echo ""
echo "Waiting 3 seconds for server to initialize..."
sleep 3
echo ""
echo "========================================"
echo "Server should now be running!"
echo "Try the health check: curl http://localhost:8000/health"
echo "========================================"
