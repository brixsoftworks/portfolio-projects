# Software, Tools & Technical Workflow Guide

This document provides a comprehensive overview of all the software, tools, libraries, and workflows used to develop and run the **Isha Yoga Center & Adiyogi 3D Exploration Game**.

---

## 1. Core Game Engine: Godot Engine 4 (v4.7+ Forward+ Vulkan)

**Godot Engine 4** serves as the primary real-time 3D game engine and runtime simulation environment.

### How It Is Used:
- **Renderer (Forward+ Clustered Vulkan 1.4)**:
  - Utilizes Vulkan hardware acceleration on the **NVIDIA GeForce RTX 5060 Laptop GPU** for desktop-tier graphical fidelity.
  - Configured with **Viewport TAA (Temporal Anti-Aliasing)**, **MSAA 2X**, and **Debanding** in `scripts/main.gd` to completely eradicate pixel shimmering and specular aliasing on fine geometric edges.
- **VoxelGI (Real-Time Voxel Global Illumination)**:
  - Bakes and renders realistic indirect lighting bounces for temple pillars, granite mandapa structures, and the cobblestone avenue.
  - Voxel data is cached to `assets/voxel_gi_data.res` and loaded dynamically.
- **Procedural Mesh Generation (`SurfaceTool` & `ArrayMesh`)**:
  - The entire **20-meter front avenue** (from $Z = 113.1$ to $Z = 570.0$), the **curved entrance transition ramp**, the **3D dressed stone curbs**, and the courtyard barriers are generated mathematically in GDScript with calculated vertex normals and UV coordinates.
- **Hardware-Instanced Foliage (`MultiMeshInstance3D`)**:
  - Over **1,480+ 3D grass tufts** and **152 dense green foliage shrubs** are rendered in a single GPU draw call using `MultiMeshInstance3D`, ensuring steady 60+ FPS performance.
- **Character & Dynamic Bicycle Mechanics (`scripts/player.gd` & `scripts/bicycle.gd`)**:
  - Custom `CharacterBody3D` controller handling walking, sprinting, and jumping.
  - Physics-based roadster bicycle attachment with dynamic pedaling and coasting animations, acceleration curves, banking turns, and spring-arm camera framing.
- **Custom Shaders (`shaders/terrain_blend.gdshader` & `shaders/water.gdshader`)**:
  - Multi-texture splatting that smoothly transitions between red laterite earth and lush grass while dynamically suppressing grass under roads and plazas using world coordinates.

---

## 2. 3D Modeling & Digital Content Creation: Blender 4.x & Python `bpy`

**Blender** is used for 3D modeling, asset optimization, bone rigging, and texture baking.

### How It Is Used:
- **Architectural & Landmark Assets**:
  - Modeling and tuning authentic structures: `assets/models/adiyogi_112ft.glb`, `assets/stepped_plaza.glb`, `assets/models/vintage_bicycle_yellow.glb`, and the monumental 235-ton granite boulder for Malai Vasal.
- **Automated Python Pipeline (`tools/`)**:
  - `tools/generate_nature_models.py`: Programmatically generates 3D foliage and botanical variations.
  - `tools/build_mandapa_roof_complete.py`: Assembles the Yogeshwar Linga sanctum roof with accurate perimeter edge sliders and dome.
  - `tools/bake_cycling_animations.py`: Rigs and bakes seamless cyclist pedaling and coasting animations.
  - `tools/export_naga_pillar.py`: Bakes and exports detailed granite Naga pillars.
- **PBR Baking & Material Calibration**:
  - Bakes high-resolution Normal, Roughness, and Ambient Occlusion maps using Cycles.
  - Strictly follows a zero-primitive policy: all models utilize organic topology and photorealistic PBR maps rather than crude geometric primitives.

---

## 3. Autonomous AI Orchestration: Google Antigravity CLI

**Antigravity CLI** is the agentic AI pair programmer embedded into the development workflow.

### How It Is Used:
- **Procedural Geometry & Shading Development**:
  - Calculates mathematical profiles for road bevels, curb skirts, elevation transitions, and terrain height functions.
  - Authors custom GLSL/Godot shaders for terrain blending and water reflections.
- **Headless Testing & Automated Verification**:
  - Automates headless camera verification passes to capture high-resolution in-game screenshots and inspect alignment before user delivery.
- **Specialized Game Dev & Shading Skills**:
  - Equipped with domain-specific skills:
    - `godot-shaders`: Advanced spatial, canvas, and compute shaders.
    - `godot-3d-essentials`: Lighting, transforms, VoxelGI, and camera systems.
    - `godot-gdscript-patterns`: Idiomatic Godot 4 architecture and signal design.
    - `blender-materials`: PBR Principled BSDF calibration and UV unwrapping.
    - `claude-mem` & `memory-md-management`: Persistent cross-session knowledge storage.

---

## 4. Geospatial Analysis & Scaling: Google Maps & Earth Satellite Data

**Google Maps and satellite elevation data** provide the real-world source of truth for all spatial layouts.

### How It Is Used:
- **Scale Calibration**:
  - $1.0\text{ Godot Unit} = 1.0\text{ Meter}$ in the real world.
- **Orientation & Axis Alignment**:
  - Adiyogi statue is positioned at origin $(0, 0, 0)$ facing due South ($+Z$).
  - Front ceremonial avenue extends south along the $+Z$ axis for $457\text{ meters}$ directly to Malai Vasal at $Z = 570.0$.
  - Avenue width is locked to exactly $20.0\text{ meters}$ flanked by pedestrian verges.

---

## 5. Version Control & Collaboration: Git & GitHub CLI (`gh`)

**Git** and the **GitHub CLI** manage the repository and team collaboration.

### How It Is Used:
- **Repository**: Hosted privately at `https://github.com/brixsoftworks/isha-yoga-center-game.git`.
- **Branch Strategy**: Fast-forward feature delivery directly on the `main` branch.
- **Multi-Collaborator Management**:
  - Repository Owner: `brixsoftworks`
  - Collaborator: `shiva7icorp-sys` (push and write access managed via `gh api`).
- **Filesystem Hygiene**:
  - Strict `.gitignore` enforcing clean working trees by ignoring `.godot/` engine caches, loose verification screenshots, temporary logs, and backup files.
  - Clear separation of concerns: runtime scripts in `scripts/`, offline generators in `tools/`.

---

## 6. Operating System & Graphics Stack: Linux (Fedora 41 / RTX 5060)

### How It Is Used:
- **OS**: Linux (Fedora, Btrfs filesystem, Wayland/X11).
- **GPU Drivers**: Official NVIDIA proprietary drivers supporting Vulkan 1.4 and Forward+ clustered rendering.
- **Direct Display Execution**: Live interactive instances are spawned directly to `DISPLAY=:0`, allowing instantaneous gameplay testing with keyboard and mouse input.

---

## 7. Project Directory Layout

```
IshaGodot/
├── AGENTS.md                  # Persistent agent memory & architectural rules
├── README.md                  # Project overview, features & player controls
├── TECH_STACK_AND_WORKFLOW.md # Complete software and workflow documentation (this file)
├── project.godot              # Godot 4 project configuration & rendering settings
├── .gitignore                 # Enforces clean version control
├── scenes/                    # Production game scenes
│   ├── main.tscn              # Primary world scene (Adiyogi, Avenue, Malai Vasal)
│   ├── player.tscn            # 3D character controller & camera spring-arm
│   └── bicycle.tscn           # Interactive roadster bicycle
├── scripts/                   # Core runtime game scripts (GDScript 2.0)
│   ├── main.gd                # World procedural generation, lighting, and scene init
│   ├── player.gd              # Character movement, states, and bicycle mounting
│   └── bicycle.gd             # Bicycle physics, steering banking, and pedaling
├── tools/                     # Offline generation, baking, and verification tools
│   ├── bake_cycling_animations.py
│   ├── bake_terracotta_pbr.py
│   ├── bake_voxel_gi.gd
│   ├── build_mandapa_roof_complete.py
│   ├── export_naga_pillar.py
│   ├── generate_nature_models.py
│   └── render_vegetation_curbs.gd
├── shaders/                   # Godot spatial & compute shaders
│   ├── terrain_blend.gdshader # Red mud & lush grass splatting with road suppression
│   └── water.gdshader         # Sacred pond water reflection shader
└── assets/                    # High-resolution 3D models, 4K PBR textures & sky HDRIs
    ├── models/                # Optimized .glb 3D models
    └── textures/              # PBR Albedo, Normal, Roughness, and Metallic maps
```
