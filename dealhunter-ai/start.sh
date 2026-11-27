#!/bin/bash
# DealHunter AI - Local Backend Startup Script
# Requires: node, cloudflared
set -e

BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_LOG="/tmp/dealhunter-backend.log"
TUNNEL_LOG="/tmp/dealhunter-tunnel.log"

echo "=== DealHunter AI Backend ==="

# Kill any existing instances
pkill -f "node server.js" 2>/dev/null || true
pkill -f "cloudflared tunnel" 2>/dev/null || true
sleep 1

# Start backend
echo "[1/2] Starting backend..."
cd "$BACKEND_DIR"
nohup node server.js > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
sleep 3

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "ERROR: Backend failed to start. Check $BACKEND_LOG"
    cat "$BACKEND_LOG"
    exit 1
fi
echo "  Backend running (PID: $BACKEND_PID)"

# Verify backend
if curl -s --max-time 3 http://localhost:3001/api/health > /dev/null 2>&1; then
    echo "  Backend health: OK"
else
    echo "ERROR: Backend health check failed"
    exit 1
fi

# Start tunnel
echo "[2/2] Starting Cloudflare tunnel..."
nohup cloudflared tunnel --url http://localhost:3001 > "$TUNNEL_LOG" 2>&1 &
TUNNEL_PID=$!
sleep 12

TUNNEL_URL=$(grep -o 'https://[a-z-]*\.trycloudflare\.com' "$TUNNEL_LOG" | head -1)
if [ -z "$TUNNEL_URL" ]; then
    echo "ERROR: Failed to get tunnel URL. Check $TUNNEL_LOG"
    cat "$TUNNEL_LOG"
    exit 1
fi

echo "  Tunnel running (PID: $TUNNEL_PID)"
echo ""
echo "=== READY ==="
echo "Backend:  http://localhost:3001"
echo "Tunnel:   $TUNNEL_URL"
echo ""
echo "Update VITE_API_URL on Vercel to: $TUNNEL_URL"
echo ""
echo "To stop: pkill -f 'node server.js' && pkill -f 'cloudflared tunnel'"
