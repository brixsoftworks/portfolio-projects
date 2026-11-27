"""
DRONE IDENTITY MEMORY & BIOMETRIC RE-ID COCKPIT
------------------------------------------------
1. Deep Face & Person Biometric Embeddings (576-Dimensional Hypersphere Vector).
2. Persistent Long-Term Memory (drone_memory_db.json).
3. Biometric Security Clearance & Name Recognition:
   - AUTHORIZED PILOT: Full flight command authorization & VIP Follow-Me mode.
   - UNKNOWN SUBJECT: Guest clearance, automatic 2.0m standoff distance.
4. One-Key Enrollment: Press 'e' on any detected person to enroll them into memory!
5. 80-Class Detection + 3D Depth Heatmap + Tactical BEV Mini-Radar + Telemetry.
"""

import sys
sys.path.append('/home/mullainathan/projects/mini-ai-drone')
import cv2
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as T
import numpy as np
import time
import os
import json
from datetime import datetime
from ultralytics import YOLO
from lesson4_depth_and_gestures import DepthNet, analyze_3d_depth, FlightSafetyArbiter
from drone_advanced_vision import get_class_style, estimate_distance_meters, draw_tactical_radar

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[+] Initializing Biometric Identity & Memory Core on: {torch.cuda.get_device_name(0)}")

# ==============================================================================
# CONCEPT 1: Deep Feature Embedding Network (Metric Learning)
# ==============================================================================
# Instead of classification (fixed classes), we use a Deep Convolutional Backbone
# that converts any face/person image into a 576-dimensional unit vector.
# Cosine Similarity between vectors:
#   Similarity = dot_product(v_A, v_B)  where ||v|| = 1.0
# If similarity >= 0.72 -> Same human identity!

class PersonEmbeddingNet(nn.Module):
    def __init__(self):
        super(PersonEmbeddingNet, self).__init__()
        weights = models.MobileNet_V3_Small_Weights.DEFAULT
        backbone = models.mobilenet_v3_small(weights=weights)
        self.features = backbone.features
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        
    def forward(self, x):
        # Input: [Batch, 3, 112, 112]
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1) # [Batch, 576]
        # L2-Normalization onto unit hypersphere
        norm = torch.norm(x, p=2, dim=1, keepdim=True).clamp(min=1e-12)
        x = x / norm
        return x

embed_model = PersonEmbeddingNet().to(device).eval()

transform_face = T.Compose([
    T.ToPILImage(),
    T.Resize((112, 112)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# ==============================================================================
# CONCEPT 2: Persistent Long-Term Memory Database
# ==============================================================================
MEMORY_DB_PATH = "/home/mullainathan/projects/mini-ai-drone/drone_memory_db.json"

class DroneMemorySystem:
    def __init__(self, db_path=MEMORY_DB_PATH):
        self.db_path = db_path
        self.database = self.load_database()

    def load_database(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    data = json.load(f)
                    print(f"[+] Loaded {len(data)} identities from long-term memory.")
                    return data
            except Exception as e:
                print(f"[!] Error loading memory DB: {e}")
        return {}

    def save_database(self):
        with open(self.db_path, "w") as f:
            json.dump(self.database, f, indent=2)
        print(f"[+] Saved memory database to: {self.db_path}")

    def enroll_person(self, name, role, clearance, embedding_vec):
        pid = f"ID_{len(self.database) + 1:02d}"
        self.database[pid] = {
            "name": name,
            "role": role,
            "clearance": clearance,
            "embedding": [float(v) for v in embedding_vec],
            "first_enrolled": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sightings": 1
        }
        self.save_database()
        return pid

    def identify(self, candidate_emb, threshold=0.72):
        best_match = None
        highest_sim = -1.0
        
        for pid, profile in self.database.items():
            stored_emb = np.array(profile["embedding"], dtype=np.float32)
            sim = float(np.dot(candidate_emb, stored_emb))
            if sim > highest_sim:
                highest_sim = sim
                best_match = (pid, profile)

        if highest_sim >= threshold and best_match is not None:
            pid, profile = best_match
            profile["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            profile["sightings"] += 1
            return True, profile["name"], profile["role"], profile["clearance"], highest_sim
        else:
            return False, "UNKNOWN SUBJECT", "GUEST", "RESTRICTED", highest_sim

memory_system = DroneMemorySystem()

# ==============================================================================
# Load YOLO, DepthNet & Flight Arbiter
# ==============================================================================
object_model = YOLO("yolov8n.pt").to(device)
depth_model = DepthNet().to(device).eval()
depth_weights = "/home/mullainathan/projects/mini-ai-drone/depth_model.pth"
if os.path.exists(depth_weights):
    depth_model.load_state_dict(torch.load(depth_weights, map_location=device))
arbiter = FlightSafetyArbiter()

# ==============================================================================
# Render Enhanced Cockpit HUD with Biometrics
# ==============================================================================
def render_biometric_cockpit(frame, depth_colored, detected_objects, identities, hazards, is_blocked, safe_turn, rc_data, fps):
    rc_roll, rc_pitch, rc_yaw, rc_throt, status_text = rc_data
    h, w, _ = frame.shape
    cx, cy = w // 2, h // 2
    
    # Crosshair
    cv2.drawMarker(frame, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 20, 1)

    # 1. Draw Biometric Badges for Recognized People
    for person_info in identities:
        x1, y1, x2, y2 = person_info['box']
        name = person_info['name']
        role = person_info['role']
        clearance = person_info['clearance']
        sim = person_info['similarity']
        is_known = person_info['is_known']
        dist_m = person_info['distance_m']

        badge_color = (0, 255, 0) if is_known else (0, 140, 255)
        
        # High-tech Sci-Fi biometric bracket
        cv2.rectangle(frame, (x1, y1), (x2, y2), badge_color, 2)
        
        # Head-level Identity Tag
        tag_main = f"{name} ({dist_m:.1f}m)"
        tag_sub = f"ROLE: {role} | {clearance}"
        
        # Background badge box
        cv2.rectangle(frame, (x1, y1 - 36), (x1 + max(len(tag_main), len(tag_sub)) * 7 + 10, y1), (20, 20, 20), -1)
        cv2.rectangle(frame, (x1, y1 - 36), (x1 + max(len(tag_main), len(tag_sub)) * 7 + 10, y1), badge_color, 1)
        
        cv2.putText(frame, tag_main, (x1 + 5, y1 - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, badge_color, 1, cv2.LINE_AA)
        cv2.putText(frame, tag_sub, (x1 + 5, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (220, 220, 220), 1, cv2.LINE_AA)

    # 2. Draw non-person Objects
    for obj in detected_objects:
        if obj['label'] == 'person':
            continue
        x1, y1, x2, y2 = obj['box']
        tag = f"{obj['label'].upper()} {obj['distance_m']:.1f}m"
        color = obj['color']
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
        cv2.putText(frame, tag, (x1 + 3, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, color, 1)

    # 3. Sector Depth Map Lines & Mini Radar
    dh, dw, _ = depth_colored.shape
    third_w = dw // 3
    cv2.line(depth_colored, (third_w, 0), (third_w, dh), (255, 255, 255), 1)
    cv2.line(depth_colored, (2 * third_w, 0), (2 * third_w, dh), (255, 255, 255), 1)
    
    left_h, center_h, right_h = hazards
    for lbl, val, x_pos in [("L-SECTOR", left_h, 15), ("C-SECTOR", center_h, third_w + 15), ("R-SECTOR", right_h, 2 * third_w + 15)]:
        c = (0, 0, 255) if val > 0.65 else (0, 255, 0)
        cv2.putText(depth_colored, f"{lbl}: {int(val*100)}%", (x_pos, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, c, 2)

    # Radar overlay
    radar_canvas = depth_colored[10:200, dw - 200:dw - 10]
    draw_tactical_radar(radar_canvas, detected_objects, radius=85, center=(95, 95))

    # 4. Side-by-Side Dual Screen
    combined = np.hstack([frame, depth_colored])
    cw = combined.shape[1]
    
    # 5. Bottom Cockpit Bar
    dash_h = 105
    dashboard = np.zeros((dash_h, cw, 3), dtype=np.uint8)
    dashboard[:] = (18, 18, 22)
    cv2.line(dashboard, (0, 0), (cw, 0), (60, 60, 68), 2)
    
    # Mission banner
    status_color = (0, 0, 255) if is_blocked else (0, 255, 120)
    cv2.putText(dashboard, f"MISSION ARBITER: {status_text.upper()}", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.60, status_color, 2)
    
    # Memory Bank Status
    known_count = len(memory_system.database)
    mem_text = f"MEMORY DATABASE: {known_count} PROFILES STORED | BIOMETRICS: 576-D METRIC LEARNING (L2-NORM)"
    cv2.putText(dashboard, mem_text, (20, 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1)

    info_text = f"FPS: {fps:.1f} (RTX 5060) | RC YAW: {rc_yaw}us | RC PITCH: {rc_pitch}us | THROTTLE: {rc_throt}us | ROLL: {rc_roll}us"
    cv2.putText(dashboard, info_text, (20, 86),
                cv2.FONT_HERSHEY_SIMPLEX, 0.46, (0, 255, 255), 1)

    # Mini RC Gauge visual bars
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

# ==============================================================================
# Frame Processing Function
# ==============================================================================
def process_biometric_frame(frame, prev_time=None, enroll_request=None):
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    arbiter.frame_width = w
    arbiter.center_x = w / 2.0

    # 1. Dense 3D Depth Map
    small_frame = cv2.resize(frame, (160, 120))
    tensor_img = torch.from_numpy(small_frame.astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0).to(device)
    with torch.no_grad():
        depth_raw = depth_model(tensor_img)[0, 0].cpu().numpy()
        
    is_blocked, hazards, safe_turn = analyze_3d_depth(depth_raw, proximity_threshold=0.68)
    
    depth_uint8 = (depth_raw * 255).astype(np.uint8)
    depth_resized = cv2.resize(depth_uint8, (w, h))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 40, 120)
    depth_composite = np.clip((depth_resized.astype(np.float32) * 0.75) + (edges.astype(np.float32) * 0.35), 0, 255).astype(np.uint8)
    depth_colored = cv2.applyColorMap(depth_composite, cv2.COLORMAP_TURBO)

    # 2. 80-Class Detection
    results = object_model.predict(frame, conf=0.35, verbose=False, device=0)[0]
    
    detected_objects = []
    identities = []
    vip_target = None
    min_dist = 999.0

    for box in results.boxes:
        coords = list(map(int, box.xyxy[0].cpu().numpy()))
        cls_id = int(box.cls[0].cpu().numpy())
        conf = float(box.conf[0].cpu().numpy())
        label = object_model.names[cls_id]
        
        x1, y1, x2, y2 = np.clip(coords[0], 0, w-1), np.clip(coords[1], 0, h-1), np.clip(coords[2], 0, w-1), np.clip(coords[3], 0, h-1)
        obj_depth_patch = depth_raw[int(y1*120/h):int(y2*120/h), int(x1*160/w):int(x2*160/w)]
        dist_m = estimate_distance_meters(obj_depth_patch)
        color, category = get_class_style(label)
        center_x = (x1 + x2) / 2.0
        azimuth_norm = (center_x - (w / 2.0)) / (w / 2.0)
        
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
        
        # --- BIOMETRIC EXTRACTION IF PERSON ---
        if label == "person":
            # Crop upper torso / head (top 45% of bounding box)
            head_y2 = y1 + int(0.45 * (y2 - y1))
            if head_y2 > y1 + 20 and x2 > x1 + 20:
                head_crop = frame[y1:head_y2, x1:x2]
                tensor_face = transform_face(head_crop).unsqueeze(0).to(device)
                
                with torch.no_grad():
                    face_emb = embed_model(tensor_face)[0].cpu().numpy()
                    
                # Check for interactive enrollment
                if enroll_request:
                    name, role, clearance = enroll_request
                    memory_system.enroll_person(name, role, clearance, face_emb)
                    enroll_request = None # Handled
                    
                # Identify via Cosine Metric
                is_known, name, role, clearance, sim = memory_system.identify(face_emb)
                
                person_info = {
                    'box': (x1, y1, x2, y2),
                    'name': name,
                    'role': role,
                    'clearance': clearance,
                    'similarity': sim,
                    'is_known': is_known,
                    'distance_m': dist_m,
                    'center': obj_info['center']
                }
                identities.append(person_info)
                
                # Priority: If authorized Chief Pilot -> Lock as VIP target!
                if is_known and "PILOT" in role.upper():
                    vip_target = person_info
                elif vip_target is None and dist_m < min_dist:
                    min_dist = dist_m
                    vip_target = person_info

    # 3. Flight Decision Arbiter based on Biometric Status
    if is_blocked:
        rc_roll, rc_pitch, rc_yaw, rc_throt, status_text = arbiter.compute_control(
            "NO_TARGET", (w // 2, h // 2), hazards, is_blocked, safe_turn
        )
    elif vip_target is not None:
        target_cx = vip_target['center'][0]
        error_x = target_cx - (w / 2.0)
        rc_yaw = int(1500 + (error_x / (w / 2.0)) * 180)
        
        # Authorized VIP pilot gets closer follow distance (1.2m); Stranger kept at 2.0m standoff
        desired_dist = 1.3 if vip_target.get('is_known', False) else 2.2
        
        if vip_target['distance_m'] > (desired_dist + 0.3):
            rc_pitch = 1550 # Advance
            action_desc = "VIP ESCORT: ADVANCING" if vip_target.get('is_known') else "STANDOFF: FOLLOWING AT DISTANCE"
        elif vip_target['distance_m'] < (desired_dist - 0.3):
            rc_pitch = 1450 # Retreat
            action_desc = "TOO CLOSE: BACKING OFF"
        else:
            rc_pitch = 1500
            action_desc = "LOCKED: HOLDING POSITION"
            
        status_text = f"TARGET: {vip_target['name']} ({vip_target['distance_m']:.1f}m) -> {action_desc}"
        rc_roll = 1500
        rc_throt = 1450
    else:
        rc_roll, rc_pitch, rc_yaw, rc_throt, status_text = 1500, 1500, 1500, 1450, "STANDBY: SCANNING FOR KNOWN PERSONNEL"

    t_now = time.time()
    fps = 1.0 / (t_now - prev_time) if prev_time else 60.0
    
    cockpit = render_biometric_cockpit(
        frame, depth_colored, detected_objects, identities, hazards, 
        is_blocked, safe_turn, (rc_roll, rc_pitch, rc_yaw, rc_throt, status_text), fps
    )
    return cockpit, t_now

if __name__ == "__main__":
    print("[+] Connecting to webcam /dev/video0...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)

    print("\n" + "=" * 65)
    print("BIOMETRIC IDENTITY DRONE GROUND STATION")
    print("Press 'e' to ENROLL the current person as 'CHIEF PILOT: Mullainathan'")
    print("Press 'q' to QUIT")
    print("=" * 65)
    
    prev_time = time.time()
    enroll_next = None

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
            
        cockpit_img, prev_time = process_biometric_frame(frame, prev_time, enroll_request=enroll_next)
        enroll_next = None # Reset after one frame
        
        cv2.imshow("MINI AI DRONE - BIOMETRIC IDENTITY COCKPIT", cockpit_img)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('e'):
            print("\n[!] ENROLLMENT TRIGGERED: Registering current face as Chief Pilot (Mullainathan)...")
            enroll_next = ("Mullainathan", "CHIEF PILOT", "CLEARANCE: ALPHA-1")

    cap.release()
    cv2.destroyAllWindows()
