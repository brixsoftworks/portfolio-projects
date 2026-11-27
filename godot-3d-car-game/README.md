# Nitro Drift 3D: Physics-Based Vehicle Racing Engine

**Lead Graphics & Engine Architect:** Mullainathan (mullainathan95@gmail.com)  
**Organization:** Brix Softworks  
**Repository:** [https://github.com/brixsoftworks/godot-3d-car-game](https://github.com/brixsoftworks/godot-3d-car-game)

---

## Technical Overview

Nitro Drift 3D is a real-time vehicle dynamics simulation and arcade racing engine engineered in Godot 4.7. The project benchmarks high-fidelity physics computation, runtime procedural audio synthesis, and Forward+ Vulkan rendering performance on desktop hardware.

The engine features a custom vehicle physics pipeline with configurable tire slip curves, dynamic downforce modeling, multi-vehicle runtime instantiation, circuit checkpoint telemetry, and drift scoring algorithms.

---

## Engine Systems Architecture

### 1. Vehicle Dynamics & Suspension Pipeline
- **Physics Core:** Implemented via Godot VehicleBody3D with customized Raycast wheel suspension solvers.
- **Slip Angle Mechanics:** Mathematical friction calculation translating lateral lateral acceleration into controlled oversteer.
- **Dynamic Downforce:** Non-linear aerodynamic drag and downforce scaling proportionally with forward velocity.
- **Vehicle Presets:** Runtime swappable vehicle archetypes:
  - Open-Wheel Formula GT: High downforce, high lateral stiffness, rapid transient response.
  - Cyber Prototype: High straight-line velocity, low aerodynamic drag profile.
  - Tuned Sports Sedan: Soft rear spring rate, extended drift slip angle.
  - Pursuit Interceptor: High mass inertia tensor, reinforced collision impulse response.

### 2. Procedural Audio Synthesis
- **Engine Synthesizer:** Real-time audio waveform generator (`scripts/audio_synth.gd`) computing frequency modulation proportional to motor RPM and throttle input.
- **Harmonic Layers:** Procedural audio blending for tire squeal frequency shifts, turbo blow-off release valves, and ambient doppler passing cues.

### 3. Rendering & Post-Processing
- **Graphics API:** Forward+ Vulkan 1.4 pipeline utilizing 16x anisotropic filtering and temporal antialiasing.
- **Visual Features:** Volumetric fog, dynamic shadow cascades, bloom lighting, and high-dynamic-range tonemapping locked at 60+ FPS at 1440p and 4K resolutions.

### 4. Race Management & Telemetry
- **Telemetry Loop:** Real-time checkpoint tracking, lap time delta calculation, and sector interval validation.
- **Drift Scoring Engine:** Continuous angular deviation calculation multiplying score metrics during sustained slide states.

---

## Repository Structure

```text
godot-3d-car-game/
|-- assets/
|   |-- cars/                # 3D vehicle meshes, PBR textures, and collision hulls
|   |-- props/               # Trackside structures, barriers, grandstands, and foliage
|   `-- track/               # Modular circuit sections, asphalt meshes, and kerbs
|-- scenes/
|   |-- car.tscn             # Configurable base vehicle scene
|   |-- hud.tscn             # Real-time telemetry and instruments overlay
|   |-- main_game.tscn       # Master game world with lighting and environment
|   `-- track.tscn           # Assembled circuit with physical collision barriers
|-- scripts/
|   |-- audio_synth.gd       # Procedural engine audio synthesis
|   |-- car_controller.gd    # Vehicle kinematics, throttle, brake, and steering
|   |-- chase_camera.gd      # Smooth damped third-person camera rig
|   |-- checkpoint.gd        # Sector split timing trigger boundaries
|   |-- hud.gd               # Telemetry rendering and speed gauge display
|   |-- race_manager.gd      # State management, lap tracking, and scoring
|   `-- track_manager.gd     # Dynamic checkpoint indexing and race initialization
|-- project.godot            # Godot 4.7 engine configuration
`-- launch_game.sh           # Terminal launcher script
```

---

## Controls & Input Mapping

| Action | Primary Input | Secondary Input |
| :--- | :--- | :--- |
| Throttle | W | Up Arrow |
| Brake / Reverse | S | Down Arrow |
| Steering Left / Right | A / D | Left / Right Arrow |
| Handbrake / Drift | Spacebar | - |
| Nitro Boost | Left Shift | - |
| Cycle Vehicle Class | 1, 2, 3, 4 | - |
| Toggle Camera Angle | C | - |
| Reset Vehicle Position | R | - |

---

## Execution & Running

### Option 1: Standalone Bash Launcher
```bash
cd /home/mullainathan/projects/godot-3d-car-game
./launch_game.sh
```

### Option 2: Godot 4 Engine CLI
```bash
godot --path /home/mullainathan/projects/godot-3d-car-game
```

---

## Performance Targets

- **Frame Time:** Consistent 16.6ms frame intervals (60 FPS) with 0.1% low variance.
- **Physics Tick Rate:** 60 Hz fixed simulation steps maintaining deterministic collision resolution.
- **Memory Overhead:** Total VRAM allocation under 650MB across high-resolution track geometry and textures.

Copyright 2026 Mullainathan. All rights reserved.
