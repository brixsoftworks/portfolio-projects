#!/usr/bin/env bash
# ==============================================================================
# MINI AI DRONE: WEBOTS 3D SIMULATION + DJI MATRICE AI LAUNCHER
# ==============================================================================
# Launches Webots 3D Physics Simulator and attaches the RTX 5060-accelerated
# Autonomous Flight Brain (MediaPipe Gestures + ActiveTrack 360 + APAS 5.0).
# ==============================================================================

set -e

# Clean up any stale Webots or controller processes first
echo "[*] Cleaning up any previous simulation instances..."
killall -9 webots webots-bin 2>/dev/null || true
sleep 1

# Canonical path to world file (avoid flatpak symlink issues)
PROJECT_DIR="$(readlink -f /home/mullainathan/projects/mini-ai-drone)"
WORLD_PATH="${PROJECT_DIR}/webots_simulation/worlds/ai_drone_arena.wbt"
CONTROLLER_SCRIPT="${PROJECT_DIR}/webots_simulation/controllers/ai_drone_controller/ai_drone_controller.py"

# Configure Webots Python Controller API on host
export WEBOTS_HOME="/var/lib/flatpak/app/com.cyberbotics.webots/x86_64/stable/b951a7b4ed04f8c295c5c3a347e09e81bb588a102115788e0b6ae2182c9485f1/files/webots"
export PYTHONPATH="${WEBOTS_HOME}/lib/controller/python:${PROJECT_DIR}:${PYTHONPATH}"
export LD_LIBRARY_PATH="${WEBOTS_HOME}/lib/controller:${LD_LIBRARY_PATH}"
export WEBOTS_ROBOT_NAME="Mavic 2 PRO"

echo "=================================================================="
echo "LAUNCHING MINI AI DRONE IN WEBOTS 3D SIMULATION..."
echo "World:      ${WORLD_PATH}"
echo "Controller: ${CONTROLLER_SCRIPT}"
echo "AI Engine:  DJI Matrice ML (MediaPipe Gestures, ActiveTrack 360, APAS 5.0)"
echo "Hardware:   NVIDIA GeForce RTX 5060 Laptop GPU"
echo "=================================================================="

# Function to clean up background processes on exit
cleanup() {
    echo ""
    echo "[*] Shutting down Webots simulation and controllers..."
    kill "$WEBOTS_PID" 2>/dev/null || true
    killall -9 webots webots-bin 2>/dev/null || true
    echo "[+] Cleaned up successfully."
}
trap cleanup EXIT INT TERM

# 1. Start Webots with full host filesystem & /tmp IPC socket access
flatpak run --filesystem=host --filesystem=/tmp --filesystem=home \
    com.cyberbotics.webots --mode=realtime "${WORLD_PATH}" &
WEBOTS_PID=$!

echo "[*] Waiting 4 seconds for Webots 3D World to initialize..."
sleep 4

# 2. Start the AI Drone Python Controller on host (CUDA & PyTorch accelerated)
echo "[*] Attaching Autonomous AI Flight Controller..."
python3 "${CONTROLLER_SCRIPT}"

# Wait for Webots to finish if controller exited
wait "$WEBOTS_PID" 2>/dev/null || true
