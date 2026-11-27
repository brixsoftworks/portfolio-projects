# 🏎️ Nitro Drift 3D - Godot 4 Racing Game

An arcade 3D racing and drifting game built with **Godot 4.7**, featuring physics-based vehicle dynamics, dynamic chase camera, procedural sound synthesizer, multiple drivable cars, circuit checkpoints, drift scoring, and integrated **Sketchfab 3D asset importer**.

---

## 🎮 How to Play

### Instant Launch
Run the launcher script from the terminal or open the folder in Godot:
```bash
cd /home/mullainathan/godot_3d_car_game
./launch_game.sh
```
Or with Godot directly:
```bash
godot --path /home/mullainathan/godot_3d_car_game
```

---

## 🕹️ Controls

| Action | Primary Key | Alternate Key |
|---|---|---|
| **Accelerate** | `W` | `Up Arrow` |
| **Brake / Reverse** | `S` | `Down Arrow` |
| **Steer Left / Right** | `A` / `D` | `Left` / `Right Arrow` |
| **Handbrake / Drift** | `Space` | - |
| **Nitro Turbo Boost** | `Shift` (Hold) | - |
| **Switch Car (1-4)** | `1`, `2`, `3`, `4` | - |
| **Open Track Selector** | `T` | Click `🏁 SELECT TRACK` on HUD |
| **Cycle Track Prev / Next** | `[` / `]` | - |
| **Change Camera View** | `C` | - |
| **Reset / Respawn Car** | `R` | - |

---

## 🏎️ Vehicle Roster
You can switch vehicles on the fly during gameplay by pressing keys `1` through `4`:
1. **[1] Neon GT Supercar** - Ultra-responsive open-wheel formula racer with balanced handling and quick drift recovery.
2. **[2] Cyber Future Racer** - High-downforce futuristic hypercar engineered for high-speed straightaways and boost pads.
3. **[3] Sports Turbo Sedan** - Tuned street racer with high slip angle, ideal for sustained drifts around the hairpin turn.
4. **[4] Police Interceptor** - Heavy pursuit cruiser with emergency light bar and high impact resistance.

---

## 🏁 Track Features & Game Mechanics
- **Full Circuit Layout**: Over 450m of circuit containing a high-speed home straight, high-g sweeper, chicane S-curves, stunt jump ramp, and a 180° hairpin drift corner.
- **Drift Scoring & Mini Turbo**: Initiate drifts with `Space` or high-speed counter-steering. Sustaining a drift awards bonus points with escalating combo multipliers; holding a drift for over 1.2 seconds triggers a free **Mini Turbo Boost** upon exit!
- **Nitro Boost System**: Hold `Shift` for explosive forward acceleration, screen FOV expansion, engine pitch escalation, and cyan particle exhaust flames.
- **Dynamic 3D Chase Camera**: Follows the vehicle with speed-reactive FOV widening (72° to 88°), smooth rotation damping, and 3 switchable views:
  - *Action Chase Cam* (standard 3rd person)
  - *High Overhead Cam* (wide tactical view)
  - *Bumper / Hood Cam* (first-person speed sensation)
- **Sector Checkpoints & Anti-Cut System**: 8 numbered sectors enforce honest racing. Sector splits and lap times (Current vs. Best) are displayed in real time on the HUD.
- **Interactive Collectibles & Boost Pads**:
  - 🟡 *Gold Coins*: +250 points with instant melodic pickup chime.
  - 🔵 *Nitro Canisters*: Instantly refills 45% nitro tank.
  - 🔴 *Boost Pads*: High-velocity accelerator pads that propel the car across track sections.
- **100% Procedural Audio Engine**: Zero missing audio assets. The built-in GDScript synthesizer dynamically generates engine harmonic rumble (pitch scales from 0.7x idle to 2.4x redline), tire skidding noise, nitro hiss, checkpoint chimes, and victory fanfare.

---

## 🌍 Real-World Racetrack Library (41 Tracks)

Integrated collection of 41 authentic, real-world racing circuits from Tyler_Dave's collection, featuring:
- **Instant In-Game Switching**: Press `T` anytime to open the Racetrack Selector with live search, or use `[` / `]` to cycle circuits on the fly.
- **Dynamic 3D Trimesh Collisions**: Automatically generates precise collision surfaces on all roads, kerbs, banking, and elevation changes.
- **Surface Elevation & Spawn Positioning**: Automatically detects the track surface, grounds the car at the starting straight, and updates respawn points (`R`).
- **Start/Finish Gate & Lap Timing**: Integrated checkpoint gate records sector splits and best lap times.
- **Featured Tracks Include**:
  - 🇧🇪 **Circuit Zolder**
  - 🇲🇨 **Monte Carlo Rally Stage**
  - 🇩🇪 **Nürburgring Gesamtstrecke (Nordschleife 1967)** & **Nürburgring GP (2016, 2022)**
  - 🇩🇪 **Sachsenring (2020)** & **Hockenheimring (1988)**
  - 🇮🇹 **Autodromo Nazionale Monza (1998 & 2020)** & **Imola Circuit (2024)**
  - 🇧🇪 **Circuit de Spa-Francorchamps (1992, 1998 & 2022)**
  - 🇬🇧 **Silverstone Circuit (1999 & 2024)**
  - 🇪🇸 **Barcelona-Catalunya GP (2023)** & **Circuito de Madrid (2026)**
  - 🇺🇸 **Daytona International Speedway** & **Indianapolis Motor Speedway**
  - 🇦🇺 **Albert Park Melbourne**, 🇨🇦 **Montreal Circuit Gilles Villeneuve**, 🇯🇵 **Suzuka**, 🇲🇾 **Sepang**, 🇦🇹 **Red Bull Ring**, 🇧🇭 **Bahrain**, 🇨🇳 **Shanghai**, 🇦🇪 **Yas Marina Abu Dhabi**, 🇺🇸 **COTA Austin**, and more.

---

## 🎨 Sketchfab Asset Importer (`sketchfab_importer.py`)

A dedicated CLI tool is included to search and download any 3D car or track model from Sketchfab directly into the Godot project.

### 1. Search Sketchfab Catalog
Search top models by keyword, category, or filter:
```bash
python3 sketchfab_importer.py search "porsche 911"
python3 sketchfab_importer.py search "drift car" --count 10
python3 sketchfab_importer.py search "race track" --category architecture
```

### 2. Download Models Automatically
Download any model by UID using your Sketchfab API Token (obtainable for free at `sketchfab.com/settings/password`):
```bash
export SKETCHFAB_API_KEY="your_sketchfab_api_token"
python3 sketchfab_importer.py download 8568d9d14a994b9cae59499f0dbed21e
```
Or directly in the command line:
```bash
python3 sketchfab_importer.py download 8568d9d14a994b9cae59499f0dbed21e --token "your_token"
```
The script automatically downloads the GLTF/GLB archive, extracts textures and meshes into `assets/sketchfab/<uid>/`, and makes them ready to import into Godot!
