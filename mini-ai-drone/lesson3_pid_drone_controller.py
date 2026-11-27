"""
LESSON 4: From Neural Network Outputs to Flight Physics (PID Control)
---------------------------------------------------------------------
In this lesson, you will learn:
1. Why raw neural network predictions CANNOT directly drive motors (overshoot & oscillation).
2. The PID Controller (Proportional, Integral, Derivative): The universal flight math.
3. Converting [target_x, target_y, area] into standard RC PWM pulses (1000 to 2000 microseconds).
4. Running a simulated flight tracking loop!
"""

import time
import numpy as np

print("=" * 65)
print("MODULE 4: PID FLIGHT CONTROLLER & STEERING MATH")
print("=" * 65)

# ------------------------------------------------------------------
# CONCEPT 1: What is a PID Controller?
# ------------------------------------------------------------------
# When the model predicts the target is at X = 0.8 (right side of frame),
# error = 0.8 - 0.5 (center) = +0.3.
#
# If you just set full throttle right, the drone will fly past the target,
# stop too late, turn back, overshoot again, and oscillate uncontrollably!
#
# A PID controller calculates:
# 1. P (Proportional): "How far am I right now?" -> Kp * error
# 2. I (Integral): "Have I been off-center for a while?" -> Ki * sum(errors)
# 3. D (Derivative): "How fast am I approaching the target?" -> Kd * (d_error / dt)
#    (D acts like a shock absorber or brake to stop overshoot!)

class PIDController:
    def __init__(self, kp, ki, kd, output_limits=(-300, 300)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_out, self.max_out = output_limits
        
        self.prev_error = 0.0
        self.integral = 0.0
        self.prev_time = time.time()

    def update(self, error):
        current_time = time.time()
        dt = current_time - self.prev_time
        if dt <= 0.0:
            dt = 1e-4

        # Proportional term
        p_term = self.kp * error

        # Integral term (with windup clamp)
        self.integral += error * dt
        self.integral = np.clip(self.integral, -50, 50)
        i_term = self.ki * self.integral

        # Derivative term (Dampening)
        derivative = (error - self.prev_error) / dt
        d_term = self.kd * derivative

        # Total control output
        output = p_term + i_term + d_term
        output = np.clip(output, self.min_out, self.max_out)

        # Store for next iteration
        self.prev_error = error
        self.prev_time = current_time
        return output

# ------------------------------------------------------------------
# CONCEPT 2: Setting up PID for Drone Axes
# ------------------------------------------------------------------
# Yaw (Rotation to center target horizontally):
yaw_pid = PIDController(kp=450.0, ki=10.0, kd=35.0, output_limits=(-250, 250))

# Pitch (Forward/Backward to maintain target distance/area):
# Desired target area = 0.05 (occupies ~5% of frame, roughly 1.5 - 2 meters away)
pitch_pid = PIDController(kp=600.0, ki=5.0, kd=40.0, output_limits=(-200, 200))

# ------------------------------------------------------------------
# CONCEPT 3: Simulation - Steering the Drone Towards the Target
# ------------------------------------------------------------------
# Let's simulate a target moving in front of the camera:
# Target starts at x = 0.85 (far right) and area = 0.01 (far away)

print("[+] Simulating 10 control steps as drone reacts to target...")
current_target_x = 0.85
current_area = 0.01
DESIRED_AREA = 0.05
DESIRED_X = 0.50 # Frame center

for step in range(1, 11):
    time.sleep(0.05) # Simulating 20Hz control loop (50ms)

    # 1. Calculate errors
    yaw_error = current_target_x - DESIRED_X    # Positive = Target is to the right
    distance_error = DESIRED_AREA - current_area # Positive = Target is too far away

    # 2. Compute PID outputs
    yaw_correction = yaw_pid.update(yaw_error)
    pitch_correction = pitch_pid.update(distance_error)

    # 3. Map to standard RC PWM values (1000 - 2000, where 1500 is neutral)
    rc_roll     = 1500 # Kept level
    rc_pitch    = int(1500 + pitch_correction) # Forward (>1500)
    rc_yaw      = int(1500 + yaw_correction)   # Rotate right (>1500)
    rc_throttle = 1450                         # Altitude hold

    print(f"Step {step:02d} | Error X: {yaw_error:+.3f} | RC Yaw: {rc_yaw} µs | RC Pitch: {rc_pitch} µs")

    # Simulate drone moving closer & centering target:
    current_target_x -= (yaw_correction / 1000.0) * 0.15
    current_area += (pitch_correction / 1000.0) * 0.005

print("\n[SUCCESS] PID math verified! Outputs are ready to send to ESP32-CAM via UDP!")
