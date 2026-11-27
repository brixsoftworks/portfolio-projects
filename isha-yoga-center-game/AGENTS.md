# Isha Yoga Center & Adiyogi 3D Exploration Game - Memory & Architecture

## 1. Project Overview & Engine Specifications
- **Engine**: Godot Engine 4.4+ / 4.7+ (Forward+ Vulkan renderer).
- **Target Hardware**: High-performance PC (NVIDIA RTX 5060 Laptop GPU, Vulkan 1.4).
- **Visual Standards**: PBR 4K textures, VoxelGI realistic global illumination, Viewport TAA (Temporal Anti-Aliasing), Debanding, Anisotropic filtering.
- **Repository**: `https://github.com/brixsoftworks/isha-yoga-center-game.git`
- **Branch**: `main`
- **Collaborators**: `brixsoftworks` (owner), `shiva7icorp-sys` (collaborator with write access).

---

## 2. Spatial Layout & Geospatial Truth
The world is oriented on a real-world scale (1 Godot unit = 1 meter):

- **Adiyogi Statue**:
  - Position: `(0.0, 0.0, 0.0)`, facing due South (`+Z` direction).
  - Statue Height: 112 feet (~34.2 meters).
  - Walkway around statue: Full 360-degree walkable perimeter.
  - Mandapa Sanctum: Situated in front of statue (`Z` around `25.0` to `45.0`).

- **Stepped Plaza / Courtyard**:
  - Bounds: `X` in `[-40.0, 40.0]`, `Z` in `[-18.5, 113.1]`.
  - Elevation: Step terraces rising towards Adiyogi, baseline ground level at `Y = 0.0`.
  - South boundary curb: Sealed at `Z = 113.1` with dressed slate curb stone.

- **Ceremonial Front Avenue (20m Walkway)**:
  - Bounds: `X` in `[-10.0, 10.0]`, `Z` from `113.1` (courtyard edge) to `570.0` (Malai Vasal).
  - Road Surface: Cobblestone PBR material at `Y = 0.18m`.
  - Entrance Ramp: Connects `Z = 113.1` (`Y = 0.0`) to `Z = 115.5` (`Y = 0.18`), zero gaps.
  - Road Side Edges (Curbs): Dressed ashlar slate 3D extruded curbs along West (`X ≈ -10.0`) and East (`X ≈ +10.0`), top surface at `Y = 0.32m` (+14cm above road), 60cm width with chamfer and foundation skirt to `Y = -0.65m`.

- **Vegetation & Landscaping**:
  - 3D Grass Tufts: 1,480+ `grass_tuft_3d.glb` instances via `MultiMeshInstance3D` along curbs.
  - 3D Foliage Shrubs: 152 `realistic_shrub.glb` dense foliage shrubs via `MultiMeshInstance3D`.
  - Indian Shade Trees: 44 trees lining the avenue (`neem_broadleaf_tree_opt.glb`, `palm_tree.glb`, `palm_tree_dense.glb`) with collision cylinders on trunks.
  - Terrain: Natural rolling red laterite mud and lush grass blended via `shaders/terrain_blend.gdshader`.

- **Malai Vasal (Hill Entrance Gateway)**:
  - Position: `Z = 570.0` directly on the front avenue axis in front of Adiyogi.
  - Architecture: Massive 235-ton natural granite boulder archway, dressed stone pillars, ornamental iron gates.

- **Excluded Areas**:
  - Inner temple complex (Dhyanalinga, Linga Bhairavi, Suryakund, Chandrakund) was removed per explicit user instruction to keep the game focused strictly on Adiyogi and Malai Vasal. Do NOT re-add without user request.

---

## 3. Gameplay Mechanics
- **Player Character**: Third-person character in traditional white dhoti and kurta (`scenes/player.tscn`). Smooth third-person spring-arm camera.
- **Vintage Bicycle**: Roadster bicycle (`scenes/bicycle.tscn`) dynamically attachable to the player. Handles pedaling, coasting, acceleration, braking, and physics.

---

## 4. Repository Structure & File Cleanliness Rules
- `scenes/`: Only core game scenes (`main.tscn`, `player.tscn`, `bicycle.tscn`).
- `scripts/`: Only runtime game logic (`main.gd`, `player.gd`, `bicycle.gd`).
- `tools/`: Offline Python generators, Blender scripts, and baking tools.
- `shaders/`: Godot visual and compute shaders (`terrain_blend.gdshader`, `water.gdshader`).
- `assets/`: Game models (`assets/models/`), textures (`assets/textures/`), audio, and VoxelGI caches.
- **NEVER** save screenshots, logs, backup files (`.bak`), or test scratch scripts in the repository root. Keep git working tree clean at all times.
