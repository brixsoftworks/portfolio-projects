#!/usr/bin/env bash
# ==============================================================================
# MINI Drone Control Station Launcher (TSX Enterprise Cockpit)
# ==============================================================================
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
export PYTHONUNBUFFERED=1

# If user requested OpenCV native window specifically:
if [[ "$1" == "--opencv" || "$1" == "--native" ]]; then
    echo "[*] Launching MINI Drone Control Station (OpenCV Native Mode)..."
    exec /usr/bin/python3 "$DIR/mini_drone_control_station.py"
fi

# 1. Start FastAPI + RTX 5060 AI Telemetry Server in Background
echo "[+] Initializing MINI Drone Control Station Backend (RTX 5060 + FastAPI)..."
/usr/bin/python3 "$DIR/backend_server.py" &
BACKEND_PID=$!

# Trap signals to ensure backend process is terminated on window close
cleanup() {
    echo "[*] Shutting down MINI Drone Control Station..."
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# 2. Wait for Backend Server to become active on port 8000
for i in {1..30}; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200"; then
        break
    fi
    sleep 0.2
done

# 3. Detect Preferred Browser for Standby Desktop App Window
APP_URL="http://localhost:8000"
WINDOW_ARGS="--app=$APP_URL --window-size=1366,768 --class=mini_drone_control_station"

if command -v google-chrome &>/dev/null; then
    google-chrome $WINDOW_ARGS
elif command -v chromium &>/dev/null; then
    chromium $WINDOW_ARGS
elif command -v brave-browser &>/dev/null; then
    brave-browser $WINDOW_ARGS
elif command -v firefox &>/dev/null; then
    firefox --new-window "$APP_URL"
else
    # Fallback: Open default browser
    xdg-open "$APP_URL"
    wait "$BACKEND_PID"
fi
