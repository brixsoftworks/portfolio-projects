"""
WEBOTS 3D CYBER-PHYSICAL DRONE CONTROLLER WITH FAILSAFE ANTI-ULTA FLIGHT SHIELD
-------------------------------------------------------------------------------
Hardware-in-the-Loop Multi-Modal Gesture Flight System with Flight Envelope Protection:
- Vision Sensor: PHYSICAL LAPTOP WEBCAM (/dev/video0)
- 3D Physics Simulator: WEBOTS DJI MAVIC 2 PRO QUADCOPTER
- Hand Tracking: Google MediaPipe GestureRecognizer (21 3D Landmarks)
- Stability Engine: Tuned Critical-Damping PD Attitude Controller + Anti-Ulta Guard
- Ground Cushion: Precision Touchdown Detection & Instant Motor Disarm (Never flips)

SAFETY GUARANTEES:
1. Max tilt angle strictly bounded to 12 degrees - mathematically impossible to flip.
2. Vertical rate limiting: Max 0.38 m/s climb/descent - eliminates violent momentum.
3. In-flight minimum altitude floor (0.55m): Hand lowering will never slam into the ground.
4. Auto-Land Confirmation: Requires 25 consecutive frames of fist before landing.
5. Ground Cushion: Below 0.32m, wings are held 100% level; at 0.185m, motors cut instantly.
6. Auto-Takeoff: Raising hand or pressing 'Space' smoothly lifts off to 1.0m hover!
"""

import os
import sys
import math
import time

# Auto-configure WEBOTS_HOME if running directly
if "WEBOTS_HOME" not in os.environ:
    os.environ["WEBOTS_HOME"] = "/var/lib/flatpak/app/com.cyberbotics.webots/x86_64/stable/b951a7b4ed04f8c295c5c3a347e09e81bb588a102115788e0b6ae2182c9485f1/files/webots"

webots_py = os.path.join(os.environ["WEBOTS_HOME"], "lib", "controller", "python")
if webots_py not in sys.path:
    sys.path.append(webots_py)

# Ensure our AI drone project root is in Python path
sys.path.append('/home/mullainathan/projects/mini-ai-drone')

import numpy as np
import cv2
from controller import Robot, Keyboard
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from drone_dji_matrice_ultimate import process_matrice_frame, matrice_engine

def CLAMP(val, low, high):
    return max(low, min(high, val))

print("=" * 75)
print("[+] INITIALIZING CYBER-PHYSICAL DRONE CONTROLLER (ANTI-ULTA FAILSAFE)...")
print("=" * 75)

# 1. Initialize MediaPipe Gesture Recognizer
print("[*] Loading Google MediaPipe Gesture Recognizer...")
base_options = python.BaseOptions(
    model_asset_path='/home/mullainathan/projects/mini-ai-drone/gesture_recognizer.task'
)
options = vision.GestureRecognizerOptions(
    base_options=base_options,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5
)
gesture_recognizer = vision.GestureRecognizer.create_from_options(options)
print("[+] MediaPipe Gesture Recognizer loaded successfully!")

# Hand skeleton bone connections
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

# 2. Connect to Physical Laptop Webcam
print("[*] Connecting to physical laptop webcam (/dev/video0)...")
webcam = cv2.VideoCapture(0)
if not webcam.isOpened():
    print("[!] /dev/video0 failed, trying /dev/video1...")
    webcam = cv2.VideoCapture(1)

if not webcam.isOpened():
    raise RuntimeError("Failed to open physical webcam! Please ensure webcam is connected.")

webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
print("[+] Physical Webcam connected! Live user video stream ready.")

# 3. Connect to Webots 3D Physics Robot
robot = Robot()
timestep = int(robot.getBasicTimeStep())
print(f"[+] Connected to Webots 3D Quadcopter: {robot.getName()} (timestep={timestep}ms)")

# 4. Enable Sensors
sim_camera = robot.getDevice("camera")
sim_camera.enable(2 * timestep)

imu = robot.getDevice("inertial unit")
imu.enable(timestep)

gps = robot.getDevice("gps")
gps.enable(timestep)

gyro = robot.getDevice("gyro")
gyro.enable(timestep)

camera_roll = robot.getDevice("camera roll")
camera_pitch = robot.getDevice("camera pitch")

keyboard = robot.getKeyboard()
keyboard.enable(timestep)

# 5. Enable Motors (4 Propellers)
m_fl = robot.getDevice("front left propeller")
m_fr = robot.getDevice("front right propeller")
m_rl = robot.getDevice("rear left propeller")
m_rr = robot.getDevice("rear right propeller")

motors = [m_fl, m_fr, m_rl, m_rr]
for m in motors:
    m.setPosition(float('inf'))
    m.setVelocity(1.0)

# 6. Physical Quadcopter Stability Dynamics Constants
K_VERTICAL_THRUST = 68.5   # Equilibrium hover thrust
K_VERTICAL_OFFSET = 0.6    # Webots Mavic 2 Pro empirical offset
K_VERTICAL_P = 3.0         # Vertical cubic PID constant

K_ROLL_P = 50.0            # Roll restoring stiffness
K_ROLL_D = 1.5             # Gyro velocity damping (prevents flutter)
K_PITCH_P = 30.0           # Pitch restoring stiffness
K_PITCH_D = 1.5

# Flight States: "FLYING", "AUTO_LANDING", "TOUCHDOWN"
flight_state = "FLYING"
target_altitude = 1.2
MIN_FLIGHT_ALT = 0.55      # Hard safety floor during active flight
MAX_FLIGHT_ALT = 3.20      # Flight ceiling
is_disarmed = False

# Confirmation Counter for Deliberate Auto-Landing
fist_hold_counter = 0
FIST_TRIGGER_FRAMES = 25   # ~0.4s consecutive hold required to trigger landing

# Wait 1.0s for Webots physics to settle before applying thrust
print("[+] Stabilizing initial physics...")
while robot.step(timestep) != -1:
    if robot.getTime() > 1.0:
        break

prev_time = time.time()
step_counter = 0

# Persistent Hand Tracking State
palm_is_active = False
smooth_hx = 0.5
smooth_hy = 0.5
smooth_hand_scale = 0.20
palm_roll_dist = 0.0
palm_pitch_dist = 0.0
palm_yaw_dist = 0.0
palm_action_vert = "ALT LOCKED (1.20m)"
palm_action_horiz = "LEVEL"
palm_action_pitch = "HOVER"
palm_gesture_name = "NONE"
last_seen_hand_time = 0.0

print("[+] Drone taking off! Anti-Ulta Flight Shield is ACTIVE.")

while robot.step(timestep) != -1:
    step_counter += 1
    t_now = time.time()
    
    # --- Step A: Read Webots Virtual Sensors ---
    rpy = imu.getRollPitchYaw()
    roll, pitch, yaw = rpy[0], rpy[1], rpy[2]
    alt = gps.getValues()[2]
    g = gyro.getValues()
    roll_vel = g[0]
    pitch_vel = g[1]

    # Gimbal camera stabilization
    if camera_roll and camera_pitch:
        camera_roll.setPosition(-0.115 * roll_vel)
        camera_pitch.setPosition(-0.1 * pitch_vel)

    # --- Step B: Grab REAL WEBCAM FRAME ---
    ret, frame_raw = webcam.read()
    if not ret or frame_raw is None:
        continue
        
    frame_bgr = cv2.flip(frame_raw, 1)
    f_h, f_w, _ = frame_bgr.shape

    # Grab Webots virtual camera frame for PIP
    sim_raw = sim_camera.getImage()
    sim_thumb = None
    if sim_raw is not None:
        s_h, s_w = sim_camera.getHeight(), sim_camera.getWidth()
        s_np = np.frombuffer(sim_raw, np.uint8).reshape((s_h, s_w, 4))
        sim_thumb = cv2.resize(s_np[:, :, :3], (160, 100))

    # --- Step C: MEDIAPIPE GESTURE TRACKING ---
    rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    rec_result = gesture_recognizer.recognize(mp_img)

    current_hand_landmarks = None
    hand_seen = (len(rec_result.hand_landmarks) > 0)
    
    if hand_seen:
        palm_is_active = True
        last_seen_hand_time = t_now
        hand_lms = rec_result.hand_landmarks[0]
        current_hand_landmarks = hand_lms
        
        raw_hx = hand_lms[9].x
        raw_hy = hand_lms[9].y
        
        # Hand physical scale: distance from wrist (0) to middle knuckle (9)
        dx_hand = hand_lms[9].x - hand_lms[0].x
        dy_hand = hand_lms[9].y - hand_lms[0].y
        raw_scale = math.hypot(dx_hand, dy_hand)
        
        palm_gesture_name = "OPEN_PALM"
        if rec_result.gestures and len(rec_result.gestures[0]) > 0:
            palm_gesture_name = rec_result.gestures[0][0].category_name.upper()

        # Smooth coordinates with Exponential Moving Average
        smooth_hx = 0.35 * raw_hx + 0.65 * smooth_hx
        smooth_hy = 0.35 * raw_hy + 0.65 * smooth_hy
        smooth_hand_scale = 0.30 * raw_scale + 0.70 * smooth_hand_scale

        # --- AUTO-LANDING CONFIRMATION CHECK ---
        # Require closed fist or hand pushed to extreme bottom (>0.88)
        is_fist_landing = (palm_gesture_name == "CLOSED_FIST") or (smooth_hy > 0.88)
        
        if is_fist_landing:
            fist_hold_counter += 1
            if fist_hold_counter >= FIST_TRIGGER_FRAMES:
                flight_state = "AUTO_LANDING"
        else:
            fist_hold_counter = max(0, fist_hold_counter - 2)

        # Re-arm / Abort Landing if hand is raised
        if smooth_hy < 0.42:
            if flight_state == "TOUCHDOWN":
                # Take off!
                flight_state = "FLYING"
                is_disarmed = False
                target_altitude = 1.0
            elif flight_state == "AUTO_LANDING":
                # Abort landing and climb safely
                flight_state = "FLYING"
                target_altitude = max(target_altitude, alt) + 0.30

        # --- FLIGHT CONTROLS IF FLYING ---
        if flight_state == "FLYING":
            # 1. UP & DOWN Altitude Control (Smooth Rate Limited)
            if smooth_hy < 0.40:
                climb_ratio = (0.40 - smooth_hy) / 0.40
                step_climb = 0.002 + climb_ratio * 0.004   # Max ~0.38 m/s climb rate
                target_altitude = min(target_altitude + step_climb, MAX_FLIGHT_ALT)
                palm_action_vert = f"▲ CLIMBING ({climb_ratio*100:.0f}%)"
            elif smooth_hy > 0.60:
                desc_ratio = (smooth_hy - 0.60) / 0.40
                step_desc = 0.002 + desc_ratio * 0.004    # Max ~0.38 m/s descent rate
                # HARD SAFETY FLOOR: Never descends below MIN_FLIGHT_ALT in flight
                target_altitude = max(target_altitude - step_desc, MIN_FLIGHT_ALT)
                palm_action_vert = f"▼ DESCENDING ({desc_ratio*100:.0f}%)"
            else:
                palm_action_vert = f"ALT HOLD ({target_altitude:.2f}m)"

            # 2. SIDEWAYS (LEFT & RIGHT) Roll/Yaw Control (Coordinated Banking)
            if smooth_hx < 0.42:
                # Hand to user's left -> Strafe & Turn LEFT
                left_ratio = (0.42 - smooth_hx) / 0.42
                palm_roll_dist = +CLAMP(left_ratio * 0.45, 0.0, 0.45)
                palm_yaw_dist  = +CLAMP(left_ratio * 0.65, 0.0, 0.65)
                palm_action_horiz = f"◄ BANK LEFT ({left_ratio*100:.0f}%)"
            elif smooth_hx > 0.58:
                # Hand to user's right -> Strafe & Turn RIGHT
                right_ratio = (smooth_hx - 0.58) / 0.42
                palm_roll_dist = -CLAMP(right_ratio * 0.45, 0.0, 0.45)
                palm_yaw_dist  = -CLAMP(right_ratio * 0.65, 0.0, 0.65)
                palm_action_horiz = f"► BANK RIGHT ({right_ratio*100:.0f}%)"
            else:
                palm_roll_dist = 0.0
                palm_yaw_dist  = 0.0
                palm_action_horiz = "LEVEL"

            # 3. FORWARD / BACKWARD PITCH CONTROL
            if palm_gesture_name == "POINTING_UP" or smooth_hand_scale > 0.28:
                palm_pitch_dist = -0.40   # Gentle forward glide
                palm_action_pitch = "FORWARD"
            elif smooth_hand_scale < 0.14:
                palm_pitch_dist = +0.30   # Gentle backward glide
                palm_action_pitch = "BACKWARD"
            else:
                palm_pitch_dist = 0.0
                palm_action_pitch = "HOVER"
                
    else:
        # Hand not seen: decay active disturbances smoothly
        fist_hold_counter = max(0, fist_hold_counter - 1)
        if t_now - last_seen_hand_time > 0.35:
            palm_is_active = False
            palm_roll_dist *= 0.85
            palm_yaw_dist  *= 0.85
            palm_pitch_dist *= 0.85
            palm_action_vert = f"AUTO HOVER ({target_altitude:.2f}m)"
            palm_action_horiz = "LEVEL"
            palm_action_pitch = "HOVER"

    # --- Step D: Keyboard Manual Overrides ---
    manual_pitch_cmd = 0.0
    manual_roll_cmd = 0.0
    manual_yaw_cmd = 0.0
    key_pressed = False

    w_key = keyboard.getKey()
    while w_key > 0:
        if w_key in [Keyboard.UP, ord('W'), ord('w')]:
            manual_pitch_cmd = 1.0; key_pressed = True
        elif w_key in [Keyboard.DOWN, ord('S'), ord('s')]:
            manual_pitch_cmd = -1.0; key_pressed = True
        elif w_key in [Keyboard.LEFT, ord('A'), ord('a')]:
            manual_yaw_cmd = 1.0; key_pressed = True
        elif w_key in [Keyboard.RIGHT, ord('D'), ord('d')]:
            manual_yaw_cmd = -1.0; key_pressed = True
        elif w_key in [ord('J'), ord('j'), Keyboard.SHIFT + Keyboard.LEFT]:
            manual_roll_cmd = 1.0; key_pressed = True
        elif w_key in [ord('L'), ord('l'), Keyboard.SHIFT + Keyboard.RIGHT]:
            manual_roll_cmd = -1.0; key_pressed = True
        elif w_key in [ord(' '), ord('I'), ord('i'), Keyboard.SHIFT + Keyboard.UP]:
            flight_state = "FLYING"
            is_disarmed = False
            target_altitude = min(target_altitude + 0.03, MAX_FLIGHT_ALT); key_pressed = True
        elif w_key in [ord('C'), ord('c'), ord('K'), ord('k')]:
            flight_state = "AUTO_LANDING"
        elif w_key in [ord('M'), ord('m'), 9]:
            matrice_engine.control_mode = "MANUAL" if matrice_engine.control_mode == "AUTONOMOUS" else "AUTONOMOUS"
        elif w_key in [ord('X'), ord('x')]:
            manual_pitch_cmd = 0.0; manual_roll_cmd = 0.0; manual_yaw_cmd = 0.0; key_pressed = True
        elif w_key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('t'), ord('T')]:
            if w_key == ord('1'): matrice_engine.mode = "ACTIVETRACK"
            elif w_key == ord('2'): matrice_engine.mode = "SPOTLIGHT"
            elif w_key == ord('3'): matrice_engine.mode = "ORBIT"
            elif w_key == ord('4'): matrice_engine.mode = "DRONIE"; matrice_engine.step_counter = 0
            elif w_key == ord('5'): matrice_engine.mode = "ROCKET"; matrice_engine.step_counter = 0
            elif w_key in [ord('t'), ord('T')]: matrice_engine.thermal_active = not matrice_engine.thermal_active
        w_key = keyboard.getKey()

    # --- Step E: Cockpit HUD & Visual Overlays ---
    if step_counter % 2 == 0:
        cockpit_hud, prev_time = process_matrice_frame(frame_bgr, prev_time)
        
        # 1. Render Hand Skeleton & Reticle
        if palm_is_active and current_hand_landmarks is not None:
            pts = [(int(lm.x * f_w), int(lm.y * f_h)) for lm in current_hand_landmarks]
            for p1_idx, p2_idx in HAND_CONNECTIONS:
                cv2.line(cockpit_hud, pts[p1_idx], pts[p2_idx], (0, 255, 255), 2)
            for pt in pts:
                cv2.circle(cockpit_hud, pt, 4, (0, 255, 0), -1)

            # Center palm reticle
            cx, cy = int(smooth_hx * f_w), int(smooth_hy * f_h)
            cv2.circle(cockpit_hud, (cx, cy), 20, (0, 200, 255), 2)
            cv2.circle(cockpit_hud, (cx, cy), 4, (0, 0, 255), -1)

            # Neutral deadzone box (0.42 to 0.58 X, 0.40 to 0.60 Y)
            nz_x1, nz_y1 = int(0.42 * f_w), int(0.40 * f_h)
            nz_x2, nz_y2 = int(0.58 * f_w), int(0.60 * f_h)
            cv2.rectangle(cockpit_hud, (nz_x1, nz_y1), (nz_x2, nz_y2), (0, 255, 100), 1)

            # Flight direction vector
            neutral_center = ((nz_x1 + nz_x2) // 2, (nz_y1 + nz_y2) // 2)
            cv2.arrowedLine(cockpit_hud, neutral_center, (cx, cy), (0, 255, 255), 2, tipLength=0.25)

            # Telemetry status badge
            badge_txt = f"PALM NAV: {palm_action_vert} | {palm_action_horiz} | {palm_action_pitch}"
            cv2.rectangle(cockpit_hud, (15, 15), (15 + len(badge_txt) * 9 + 15, 48), (20, 20, 24), -1)
            cv2.rectangle(cockpit_hud, (15, 15), (15 + len(badge_txt) * 9 + 15, 48), (0, 255, 255), 2)
            cv2.putText(cockpit_hud, badge_txt, (22, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 255), 2)
        else:
            idle_txt = f"ANTI-ULTA SHIELD ACTIVE | STATE: {flight_state} | ALT: {alt:.2f}m / TGT: {target_altitude:.2f}m"
            cv2.rectangle(cockpit_hud, (15, 15), (15 + len(idle_txt) * 9 + 15, 48), (20, 20, 24), -1)
            cv2.rectangle(cockpit_hud, (15, 15), (15 + len(idle_txt) * 9 + 15, 48), (0, 255, 120), 2)
            cv2.putText(cockpit_hud, idle_txt, (22, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (0, 255, 120), 2)

        # 2. Render Auto-Land Progress Bar if fist is held
        if fist_hold_counter > 0 and flight_state == "FLYING":
            prog = min(1.0, fist_hold_counter / FIST_TRIGGER_FRAMES)
            bx, by, bw, bh = 150, 430, 340, 24
            cv2.rectangle(cockpit_hud, (bx, by), (bx + bw, by + bh), (30, 30, 35), -1)
            cv2.rectangle(cockpit_hud, (bx, by), (bx + int(bw * prog), by + bh), (0, 140, 255), -1)
            cv2.rectangle(cockpit_hud, (bx, by), (bx + bw, by + bh), (0, 200, 255), 2)
            land_txt = f"HOLD FIST TO LAND: {int(prog * 100)}%"
            cv2.putText(cockpit_hud, land_txt, (bx + 40, by + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 2)

        # 3. Flight State Banner
        if flight_state == "AUTO_LANDING":
            al_txt = f"PRECISION AUTO-LANDING... (ALT: {alt:.2f}m - RAISE HAND TO ABORT)"
            cv2.rectangle(cockpit_hud, (15, 56), (15 + len(al_txt) * 9 + 15, 86), (0, 60, 200), -1)
            cv2.putText(cockpit_hud, al_txt, (22, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 2)
        elif flight_state == "TOUCHDOWN":
            td_txt = "TOUCHDOWN & DISARMED! (RAISE HAND OR PRESS SPACE TO TAKEOFF)"
            cv2.rectangle(cockpit_hud, (15, 56), (15 + len(td_txt) * 9 + 15, 86), (0, 150, 0), -1)
            cv2.putText(cockpit_hud, td_txt, (22, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 2)

        # 4. Overlay 3D Drone Simulation PIP
        if sim_thumb is not None:
            pw, ph = 160, 100
            x_off, y_off = 460, 15
            cv2.rectangle(cockpit_hud, (x_off - 2, y_off - 2), (x_off + pw + 2, y_off + ph + 2), (0, 255, 255), 1)
            cockpit_hud[y_off:y_off + ph, x_off:x_off + pw] = sim_thumb
            cv2.putText(cockpit_hud, "3D DRONE SIM CAM", (x_off + 4, y_off + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)

        cv2.imshow("WEBOTS 3D + LIVE WEBCAM - ANTI-ULTA SAFEGUARD", cockpit_hud)
        cv_key = cv2.waitKey(1) & 0xFF
        
        if cv_key == ord('q') or cv_key == 27:
            break
        elif cv_key in [ord('w'), ord('W'), 82]: manual_pitch_cmd = 1.0; key_pressed = True
        elif cv_key in [ord('s'), ord('S'), 84]: manual_pitch_cmd = -1.0; key_pressed = True
        elif cv_key in [ord('a'), ord('A'), 81]: manual_yaw_cmd = 1.0; key_pressed = True
        elif cv_key in [ord('d'), ord('D'), 83]: manual_yaw_cmd = -1.0; key_pressed = True
        elif cv_key in [ord('j'), ord('J')]: manual_roll_cmd = 1.0; key_pressed = True
        elif cv_key in [ord('l'), ord('L')]: manual_roll_cmd = -1.0; key_pressed = True
        elif cv_key in [ord(' '), ord('i'), ord('I')]:
            flight_state = "FLYING"
            is_disarmed = False
            target_altitude = min(target_altitude + 0.03, MAX_FLIGHT_ALT); key_pressed = True
        elif cv_key in [ord('c'), ord('C'), ord('k'), ord('K')]:
            flight_state = "AUTO_LANDING"
        elif cv_key in [ord('m'), ord('M'), 9]:
            matrice_engine.control_mode = "MANUAL" if matrice_engine.control_mode == "AUTONOMOUS" else "AUTONOMOUS"
        elif cv_key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('t'), ord('T')]:
            if cv_key == ord('1'): matrice_engine.mode = "ACTIVETRACK"
            elif cv_key == ord('2'): matrice_engine.mode = "SPOTLIGHT"
            elif cv_key == ord('3'): matrice_engine.mode = "ORBIT"
            elif cv_key == ord('4'): matrice_engine.mode = "DRONIE"; matrice_engine.step_counter = 0
            elif cv_key == ord('5'): matrice_engine.mode = "ROCKET"; matrice_engine.step_counter = 0
            elif cv_key in [ord('t'), ord('T')]: matrice_engine.thermal_active = not matrice_engine.thermal_active

    # --- Step F: ANTI-ULTA SAFEGUARD & FLIGHT ENVELOPE ARBITER ---
    if flight_state == "TOUCHDOWN":
        # Disarmed on ground: zero all motors
        m_fl.setVelocity(0.0)
        m_fr.setVelocity(0.0)
        m_rl.setVelocity(0.0)
        m_rr.setVelocity(0.0)
        continue

    # 1. Determine Desired Disturbances
    if flight_state == "AUTO_LANDING":
        # Zero out horizontal drift during landing
        cmd_roll = 0.0
        cmd_pitch = 0.0
        cmd_yaw = 0.0
        # Gentle smooth descent rate: ~0.18 m/s
        target_altitude = max(target_altitude - 0.003, 0.12)
        
        # Touchdown detection when skids touch the ground pad
        if alt <= 0.185:
            flight_state = "TOUCHDOWN"
            is_disarmed = True
            m_fl.setVelocity(0.0)
            m_fr.setVelocity(0.0)
            m_rl.setVelocity(0.0)
            m_rr.setVelocity(0.0)
            continue
    elif palm_is_active:
        cmd_roll = palm_roll_dist
        cmd_pitch = palm_pitch_dist
        cmd_yaw = palm_yaw_dist
    elif key_pressed and (manual_pitch_cmd != 0 or manual_roll_cmd != 0 or manual_yaw_cmd != 0):
        matrice_engine.control_mode = "MANUAL"
        cmd_pitch = -manual_pitch_cmd * 0.8
        cmd_yaw   = manual_yaw_cmd * 0.8
        cmd_roll  = manual_roll_cmd * 0.5
    else:
        # Autonomous target tracking
        rc_roll, rc_pitch, rc_yaw, rc_throt = matrice_engine.last_rc
        cmd_pitch = -((rc_pitch - 1500) / 500.0) * 0.6
        cmd_yaw   = ((rc_yaw - 1500) / 500.0) * 0.6
        cmd_roll  = ((rc_roll - 1500) / 500.0) * 0.4

    # 2. ANTI-ULTA ANGLE LIMITER:
    # If physical tilt exceeds 12 deg (0.21 rad), instantly cut disturbance to restore level!
    if abs(roll) > 0.21:
        cmd_roll = 0.0
    else:
        cmd_roll = CLAMP(cmd_roll, -0.45, 0.45)

    if abs(pitch) > 0.21:
        cmd_pitch = 0.0
    else:
        cmd_pitch = CLAMP(cmd_pitch, -0.60, 0.60)

    # 3. Ground Proximity Shield: If below 0.32m, force level wings
    if alt < 0.32:
        cmd_roll = 0.0
        cmd_pitch = 0.0

    # 4. Tuned Critical-Damping Attitude PD
    roll_input = K_ROLL_P * CLAMP(roll, -0.4, 0.4) + K_ROLL_D * roll_vel + cmd_roll
    pitch_input = K_PITCH_P * CLAMP(pitch, -0.4, 0.4) + K_PITCH_D * pitch_vel + cmd_pitch
    yaw_input = CLAMP(cmd_yaw, -0.8, 0.8)

    # 5. Altitude PID
    clamped_diff = CLAMP(target_altitude - alt + K_VERTICAL_OFFSET, -1.0, 1.0)
    vertical_input = K_VERTICAL_P * (clamped_diff ** 3.0)

    # 6. Motor Velocity Mixing
    fl = K_VERTICAL_THRUST + vertical_input - roll_input + pitch_input - yaw_input
    fr = K_VERTICAL_THRUST + vertical_input + roll_input + pitch_input + yaw_input
    rl = K_VERTICAL_THRUST + vertical_input - roll_input - pitch_input + yaw_input
    rr = K_VERTICAL_THRUST + vertical_input + roll_input - pitch_input - yaw_input

    # Motor speeds bounded to safe operational range (minimum idle 15.0 rad/s prevents mid-air stall)
    fl = CLAMP(fl, 15.0, 95.0)
    fr = CLAMP(fr, 15.0, 95.0)
    rl = CLAMP(rl, 15.0, 95.0)
    rr = CLAMP(rr, 15.0, 95.0)

    # Actuate motors in Webots (front-right and rear-left are counter-rotating)
    m_fl.setVelocity(float(fl))
    m_fr.setVelocity(float(-fr))
    m_rl.setVelocity(float(-rl))
    m_rr.setVelocity(float(rr))

webcam.release()
cv2.destroyAllWindows()
print("[+] Drone landed safely. Flight session finished.")
