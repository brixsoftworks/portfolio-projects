"""
LIVE INTERACTIVE TEST: Laptop Webcam AI Drone Ground Station
------------------------------------------------------------
Run this script to test the complete Multi-Task AI Vision Pipeline
using your laptop's built-in webcam!

Gestures you can try in front of your camera:
1. RAISE RIGHT HAND: Activates 'FOLLOW ME' mode (Drone tracks you).
2. RAISE BOTH HANDS (V-Shape): Activates 'HOVER / STOP' mode.
3. CROSS ARMS (Wrists touching chest): Activates 'EMERGENCY LAND / DISARM'.
"""

import sys
sys.path.append('/home/mullainathan/projects/mini-ai-drone')
import cv2
import torch
import numpy as np
from ultralytics import YOLO
from lesson4_depth_and_gestures import DepthNet, analyze_3d_depth, classify_gesture, FlightSafetyArbiter

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[+] Launching Drone Vision HUD on: {torch.cuda.get_device_name(0)}")

# Load models
pose_model = YOLO("yolov8n-pose.pt").to(device)
depth_model = DepthNet().to(device).eval()
arbiter = FlightSafetyArbiter()

# Open laptop webcam (device index 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("[!] Warning: Could not open webcam 0. Trying device index 1...")
    cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("[!] Error: No webcam detected. Please ensure your camera is enabled.")
    sys.exit(1)

print("\n" + "=" * 65)
print("LIVE AI DRONE STATION RUNNING! Press 'q' in the window to quit.")
print("=" * 65)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Resize to standard working resolution (e.g. 640x480)
    frame = cv2.flip(frame, 1) # Mirror preview
    h, w, _ = frame.shape
    arbiter.frame_width = w
    arbiter.center_x = w / 2.0

    # 1. Monocular 3D Depth Estimation
    small_frame = cv2.resize(frame, (160, 120))
    tensor_img = torch.from_numpy(small_frame.astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0).to(device)
    with torch.no_grad():
        depth_map = depth_model(tensor_img)[0, 0].cpu().numpy()
        
    is_blocked, hazards, safe_turn = analyze_3d_depth(depth_map, proximity_threshold=0.75)
    left_h, center_h, right_h = hazards

    # 2. Human Pose & Gesture Classification
    pose_results = pose_model(frame, verbose=False)[0]
    gesture = "NO_TARGET"
    target_coords = (w // 2, h // 2)

    if pose_results.keypoints is not None and len(pose_results.keypoints) > 0:
        kpts = pose_results.keypoints.xy[0].cpu().numpy() # First detected person
        gesture, target_coords = classify_gesture(kpts)

        # Draw skeleton keypoints on the live frame
        for kp in kpts:
            if kp[0] > 0 and kp[1] > 0:
                cv2.circle(frame, (int(kp[0]), int(kp[1])), 4, (0, 255, 0), -1)

    # 3. Decision Arbiter: Merge Gesture + 3D Safety
    rc_roll, rc_pitch, rc_yaw, rc_throt, status_text = arbiter.compute_control(
        gesture, target_coords, hazards, is_blocked, safe_turn
    )

    # 4. Heads-Up Display (HUD) Rendering
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (w - 10, 110), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    # Status & Mode
    status_color = (0, 0, 255) if is_blocked else ((0, 255, 0) if "FOLLOW" in gesture else (255, 255, 0))
    cv2.putText(frame, f"STATUS: {status_text}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2)
    cv2.putText(frame, f"GESTURE: {gesture} | TARGET: ({int(target_coords[0])}, {int(target_coords[1])})", 
                (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)
    cv2.putText(frame, f"RC PWM: Pitch={rc_pitch}us | Yaw={rc_yaw}us | Throttle={rc_throt}us | Roll={rc_roll}us", 
                (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)

    # Show live window
    cv2.imshow("NVIDIA AI Drone Ground Station (Webcam HUD)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
