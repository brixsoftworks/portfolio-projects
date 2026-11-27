extends Camera3D
class_name ChaseCamera

@export var target: Node3D
@export var follow_speed: float = 8.5
@export var rotation_speed: float = 6.0

enum ViewMode { CHASE, FAR, BUMPER }
var current_mode: ViewMode = ViewMode.CHASE

var base_fov: float = 72.0
var boost_fov: float = 88.0

var offsets: Dictionary = {
    ViewMode.CHASE: Vector3(0.0, 2.3, 5.5),
    ViewMode.FAR: Vector3(0.0, 4.2, 8.5),
    ViewMode.BUMPER: Vector3(0.0, 1.15, -0.4)
}

func _ready() -> void:
    current_mode = ViewMode.CHASE
    fov = base_fov

func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_C:
            cycle_view()

func cycle_view() -> void:
    match current_mode:
        ViewMode.CHASE: current_mode = ViewMode.FAR
        ViewMode.FAR: current_mode = ViewMode.BUMPER
        ViewMode.BUMPER: current_mode = ViewMode.CHASE

func _physics_process(delta: float) -> void:
    if not target:
        return

    var car_controller = target
    var speed_ratio: float = 0.0
    var is_boosting: bool = false
    if car_controller:
        speed_ratio = clampf(absf(car_controller.current_forward_speed) / car_controller.max_speed, 0.0, 1.3)
        is_boosting = car_controller.is_boosting

    # Dynamic FOV
    var target_fov: float = boost_fov if is_boosting else lerpf(base_fov, 80.0, speed_ratio)
    fov = lerpf(fov, target_fov, delta * 6.0)

    # Desired position
    var local_offset: Vector3 = offsets[current_mode]
    var desired_pos: Vector3 = target.global_position + (target.global_transform.basis * local_offset)

    if current_mode == ViewMode.BUMPER:
        global_position = desired_pos
        global_transform.basis = target.global_transform.basis
    else:
        # Smooth interpolation
        global_position = global_position.lerp(desired_pos, delta * follow_speed)
        
        # Look ahead target
        var forward_dir: Vector3 = -target.global_transform.basis.z.normalized()
        var look_target: Vector3 = target.global_position + forward_dir * 4.0 + Vector3(0, 1.0, 0)
        
        var current_transform := global_transform
        var target_transform := current_transform.looking_at(look_target, Vector3.UP)
        global_transform.basis = global_transform.basis.slerp(target_transform.basis, delta * rotation_speed)
