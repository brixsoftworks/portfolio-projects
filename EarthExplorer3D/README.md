# EarthExplorer3D: Planetary Geospatial 3D Simulation & Autonomous MCP Pipeline

**Lead Systems Architect:** Mullainathan (`mullainathan95@gmail.com`)  
**Organization:** Brix Softworks  
**Role:** Principal Systems Architect & Senior Software Engineer  
**Repository Status:** Production / Fully Functional  

---

## Executive Summary

EarthExplorer3D is a high-performance planetary-scale flight simulation engine and automated 3D development pipeline built with **Unity 6 Engine**, **Cesium for Unity**, and **Google Photorealistic 3D Tiles**. 

The platform integrates an automated **Model Context Protocol (MCP)** pipeline connecting LLM agent workstations directly to live Unity editor sessions, headless Blender instances, and Higgsfield AI generative video/texture models. This enables programmatic spatial inspection, asset generation, terrain synthesis, and flight trajectory optimization from natural language control.

The simulation runtime implements true 64-bit double-precision georeferencing, high-speed terrain tile streaming, 6-Degree-of-Freedom (6DOF) flight kinematics, and real-time atmospheric post-processing running on the Vulkan graphics API.

---

## System Architecture

```
  [ Claude Desktop / Agent Host ]
                 │
                 ├──[ Model Context Protocol (MCP) Router ]
                 │                    │
                 │                    ├── [ Unity Engine MCP Bridge ] (uvx: mcp-for-unity)
                 │                    │    - Scene hierarchy traversal
                 │                    │    - Script hot-reloading & compilation
                 │                    │    - Play-mode telemetry & camera manipulation
                 │                    │
                 │                    ├── [ Blender 3D MCP Bridge ] (uvx: blender-mcp)
                 │                    │    - Procedural CAD & mesh generation
                 │                    │    - Texture baking & FBX/GLTF asset export
                 │                    │
                 │                    └── [ Higgsfield AI & Media API ] (mcp-remote)
                 │                         - Cinematic synthetic texturing & skies
                 │
                 ▼
  [ Unity 6 Engine Runtime ]
         │
         ├── [ Cesium 3D Tileset Native Subsystem ]
         │      - 3D Tiles 1.1 Specification (OGC)
         │      - Hierarchical Level-of-Detail (HLOD) streaming
         │      - Dynamic Octree screen-space error (SSE) optimization
         │
         ├── [ Google Maps Platform Photorealistic 3D Tiles API ]
         │      - Global textured 3D mesh ingestion
         │      - Sub-meter geometry resolution for metropolitan cores
         │
         └── [ Kinematics & Avionics Engine ]
                - 6DOF Newtonian physics solver
                - Inertia tensors, thrust curves, and dynamic aerodynamic drag
                - Real-time GPS coordinate telemetry HUD
```

---

## Technical Specifications & Infrastructure

- **Engine:** Unity 6 LTS (6000.0+) / Unity 2022.3 LTS.
- **Rendering Backend:** Forward+ rendering on Vulkan 1.4 / DirectX 12 with Temporal Anti-Aliasing (TAA) and Depth of Field.
- **Geospatial Pipeline:** Cesium for Unity native package (`com.cesium.unity`) utilizing WGS84 ellipsoidal coordinate transformations.
- **Data Ingestion:** Google Maps Platform Photorealistic 3D Tiles via authenticated REST endpoints.
- **Automation Protocol:** Model Context Protocol (MCP) JSON-RPC bridge over stdio and Server-Sent Events (SSE).
- **Target Hardware Architecture:** x86_64 Linux (Fedora 44), NVIDIA RTX 5060 (8GB VRAM, Driver 620+), Intel Core 7 240H (16 Threads), 16GB DDR5 RAM.

---

## Connected MCP Agent Services

| Service | MCP Bridge Adapter | Functional Scope |
| :--- | :--- | :--- |
| **Unity Engine** | `mcp-for-unity` (`uvx`) | Live scene hierarchy inspection, component inspection, script authoring, and Play-mode automation. |
| **Blender 3D** | `blender-mcp` (`uvx`) | Procedural 3D modeling, asset ingestion (Poly Haven, Sketchfab), and zero-loss export to Unity assets. |
| **Higgsfield AI** | `mcp-remote` (SSE/HTTP) | Generative neural textures, skybox maps, and video sequence synthesis via natural language. |
| **Google Maps Platform** | `@modelcontextprotocol/server-google-maps` | WGS84 coordinate resolution, geocoding, and planetary elevation profile extraction. |

---

## Kinematics & Avionics Controls

The flight control system utilizes a deterministic 6DOF aerodynamic physics controller with variable damping, banking compensation, and supersonic velocity scaling:

- **W / S:** Longitudinal Pitch (Dive / Climb) and Forward Propulsion.
- **A / D:** Lateral Strafe and Horizontal Coordinate Translation.
- **Space:** Vertical Climb (Upward Vector).
- **Left Control:** Vertical Descent (Downward Vector).
- **Left Shift:** Afterburner Thrust Vector (3.0x velocity scalar).
- **Q / E:** Angular Roll and Aerodynamic Banking.
- **Mouse Drag (Right Mouse Button):** Dual-Axis Free-Look and Gimbal Pitch/Yaw.
- **Key 1:** Real-Time Geodetic Warp to Indexed Planetary Landmarks:
  - San Francisco Bay & Golden Gate (`37.8199 N, 122.4783 W`)
  - Manhattan Financial District (`40.7128 N, 74.0060 W`)
  - Tokyo Shibuya Crossing (`35.6595 N, 139.7004 E`)
  - Paris Eiffel Tower & Champ de Mars (`48.8584 N, 2.2945 E`)
  - Dubai Downtown & Burj Khalifa (`25.1972 N, 55.2744 E`)
  - Himalayan Range & Mount Everest (`27.9881 N, 86.9250 E`)

---

## Setup & Execution

### 1. Project Initialization

1. Launch Unity Hub.
2. Select **Add Project from disk** and open:
   ```text
   /home/mullainathan/projects/EarthExplorer3D
   ```
3. Ensure the project opens under Unity 6 LTS.

### 2. Configure Photorealistic 3D Tiles

1. Navigate to **Cesium > Cesium Window** in the top menu bar.
2. Connect your Cesium ion account or configure direct Google Photorealistic 3D Tiles streaming:
   ```text
   https://tile.googleapis.com/v1/3dtiles/root.json?key=YOUR_GOOGLE_MAPS_API_KEY
   ```
3. Load the primary scene `Assets/Scenes/MainFlightSim.unity` and press **Play**.

### 3. Agentic Automation Interface

To connect autonomous LLM agents to the live simulation:
```bash
# Verify active MCP bridge listener
curl -s http://localhost:9876/status
```
Agents running inside Claude Desktop or standalone CLI processes can directly query spatial transforms, spawn vehicle prefabs, or manipulate camera angles via standard MCP tool calls.

---

## Authorship & Intellectual Property

- **Lead Systems Architect:** Mullainathan
- **Email:** mullainathan95@gmail.com
- **Organization:** Brix Softworks
- **License:** Proprietary - All rights reserved by Mullainathan
