class_name Player
extends CharacterBody3D

@export var walk_speed: float = 4.2
@export var sprint_speed: float = 7.0
@export var crouch_speed: float = 2.2
@export var jump_velocity: float = 5.5
@export var mouse_sensitivity: float = 0.0032
@export var turn_speed: float = 12.0

# Bicycle riding physics parameters
@export var bike_cruise_speed: float = 9.0
@export var bike_sprint_speed: float = 14.5
@export var bike_reverse_speed: float = 2.5
@export var bike_acceleration: float = 11.0
@export var bike_deceleration: float = 8.5
@export var bike_turn_rate: float = 2.4
@export var bike_max_bank_angle: float = deg_to_rad(12.0)
@export var bike_wheel_radius: float = 0.34

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity", 15.0)

var is_crouching: bool = false
var is_sprinting: bool = false
var is_dragging: bool = false

# Bicycle riding state
var is_riding_bicycle: bool = false
var bicycle_visual: Node3D = null
var wheel_front: Node3D = null
var wheel_rear: Node3D = null
var current_bike_ref: Node3D = null

var bike_current_speed: float = 0.0
var bike_heading_angle: float = 0.0
var bike_steer_angle: float = 0.0
var bike_wheel_rot: float = 0.0
var bike_mount_cooldown: float = 0.0

# Interactive mode: tour disabled so player has full direct control from launch
var tour_active: bool = false
var tour_time: float = 0.0

# Dynamic Camera Parameters
@export var base_camera_fov: float = 70.0
@export var max_sprint_fov: float = 77.0
@export var max_bike_fov: float = 84.0
@export var fov_lerp_speed: float = 4.5

var _target_fov: float = 70.0
var _user_zoom_dist: float = 4.4
var _head_bob_timer: float = 0.0
var _prev_visual_yaw: float = 0.0
var _base_cam_pos: Vector3 = Vector3.ZERO

var cam_light: SpotLight3D
var cam_rim_light: OmniLight3D

@onready var visual: Node3D = $Visual
@onready var anim_player: AnimationPlayer = $Visual/character/AnimationPlayer
@onready var camera_pivot: Node3D = $CameraPivot
@onready var spring_arm: SpringArm3D = $CameraPivot/SpringArm3D
@onready var camera: Camera3D = $CameraPivot/SpringArm3D/Camera3D
@onready var collision_shape: CollisionShape3D = $CollisionShape3D

func _ready():
	add_to_group("players")
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	
	# Separate player collision layer from environment
	collision_layer = 2
	collision_mask = 1
	
	# Exclude character from spring arm collision so camera does not collapse to 0 distance!
	spring_arm.add_excluded_object(get_rid())
	spring_arm.collision_mask = 1
	
	# Enable smooth stair & slope climbing in Godot 4
	floor_snap_length = 0.4
	floor_constant_speed = true
	floor_max_angle = deg_to_rad(50.0)
	max_slides = 6
	
	# Initial camera angle & distance: balanced elevation to view player, 112ft Adiyogi and mountain backdrop
	_user_zoom_dist = 4.4
	spring_arm.spring_length = 4.4
	spring_arm.rotation.x = deg_to_rad(10.0)
	spring_arm.margin = 0.12
	if camera:
		_base_cam_pos = camera.position
		camera.fov = base_camera_fov
		camera.near = 0.25
		camera.far = 2500.0
	
	_setup_input_actions()
	_setup_bicycle_visual()
	_setup_animations()
	_setup_camera_lighting()
	
	# Ensure character, avatar root and bone poses are in clean rest state
	var char_node = visual.get_node_or_null("character") if visual else null
	if char_node:
		char_node.rotation_degrees = Vector3.ZERO
		char_node.position = Vector3.ZERO
		var avatar_root = char_node.get_node_or_null("AvatarRoot")
		if avatar_root:
			avatar_root.rotation_degrees = Vector3(90, 0, 0)
			avatar_root.position = Vector3.ZERO
		var skel: Skeleton3D = char_node.get_node_or_null("AvatarRoot/Skeleton3D")
		if skel:
			skel.reset_bone_poses()

func _setup_bicycle_visual():
	var bike_glb = load("res://assets/models/vintage_bicycle_yellow.glb")
	if bike_glb:
		bicycle_visual = bike_glb.instantiate()
		bicycle_visual.name = "Bicycle"
		visual.add_child(bicycle_visual)
		bicycle_visual.visible = false
		wheel_front = bicycle_visual.get_node_or_null("Wheel_Front")
		wheel_rear = bicycle_visual.get_node_or_null("Wheel_Rear")
		print("[Player] Successfully configured dynamic bicycle attachment!")
	else:
		push_error("[Player] Failed to load vintage_bicycle_yellow.glb")

func _setup_camera_lighting():
	# Cinematic camera-linked fill spotlight that follows every camera pan, tilt and orbit
	cam_light = SpotLight3D.new()
	cam_light.name = "CameraCinematicLight"
	cam_light.light_color = Color(0.96, 0.98, 1.0) # Soft daylight fill
	cam_light.light_energy = 0.30
	cam_light.light_specular = 0.0 # Zero specular to prevent ground reflection
	cam_light.spot_range = 45.0
	cam_light.spot_angle = 68.0
	cam_light.spot_attenuation = 1.35
	cam_light.shadow_enabled = false
	camera.add_child(cam_light)
	
	# Character rim light on camera pivot to highlight silhouettes against the sky
	cam_rim_light = OmniLight3D.new()
	cam_rim_light.name = "CameraRimLight"
	cam_rim_light.light_color = Color(0.92, 0.95, 1.0) # Soft daylight sky rim light
	cam_rim_light.light_energy = 0.25
	cam_rim_light.light_specular = 0.0 # Zero specular
	cam_rim_light.omni_range = 10.0
	cam_rim_light.omni_attenuation = 1.5
	cam_rim_light.shadow_enabled = false
	camera_pivot.add_child(cam_rim_light)

func _setup_input_actions():
	_ensure_action("move_forward", [KEY_W, KEY_UP])
	_ensure_action("move_backward", [KEY_S, KEY_DOWN])
	_ensure_action("move_left", [KEY_A, KEY_LEFT])
	_ensure_action("move_right", [KEY_D, KEY_RIGHT])
	_ensure_action("jump", [KEY_SPACE])
	_ensure_action("crouch", [KEY_C, KEY_CTRL])
	_ensure_action("sprint", [KEY_SHIFT])
	_ensure_action("flip_view", [KEY_F, KEY_V])
	_ensure_action("interact_bike", [KEY_E])
	_ensure_action("toggle_bike", [KEY_B])

func _ensure_action(action_name: String, keycodes: Array):
	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name)
	for key in keycodes:
		var ev = InputEventKey.new()
		ev.physical_keycode = key
		InputMap.action_add_event(action_name, ev)

func _setup_animations():
	if not anim_player:
		return
	
	# Dynamically link Bicycle animations into library
	var lib = anim_player.get_animation_library("")
	if lib:
		var pedal_res = load("res://assets/bicycle_pedal.res")
		if pedal_res:
			if lib.has_animation("Bicycle_Pedal"):
				lib.remove_animation("Bicycle_Pedal")
			lib.add_animation("Bicycle_Pedal", pedal_res)
			print("[Player] Registered updated Bicycle_Pedal animation!")
		var coast_res = load("res://assets/bicycle_coast.res")
		if coast_res:
			if lib.has_animation("Bicycle_Coast"):
				lib.remove_animation("Bicycle_Coast")
			lib.add_animation("Bicycle_Coast", coast_res)
			print("[Player] Registered updated Bicycle_Coast animation!")
	
	# Strip horizontal root-motion drift so walk/strafe play cleanly in place
	for anim_name in anim_player.get_animation_list():
		var anim = anim_player.get_animation(anim_name)
		if not "Bicycle" in anim_name:
			_make_in_place(anim)
	
	var loop_anims = ["Idle", "Walk", "Walk_Backwards", "Strafe_Left", "Strafe_Right", "Crouch_Idle", "Crouch_Walk", "Bicycle_Pedal", "Bicycle_Coast"]
	for anim_name in loop_anims:
		if anim_player.has_animation(anim_name):
			anim_player.get_animation(anim_name).loop_mode = Animation.LOOP_LINEAR
	
	if anim_player.has_animation("Jump"):
		anim_player.get_animation("Jump").loop_mode = Animation.LOOP_NONE
	
	anim_player.play("Idle")

func _make_in_place(anim: Animation):
	for i in range(anim.get_track_count()):
		if anim.track_get_type(i) == Animation.TYPE_POSITION_3D and "Hips" in str(anim.track_get_path(i)):
			var key_count = anim.track_get_key_count(i)
			if key_count > 1:
				var k0 = anim.track_get_key_value(i, 0) as Vector3
				var kend = anim.track_get_key_value(i, key_count - 1) as Vector3
				var delta_pos = kend - k0
				var length = anim.length
				for k in range(key_count):
					var t = anim.track_get_key_time(i, k)
					var progress = t / length if length > 0.0 else 0.0
					var cur = anim.track_get_key_value(i, k) as Vector3
					cur.x -= delta_pos.x * progress
					cur.y -= delta_pos.y * progress
					anim.track_set_key_value(i, k, cur)

func capture_screenshot(filename: String):
	await RenderingServer.frame_post_draw
	var vp = get_viewport()
	if vp:
		var tex = vp.get_texture()
		if tex:
			var img = tex.get_image()
			if img:
				var path = ProjectSettings.globalize_path("res://" + filename)
				img.save_png(path)
				print("[Screenshot] Successfully saved: ", path)

func _unhandled_input(event):
	# If player presses any movement key, stop automated tour
	if event is InputEventKey and event.pressed:
		if event.physical_keycode in [KEY_W, KEY_A, KEY_S, KEY_D, KEY_SPACE]:
			tour_active = false
	
	# Click & Drag Mouse detection
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT or event.button_index == MOUSE_BUTTON_RIGHT:
			is_dragging = event.pressed
		
		# Mouse Wheel Zoom
		elif event.button_index == MOUSE_BUTTON_WHEEL_UP and event.pressed:
			var min_dist = 2.0 if is_riding_bicycle else 1.0
			_user_zoom_dist = clamp(_user_zoom_dist - 0.35, min_dist, 8.5)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN and event.pressed:
			var min_dist = 2.0 if is_riding_bicycle else 1.0
			_user_zoom_dist = clamp(_user_zoom_dist + 0.35, min_dist, 8.5)
	
	# Orbit Camera when dragging or when mouse is captured
	if event is InputEventMouseMotion:
		if is_dragging or Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			camera_pivot.rotate_y(-event.relative.x * mouse_sensitivity)
			spring_arm.rotate_x(-event.relative.y * mouse_sensitivity)
			spring_arm.rotation.x = clamp(spring_arm.rotation.x, deg_to_rad(-60.0), deg_to_rad(65.0))
	
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_F or event.physical_keycode == KEY_V:
			camera_pivot.rotation.y += PI
		
		# Fast-travel shortcuts to explore the vast sacred complex
		if event.physical_keycode == KEY_1:
			global_position = Vector3(0.0, 0.2, 55.0)
			velocity = Vector3.ZERO
			print("[Player] Fast-travel to Adiyogi Courtyard (Key 1)")
		elif event.physical_keycode == KEY_2:
			global_position = Vector3(-409.30, 0.2, -560.0)
			velocity = Vector3.ZERO
			print("[Player] Fast-travel to Suryakund Complex on Mud Terrain (Key 2)")
		elif event.physical_keycode == KEY_3:
			global_position = Vector3(0.0, 0.2, 545.0)
			velocity = Vector3.ZERO
			print("[Player] Fast-travel to Malai Vasal Monumental Gate (Key 3)")

		if event.physical_keycode == KEY_ESCAPE:
			if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
				Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
			else:
				Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		
		# Bicycle mount/dismount shortcut keys
		if event.physical_keycode == KEY_B:
			get_viewport().set_input_as_handled()
			toggle_bicycle()
		elif event.physical_keycode == KEY_E and bike_mount_cooldown <= 0.0:
			if is_riding_bicycle:
				get_viewport().set_input_as_handled()
				dismount_bicycle()
			elif is_inside_tree():
				var bikes = get_tree().get_nodes_in_group("bicycles")
				for b in bikes:
					if b is Node3D and is_instance_valid(b) and ("is_parked" in b and b.is_parked) and global_position.distance_to(b.global_position) <= 3.0:
						get_viewport().set_input_as_handled()
						if b.has_method("mount_by_player"):
							b.mount_by_player(self)
						else:
							mount_bicycle(b)
						break

func toggle_bicycle():
	if is_riding_bicycle:
		dismount_bicycle()
	else:
		mount_bicycle()

func mount_bicycle(bike_ref: Node3D = null):
	if is_riding_bicycle:
		return
	is_riding_bicycle = true
	bike_mount_cooldown = 0.4
	current_bike_ref = bike_ref
	if not current_bike_ref and is_inside_tree():
		var bikes = get_tree().get_nodes_in_group("bicycles")
		if bikes.size() > 0:
			current_bike_ref = bikes[0]
	
	if current_bike_ref and is_instance_valid(current_bike_ref):
		global_position = current_bike_ref.global_position
		bike_heading_angle = current_bike_ref.global_rotation.y
		current_bike_ref.visible = false
		if "is_parked" in current_bike_ref:
			current_bike_ref.is_parked = false
	else:
		bike_heading_angle = wrapf(visual.rotation.y - PI, -PI, PI) if visual else 0.0
	
	if visual:
		visual.rotation.y = bike_heading_angle
		visual.rotation.z = 0.0
	
	if bicycle_visual:
		bicycle_visual.visible = true
	
	# Seat character facing forward on bicycle saddle
	var char_node = visual.get_node_or_null("character") if visual else null
	if char_node:
		char_node.rotation_degrees = Vector3(0, 180, 0)
		char_node.position = Vector3(0, -0.14, 0.11)
		var avatar_root = char_node.get_node_or_null("AvatarRoot")
		if avatar_root:
			avatar_root.rotation_degrees = Vector3(90, 0, 0)
			avatar_root.position = Vector3.ZERO
	
	bike_current_speed = 0.0
	bike_steer_angle = 0.0
	
	# Widen camera view for dynamic vehicle perspective
	_user_zoom_dist = 5.2
	_play_anim("Bicycle_Coast", 0.15)
	print("[Player] Mounted bicycle! Riding enabled.")

func dismount_bicycle():
	if not is_riding_bicycle:
		return
	is_riding_bicycle = false
	bike_mount_cooldown = 0.4
	bike_current_speed = 0.0
	velocity = Vector3.ZERO
	
	if bicycle_visual:
		bicycle_visual.visible = false
	
	var park_heading = bike_heading_angle
	if visual:
		visual.rotation.y = wrapf(park_heading + PI, -PI, PI)
		visual.rotation.z = 0.0
	_user_zoom_dist = 4.4
	if anim_player:
		anim_player.speed_scale = 1.0
	
	# Restore character node and avatar root transforms
	var char_node = visual.get_node_or_null("character") if visual else null
	if char_node:
		char_node.rotation_degrees = Vector3.ZERO
		char_node.position = Vector3.ZERO
		var avatar_root = char_node.get_node_or_null("AvatarRoot")
		if avatar_root:
			avatar_root.rotation_degrees = Vector3(90, 0, 0)
			avatar_root.position = Vector3.ZERO
		var skel: Skeleton3D = char_node.get_node_or_null("AvatarRoot/Skeleton3D")
		if skel:
			skel.reset_bone_poses()
	
	# Park bicycle in world at current location
	var park_transform = Transform3D(Basis(Vector3.UP, park_heading), global_position)
	if current_bike_ref and is_instance_valid(current_bike_ref):
		if current_bike_ref.has_method("park_at"):
			current_bike_ref.park_at(park_transform)
		else:
			current_bike_ref.global_transform = park_transform
			current_bike_ref.visible = true
		current_bike_ref = null
	elif is_inside_tree():
		var bikes = get_tree().get_nodes_in_group("bicycles")
		if bikes.size() > 0:
			var b = bikes[0]
			if b and is_instance_valid(b) and b.has_method("park_at"):
				b.park_at(park_transform)
	
	# Step 0.85m to the left of the bike
	var left_dir = Vector3(-cos(park_heading), 0.0, sin(park_heading))
	global_position += left_dir * 0.85
	
	_play_anim("Idle", 0.1)
	print("[Player] Dismounted bicycle! Parked in world.")

func _physics_process(delta):
	tour_time += delta
	if bike_mount_cooldown > 0.0:
		bike_mount_cooldown -= delta
	
	# Dynamic camera light adaptation with camera pitch and movement
	if cam_light:
		var pitch = spring_arm.rotation.x
		var pitch_clamped = clamp(pitch, deg_to_rad(-20.0), deg_to_rad(45.0))
		var norm_pitch = (pitch_clamped - deg_to_rad(-20.0)) / (deg_to_rad(45.0) - deg_to_rad(-20.0))
		var t_range = lerp(34.0, 65.0, norm_pitch)
		var t_energy = lerp(0.65, 0.95, norm_pitch)
		cam_light.spot_range = lerp(cam_light.spot_range, t_range, delta * 6.0)
		cam_light.light_energy = lerp(cam_light.light_energy, t_energy, delta * 6.0)
	
	if is_riding_bicycle:
		_physics_process_bicycle(delta)
	else:
		_physics_process_walking(delta)
	
	# AAA Dynamic Camera System: dynamic FOV, banking on turns, velocity pushback & head-bob/vibration
	_process_dynamic_camera(delta)

func _process_dynamic_camera(delta: float):
	if not camera or not spring_arm:
		return
	
	# 1. Dynamic Velocity-Based FOV Expansion
	var h_vel = Vector2(velocity.x, velocity.z).length()
	var fov_target = base_camera_fov
	if is_riding_bicycle:
		var bike_ratio = clamp(abs(bike_current_speed) / bike_sprint_speed, 0.0, 1.0)
		fov_target = lerp(base_camera_fov + 2.0, max_bike_fov, bike_ratio)
	else:
		var walk_ratio = clamp(h_vel / sprint_speed, 0.0, 1.0)
		if is_crouching:
			fov_target = base_camera_fov - 3.0
		else:
			fov_target = lerp(base_camera_fov, max_sprint_fov, walk_ratio)
	
	# Slight FOV breathing when airborne/falling
	if not is_on_floor():
		fov_target += clamp(abs(velocity.y) * 0.45, 0.0, 3.0)
	
	camera.fov = lerp(camera.fov, fov_target, delta * fov_lerp_speed)
	
	# 2. Dynamic Follow Distance (Speed Pushback & SpringArm Smoothing)
	var speed_dist_add = 0.0
	if is_riding_bicycle:
		speed_dist_add = clamp(abs(bike_current_speed) / bike_sprint_speed, 0.0, 1.0) * 0.85
	else:
		speed_dist_add = clamp(h_vel / sprint_speed, 0.0, 1.0) * 0.45
	var target_len = _user_zoom_dist + speed_dist_add
	spring_arm.spring_length = lerp(spring_arm.spring_length, target_len, delta * 3.5)
	
	# 3. Dynamic Camera Banking / Roll Lean on Turns
	var target_roll = 0.0
	if is_riding_bicycle:
		var steer_ratio = clamp(abs(bike_current_speed) / 5.0, 0.0, 1.0)
		target_roll = -bike_steer_angle * 0.22 * steer_ratio
	else:
		if visual:
			var cur_yaw = visual.rotation.y
			var yaw_delta = wrapf(cur_yaw - _prev_visual_yaw, -PI, PI)
			_prev_visual_yaw = cur_yaw
			target_roll = clamp(-yaw_delta * 0.35, deg_to_rad(-3.0), deg_to_rad(3.0))
	camera.rotation.z = lerp_angle(camera.rotation.z, target_roll, delta * 5.0)
	
	# 4. Dynamic Head Bob & Surface Vibration
	var bob_x = 0.0
	var bob_y = 0.0
	if is_riding_bicycle:
		var bike_spd = abs(bike_current_speed)
		if bike_spd > 0.3:
			bob_y = sin(tour_time * 26.0) * 0.007 * clamp(bike_spd / 8.0, 0.1, 1.0)
			bob_x = cos(tour_time * 13.0) * 0.004 * clamp(bike_spd / 8.0, 0.1, 1.0)
	else:
		if is_on_floor() and h_vel > 0.2:
			var stride_speed = (h_vel / walk_speed) * 8.5
			_head_bob_timer += delta * stride_speed
			var bob_intensity = clamp(h_vel / sprint_speed, 0.25, 1.0)
			bob_y = sin(_head_bob_timer) * 0.025 * bob_intensity
			bob_x = cos(_head_bob_timer * 0.5) * 0.015 * bob_intensity
		else:
			# Gentle resting breathing bob
			bob_y = sin(tour_time * 1.6) * 0.005
	
	camera.position = lerp(camera.position, _base_cam_pos + Vector3(bob_x, bob_y, 0.0), delta * 8.0)

func _physics_process_bicycle(delta: float):
	# Gravity & ground contact
	if not is_on_floor():
		velocity.y -= gravity * delta
	else:
		velocity.y = 0.0
	
	# Inputs
	var forward_input = 0.0
	var steer_input = 0.0
	if Input.is_action_pressed("move_forward"): forward_input += 1.0
	if Input.is_action_pressed("move_backward"): forward_input -= 1.0
	if Input.is_action_pressed("move_left"): steer_input += 1.0
	if Input.is_action_pressed("move_right"): steer_input -= 1.0
	
	is_sprinting = Input.is_action_pressed("sprint")
	
	# Speed acceleration & braking
	if forward_input > 0.0:
		var target_top = bike_sprint_speed if is_sprinting else bike_cruise_speed
		bike_current_speed = move_toward(bike_current_speed, target_top, bike_acceleration * delta)
	elif forward_input < 0.0:
		if bike_current_speed > 0.8:
			# Braking
			bike_current_speed = move_toward(bike_current_speed, 0.0, bike_acceleration * 1.8 * delta)
		else:
			# Reverse backpedal
			bike_current_speed = move_toward(bike_current_speed, -bike_reverse_speed, bike_acceleration * 0.6 * delta)
	else:
		# Freewheel coasting friction
		bike_current_speed = move_toward(bike_current_speed, 0.0, bike_deceleration * 0.35 * delta)
	
	# Steering heading
	var speed_abs = abs(bike_current_speed)
	var steer_efficiency = clamp(speed_abs / 3.0, 0.25, 1.0)
	var active_steer = steer_input
	if bike_current_speed < 0.0:
		active_steer = -active_steer
	bike_heading_angle += active_steer * bike_turn_rate * steer_efficiency * delta
	
	# Handlebar visual steering
	var target_steer = steer_input * deg_to_rad(24.0)
	bike_steer_angle = lerp(bike_steer_angle, target_steer, delta * 10.0)
	
	# Physical wheel pitch rolling
	bike_wheel_rot -= (bike_current_speed * delta) / bike_wheel_radius
	if wheel_front:
		wheel_front.rotation = Vector3(bike_wheel_rot, bike_steer_angle, 0.0)
	if wheel_rear:
		wheel_rear.rotation = Vector3(bike_wheel_rot, 0.0, 0.0)
	
	# Visual orientation with authentic corner banking
	visual.rotation.y = bike_heading_angle
	var target_bank = -steer_input * bike_max_bank_angle * clamp(speed_abs / bike_cruise_speed, 0.0, 1.0)
	visual.rotation.z = lerp_angle(visual.rotation.z, target_bank, delta * 6.5)
	
	# Forward velocity
	var fwd = -Vector3(sin(bike_heading_angle), 0.0, cos(bike_heading_angle)).normalized()
	velocity.x = fwd.x * bike_current_speed
	velocity.z = fwd.z * bike_current_speed
	
	move_and_slide()
	
	# Dynamic camera following heading smoothly when not manually orbiting
	if not is_dragging and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		camera_pivot.rotation.y = lerp_angle(camera_pivot.rotation.y, bike_heading_angle, delta * 3.5)
	
	# Cycling animation state
	if bike_current_speed > 0.2 and forward_input > 0.0:
		_play_anim("Bicycle_Pedal", 0.15)
		anim_player.speed_scale = clamp(bike_current_speed / 6.0, 0.6, 2.2)
	else:
		_play_anim("Bicycle_Coast", 0.2)
		anim_player.speed_scale = 1.0

func _physics_process_walking(delta: float):
	# Crouch toggle
	if Input.is_action_just_pressed("crouch"):
		is_crouching = not is_crouching
		_update_crouch_collider()
	
	is_sprinting = Input.is_action_pressed("sprint") and not is_crouching
	
	# Gravity & Jump
	if not is_on_floor():
		velocity.y -= gravity * delta
	else:
		if Input.is_action_just_pressed("jump") and not is_crouching:
			velocity.y = jump_velocity
	
	# Movement input
	var forward_input = 0.0
	var right_input = 0.0
	if Input.is_action_pressed("move_forward"): forward_input += 1.0
	if Input.is_action_pressed("move_backward"): forward_input -= 1.0
	if Input.is_action_pressed("move_right"): right_input += 1.0
	if Input.is_action_pressed("move_left"): right_input -= 1.0
	
	# If tour is active and no manual input, walk forward up the stairs towards Adiyogi
	if tour_active and forward_input == 0.0 and right_input == 0.0:
		if global_position.z > 14.0:
			forward_input = 1.0
			is_sprinting = true
		else:
			tour_active = false
	
	var cam_yaw = camera_pivot.global_rotation.y
	var cam_fwd = -Vector3(sin(cam_yaw), 0.0, cos(cam_yaw)).normalized()
	var cam_right = Vector3(cos(cam_yaw), 0.0, -sin(cam_yaw)).normalized()
	
	var move_vector = Vector2(right_input, forward_input)
	if move_vector.length_squared() > 1.0:
		move_vector = move_vector.normalized()
	
	var move_dir = (cam_fwd * move_vector.y + cam_right * move_vector.x)
	
	var speed = walk_speed
	if is_crouching:
		speed = crouch_speed
	elif is_sprinting and forward_input > 0.0:
		speed = sprint_speed
	
	if move_dir.length_squared() > 0.001:
		velocity.x = move_dir.x * speed
		velocity.z = move_dir.z * speed
		var target_angle = atan2(move_dir.x, move_dir.z)
		visual.rotation.y = lerp_angle(visual.rotation.y, target_angle, delta * turn_speed)
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed * delta * 10.0)
		velocity.z = move_toward(velocity.z, 0.0, speed * delta * 10.0)
	
	move_and_slide()
	_update_animation(move_dir)

func _update_crouch_collider():
	if collision_shape and collision_shape.shape is CapsuleShape3D:
		var capsule = collision_shape.shape as CapsuleShape3D
		if is_crouching:
			capsule.height = 1.1
			collision_shape.position.y = 0.55
		else:
			capsule.height = 1.8
			collision_shape.position.y = 0.9

func _update_animation(move_dir: Vector3):
	if not anim_player:
		return
	
	var is_moving = (move_dir.length_squared() > 0.001) and (Vector2(velocity.x, velocity.z).length() > 0.15)
	
	if not is_on_floor():
		_play_anim("Jump", 0.12)
	elif is_crouching:
		if is_moving:
			_play_anim("Crouch_Walk", 0.2)
		else:
			_play_anim("Crouch_Idle", 0.2)
	else:
		if is_moving:
			_play_anim("Walk", 0.2)
		else:
			_play_anim("Idle", 0.2)

func _play_anim(anim_name: String, blend_time: float = 0.2):
	if anim_player and anim_player.current_animation != anim_name:
		if anim_player.has_animation(anim_name):
			anim_player.play(anim_name, blend_time)
