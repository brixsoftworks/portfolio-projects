import bpy
import math
from mathutils import Vector, Euler, Quaternion

print("=== STARTING ACCURATE CYCLING ANIMATION BAKING ===")

# Reset Blender
bpy.ops.wm.read_factory_settings(use_empty=True)

# 1. Import Bicycle for exact geometry alignment
bpy.ops.import_scene.gltf(filepath='/home/mullainathan/Games/IshaGodot/assets/models/vintage_bicycle_yellow.glb')

# 2. Import Character (AvatarRoot)
bpy.ops.import_scene.gltf(filepath='/home/mullainathan/Games/IshaGodot/assets/character.glb')

arm = bpy.data.objects['AvatarRoot']
if arm.animation_data:
    arm.animation_data.action = None

# Reset all pose bones to clean rest pose
for pb in arm.pose.bones:
    pb.location = Vector((0, 0, 0))
    pb.rotation_quaternion = Quaternion((1, 0, 0, 0))
    pb.rotation_euler = Euler((0, 0, 0))
bpy.context.view_layer.update()

def make_empty(name, loc):
    emp = bpy.data.objects.new(name, None)
    emp.empty_display_type = 'SPHERE'
    emp.empty_display_size = 0.04
    emp.location = loc
    bpy.context.scene.collection.objects.link(emp)
    return emp

# Bicycle kinematic constants
Y_BB = 0.093   # Bottom bracket forward pos in meters
Z_BB = 0.321   # Bottom bracket height in meters
R_CRANK = 0.165 # Crank arm radius in meters
X_PEDAL = 0.135 # Half tread width (pedal lateral distance from bike center)

# Handlebar grip positions (X=+0.23 is left, X=-0.23 is right)
GRIP_L = Vector((0.23, 0.38, 0.96))
GRIP_R = Vector((-0.23, 0.38, 0.96))

# Saddle position
SADDLE_POS = Vector((0.0, -0.18, 0.81))

# Create IK Targets
r_pedal = make_empty("IK_R_Foot", Vector((-X_PEDAL, Y_BB, Z_BB + R_CRANK)))
l_pedal = make_empty("IK_L_Foot", Vector((X_PEDAL, Y_BB, Z_BB - R_CRANK)))

r_grip = make_empty("IK_R_Hand", GRIP_R)
l_grip = make_empty("IK_L_Hand", GRIP_L)

r_knee_pole = make_empty("Pole_R_Leg", Vector((-0.18, 0.45, 0.50)))
l_knee_pole = make_empty("Pole_L_Leg", Vector((0.18, 0.45, 0.30)))

r_elbow_pole = make_empty("Pole_R_Arm", Vector((-0.45, 0.15, 1.15)))
l_elbow_pole = make_empty("Pole_L_Arm", Vector((0.45, 0.15, 1.15)))

# Attach 2-chain IK constraints
c_l_foot = arm.pose.bones['LeftFoot'].constraints.new('IK')
c_l_foot.target = l_pedal
c_l_foot.pole_target = l_knee_pole
c_l_foot.chain_count = 2

c_r_foot = arm.pose.bones['RightFoot'].constraints.new('IK')
c_r_foot.target = r_pedal
c_r_foot.pole_target = r_knee_pole
c_r_foot.chain_count = 2

c_l_hand = arm.pose.bones['LeftHand'].constraints.new('IK')
c_l_hand.target = l_grip
c_l_hand.pole_target = l_elbow_pole
c_l_hand.chain_count = 2

c_r_hand = arm.pose.bones['RightHand'].constraints.new('IK')
c_r_hand.target = r_grip
c_r_hand.pole_target = r_elbow_pole
c_r_hand.chain_count = 2

# Wrist and hand grip orientation
pb_l_hand = arm.pose.bones['LeftHand']
pb_r_hand = arm.pose.bones['RightHand']
pb_l_hand.rotation_mode = 'XYZ'
pb_r_hand.rotation_mode = 'XYZ'
pb_l_hand.rotation_euler = Euler((math.radians(-25), math.radians(20), math.radians(-15)))
pb_r_hand.rotation_euler = Euler((math.radians(-25), math.radians(-20), math.radians(15)))

# Natural finger curling around the handlebars
for side in ['Left', 'Right']:
    for f in ['Index', 'Middle', 'Ring', 'Pinky']:
        for seg in ['1', '2', '3']:
            bn = f"{side}Hand{f}{seg}"
            if bn in arm.pose.bones:
                arm.pose.bones[bn].rotation_mode = 'XYZ'
                arm.pose.bones[bn].rotation_euler = Euler((math.radians(45), 0, 0))
    # Thumb curls across the underside
    for seg in ['1', '2']:
        bn = f"{side}HandThumb{seg}"
        if bn in arm.pose.bones:
            arm.pose.bones[bn].rotation_mode = 'XYZ'
            arm.pose.bones[bn].rotation_euler = Euler((math.radians(25), 0, math.radians(20)))

# Spine and posture bones
pb_hips = arm.pose.bones['Hips']
pb_spine = arm.pose.bones['Spine']
pb_spine1 = arm.pose.bones['Spine1']
pb_neck = arm.pose.bones['Neck']
pb_head = arm.pose.bones['Head']

pb_spine.rotation_mode = 'XYZ'
pb_spine1.rotation_mode = 'XYZ'
pb_neck.rotation_mode = 'XYZ'
pb_head.rotation_mode = 'XYZ'

# Base translation to sit on saddle
hips_rest_local = pb_hips.bone.head_local
hips_target_local = arm.matrix_world.inverted() @ SADDLE_POS
base_hips_loc = hips_target_local - hips_rest_local

TOTAL_FRAMES = 60 # 60 frames @ 30fps = 2.0s per revolution

# --- 1. KEYFRAME BICYCLE_PEDAL (Seamless loop) ---
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = TOTAL_FRAMES

for frame in range(TOTAL_FRAMES + 1):
    bpy.context.scene.frame_set(frame)
    theta = 2.0 * math.pi * (frame / float(TOTAL_FRAMES))
    
    # Right pedal circular trajectory (clockwise looking from right side)
    # At theta = 0: right pedal is forward/top (at 2 o'clock, power stroke onset)
    r_y = Y_BB + R_CRANK * math.sin(theta + 0.35)
    r_z = Z_BB + R_CRANK * math.cos(theta + 0.35)
    
    # Left pedal is 180 degrees opposite
    l_y = Y_BB - R_CRANK * math.sin(theta + 0.35)
    l_z = Z_BB - R_CRANK * math.cos(theta + 0.35)
    
    r_pedal.location = Vector((-X_PEDAL, r_y, r_z))
    l_pedal.location = Vector((X_PEDAL, l_y, l_z))
    
    r_pedal.keyframe_insert(data_path="location", frame=frame)
    l_pedal.keyframe_insert(data_path="location", frame=frame)
    
    # Knee pole targets tracking forward
    r_knee_pole.location = Vector((-0.18, r_y + 0.32, max(r_z + 0.16, 0.42)))
    l_knee_pole.location = Vector((0.18, l_y + 0.32, max(l_z + 0.16, 0.42)))
    r_knee_pole.keyframe_insert(data_path="location", frame=frame)
    l_knee_pole.keyframe_insert(data_path="location", frame=frame)
    
    # Hips cadence sway and subtle bob
    sway_x = 0.007 * math.sin(theta)
    bob_z = 0.002 * math.cos(2.0 * theta)
    pb_hips.location = base_hips_loc + Vector((sway_x, 0.0, bob_z))
    pb_hips.keyframe_insert(data_path="location", frame=frame)
    
    # Torso lean and gentle cadence counter-roll
    sway_roll = math.radians(1.2 * math.sin(theta))
    pb_spine.rotation_euler = Euler((math.radians(-24), sway_roll, 0))
    pb_spine1.rotation_euler = Euler((math.radians(-16), sway_roll * 0.5, 0))
    pb_neck.rotation_euler = Euler((math.radians(26), -sway_roll * 0.7, 0))
    pb_head.rotation_euler = Euler((math.radians(12), -sway_roll * 0.5, 0))
    
    pb_spine.keyframe_insert(data_path="rotation_euler", frame=frame)
    pb_spine1.keyframe_insert(data_path="rotation_euler", frame=frame)
    pb_neck.keyframe_insert(data_path="rotation_euler", frame=frame)
    pb_head.keyframe_insert(data_path="rotation_euler", frame=frame)

print("Baking Bicycle_Pedal pose action...")
bpy.ops.nla.bake(
    frame_start=0,
    frame_end=TOTAL_FRAMES,
    only_selected=False,
    visual_keying=True,
    clear_constraints=False,
    bake_types={'POSE'}
)

pedal_action = arm.animation_data.action
pedal_action.name = "Bicycle_Pedal"
pedal_action.use_fake_user = True
print("Bicycle_Pedal baked successfully! Frame range:", pedal_action.frame_range)


# --- 2. KEYFRAME BICYCLE_COAST (Resting pose: right foot forward, left foot back) ---
arm.animation_data.action = None

r_pedal.animation_data_clear()
l_pedal.animation_data_clear()
r_knee_pole.animation_data_clear()
l_knee_pole.animation_data_clear()

# Coasting crank angle: Right foot forward at 3 o'clock (horizontal resting)
theta_coast = math.pi / 2.0
r_y = Y_BB + R_CRANK * math.sin(theta_coast)
r_z = Z_BB + R_CRANK * math.cos(theta_coast)
l_y = Y_BB - R_CRANK * math.sin(theta_coast)
l_z = Z_BB - R_CRANK * math.cos(theta_coast)

r_pedal.location = Vector((-X_PEDAL, r_y, r_z))
l_pedal.location = Vector((X_PEDAL, l_y, l_z))

r_knee_pole.location = Vector((-0.18, r_y + 0.32, 0.44))
l_knee_pole.location = Vector((0.18, l_y + 0.32, 0.44))

pb_hips.location = base_hips_loc
pb_spine.rotation_euler = Euler((math.radians(-24), 0, 0))
pb_spine1.rotation_euler = Euler((math.radians(-16), 0, 0))
pb_neck.rotation_euler = Euler((math.radians(26), 0, 0))
pb_head.rotation_euler = Euler((math.radians(12), 0, 0))

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 30

for f in range(31):
    bpy.context.scene.frame_set(f)
    r_pedal.keyframe_insert(data_path="location", frame=f)
    l_pedal.keyframe_insert(data_path="location", frame=f)
    r_knee_pole.keyframe_insert(data_path="location", frame=f)
    l_knee_pole.keyframe_insert(data_path="location", frame=f)
    pb_hips.keyframe_insert(data_path="location", frame=f)
    pb_spine.keyframe_insert(data_path="rotation_euler", frame=f)
    pb_spine1.keyframe_insert(data_path="rotation_euler", frame=f)
    pb_neck.keyframe_insert(data_path="rotation_euler", frame=f)
    pb_head.keyframe_insert(data_path="rotation_euler", frame=f)

print("Baking Bicycle_Coast pose action...")
bpy.ops.nla.bake(
    frame_start=0,
    frame_end=30,
    only_selected=False,
    visual_keying=True,
    clear_constraints=False,
    bake_types={'POSE'}
)

coast_action = arm.animation_data.action
coast_action.name = "Bicycle_Coast"
coast_action.use_fake_user = True
print("Bicycle_Coast baked successfully! Frame range:", coast_action.frame_range)

# Clean up empty constraint objects
for obj in [r_pedal, l_pedal, r_grip, l_grip, r_knee_pole, l_knee_pole, r_elbow_pole, l_elbow_pole]:
    bpy.data.objects.remove(obj, do_unlink=True)

# Remove the temporary bicycle model before character export
for obj in list(bpy.data.objects):
    if "rama" in obj.name.lower() or "wheel" in obj.name.lower() or "bicycle" in obj.name.lower():
        bpy.data.objects.remove(obj, do_unlink=True)

# Remove constraints from pose bones
for pb in arm.pose.bones:
    for c in list(pb.constraints):
        pb.constraints.remove(c)

# Ensure all 12 animations are saved in the file
actions_to_export = [
    "Idle", "Walk", "Walk_Backwards", "Strafe_Left", "Strafe_Right",
    "Jump", "Crouch_Idle", "Crouch_Walk", "Walk_Turn",
    "Bicycle_Pedal", "Bicycle_Coast"
]
print("Exporting character with actions:", [a.name for a in bpy.data.actions])

out_glb = '/home/mullainathan/Games/IshaGodot/assets/character_biking.glb'
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    use_selection=False,
    export_animation_mode='ACTIONS'
)
print("Saved full character to:", out_glb)
