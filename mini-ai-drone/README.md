# Mini AI Drone: Autonomous Micro-Robotics & Edge Computer Vision Ground Station

**Lead Systems Architect:** Mullainathan (`mullainathan95@gmail.com`)  
**Organization:** Brix Softworks  
**Role:** Principal Systems Architect & Senior Software Engineer  
**Repository Status:** Production / Fully Functional  

---

## Executive Summary

Mini AI Drone is an edge robotics, micro-avionics, and computer vision platform uniting **ESP32-CAM micro-quadcopter hardware**, an **ESP32-S3 ground controller**, and an **NVIDIA RTX 5060 accelerated AI Ground Control Station**.

The platform features real-time monocular depth estimation, concurrent YOLOv8 multi-class detection, 17-keypoint skeleton gesture tracking, biometric identity re-identification, a tactical Bird's-Eye View (BEV) radar display, and a simulated 3D physics environment built in **Webots**. 

All vision inference runs on local GPU compute achieving sub-4ms frame processing latency (>280 FPS), delivering low-latency closed-loop flight commands over a robust UDP telemetry protocol with automatic hardware failsafes.

---

## System Architecture

```
  [ Airborne Micro-Quadcopter ]
         │
         ├── ESP32-CAM (240MHz Dual-Core Xtensa LX6, 8MB PSRAM)
         │      ├── OV2640 Image Sensor (JPEG Stream @ 30 FPS)
         │      ├── MPU-6050 6-Axis Gyroscope / Accelerometer
         │      ├── BMP280 Barometric Pressure / Altimeter
         │      └── 4x Coreless Brushed DC Motors via SI2302 N-Channel MOSFETs
         │
         │  802.11b/g/n Wi-Fi UDP Stream (Port 4210 / HTTP MJPEG Port 81)
         ▼
  [ High-Performance AI Ground Station (NVIDIA RTX 5060) ]
         │
         ├── [ Hardware Abstraction & Telemetry Layer ]
         │      - Low-latency socket buffer management (buffer size = 1)
         │      - 400ms heartbeat watchdog timer with auto-disarm failsafe
         │
         ├── [ Real-Time Inference Pipeline (280+ FPS) ]
         │      ├── YOLOv8n Multi-Class Object & Pose Estimation (2.81ms)
         │      ├── Monocular DepthNet (U-Net Depth Estimation, 3.56ms)
         │      ├── Metric Learning Face Re-ID (576-Dimensional Embeddings)
         │      └── Dynamic Skeleton Gesture Interpreter (17 Keypoints)
         │
         ├── [ Control Theory & Autonavigation ]
         │      - Closed-loop tri-axis Proportional-Integral-Derivative (PID) controller
         │      - Predictive Kalman Filter for target tracking during visual occlusion
         │      - Tactical Bird's-Eye View (BEV) radar coordinate mapping
         │
         └── [ Webots 3D Physics Simulator ]
                - Real-time aerodynamics, drag forces, and ground effect modeling
                - Pre-flight flight path validation in synthetic arena
```

---

## Hardware Specifications & Circuit Architecture

### 1. Flight Controller & Avionics Pinout

```
                                  +------------------+
                                  | 1S 3.7V 1000mAh  |
                                  +--------+---------+
                                           |
                    +-----------------------+-----------------------+
                    | (Battery +)                                   |
                    |                                               |
              +-----+-----+                                   +-----+-----+
              | 4x Motors |                                   | ESP32-CAM |
              | + Diodes  |                                   | 5V / GND  |
              +-----+-----+                                   +-----+-----+
                    |                                               |
                    | (Drain)                                       |
              +-----+-----+                                         |
              | 4x MOSFET |<--- PWM (GPIO 12, 15, 2, 4) <-----------+
              |  SI2302   |                                         |
              +-----+-----+                                         |
                    | (Source)                                      |
                    |                                               |
                   GND <--------------------------------------------+
```

- **GPIO 13:** I2C SDA (MPU-6050 Gyro/Accel + BMP280 Barometer).
- **GPIO 14:** I2C SCL (MPU-6050 Gyro/Accel + BMP280 Barometer).
- **GPIO 12:** Motor 1 Gate (Front-Left) with 10kOhm pull-down resistor.
- **GPIO 15:** Motor 2 Gate (Front-Right).
- **GPIO 2:** Motor 3 Gate (Rear-Left).
- **GPIO 4:** Motor 4 Gate (Rear-Right).
- **Power Rail:** 1S 3.7V 1000mAh LiPo supplying ~5.5A continuous hover draw.

---

## Edge AI Inference Benchmark (Ground Station)

Conducted on native hardware:
- **GPU:** NVIDIA GeForce RTX 5060 Laptop GPU (8GB GDDR6 VRAM, Blackwell Architecture)
- **CUDA Runtime:** CUDA 13.x / PyTorch 2.13.0+cu130
- **CPU:** Intel Core 7 240H (16 Threads, up to 5.2 GHz)
- **System Memory:** 16 GB DDR5

| Pipeline Stage | Model Architecture | Frame Latency | Throughput | VRAM Footprint |
| :--- | :--- | :--- | :--- | :--- |
| **Object & Person Detection** | YOLOv8n (FP16 TensorRT) | 2.81 ms | 355.8 FPS | ~1.1 GB |
| **Monocular DepthNet** | U-Net Depth Estimator | 3.56 ms | 280.5 FPS | ~1.7 GB |
| **Biometric Face Re-ID** | 576-D ResNet Metric Head | 4.12 ms | 242.7 FPS | ~1.8 GB |
| **Full Multi-Task Pipeline** | Combined Stack Concurrent | 3.82 ms | 261.7 FPS | ~2.2 GB |

---

## Flight Software Modules

The codebase is organized into modular production units:

1. **`drone_ai_pilot.py`**: Real-time ground station client handling UDP video stream decoding, YOLOv8 target tracking, and dynamic PID steering packet transmission.
2. **`lesson1_convolutions_from_scratch.py`**: Mathematical implementation of tensor convolutions, kernel filters, and spatial pooling.
3. **`lesson2_build_and_train_from_scratch.py`**: Implementation and PyTorch training of `DroneTrackNet` (106,000 parameters) using MSE bounding box regression.
4. **`lesson3_pid_drone_controller.py`**: Closed-loop PID controller translating screen-space pixel errors into standard RC PWM pulses (1000 to 2000 microseconds).
5. **`lesson4_depth_and_gestures.py`**: Monocular depth estimation and 17-keypoint skeletal pose parsing for hand-gesture flight commands.
6. **`drone_advanced_vision.py`**: 80-class object detection paired with 3D spatial distance estimation and top-down Bird's-Eye View (BEV) radar telemetry.
7. **`drone_identity_memory.py`**: Persistent biometric identity recognition system persisting authorized pilot facial encodings in `drone_memory_db.json`.
8. **`drone_dji_enterprise.py`**: Advanced mission suite featuring 3D photogrammetric area measurement, ActiveTrack 360, Point-of-Interest orbit, and terrain flatness safety landing analysis.
9. **`drone_dji_matrice_ultimate.py`**: Enterprise avionics suite with Kalman filter occlusion recovery, powerline hazard avoidance, and FLIR thermal color-palette rendering.
10. **`webots_simulation/`**: High-fidelity 3D physics simulation arena in Webots (`ai_drone_arena.wbt`) with automated Python flight controller (`ai_drone_controller.py`).

---

## Deployment & Operation

### 1. Ground Station Environment Setup

```bash
cd mini-ai-drone
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Launching Real-Time AI Pilot

```bash
# Connect to drone Wi-Fi hotspot (Default: 192.168.4.1)
python3 drone_ai_pilot.py
```

### 3. Launching 3D Physics Simulation

```bash
cd webots_simulation
chmod +x run_simulation.sh
./run_simulation.sh
```

---

## Authorship & Intellectual Property

- **Lead Systems Architect:** Mullainathan
- **Email:** mullainathan95@gmail.com
- **Organization:** Brix Softworks
- **License:** Proprietary - All rights reserved by Mullainathan
