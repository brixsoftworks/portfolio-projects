# EarthExplorer3D: Real-World 3D Game & AI Pipeline

An AI-accelerated real-world 3D game and simulation built with **Unity Engine**, **Google Photorealistic 3D Tiles (Cesium for Unity)**, and automated through **Claude Desktop** with **MCP (Model Context Protocol)** connected to **Unity**, **Blender**, and **Higgsfield AI**.

---

## 🖥️ System Architecture & Hardware Specs

- **OS:** Fedora Linux 44 (Workstation Edition, x86_64)
- **CPU:** Intel(R) Core(TM) 7 240H (16 Threads, up to 5.2 GHz)
- **GPU:** NVIDIA GeForce RTX 5060 Laptop (8GB GDDR6 VRAM, Driver 620.70.06, Vulkan & CUDA 13.5)
- **RAM:** 16 GB DDR5
- **Storage:** NVMe SSD (/home/mullainathan/Projects)

---

## 🔌 Connected AI & MCP Pipeline

Claude Desktop is configured via `~/.config/Claude/claude_desktop_config.json`:

| Service | MCP Bridge Type | Functionality |
| :--- | :--- | :--- |
| **Unity Engine** | `mcp-for-unity` (`uvx`) | Live scene inspection, script authoring, object instantiation, and Play-mode automation from Claude. |
| **Blender 3D** | `blender-mcp` (`uvx`) | Procedural 3D modeling, asset import (Poly Haven / Sketchfab), and direct export to Unity. |
| **Higgsfield AI** | `mcp-remote` (SSE/HTTP) | Generative cinematic video, textures, and multimodal asset generation via Claude prompts. |
| **Google Maps / Earth** | `@modelcontextprotocol/server-google-maps` | Real-world geolocation resolution, coordinates lookup, and elevation queries. |

---

## 🚀 Quick Start Guide

### 1. Launch Claude Desktop
Launch Claude Desktop from your GNOME application menu or from the terminal:
```bash
claude-desktop
```
In Claude Desktop, look for the **MCP Hammer/Plug icon** in the bottom right of the prompt box to see your active tools for **Unity**, **Blender**, and **Higgsfield**.

---

### 2. Connect Blender to Claude
1. Open Blender:
   ```bash
   blender
   ```
2. In the 3D Viewport sidebar (press `N` if hidden), go to the **MCP for Blender** tab.
3. Click **Start MCP Server** (running on `localhost:9876`).
4. You can now ask Claude Desktop:
   > *"Generate a futuristic drone chassis in Blender and export it as FBX to `/home/mullainathan/Projects/EarthExplorer3D/Assets/Models/Drone.fbx`."*

---

### 3. Open the Game in Unity
1. Launch Unity Hub:
   ```bash
   unityhub
   ```
2. Click **Add Project from disk** and select:
   ```text
   /home/mullainathan/Projects/EarthExplorer3D
   ```
3. Open the project with **Unity 6 LTS** (or 2022.3 LTS).
4. The project automatically loads:
   - **Cesium for Unity** (`com.cesium.unity`) via the Cesium scoped registry.
   - **MCP for Unity** (`com.coplaydev.unity-mcp`) to enable Claude's live connection.

---

### 4. Enable Google Photorealistic 3D Tiles
1. In the Unity Editor top menu, open **Cesium > Cesium**.
2. Click **Connect to Cesium ion** (free account) OR select **Add 3D Tileset from URL**.
3. Choose **Google Photorealistic 3D Tiles** (or paste your Google Maps Platform 3D Tiles API URL):
   ```text
   https://tile.googleapis.com/v1/3dtiles/root.json?key=YOUR_GOOGLE_MAPS_API_KEY
   ```
4. Place the `PlayerFlight` prefab or attach `PlayerFlightController.cs` and `GeoCoordinatesHUD.cs` to your player camera.

---

## 🎮 Flight Controls

- **W / S:** Move Forward / Backward
- **A / D:** Strafe Left / Right
- **Space:** Ascend (Climb)
- **Left Control:** Descend (Dive)
- **Left Shift:** Boost Speed (3x)
- **Q / E:** Bank / Roll left and right
- **Mouse Drag (Right Click):** Pitch & Yaw camera view
- **1 Key:** Cycle through global landmarks (San Francisco, Manhattan NYC, Tokyo Shibuya, Paris Eiffel Tower, Burj Khalifa, Mount Everest)
