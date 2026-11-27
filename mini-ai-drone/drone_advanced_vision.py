"""
ADVANCED 3D MULTI-OBJECT DRONE GROUND STATION
---------------------------------------------
1. Detects ALL 80 COCO Object Classes (furniture, electronics, humans, pets, obstacles).
2. Per-Object 3D Distance Estimation: Measures physical distance in meters to each item.
3. Tactical Top-Down Bird's-Eye View (BEV) Mini-Radar: Plots objects in 2D spatial coordinates.
4. Dense 3D Depth Map (TURBO Heatmap) with structural edges.
5. Smart Collision Avoidance: Flags obstacle threats and steers drone around them.
"""

import sys
sys.path.append('/home/mullainathan/projects/mini-ai-drone')
import cv2
import torch
import numpy as np
import time
import os
from ultralytics import YOLO
from lesson4_depth_and_gestures import DepthNet, analyze_3d_depth, FlightSafetyArbiter

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load models
print("[+] Loading Multi-Class YOLOv8 (80 Classes) onto RTX 5060...")
object_model = YOLO("yolov8n.pt").to(device)

print("[+] Loading 3D DepthNet...")
depth_model = DepthNet().to(device).eval()
depth_weights = "/home/mullainathan/projects/mini-ai-drone/depth_model.pth"
if os.path.exists(depth_weights):
    depth_model.load_state_dict(torch.load(depth_weights, map_location=device))

arbiter = FlightSafetyArbiter()

# Semantic Category Class Mapping for 80 COCO classes
FURNITURE_OBSTACLES = {
    'chair', 'couch', 'bed', 'dining table', 'toilet', 'tv', 'refrigerator',
    'oven', 'sink', 'microwave', 'bench', 'potted plant', 'door'
}
TECH_ITEMS = {
    'laptop', 'cell phone', 'keyboard', 'mouse', 'remote', 'clock', 'book', 'bottle', 'cup', 'backpack'
}
ANIMAL_CLASSES = {'dog', 'cat', 'bird', 'horse', 'sheep', 'cow'}

def get_class_style(cls_name):
    """Returns color and threat category for any detected object."""
    if cls_name == 'person':
        return (0, 255, 0), "TARGET"          # Neon Green
    elif cls_name in FURNITURE_OBSTACLES:
        return (0, 69, 255), "OBSTACLE"        # Orange-Red
    elif cls_name in TECH_ITEMS:
        return (255, 200, 0), "GADGET"         # Cyan
    elif cls_name in ANIMAL_CLASSES:
        return (255, 0, 255), "ANIMAL"         # Magenta
    else:
        return (200, 200, 200), "OBJECT"       # White-Gray

def estimate_distance_meters(depth_patch):
    """
    Translates normalized depth intensity [0.0 - 1.0] into physical meters.
    Higher depth intensity = Closer object.
    """
    if depth_patch.size == 0:
        return 2.5
    mean_val = float(np.mean(depth_patch))
    # Distance curve: 0.9 -> ~0.6m, 0.5 -> ~1.5m, 0.2 -> ~3.5m
    dist_m = 0.5 / (mean_val + 0.15)
    return np.clip(dist_m, 0.4, 5.0)

def draw_tactical_radar(radar_img, tracked_objects, radius=85, center=(95, 95)):
    """
    Draws a Top-Down Bird's-Eye View (BEV) radar display.
    Center = Drone. Outer rings = 1m, 2m, 3m range.
    """
    cx, cy = center
    # Radar background & grid rings
    cv2.circle(radar_img, center, radius, (0, 80, 0), 1)
    cv2.circle(radar_img, center, int(radius * 0.66), (0, 60, 0), 1)
    cv2.circle(radar_img, center, int(radius * 0.33), (0, 40, 0), 1)
    
    # 60-degree Field-of-View wedge lines
    cv2.line(radar_img, center, (cx - int(radius * 0.7), cy - radius), (0, 70, 0), 1)
    cv2.line(radar_img, center, (cx + int(radius * 0.7), cy - radius), (0, 70, 0), 1)
    
    # Drone icon (triangle at center)
    pts = np.array([[cx, cy - 6], [cx - 5, cy + 4], [cx + 5, cy + 4]], np.int32)
    cv2.fillPoly(radar_img, [pts], (0, 255, 255))
    cv2.putText(radar_img, "RADAR (3m)", (cx - 40, cy + radius - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 200, 0), 1)

    # Plot detected objects as blips on the radar
    for obj in tracked_objects:
        azimuth_norm = obj['azimuth'] # -1.0 (left) to +1.0 (right)
        dist_m = obj['distance_m']     # 0.5m to 3.5m
        color = obj['color']
        
        # Polar to Cartesian
        r_px = int((dist_m / 3.5) * radius)
        r_px = np.clip(r_px, 10, radius)
        
        angle_rad = azimuth_norm * (np.pi / 4.0) # +/- 45 deg FOV
        blip_x = int(cx + r_px * np.sin(angle_rad))
        blip_y = int(cy - r_px * np.cos(angle_rad))
        
        cv2.circle(radar_img, (blip_x, blip_y), 4, color, -1)
        cv2.putText(radar_img, obj['label'][:4], (blip_x + 5, blip_y + 3),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)

def render_advanced_cockpit(frame, depth_colored, detected_objects, hazards, is_blocked, safe_turn, rc_data, fps):
    rc_roll, rc_pitch, rc_yaw, rc_throt, status_text = rc_data
    h, w, _ = frame.shape
    
    # 1. Draw High-Tech Brackets & Distance Tags on RGB FPV View
    cx, cy = w // 2, h // 2
    cv2.drawMarker(frame, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 24, 1)
    
    for obj in detected_objects:
        x1, y1, x2, y2 = obj['box']
        label = obj['label']
        conf = obj['conf']
        dist_m = obj['distance_m']
        color = obj['color']
        cat = obj['category']
        
        # Corner brackets (sci-fi HUD style)
        corner_len = min(15, (x2 - x1) // 4, (y2 - y1) // 4)
        # Top-Left
        cv2.line(frame, (x1, y1), (x1 + corner_len, y1), color, 2)
        cv2.line(frame, (x1, y1), (x1, y1 + corner_len), color, 2)
        # Top-Right
        cv2.line(frame, (x2, y1), (x2 - corner_len, y1), color, 2)
        cv2.line(frame, (x2, y1), (x2, y1 + corner_len), color, 2)
        # Bottom-Left
        cv2.line(frame, (x1, y2), (x1 + corner_len, y2), color, 2)
        cv2.line(frame, (x1, y2), (x1, y2 - corner_len), color, 2)
        # Bottom-Right
        cv2.line(frame, (x2, y2), (x2 - corner_len, y2), color, 2)
        cv2.line(frame, (x2, y2), (x2, y2 - corner_len), color, 2)
        
        # Tag text: [LABEL | 1.2m | CAT]
        tag = f"{label.upper()} {dist_m:.1f}m"
        cv2.rectangle(frame, (x1, y1 - 18), (x1 + len(tag) * 8 + 10, y1), color, -1)
        cv2.putText(frame, tag, (x1 + 4, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1, cv2.LINE_AA)

    # 2. Sector lines on 3D Depth Map
    dh, dw, _ = depth_colored.shape
    third_w = dw // 3
    left_h, center_h, right_h = hazards
    cv2.line(depth_colored, (third_w, 0), (third_w, dh), (255, 255, 255), 1)
    cv2.line(depth_colored, (2 * third_w, 0), (2 * third_w, dh), (255, 255, 255), 1)
    
    for lbl, val, x_pos in [("L-SECTOR", left_h, 15), ("C-SECTOR", center_h, third_w + 15), ("R-SECTOR", right_h, 2 * third_w + 15)]:
        c = (0, 0, 255) if val > 0.65 else (0, 255, 0)
        cv2.putText(depth_colored, f"{lbl}: {int(val*100)}%", (x_pos, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, c, 2)

    # Overlay Tactical BEV Radar in the top-right of the Depth map
    radar_canvas = depth_colored[10:200, dw - 200:dw - 10]
    draw_tactical_radar(radar_canvas, detected_objects, radius=85, center=(95, 95))

    # 3. Side-by-side cockpit
    combined = np.hstack([frame, depth_colored])
    cw = combined.shape[1]
    
    # 4. Telemetry Bar
    dash_h = 100
    dashboard = np.zeros((dash_h, cw, 3), dtype=np.uint8)
    dashboard[:] = (20, 20, 24)
    cv2.line(dashboard, (0, 0), (cw, 0), (60, 60, 65), 2)
    
    # Status
    status_color = (0, 0, 255) if is_blocked else (0, 255, 100)
    cv2.putText(dashboard, f"MISSION ARBITER: {status_text.upper()}", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.62, status_color, 2)
    
    obj_summary = f"DETECTED: {len(detected_objects)} OBJECTS | ACTIVE SENSORS: 80-CLASS YOLO + 3D DEPTHNET + TACTICAL BEV RADAR"
    cv2.putText(dashboard, obj_summary, (20, 56),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1)

    info_text = f"FPS: {fps:.1f} (RTX 5060) | RC YAW: {rc_yaw}us | RC PITCH: {rc_pitch}us | THROTTLE: {rc_throt}us | ROLL: {rc_roll}us"
    cv2.putText(dashboard, info_text, (20, 84),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 255), 1)

    # Gauges
    def draw_mini_bar(img, x, y, name, val):
        norm = (val - 1000) / 1000.0
        cv2.rectangle(img, (x, y), (x + 65, y + 7), (40, 40, 40), -1)
        fill_w = int(norm * 65)
        cv2.rectangle(img, (x, y), (x + fill_w, y + 7), (0, 255, 180), -1)
        cv2.putText(img, name, (x, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (150, 150, 150), 1)

    draw_mini_bar(dashboard, cw - 320, 50, "YAW", rc_yaw)
    draw_mini_bar(dashboard, cw - 240, 50, "PITCH", rc_pitch)
    draw_mini_bar(dashboard, cw - 160, 50, "THROT", rc_throt)
    draw_mini_bar(dashboard, cw - 80,  50, "ROLL", rc_roll)

    return np.vstack([combined, dashboard])

def process_advanced_frame(frame, prev_time=None):
    t0 = time.time()
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    arbiter.frame_width = w
    arbiter.center_x = w / 2.0

    # --- 1. Dense 3D Depth Map ---
    small_frame = cv2.resize(frame, (160, 120))
    tensor_img = torch.from_numpy(small_frame.astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0).to(device)
    with torch.no_grad():
        depth_raw = depth_model(tensor_img)[0, 0].cpu().numpy()
        
    is_blocked, hazards, safe_turn = analyze_3d_depth(depth_raw, proximity_threshold=0.68)
    
    # Structural depth composite with edges
    depth_uint8 = (depth_raw * 255).astype(np.uint8)
    depth_resized = cv2.resize(depth_uint8, (w, h))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 40, 120)
    depth_composite = np.clip((depth_resized.astype(np.float32) * 0.75) + (edges.astype(np.float32) * 0.35), 0, 255).astype(np.uint8)
    depth_colored = cv2.applyColorMap(depth_composite, cv2.COLORMAP_TURBO)

    # --- 2. 80-Class Object Detection ---
    results = object_model.predict(frame, conf=0.35, verbose=False, device=0)[0]
    
    detected_objects = []
    primary_target = None
    min_target_dist = 999.0

    for box in results.boxes:
        coords = list(map(int, box.xyxy[0].cpu().numpy()))
        cls_id = int(box.cls[0].cpu().numpy())
        conf = float(box.conf[0].cpu().numpy())
        label = object_model.names[cls_id]
        
        # Sample 3D depth inside this object's bounding box
        x1, y1, x2, y2 = np.clip(coords[0], 0, w-1), np.clip(coords[1], 0, h-1), np.clip(coords[2], 0, w-1), np.clip(coords[3], 0, h-1)
        obj_depth_patch = depth_raw[int(y1*120/h):int(y2*120/h), int(x1*160/w):int(x2*160/w)]
        dist_m = estimate_distance_meters(obj_depth_patch)
        
        color, category = get_class_style(label)
        center_x = (x1 + x2) / 2.0
        azimuth_norm = (center_x - (w / 2.0)) / (w / 2.0) # -1.0 to +1.0
        
        obj_info = {
            'box': (x1, y1, x2, y2),
            'label': label,
            'conf': conf,
            'distance_m': dist_m,
            'azimuth': azimuth_norm,
            'color': color,
            'category': category,
            'center': (center_x, (y1 + y2) / 2.0)
        }
        detected_objects.append(obj_info)
        
        # Prioritize tracking: closest Person or nearest designated Target
        if category == "TARGET" and dist_m < min_target_dist:
            min_target_dist = dist_m
            primary_target = obj_info

    # --- 3. Safety Arbiter & Flight Commands ---
    if is_blocked:
        rc_roll, rc_pitch, rc_yaw, rc_throt, status_text = arbiter.compute_control(
            "NO_TARGET", (w // 2, h // 2), hazards, is_blocked, safe_turn
        )
    elif primary_target is not None:
        # Steer drone towards the primary target
        target_cx = primary_target['center'][0]
        error_x = target_cx - (w / 2.0)
        rc_yaw = int(1500 + (error_x / (w / 2.0)) * 180)
        
        # Distance control: If target > 1.5m -> Fly Forward; If < 1.0m -> Back Away
        if primary_target['distance_m'] > 1.6:
            rc_pitch = 1550 # Move forward
            status_text = f"TRACKING {primary_target['label'].upper()} ({primary_target['distance_m']:.1f}m) -> ADVANCING"
        elif primary_target['distance_m'] < 1.0:
            rc_pitch = 1450 # Back away
            status_text = f"TRACKING {primary_target['label'].upper()} ({primary_target['distance_m']:.1f}m) -> RETREATING"
        else:
            rc_pitch = 1500 # Hold distance
            status_text = f"LOCKED ON {primary_target['label'].upper()} ({primary_target['distance_m']:.1f}m) -> DISTANCE HOLD"
            
        rc_roll = 1500
        rc_throt = 1450
    else:
        rc_roll, rc_pitch, rc_yaw, rc_throt, status_text = 1500, 1500, 1500, 1450, "STANDBY: SCANNING SECTORS FOR TARGETS"

    t_now = time.time()
    fps = 1.0 / (t_now - prev_time) if prev_time else 60.0
    
    cockpit = render_advanced_cockpit(
        frame, depth_colored, detected_objects, hazards, 
        is_blocked, safe_turn, (rc_roll, rc_pitch, rc_yaw, rc_throt, status_text), fps
    )
    return cockpit, t_now

if __name__ == "__main__":
    print("[+] Connecting to webcam /dev/video0...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)

    print("[+] Advanced Drone Ground Station running! Press 'q' to quit.")
    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
            
        cockpit_img, prev_time = process_advanced_frame(frame, prev_time)
        cv2.imshow("MINI AI DRONE - ADVANCED 80-CLASS 3D COCKPIT", cockpit_img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
