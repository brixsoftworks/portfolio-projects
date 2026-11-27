"""
DRONE VISION COCKPIT & 3D HUD GROUND STATION
--------------------------------------------
Side-by-side dual-screen Ground Station:
- LEFT: RGB FPV Camera Feed + 3D Skeleton + Gestures + Artificial Horizon + Flight Vector
- RIGHT: Dense 3D Depth Map (TURBO Heatmap) + Sector Obstacle Clearance Gauges
- BOTTOM: Telemetry Dashboard with RC PWM Indicators (Pitch, Roll, Yaw, Throttle)
"""

import sys
sys.path.append('/home/mullainathan/projects/mini-ai-drone')
import cv2
import torch
import numpy as np
import time
from ultralytics import YOLO
from lesson4_depth_and_gestures import DepthNet, analyze_3d_depth, classify_gesture, FlightSafetyArbiter

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

import os

# Load models
pose_model = YOLO("yolov8n-pose.pt").to(device)
depth_model = DepthNet().to(device).eval()
depth_weights = "/home/mullainathan/projects/mini-ai-drone/depth_model.pth"
if os.path.exists(depth_weights):
    depth_model.load_state_dict(torch.load(depth_weights, map_location=device))
    print("[+] Loaded trained DepthNet weights!")
arbiter = FlightSafetyArbiter()

# Skeleton bone pairs in COCO format:
SKELETON_PAIRS = [
    (5, 6),   # Shoulders
    (5, 7), (7, 9),   # Left Arm (Shoulder -> Elbow -> Wrist)
    (6, 8), (8, 10),  # Right Arm (Shoulder -> Elbow -> Wrist)
    (5, 11), (6, 12), # Torso (Shoulder -> Hip)
    (11, 12),         # Hips
    (11, 13), (13, 15), # Left Leg
    (12, 14), (14, 16)  # Right Leg
]

def draw_hud(frame, depth_map_colored, gesture, target_coords, hazards, is_blocked, safe_turn, rc_data, fps):
    rc_roll, rc_pitch, rc_yaw, rc_throt, status_text = rc_data
    h, w, _ = frame.shape
    
    # 1. Draw Artificial Horizon & Flight Crosshairs on RGB View
    cx, cy = w // 2, h // 2
    cv2.line(frame, (cx - 40, cy), (cx - 10, cy), (0, 255, 255), 2)
    cv2.line(frame, (cx + 10, cy), (cx + 40, cy), (0, 255, 255), 2)
    cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)
    
    # Target vector line
    tx, ty = int(target_coords[0]), int(target_coords[1])
    if gesture != "NO_TARGET":
        cv2.line(frame, (cx, cy), (tx, ty), (0, 255, 0), 1, cv2.LINE_AA)
        cv2.circle(frame, (tx, ty), 8, (0, 255, 0), 2)
        cv2.putText(frame, f"TRACK: ID-01 [{gesture}]", (tx - 50, ty - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

    # 2. Draw Sector Clearance Overlay on Depth Map
    dh, dw, _ = depth_map_colored.shape
    third_w = dw // 3
    left_h, center_h, right_h = hazards
    
    # Sector divider lines
    cv2.line(depth_map_colored, (third_w, 0), (third_w, dh), (255, 255, 255), 1)
    cv2.line(depth_map_colored, (2 * third_w, 0), (2 * third_w, dh), (255, 255, 255), 1)
    
    # Sector labels & hazard bars
    for idx, (label, val, x_start) in enumerate([
        ("LEFT", left_h, 10),
        ("CENTER", center_h, third_w + 10),
        ("RIGHT", right_h, 2 * third_w + 10)
    ]):
        color = (0, 0, 255) if val > 0.65 else (0, 255, 0)
        cv2.putText(depth_map_colored, f"{label}: {int(val*100)}%", (x_start, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    if is_blocked:
        cv2.putText(depth_map_colored, "! COLLISION ALERT !", (third_w - 40, dh // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # 3. Stack Side-by-Side: RGB FPV (Left) | 3D Depth (Right)
    combined = np.hstack([frame, depth_map_colored])
    cw = combined.shape[1]
    
    # 4. Bottom Cockpit Telemetry Dashboard Bar
    dash_h = 100
    dashboard = np.zeros((dash_h, cw, 3), dtype=np.uint8)
    dashboard[:] = (25, 25, 28) # Dark carbon background
    
    # Top border line
    cv2.line(dashboard, (0, 0), (cw, 0), (70, 70, 75), 2)
    
    # Status Banner
    status_color = (0, 0, 255) if is_blocked else ((0, 255, 0) if "FOLLOW" in gesture else (0, 200, 255))
    cv2.putText(dashboard, f"MISSION: {status_text.upper()}", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2)
    
    # Telemetry Columns
    info_text = (
        f"FPS: {fps:.1f} (RTX 5060) | "
        f"RC YAW: {rc_yaw}us | "
        f"RC PITCH: {rc_pitch}us | "
        f"THROTTLE: {rc_throt}us | "
        f"ROLL: {rc_roll}us"
    )
    cv2.putText(dashboard, info_text, (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, (200, 200, 200), 1)

    # Mini RC Gauge visual bars
    def draw_gauge(img, x, y, label, val, min_v=1000, max_v=2000):
        norm = (val - min_v) / (max_v - min_v)
        bar_w = 70
        cv2.rectangle(img, (x, y), (x + bar_w, y + 8), (50, 50, 50), -1)
        fill_w = int(norm * bar_w)
        cv2.rectangle(img, (x, y), (x + fill_w, y + 8), (0, 255, 200), -1)
        cv2.putText(img, label, (x, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (160, 160, 160), 1)

    draw_gauge(dashboard, cw - 360, 45, "YAW", rc_yaw)
    draw_gauge(dashboard, cw - 270, 45, "PITCH", rc_pitch)
    draw_gauge(dashboard, cw - 180, 45, "THROT", rc_throt)
    draw_gauge(dashboard, cw - 90,  45, "ROLL", rc_roll)

    # Combine Cockpit
    cockpit = np.vstack([combined, dashboard])
    return cockpit

def process_single_frame(frame, prev_time=None):
    t0 = time.time()
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    arbiter.frame_width = w
    arbiter.center_x = w / 2.0

    # 1. Dense 3D DepthNet
    small_frame = cv2.resize(frame, (160, 120))
    tensor_img = torch.from_numpy(small_frame.astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0).to(device)
    with torch.no_grad():
        depth_raw = depth_model(tensor_img)[0, 0].cpu().numpy()
        
    is_blocked, hazards, safe_turn = analyze_3d_depth(depth_raw, proximity_threshold=0.70)
    
    # Generate Enhanced 3D Heatmap (TURBO colormap with edge structure)
    depth_uint8 = (depth_raw * 255).astype(np.uint8)
    depth_resized = cv2.resize(depth_uint8, (w, h))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 40, 120)
    depth_composite = np.clip((depth_resized.astype(np.float32) * 0.75) + (edges.astype(np.float32) * 0.35), 0, 255).astype(np.uint8)
    depth_colored = cv2.applyColorMap(depth_composite, cv2.COLORMAP_TURBO)

    # 2. 3D Pose & Gesture
    pose_results = pose_model(frame, verbose=False)[0]
    gesture = "NO_TARGET"
    target_coords = (w // 2, h // 2)

    if pose_results.keypoints is not None and len(pose_results.keypoints) > 0:
        kpts = pose_results.keypoints.xy[0].cpu().numpy()
        gesture, target_coords = classify_gesture(kpts)

        # Draw Skeleton Bones
        for p1, p2 in SKELETON_PAIRS:
            if p1 < len(kpts) and p2 < len(kpts):
                pt1 = (int(kpts[p1][0]), int(kpts[p1][1]))
                pt2 = (int(kpts[p2][0]), int(kpts[p2][1]))
                if pt1[0] > 0 and pt2[0] > 0:
                    cv2.line(frame, pt1, pt2, (0, 255, 255), 2)
        
        # Draw Keypoint Joints
        for kp in kpts:
            if kp[0] > 0 and kp[1] > 0:
                cv2.circle(frame, (int(kp[0]), int(kp[1])), 5, (0, 128, 255), -1)

    # 3. Flight Arbiter
    rc_roll, rc_pitch, rc_yaw, rc_throt, status_text = arbiter.compute_control(
        gesture, target_coords, hazards, is_blocked, safe_turn
    )

    t_now = time.time()
    fps = 1.0 / (t_now - prev_time) if prev_time else 60.0
    
    cockpit_frame = draw_hud(
        frame, depth_colored, gesture, target_coords, hazards, 
        is_blocked, safe_turn, (rc_roll, rc_pitch, rc_yaw, rc_throt, status_text), fps
    )
    return cockpit_frame, t_now

if __name__ == "__main__":
    print("[+] Connecting to webcam /dev/video0...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[!] Trying /dev/video1...")
        cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("[!] Error: No webcam accessible.")
        sys.exit(1)

    print("[+] Drone Vision Cockpit active! Press 'q' to quit.")
    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
            
        cockpit_img, prev_time = process_single_frame(frame, prev_time)
        cv2.imshow("MINI AI DRONE - 3D VISION GROUND STATION", cockpit_img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
