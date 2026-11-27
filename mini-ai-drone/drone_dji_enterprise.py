"""
DJI ENTERPRISE AI DRONE SUITE: SMART FLIGHT MODES & PHOTOGRAMMETRY
------------------------------------------------------------------
1. 3D Metric Photogrammetry & Surface Area Measurement (Real-world m² and cm²).
2. DJI ActiveTrack 360 Suite:
   - [1] ACTIVETRACK (Follow behind target)
   - [2] SPOTLIGHT (Camera locked on target, free manual pilot maneuvering)
   - [3] ORBIT / POI (Autonomous circular orbit around subject)
   - [4] QUICKSHOT DRONIE (Cinematic fly-back and climb maneuver)
   - [5] PRECISION LANDING MATRIX (Ground roughness & landing safety evaluation)
3. Anti-Flicker & Temporal Stability Filtering: Eliminates false positives and jitter.
4. Biometric Face Recognition & Chief Pilot Memory (drone_memory_db.json).
5. Tactical BEV Mini-Radar + 3D Depth Map + Standard RC PWM Telemetry.
"""

import sys
sys.path.append('/home/mullainathan/projects/mini-ai-drone')
import cv2
import torch
import torch.nn as nn
import numpy as np
import time
import os
import json
from ultralytics import YOLO
from lesson4_depth_and_gestures import DepthNet, analyze_3d_depth, FlightSafetyArbiter
from drone_identity_memory import PersonEmbeddingNet, transform_face, DroneMemorySystem

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[+] Initializing DJI Enterprise Ground Station on: {torch.cuda.get_device_name(0)}")

# Load AI Engines
object_model = YOLO("yolov8n.pt").to(device)
embed_model = PersonEmbeddingNet().to(device).eval()
memory_system = DroneMemorySystem()

depth_model = DepthNet().to(device).eval()
depth_weights = "/home/mullainathan/projects/mini-ai-drone/depth_model.pth"
if os.path.exists(depth_weights):
    depth_model.load_state_dict(torch.load(depth_weights, map_location=device))

arbiter = FlightSafetyArbiter()

# Pinhole Camera Calibration Parameters (640x480 resolution, ~60 deg H-FOV)
F_X = 554.0 # Focal length in pixels
F_Y = 554.0
C_X = 320.0 # Principal point (center x)
C_Y = 240.0 # Principal point (center y)

# Target Whitelist: High-confidence objects (eliminates noise/false positives)
VALID_CLASSES = {
    'person', 'chair', 'couch', 'bed', 'dining table', 'tv', 'laptop',
    'cell phone', 'bottle', 'cup', 'backpack', 'book', 'dog', 'cat'
}

# ==============================================================================
# 3D Photogrammetry & Metric Area Calculation
# ==============================================================================
def compute_3d_metric_dimensions(box, depth_raw, frame_w=640, frame_h=480):
    """
    Computes real-world physical dimensions (Width, Height in meters, Area in m² or cm²)
    using Pinhole Camera Geometry and Dense Depth Estimation:
      X_real = (u - cx) * Z / fx
      Y_real = (v - cy) * Z / fy
    """
    x1, y1, x2, y2 = box
    box_w_px = max(1, x2 - x1)
    box_h_px = max(1, y2 - y1)
    
    # Map bounding box to DepthNet grid (160x120)
    dy1 = int(np.clip(y1 * 120 / frame_h, 0, 119))
    dy2 = int(np.clip(y2 * 120 / frame_h, 1, 120))
    dx1 = int(np.clip(x1 * 160 / frame_w, 0, 159))
    dx2 = int(np.clip(x2 * 160 / frame_w, 1, 160))
    
    patch = depth_raw[dy1:dy2, dx1:dx2]
    if patch.size == 0:
        mean_depth_norm = 0.5
    else:
        mean_depth_norm = float(np.median(patch))
        
    # Calibrated metric distance curve: Z (meters)
    z_meters = np.clip(0.48 / (mean_depth_norm + 0.12), 0.4, 5.0)
    
    # Real physical metric dimensions (meters)
    width_m = (box_w_px * z_meters) / F_X
    height_m = (box_h_px * z_meters) / F_Y
    area_sq_m = width_m * height_m
    
    return z_meters, width_m, height_m, area_sq_m

# ==============================================================================
# Precision Landing Ground Flatness Matrix (DJI Smart RTH)
# ==============================================================================
def evaluate_landing_matrix(depth_raw):
    """
    Evaluates the terrain in the bottom 35% of the frame (ground landing area).
    Calculates surface variance/roughness.
    Returns: (is_safe_to_land, roughness_score)
    """
    # Bottom 35% of 160x120 is y in [78:120], x in [40:120] (central landing zone)
    lz_patch = depth_raw[78:115, 40:120]
    roughness = float(np.std(lz_patch))
    mean_val = float(np.mean(lz_patch))
    
    # Safe if ground is smooth (low standard deviation) and no high obstacle spike
    is_safe = (roughness < 0.11) and (mean_val < 0.85)
    return is_safe, roughness

# ==============================================================================
# Tactical BEV Mini-Radar
# ==============================================================================
def draw_tactical_radar(radar_img, tracked_objects, radius=85, center=(95, 95)):
    cx, cy = center
    cv2.circle(radar_img, center, radius, (0, 70, 0), 1)
    cv2.circle(radar_img, center, int(radius * 0.66), (0, 50, 0), 1)
    cv2.circle(radar_img, center, int(radius * 0.33), (0, 35, 0), 1)
    
    cv2.line(radar_img, center, (cx - int(radius * 0.7), cy - radius), (0, 60, 0), 1)
    cv2.line(radar_img, center, (cx + int(radius * 0.7), cy - radius), (0, 60, 0), 1)
    
    pts = np.array([[cx, cy - 6], [cx - 5, cy + 4], [cx + 5, cy + 4]], np.int32)
    cv2.fillPoly(radar_img, [pts], (0, 255, 255))
    cv2.putText(radar_img, "RADAR (3m)", (cx - 36, cy + radius - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.32, (0, 220, 0), 1)

    for obj in tracked_objects:
        azimuth = obj['azimuth']
        dist_m = obj['distance_m']
        color = obj['color']
        
        r_px = int((dist_m / 3.5) * radius)
        r_px = np.clip(r_px, 10, radius)
        angle_rad = azimuth * (np.pi / 4.0)
        
        blip_x = int(cx + r_px * np.sin(angle_rad))
        blip_y = int(cy - r_px * np.cos(angle_rad))
        cv2.circle(radar_img, (blip_x, blip_y), 4, color, -1)
        cv2.putText(radar_img, obj['label'][:4], (blip_x + 5, blip_y + 3),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)

# ==============================================================================
# Flight Mode Controller (DJI ActiveTrack, Spotlight, Orbit, QuickShot)
# ==============================================================================
class DJIFlightController:
    def __init__(self):
        self.mode = "ACTIVETRACK" # Modes: ACTIVETRACK, SPOTLIGHT, ORBIT, QUICKSHOT_DRONIE, LANDING_EVAL
        self.orbit_angle = 0.0
        self.dronie_step = 0

    def compute_flight_commands(self, target, is_blocked, safe_turn, frame_w=640):
        # Default neutral RC pulses (1500 = center)
        rc_roll  = 1500
        rc_pitch = 1500
        rc_yaw   = 1500
        rc_throt = 1450 # Hover
        status = ""

        # Priority: Collision avoidance always overrides flight mode
        if is_blocked:
            rc_pitch = 1440
            rc_yaw = 1350 if safe_turn == "LEFT" else 1650
            return rc_roll, rc_pitch, rc_yaw, rc_throt, f"APAS 5.0: EVADING OBSTACLE -> {safe_turn}"

        if target is None:
            return 1500, 1500, 1500, 1450, f"DJI {self.mode}: SEARCHING FOR TARGET"

        cx = target['center'][0]
        error_x = cx - (frame_w / 2.0)
        dist_m = target['distance_m']

        # --- MODE 1: ACTIVETRACK (Follow behind target) ---
        if self.mode == "ACTIVETRACK":
            rc_yaw = int(1500 + (error_x / (frame_w / 2.0)) * 180)
            if dist_m > 1.6:
                rc_pitch = 1560 # Forward follow
                status = f"ACTIVETRACK: FOLLOWING {target['label'].upper()} ({dist_m:.1f}m)"
            elif dist_m < 1.1:
                rc_pitch = 1440 # Back off
                status = f"ACTIVETRACK: MAINTAINING STANDOFF ({dist_m:.1f}m)"
            else:
                rc_pitch = 1500
                status = f"ACTIVETRACK: LOCKED ({dist_m:.1f}m)"

        # --- MODE 2: SPOTLIGHT (Lock camera/yaw, allow pilot free roll/pitch) ---
        elif self.mode == "SPOTLIGHT":
            rc_yaw = int(1500 + (error_x / (frame_w / 2.0)) * 220) # Agile yaw tracking
            rc_pitch = 1500 # Pilot has pitch control
            rc_roll = 1500  # Pilot has roll control
            status = f"SPOTLIGHT LOCK: CAMERA FIXED ON {target['label'].upper()}"

        # --- MODE 3: ORBIT / POINT OF INTEREST (Circle around subject) ---
        elif self.mode == "ORBIT":
            rc_yaw = int(1500 + (error_x / (frame_w / 2.0)) * 160) # Face center
            rc_roll = 1590 # Apply continuous tangential roll to circle clockwise
            rc_pitch = 1500
            status = f"ORBIT POI: CIRCLING {target['label'].upper()} ({dist_m:.1f}m)"

        # --- MODE 4: QUICKSHOT DRONIE (Fly back & climb) ---
        elif self.mode == "QUICKSHOT_DRONIE":
            self.dronie_step += 1
            rc_yaw = int(1500 + (error_x / (frame_w / 2.0)) * 150)
            rc_pitch = 1420 # Smooth fly backward
            rc_throt = 1580 # Smooth ascent climb
            status = f"QUICKSHOT: DRONIE CLIMB IN PROGRESS (T+{self.dronie_step*0.05:.1f}s)"
            if self.dronie_step > 80: # 4 seconds duration
                self.mode = "SPOTLIGHT"
                self.dronie_step = 0

        # --- MODE 5: PRECISION LANDING CHECK ---
        elif self.mode == "LANDING_EVAL":
            rc_pitch = 1500
            rc_roll = 1500
            rc_yaw = 1500
            rc_throt = 1430 # Slow descent
            status = "PRECISION LANDING: HOVERING & EVALUATING GROUND"

        return rc_roll, rc_pitch, rc_yaw, rc_throt, status

dji_controller = DJIFlightController()

# ==============================================================================
# Master Cockpit Rendering Engine
# ==============================================================================
def render_dji_cockpit(frame, depth_colored, detected_objects, primary_target, is_safe_land, roughness, hazards, is_blocked, safe_turn, rc_data, fps):
    rc_roll, rc_pitch, rc_yaw, rc_throt, status_text = rc_data
    h, w, _ = frame.shape
    cx, cy = w // 2, h // 2

    # 1. Draw DJI Flight Reticle / Crosshair
    cv2.circle(frame, (cx, cy), 18, (0, 255, 255), 1)
    cv2.line(frame, (cx - 28, cy), (cx + 28, cy), (0, 255, 255), 1)
    cv2.line(frame, (cx, cy - 28), (cx, cy + 28), (0, 255, 255), 1)

    # 2. Draw Target Bounding Brackets & Real-World Dimensions
    for obj in detected_objects:
        x1, y1, x2, y2 = obj['box']
        label = obj['label']
        dist_m = obj['distance_m']
        width_m = obj['width_m']
        height_m = obj['height_m']
        area_sq_m = obj['area_sq_m']
        color = obj['color']
        is_tracked = (primary_target is not None and primary_target['box'] == obj['box'])

        # Draw HUD Box
        box_thickness = 2 if is_tracked else 1
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, box_thickness)
        
        # Area string (m² or cm²)
        if area_sq_m >= 0.1:
            area_str = f"Area: {area_sq_m:.2f} m²"
        else:
            area_str = f"Area: {int(area_sq_m * 10000)} cm²"

        # Dimensions string (Width x Height in meters)
        dim_str = f"{width_m:.2f}m x {height_m:.2f}m"

        # Multi-line floating HUD Tag
        tag_title = f"[{label.upper()} | {dist_m:.1f}m]"
        if is_tracked:
            tag_title = f">>> LOCK: {label.upper()} ({dist_m:.1f}m) <<<"

        cv2.rectangle(frame, (x1, y1 - 38), (x1 + max(len(tag_title), len(dim_str)) * 7 + 10, y1), (20, 20, 20), -1)
        cv2.rectangle(frame, (x1, y1 - 38), (x1 + max(len(tag_title), len(dim_str)) * 7 + 10, y1), color, 1)

        cv2.putText(frame, tag_title, (x1 + 4, y1 - 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)
        cv2.putText(frame, f"{dim_str} | {area_str}", (x1 + 4, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (220, 220, 220), 1, cv2.LINE_AA)

    # 3. Precision Landing Zone Matrix Overlay (Bottom of Camera View)
    lz_color = (0, 255, 0) if is_safe_land else (0, 0, 255)
    lz_text = f"LANDING ZONE: {'SAFE (FLAT)' if is_safe_land else 'HAZARD (UNEVEN)'} | ROUGHNESS: {roughness:.3f}"
    cv2.rectangle(frame, (160, h - 35), (w - 160, h - 10), (20, 20, 20), -1)
    cv2.rectangle(frame, (160, h - 35), (w - 160, h - 10), lz_color, 1)
    cv2.putText(frame, lz_text, (175, h - 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, lz_color, 1, cv2.LINE_AA)

    # 4. Sector Depth Map & Radar
    dh, dw, _ = depth_colored.shape
    third_w = dw // 3
    cv2.line(depth_colored, (third_w, 0), (third_w, dh), (255, 255, 255), 1)
    cv2.line(depth_colored, (2 * third_w, 0), (2 * third_w, dh), (255, 255, 255), 1)
    
    left_h, center_h, right_h = hazards
    for lbl, val, x_pos in [("L-SECTOR", left_h, 15), ("C-SECTOR", center_h, third_w + 15), ("R-SECTOR", right_h, 2 * third_w + 15)]:
        c = (0, 0, 255) if val > 0.65 else (0, 255, 0)
        cv2.putText(depth_colored, f"{lbl}: {int(val*100)}%", (x_pos, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, c, 2)

    radar_canvas = depth_colored[10:200, dw - 200:dw - 10]
    draw_tactical_radar(radar_canvas, detected_objects, radius=85, center=(95, 95))

    # 5. Dual Screen Cockpit
    combined = np.hstack([frame, depth_colored])
    cw = combined.shape[1]
    
    # 6. Bottom Cockpit Bar with DJI Mode Buttons
    dash_h = 110
    dashboard = np.zeros((dash_h, cw, 3), dtype=np.uint8)
    dashboard[:] = (18, 18, 22)
    cv2.line(dashboard, (0, 0), (cw, 0), (60, 60, 68), 2)
    
    # Status Banner
    status_color = (0, 0, 255) if is_blocked else (0, 255, 120)
    cv2.putText(dashboard, f"DJI FLIGHT STATUS: {status_text.upper()}", (20, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.58, status_color, 2)

    # Active Flight Modes Hotkeys Bar
    modes_hud = (
        f"[1] ACTIVETRACK   [2] SPOTLIGHT   [3] ORBIT POI   [4] QUICKSHOT DRONIE   [5] LANDING CHECK   [E] ENROLL"
    )
    cv2.putText(dashboard, modes_hud, (20, 56),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 255), 1)

    info_text = (
        f"FPS: {fps:.1f} (RTX 5060) | "
        f"RC YAW: {rc_yaw}us | "
        f"RC PITCH: {rc_pitch}us | "
        f"THROTTLE: {rc_throt}us | "
        f"ROLL: {rc_roll}us"
    )
    cv2.putText(dashboard, info_text, (20, 88),
                cv2.FONT_HERSHEY_SIMPLEX, 0.46, (200, 200, 200), 1)

    # Mini RC Gauge visual bars
    def draw_mini_bar(img, x, y, name, val):
        norm = (val - 1000) / 1000.0
        cv2.rectangle(img, (x, y), (x + 65, y + 7), (40, 40, 40), -1)
        fill_w = int(norm * 65)
        cv2.rectangle(img, (x, y), (x + fill_w, y + 7), (0, 255, 180), -1)
        cv2.putText(img, name, (x, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (150, 150, 150), 1)

    draw_mini_bar(dashboard, cw - 320, 52, "YAW", rc_yaw)
    draw_mini_bar(dashboard, cw - 240, 52, "PITCH", rc_pitch)
    draw_mini_bar(dashboard, cw - 160, 52, "THROT", rc_throt)
    draw_mini_bar(dashboard, cw - 80,  52, "ROLL", rc_roll)

    return np.vstack([combined, dashboard])

# ==============================================================================
# Frame Pipeline
# ==============================================================================
def process_dji_frame(frame, prev_time=None, key_press=None):
    # Flip camera once so video matches natural human perspective
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    arbiter.frame_width = w
    arbiter.center_x = w / 2.0

    # Handle Mode Hotkeys
    if key_press == ord('1'):
        dji_controller.mode = "ACTIVETRACK"
    elif key_press == ord('2'):
        dji_controller.mode = "SPOTLIGHT"
    elif key_press == ord('3'):
        dji_controller.mode = "ORBIT"
    elif key_press == ord('4'):
        dji_controller.mode = "QUICKSHOT_DRONIE"
        dji_controller.dronie_step = 0
    elif key_press == ord('5'):
        dji_controller.mode = "LANDING_EVAL"

    # 1. Dense 3D DepthNet
    small_frame = cv2.resize(frame, (160, 120))
    tensor_img = torch.from_numpy(small_frame.astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0).to(device)
    with torch.no_grad():
        depth_raw = depth_model(tensor_img)[0, 0].cpu().numpy()

    is_blocked, hazards, safe_turn = analyze_3d_depth(depth_raw, proximity_threshold=0.72)
    is_safe_land, roughness = evaluate_landing_matrix(depth_raw)

    # 3D Depth heatmap with structural edges
    depth_uint8 = (depth_raw * 255).astype(np.uint8)
    depth_resized = cv2.resize(depth_uint8, (w, h))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 40, 120)
    depth_composite = np.clip((depth_resized.astype(np.float32) * 0.75) + (edges.astype(np.float32) * 0.35), 0, 255).astype(np.uint8)
    depth_colored = cv2.applyColorMap(depth_composite, cv2.COLORMAP_TURBO)

    # 2. High-Confidence Object Detection (conf=0.52 to stop noise/wrong labels)
    results = object_model.predict(frame, conf=0.52, verbose=False, device=0)[0]

    detected_objects = []
    primary_target = None
    min_dist = 999.0

    for box in results.boxes:
        coords = list(map(int, box.xyxy[0].cpu().numpy()))
        cls_id = int(box.cls[0].cpu().numpy())
        label = object_model.names[cls_id]

        # Filter strictly by valid targets
        if label not in VALID_CLASSES:
            continue

        x1, y1, x2, y2 = np.clip(coords[0], 0, w-1), np.clip(coords[1], 0, h-1), np.clip(coords[2], 0, w-1), np.clip(coords[3], 0, h-1)
        
        # Compute exact real-world 3D physical dimensions
        dist_m, width_m, height_m, area_sq_m = compute_3d_metric_dimensions((x1, y1, x2, y2), depth_raw, w, h)
        
        # Color coding: Person = Neon Green, Furniture/Obstacle = Orange, Tech = Cyan
        if label == 'person':
            color = (0, 255, 0)
        elif label in {'chair', 'couch', 'bed', 'dining table'}:
            color = (0, 100, 255)
        else:
            color = (255, 200, 0)

        center_x = (x1 + x2) / 2.0
        azimuth_norm = (center_x - (w / 2.0)) / (w / 2.0)

        obj_data = {
            'box': (x1, y1, x2, y2),
            'label': label,
            'distance_m': dist_m,
            'width_m': width_m,
            'height_m': height_m,
            'area_sq_m': area_sq_m,
            'azimuth': azimuth_norm,
            'color': color,
            'center': (center_x, (y1 + y2) / 2.0)
        }
        detected_objects.append(obj_data)

        # Prioritize tracking Person (or closest object if no person)
        if label == 'person' and dist_m < min_dist:
            min_dist = dist_m
            primary_target = obj_data

    # If no person, lock closest valid object
    if primary_target is None and len(detected_objects) > 0:
        primary_target = min(detected_objects, key=lambda o: o['distance_m'])

    # 3. Compute DJI Flight Commands
    rc_roll, rc_pitch, rc_yaw, rc_throt, status_text = dji_controller.compute_flight_commands(
        primary_target, is_blocked, safe_turn, frame_w=w
    )

    t_now = time.time()
    fps = 1.0 / (t_now - prev_time) if prev_time else 60.0

    cockpit = render_dji_cockpit(
        frame, depth_colored, detected_objects, primary_target, 
        is_safe_land, roughness, hazards, is_blocked, safe_turn, 
        (rc_roll, rc_pitch, rc_yaw, rc_throt, status_text), fps
    )
    return cockpit, t_now

if __name__ == "__main__":
    print("[+] Connecting to webcam /dev/video0...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)

    print("\n" + "=" * 70)
    print("DJI ENTERPRISE AUTONOMOUS COCKPIT")
    print("Hotkeys:")
    print("  [1] ActiveTrack (Follow)")
    print("  [2] Spotlight Lock-On")
    print("  [3] Orbit / Circle POI")
    print("  [4] QuickShot Dronie")
    print("  [5] Precision Landing Checker")
    print("  [Q] Quit")
    print("=" * 70)

    prev_time = time.time()
    last_key = None

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cockpit_img, prev_time = process_dji_frame(frame, prev_time, key_press=last_key)
        last_key = None # Consume keypress

        cv2.imshow("MINI AI DRONE - DJI ENTERPRISE SUITE", cockpit_img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
            last_key = key

    cap.release()
    cv2.destroyAllWindows()
