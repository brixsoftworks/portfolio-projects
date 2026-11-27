extends CharacterBody3D
class_name CarController

signal speed_changed(kmh: float, speed_ratio: float)
signal nitro_changed(current: float, maximum: float)
signal drift_started()
signal drift_updated(score: int, multiplier: float)
signal drift_ended(final_score: int)
signal car_model_changed(car_name: String)

@export var max_speed: float = 38.0
@export var boost_speed: float = 54.0
@export var reverse_speed: float = 14.0
@export var acceleration: float = 24.0
@export var boost_acceleration: float = 50.0
@export var brake_strength: float = 34.0
@export var natural_drag: float = 6.0
@export var turn_speed: float = 2.8
@export var gravity: float = 28.0

@export var nitro_drain: float = 30.0
@export var nitro_recharge: float = 9.0

var current_forward_speed: float = 0.0
var lateral_velocity: Vector3 = Vector3.ZERO
var steer_angle: float = 0.0
var visual_steer: float = 0.0
var wheel_roll: float = 0.0

# Drift system
var is_drifting: bool = false
var drift_duration: float = 0.0
var current_drift_score: int = 0
var drift_boost_timer: float = 0.0

# Nitro system
var nitro: float = 100.0
var max_nitro: float = 100.0
var is_boosting: bool = false

# Visual nodes
@onready var visual_root: Node3D = $Visuals
@onready var smoke_left: CPUParticles3D = $SmokeLeft
@onready var smoke_right: CPUParticles3D = $SmokeRight
@onready var nitro_flame: CPUParticles3D = $NitroFlame

var current_car_index: int = 0
var car_nodes: Array[Node3D] = []
var car_names: Array[String] = [
    "Neon GT Supercar",
    "Cyber Future Racer",
    "Sports Turbo Sedan",
    "Police Interceptor"
]

# Wheel references for active car
var active_front_left_wheel: Node3D
var active_front_right_wheel: Node3D
var active_back_left_wheel: Node3D
var active_back_right_wheel: Node3D
var active_body: Node3D

# Respawn tracking
var last_checkpoint_transform: Transform3D

func _ready() -> void:
    last_checkpoint_transform = global_transform
    _setup_car_models()
    select_car(current_car_index)

func _get_visual_root() -> Node3D:
    if visual_root:
        return visual_root
    visual_root = get_node_or_null("Visuals")
    return visual_root

func _setup_car_models() -> void:
    car_nodes.clear()
    var v = _get_visual_root()
    if v:
        for child in v.get_children():
            if child is Node3D:
                car_nodes.append(child)

func select_car(index: int) -> void:
    if car_nodes.is_empty():
        _setup_car_models()
    if car_nodes.is_empty():
        return
    current_car_index = posmod(index, car_nodes.size())
    for i in range(car_nodes.size()):
        car_nodes[i].visible = (i == current_car_index)
        if i == current_car_index:
            _bind_wheel_references(car_nodes[i])
    car_model_changed.emit(car_names[current_car_index])

func _bind_wheel_references(car_node: Node3D) -> void:
    active_front_left_wheel = null
    active_front_right_wheel = null
    active_back_left_wheel = null
    active_back_right_wheel = null
    active_body = null

    for child in car_node.get_children():
        var lower_name: String = child.name.to_lower()
        if "wheel" in lower_name and "front" in lower_name and "left" in lower_name:
            active_front_left_wheel = child
        elif "wheel" in lower_name and "front" in lower_name and "right" in lower_name:
            active_front_right_wheel = child
        elif "wheel" in lower_name and "back" in lower_name and "left" in lower_name:
            active_back_left_wheel = child
        elif "wheel" in lower_name and "back" in lower_name and "right" in lower_name:
            active_back_right_wheel = child
        elif "body" in lower_name:
            active_body = child

func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        match event.keycode:
            KEY_1: select_car(0)
            KEY_2: select_car(1)
            KEY_3: select_car(2)
            KEY_4: select_car(3)
            KEY_R: respawn_at_checkpoint()
            KEY_T:
                var hud = get_node_or_null("/root/MainGame/HUD")
                if hud and hud.has_method("toggle_track_menu"):
                    hud.toggle_track_menu()
            KEY_BRACKETLEFT:
                var tm = get_node_or_null("/root/MainGame/TrackManager")
                if tm and tm.has_method("prev_track"):
                    tm.prev_track()
            KEY_BRACKETRIGHT:
                var tm = get_node_or_null("/root/MainGame/TrackManager")
                if tm and tm.has_method("next_track"):
                    tm.next_track()

func _physics_process(delta: float) -> void:
    # 1. Inputs
    var throttle: float = 0.0
    if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP) or Input.is_action_pressed("ui_up"):
        throttle += 1.0
    if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN) or Input.is_action_pressed("ui_down"):
        throttle -= 1.0

    var steer_input: float = 0.0
    if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT) or Input.is_action_pressed("ui_left"):
        steer_input += 1.0
    if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT) or Input.is_action_pressed("ui_right"):
        steer_input -= 1.0

    var handbrake: bool = Input.is_key_pressed(KEY_SPACE)
    var boost_pressed: bool = (Input.is_key_pressed(KEY_SHIFT) or drift_boost_timer > 0.0)

    # 2. Nitro Handling
    if boost_pressed and nitro > 5.0 and throttle > 0.0:
        is_boosting = true
        nitro = maxf(0.0, nitro - nitro_drain * delta)
    else:
        is_boosting = false
        nitro = minf(max_nitro, nitro + nitro_recharge * delta)

    if drift_boost_timer > 0.0:
        drift_boost_timer -= delta
        is_boosting = true

    nitro_changed.emit(nitro, max_nitro)

    # 3. Acceleration & Speed Limits
    var effective_max: float = boost_speed if is_boosting else max_speed
    var effective_accel: float = boost_acceleration if is_boosting else acceleration

    if throttle > 0.0:
        if current_forward_speed < 0.0:
            current_forward_speed = move_toward(current_forward_speed, 0.0, brake_strength * delta)
        else:
            current_forward_speed = move_toward(current_forward_speed, effective_max, effective_accel * delta)
    elif throttle < 0.0:
        if current_forward_speed > 0.0:
            current_forward_speed = move_toward(current_forward_speed, 0.0, brake_strength * delta)
        else:
            current_forward_speed = move_toward(current_forward_speed, -reverse_speed, acceleration * 0.7 * delta)
    else:
        current_forward_speed = move_toward(current_forward_speed, 0.0, natural_drag * delta)

    # 4. Steering & Drift Dynamics
    var speed_ratio: float = absf(current_forward_speed) / max_speed
    var steer_speed_factor: float = clampf(1.0 - (speed_ratio * 0.45), 0.35, 1.0)
    
    var wants_drift: bool = handbrake or (speed_ratio > 0.4 and absf(steer_input) > 0.7)
    if is_on_floor() and wants_drift and speed_ratio > 0.25:
        if not is_drifting:
            is_drifting = true
            current_drift_score = 0
            drift_duration = 0.0
            drift_started.emit()
    else:
        if is_drifting:
            is_drifting = false
            if drift_duration > 1.2:
                # Award mini turbo boost for good drift!
                drift_boost_timer = 1.6
                var sound = get_node_or_null("/root/SoundManager")
                if sound and sound.has_method("play_boost_pad"):
                    sound.play_boost_pad()
            drift_ended.emit(current_drift_score)

    var drift_turn_mult: float = 1.45 if is_drifting else 1.0
    var turn_amount: float = steer_input * turn_speed * steer_speed_factor * drift_turn_mult * delta

    if absf(current_forward_speed) > 0.5:
        var direction_sign: float = signf(current_forward_speed)
        rotate_y(turn_amount * direction_sign)

    # 5. Drift Physics & Lateral Grip
    var forward_dir: Vector3 = -global_transform.basis.z.normalized()
    var right_dir: Vector3 = global_transform.basis.x.normalized()
    
    var grip_ratio: float = 0.90 if is_drifting else 0.98
    var forward_vel: Vector3 = forward_dir * current_forward_speed
    lateral_velocity = lateral_velocity.lerp(Vector3.ZERO, grip_ratio * delta * 12.0)
    
    if is_drifting:
        var drift_slip: float = steer_input * current_forward_speed * 0.35
        lateral_velocity += right_dir * drift_slip * delta * 5.0
        drift_duration += delta
        var multiplier: float = 1.0 + clampf(drift_duration * 0.5, 0.0, 4.0)
        current_drift_score += int(absf(current_forward_speed) * 12.0 * delta * multiplier)
        drift_updated.emit(current_drift_score, multiplier)

    # 6. Apply Movement Velocity
    var h_velocity: Vector3 = forward_vel + lateral_velocity
    velocity.x = h_velocity.x
    velocity.z = h_velocity.z

    if not is_on_floor():
        velocity.y -= gravity * delta
    else:
        velocity.y = -1.0 # Keep grounded smoothly

    move_and_slide()

    # 7. Visual Animations (Steering, Wheel Spin, Chassis Tilt, Particles)
    _animate_visuals(steer_input, delta)

    # 8. Signals & Audio
    var speed_kmh: float = absf(current_forward_speed) * 3.6
    speed_changed.emit(speed_kmh, speed_ratio)

    var sound = get_node_or_null("/root/SoundManager")
    if sound and sound.has_method("update_car_sound"):
        var drift_intensity: float = 1.0 if is_drifting else (0.4 if handbrake else 0.0)
        sound.update_car_sound(speed_ratio, drift_intensity, is_boosting)

func _animate_visuals(steer_input: float, delta: float) -> void:
    # Wheel steering
    visual_steer = lerpf(visual_steer, steer_input * 0.48, delta * 12.0)
    if active_front_left_wheel:
        active_front_left_wheel.rotation.y = visual_steer
    if active_front_right_wheel:
        active_front_right_wheel.rotation.y = visual_steer

    # Wheel spin (around X axis)
    wheel_roll += current_forward_speed * delta * 3.5
    for w in [active_front_left_wheel, active_front_right_wheel, active_back_left_wheel, active_back_right_wheel]:
        if w:
            w.rotation.x = wheel_roll

    # Chassis lean / suspension tilt
    if active_body:
        var target_roll: float = -steer_input * clampf(absf(current_forward_speed) / max_speed, 0.0, 1.0) * 0.08
        var target_pitch: float = 0.0
        if current_forward_speed > 2.0:
            target_pitch = 0.03 if is_boosting else 0.015
        elif current_forward_speed < -1.0:
            target_pitch = -0.03
        active_body.rotation.z = lerpf(active_body.rotation.z, target_roll, delta * 10.0)
        active_body.rotation.x = lerpf(active_body.rotation.x, target_pitch, delta * 8.0)

    # Particle emissions
    var emit_smoke: bool = (is_drifting or (Input.is_key_pressed(KEY_SPACE) and absf(current_forward_speed) > 5.0))
    if smoke_left:
        smoke_left.emitting = emit_smoke
    if smoke_right:
        smoke_right.emitting = emit_smoke
    if nitro_flame:
        nitro_flame.emitting = is_boosting

func apply_speed_boost(multiplier: float = 1.4, duration: float = 2.0) -> void:
    drift_boost_timer = maxf(drift_boost_timer, duration)
    nitro = minf(max_nitro, nitro + 40.0)
    current_forward_speed = maxf(current_forward_speed * multiplier, boost_speed * 0.9)
    var sound = get_node_or_null("/root/SoundManager")
    if sound and sound.has_method("play_boost_pad"):
        sound.play_boost_pad()

func add_nitro(amount: float) -> void:
    nitro = minf(max_nitro, nitro + amount)
    nitro_changed.emit(nitro, max_nitro)

func respawn_at_checkpoint() -> void:
    current_forward_speed = 0.0
    lateral_velocity = Vector3.ZERO
    velocity = Vector3.ZERO
    global_transform = last_checkpoint_transform
    # Slightly lift above road to avoid getting stuck in geometry
    global_position.y += 0.8
