class_name Bicycle
extends Node3D

@export var is_parked: bool = true

@onready var model: Node3D = $Model
@onready var interact_area: Area3D = $InteractArea
@onready var prompt_label: Label3D = $PromptLabel
@onready var wheel_front: Node3D = $Model/Wheel_Front
@onready var wheel_rear: Node3D = $Model/Wheel_Rear

var player_in_range: Node = null
var wheel_rot: float = 0.0

func _ready():
	add_to_group("bicycles")
	if prompt_label:
		prompt_label.visible = false
	
	if interact_area:
		interact_area.body_entered.connect(_on_body_entered)
		interact_area.body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node):
	if body.has_method("mount_bicycle"):
		player_in_range = body
		if prompt_label:
			prompt_label.visible = true

func _on_body_exited(body: Node):
	if body == player_in_range:
		player_in_range = null
		if prompt_label:
			prompt_label.visible = false

func _process(_delta: float):
	if not is_parked:
		if prompt_label and prompt_label.visible:
			prompt_label.visible = false
		return
	
	# Keep prompt visibility accurate based on player proximity
	if player_in_range and is_instance_valid(player_in_range):
		if prompt_label and not prompt_label.visible:
			prompt_label.visible = true
	else:
		var players = get_tree().get_nodes_in_group("players")
		if players.size() > 0:
			var p = players[0]
			if p is Node3D and global_position.distance_to(p.global_position) <= 2.8:
				player_in_range = p
				if prompt_label and not prompt_label.visible:
					prompt_label.visible = true
			else:
				if prompt_label and prompt_label.visible:
					prompt_label.visible = false

func _unhandled_input(event: InputEvent):
	if not is_parked:
		return
	if not player_in_range or not is_instance_valid(player_in_range):
		var players = get_tree().get_nodes_in_group("players")
		if players.size() > 0:
			var p = players[0]
			if p is Node3D and global_position.distance_to(p.global_position) <= 2.8:
				player_in_range = p
	if not player_in_range:
		return
	
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_E:
			get_viewport().set_input_as_handled()
			mount_by_player(player_in_range)

func mount_by_player(player_node: Node):
	if not is_parked:
		return
	is_parked = false
	if prompt_label:
		prompt_label.visible = false
	visible = false
	player_node.mount_bicycle(self)

func park_at(new_transform: Transform3D):
	global_transform = new_transform
	is_parked = true
	visible = true
	# Slight kickstand lean (3.5 deg)
	rotation.z = deg_to_rad(3.5)
	if prompt_label:
		prompt_label.visible = false

