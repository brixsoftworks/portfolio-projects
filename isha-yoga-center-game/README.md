# Isha Yoga Center & Adiyogi 3D Simulation Experience

**Lead Systems Architect:** Mullainathan (`mullainathan95@gmail.com`)  
**Organization:** Brix Softworks  
**Role:** Principal Systems Architect & Senior Software Engineer  
**Engine:** Godot Engine 4.7+ (Forward+ Vulkan 1.4 Clustered Renderer)  
**Standalone Repository:** [brixsoftworks/isha-yoga-center-game](https://github.com/brixsoftworks/isha-yoga-center-game)  
**Repository Status:** Production / Active Simulation  

---

## Executive Summary

An authentic, geographically calibrated 3D interactive digital twin of the sacred precinct at the **Isha Yoga Center**, situated at the foothills of the Velliangiri Mountains in Coimbatore, Tamil Nadu.

Engineered on Godot 4 running the **Forward+ Vulkan 1.4 clustered renderer**, the simulation features high-density sculpted architectural assets, true-to-scale GPS georeferenced landmarks, VoxelGI realistic bounce global illumination, Viewport Temporal Anti-Aliasing (TAA), custom multi-layer terrain blending shaders, and hardware-accelerated vegetation instancing.

The platform includes an interactive mountable vintage bicycle physics system with authentic forward seating, steer banking, dynamic wheel rotation, and pedaling animation state machines.

---

## Geographically Calibrated Precinct Layout

All landmarks, shrines, and plazas are positioned using real-world geodetic coordinates and millimeter-precise meter deltas relative to the 112-foot Adiyogi statue:

```text
[ 0.0m ]  Adiyogi 112-ft Shiva Statue & Stepped Granite Plaza (Facing South)
[ 156m ]  Visitor Transit Drop-Off Loop & Outer Peripheral Parkway
[ 365m ]  Bullock Cart Station & Palm Tree Boulevard
[ 635m ]  Malai Vasal Monumental Gateway with 235-ton Granite Monolith
[ 700m ]  Naga Shrine & Sacred Serpentine Granite Pedestal
[ 740m ]  Suryakund Stepped Water Complex (22-ft Subterranean Excavation & Sun Lingam)
[ 790m ]  Sarva Dharma Sthambha (Polished Granite Monolith with World Faith Symbols)
[ 841m ]  Dhyanalinga Meditation Temple (Pillarless Elliptical Burnt-Brick Dome, 48m Plaza)
[ 850m ]  Linga Bhairavi Devi Temple (36m x 36m Terracotta Brick Plinth & Inner Sanctum)
[ 871m ]  Chandrakund Subterranean Water Body (30-ft Excavation & Moon Pedestal)
[ Valley] Velliangiri Mountain Range Backdrop (High-Altitude Western Ghats Topography)
```

---

## Graphics & Rendering Architecture

- **Renderer:** Godot 4 Forward+ Vulkan 1.4 Clustered Lighting.
- **Global Illumination:** VoxelGI dynamic voxel bounce lighting paired with high-dynamic-range physical sky atmospheric models.
- **Anti-Aliasing & Post-Processing:** Viewport TAA (Temporal Anti-Aliasing), Debanding, Screen-Space Ambient Occlusion (SSAO), and Screen-Space Reflections (SSR).
- **Depth Precision:** Camera near/far clipping planes tuned (`near = 0.25m`, `far = 2500.0m`) to eliminate z-fighting across vast mountain vistas.
- **Hardware Instancing:** Vegetation pipelines (1,480+ 3D grass tufts, 152 shrubs, 44 neem and palm trees) batched via `MultiMeshInstance3D` to guarantee locked 60+ FPS performance on modern silicon (NVIDIA RTX 5060).
- **Custom Shaders:** Multi-layer terrain blending shader (`shaders/terrain_blend.gdshader`) automatically clearing vegetation under roadways while blending red gravel aprons and granite pavers.

---

## Vehicle & Character Physics

- **Vintage Yellow Bicycle:** Custom raycast suspension and kinematic controller featuring authentic rider kinematics, dynamic steer lean, angular momentum damping, and real-time wheel RPM synchronization.
- **Pedestrian Navigation:** Full 6DOF first/third-person character controller with dynamic slope compensation and sprint multipliers.

---

## Project Structure & Architecture

```text
isha-yoga-center-game/
  ├── scripts/
  │     ├── main.gd          # Precinct initialization, GPS offsets, camera capture
  │     ├── player.gd        # First/third-person character controller
  │     └── bicycle.gd       # Dynamic bicycle vehicle physics & animation
  ├── shaders/
  │     ├── terrain_blend.gdshader  # Procedural multi-texture terrain blend
  │     ├── water.gdshader          # Subterranean Suryakund water surface
  │     └── waterfall.gdshader      # Sacred cascade refraction shader
  ├── tools/
  │     ├── build_dhyanalinga_temple.py   # Procedural dome & monolith builder
  │     ├── build_lingabhairavi_temple.py # Terracotta brick plinth generator
  │     └── generate_nature_models.py     # Vegetation PBR generator
  ├── AGENTS.md              # Engineering standards & coordinate contracts
  ├── TECH_STACK_AND_WORKFLOW.md # Comprehensive 3D modeling workflow documentation
  └── project.godot          # Godot 4 engine configuration
```

---

## Authorship & Intellectual Property

- **Lead Systems Architect:** Mullainathan
- **Email:** mullainathan95@gmail.com
- **Organization:** Brix Softworks
- **License:** Proprietary - All rights reserved by Mullainathan
