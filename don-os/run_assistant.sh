#!/bin/bash
# run_assistant.sh
# One-click launcher for the Antigravity PA Personal Assistant (Electron GUI + Python Brain)

# Unset IDE-inherited Electron variables
unset ELECTRON_RUN_AS_NODE

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"

echo "=========================================================="
echo "   Starting Antigravity PA Assistant (Electron + Brain) "
echo "=========================================================="

# 1. Start Python Agent Server if not running
if ! curl -s http://127.0.0.1:8765/api/health > /dev/null 2>&1; then
    echo "• Launching Python Agent Server on port 8765..."
    python3 agent_server.py &
    SERVER_PID=$!
    
    # Wait for server ready
    for i in {1..20}; do
        if curl -s http://127.0.0.1:8765/api/health > /dev/null 2>&1; then
            echo "• Python Agent Server is ONLINE!"
            break
        fi
        sleep 0.5
    done
else
    echo "• Python Agent Server is already running."
fi

# 2. Launch Electron Desktop GUI
echo "• Launching Electron Desktop Interface..."
cd electron_app
./node_modules/.bin/electron --no-sandbox --disable-dev-shm-usage .


# 3. Cleanup on exit
if [ ! -z "$SERVER_PID" ]; then
    echo "• Stopping backend agent server (PID: $SERVER_PID)..."
    kill $SERVER_PID 2>/dev/null
fi
echo "• PA Assistant closed."

