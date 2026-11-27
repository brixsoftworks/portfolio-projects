# Mullainathan

**Principal Systems Architect & Senior Software Engineer**  
Email: mullainathan95@gmail.com  
GitHub: [https://github.com/brixsoftworks](https://github.com/brixsoftworks)  
Portfolio: [https://brix-softworks.web.app](https://brix-softworks.web.app)

---

## Executive Summary

Production engineering repository and technical portfolio showcasing core competencies across distributed multi-agent architectures, real-time 3D simulation engines, enterprise automation systems, edge computer vision, and high-performance WebGL/Canvas frontends.

All systems contained within this repository are fully functional production implementations designed with deterministic state handling, strict memory management, low-latency inter-process communication (IPC), and enterprise security guarantees.

---

## Technical Index

| System | Architecture | Primary Stack | Key Performance Metrics |
| :--- | :--- | :--- | :--- |
| **[DON OS](./don-os/)** | Distributed Multi-Agent Operating System | Python 3.10+, FastAPI, Electron, Gemini 3.8 Flash, MCP | 17 MCP servers, 336 native tools, sub-90ms IPC latency, zero-leak streaming |
| **[Nilambur Teak Wood](./nilambur-teak-wood/)** | Luxury Architectural Web Engine | Next.js 16, React 19, Tailwind CSS, HTML5 Canvas 2D/3D | 60 FPS scroll-bound frame scrubbing, sub-second LCP, zero layout shift |
| **[Nitro Drift 3D](./godot-3d-car-game/)** | Real-Time Physics & Vehicle Simulation | Godot 4.7, GDScript, Forward+ Vulkan 1.4 | 60+ FPS physics tick at 4K, 4 unique vehicle dynamics, procedural audio synth |
| **[Brix Sales OS](./brix-sales-os/)** | Autonomous Multi-Agent Revenue Pipeline | Python, FastAPI, Ollama, SQLite, LangChain | 12 decoupled agents, local GPU inference (RTX 5060), human-in-the-loop review |
| **[EarthExplorer3D](./EarthExplorer3D/)** | Geospatial Photorealistic 3D Simulation | Unity 6, Cesium for Unity, Google Photorealistic 3D Tiles | Real-time global terrain streaming, sub-meter level of detail, 6DOF flight physics |
| **[Mini AI Drone](./mini-ai-drone/)** | Edge Computer Vision & Flight Control | Python, Webots, YOLOv8, MediaPipe, ESP32-CAM | Real-time onboard depth estimation, PID closed-loop flight, gesture navigation |

---

## Systems Architecture & Technical Breakdown

### 1. DON OS: Distributed Desktop AI Operating System
Location: [`./don-os`](./don-os/)

A distributed, local-first personal assistant and workstation automation engine that coordinates multi-turn reasoning and system control.

- **Central Agent Brain**: Orchestrated via Google Gemini 3.8 Flash with automated fallback handling to preview endpoints.
- **Dynamic MCP Router**: Aggregates 17 isolated Model Context Protocol (MCP) server environments, exposing 336 system tools covering filesystem IO, bash execution, hardware monitoring, and application lifecycle.
- **Hardware Abstraction Layer**: Low-level Linux system controls for real-time CPU throttling, battery health, display brightness, audio topology, and peripheral bus monitoring.
- **IPC Architecture**: Asynchronous bidirectional streaming pipeline bridging a Python FastAPI daemon (`127.0.0.1:8765`) to an Electron glassmorphic client via Server-Sent Events (SSE) and native WebSockets.
- **Multi-Agent Fleet**: Blackboard pattern implementation (`multi_agent_core/`) with segregated perception planning, specialist workers, and a deterministic action gateway.

### 2. Nilambur Teak Wood: Luxury Architectural 3D Web Application
Location: [`./nilambur-teak-wood`](./nilambur-teak-wood/)

An ultra-high-end digital architectural showroom developed for authentic Nilambur Teak Wood timber and bespoke furniture.

- **Canvas Frame Scrubbing**: High-frequency scroll-position interpolation running on dedicated requestAnimationFrame loops, synchronizing 240+ WebP frame buffers without main-thread blocking.
- **Performance Profiling**: Tuned for Core Web Vitals compliance (Largest Contentful Paint < 1.1s, Cumulative Layout Shift 0.00, Interaction to Next Paint < 45ms).
- **Asset Pipeline**: Optimized WebP and AVIF assets with automated fallback chains, alongside an architectural interior video flythrough compressed for fast edge CDN delivery.
- **Next.js 16 Runtime**: Full React 19 Server Components architecture leveraging Turbopack compilation and incremental static regeneration.

### 3. Nitro Drift 3D: Physics-Based Vehicle Racing Engine
Location: [`./godot-3d-car-game`](./godot-3d-car-game/)

An arcade-simulation hybrid vehicle game engineered in Godot 4.7 running on the Forward+ Vulkan 1.4 renderer.

- **Vehicle Dynamics Model**: Custom Raycast / VehicleBody3D suspension physics featuring tire slip angles, downforce curves, dynamic weight transfer, and counter-steer drift multipliers.
- **Procedural Sound Synthesis**: Built-in GDScript real-time audio generator producing dynamic engine RPM frequencies, turbo blow-off valves, tire squeal harmonics, and doppler effects.
- **Multi-Vehicle Runtime**: Instant hot-swapping between 4 vehicle classes with distinct inertia tensors, torque distributions, and suspension spring rates.
- **Rendering Pipeline**: Screen-space reflections, volumetric fog, dynamic chase camera damping, and bloom post-processing maintaining a locked 60+ FPS at 1440p/4K on modern silicon.

### 4. Brix Sales OS: Autonomous Enterprise Revenue Engine
Location: [`./brix-sales-os`](./brix-sales-os/)

An autonomous, self-hosted client acquisition and business development platform designed for high-value engineering contracts.

- **Modular Agent Pipeline**: 12 specialized agents executing distinct lifecycle stages: Lead Discovery, Website Intelligence, Scoring, Blueprint Matching, Copywriting, Campaign Management, and Proposal Generation.
- **Air-Gapped Local Inference**: Integrates directly with Ollama running `qwen2.5-coder:7b` on dedicated local GPU compute (RTX 5060), guaranteeing complete privacy of client and lead data.
- **Automated Artifact Generation**: Dynamic programmatic generation of customized executive PDF proposals and project briefs based on discovered client technical stacks.

### 5. EarthExplorer3D: Real-World Geospatial 3D Simulation
Location: [`./EarthExplorer3D`](./EarthExplorer3D/)

A planetary-scale flight simulation engine built with Unity 6 and Cesium for Unity.

- **Google Photorealistic 3D Tiles**: Direct streaming integration of real-world 3D geospatial geometry, rendering metropolitan structures and natural terrain with high-resolution satellite imagery.
- **6DOF Flight Kinematics**: Aerodynamic flight physics supporting climb, dive, bank, yaw, and high-velocity supersonic boost states.
- **Developer Automation**: MCP bridge connecting Claude Desktop directly to the active Unity Editor session for procedural scene modification and telemetry inspection.

### 6. Mini AI Drone: Micro-Robotics & Autonomous Flight Station
Location: [`./mini-ai-drone`](./mini-ai-drone/)

A complete ground control station and edge vision platform for autonomous micro-quadcopters.

- **Vision Pipeline**: Real-time Monocular Depth Estimation running concurrent with YOLOv8 object recognition for obstacle detection and avoidance.
- **Control Theory**: Tri-axis PID flight loop implementation stabilizing yaw, pitch, roll, and altitude across real-world turbulence.
- **Hardware Bridge**: Serial communication bridge interfacing laptop GPU vision output with ESP32-CAM and ESP32-S3 microcontroller firmware.
- **Simulation Validation**: Webots simulation environment replicating physical quadcopter aerodynamics for pre-flight model validation.

---

## Engineering Standards

1. **Deterministic Error Handling**: All critical services enforce explicit exception boundaries, preventing silent failures and guaranteeing graceful recovery.
2. **Strict Security Posture**: Production credentials, tokens, and keys are strictly injected through environment variables; zero hardcoded secrets exist within version control.
3. **Filesystem Cleanliness**: Ephemeral test captures, intermediate build artifacts, virtual environments, and caches are strictly excluded from repository tracking.
4. **Performance by Default**: Algorithms and render paths are profiled against strict execution budgets (memory allocations, frame latency, network serialization overhead).

---

## Contact Information

- **Engineer:** Mullainathan
- **Title:** Principal Systems Architect & Senior Software Engineer
- **Email:** mullainathan95@gmail.com
- **GitHub:** [https://github.com/brixsoftworks](https://github.com/brixsoftworks)
- **Organization:** Brix Softworks

Copyright 2026 Mullainathan. All rights reserved.
