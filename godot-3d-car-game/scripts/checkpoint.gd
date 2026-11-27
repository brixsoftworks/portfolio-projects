extends Area3D
class_name Checkpoint

@export var checkpoint_index: int = 0
@export var is_finish_line: bool = false

func _ready() -> void:
    body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node3D) -> void:
    if body.has_method("apply_speed_boost"): 
        var race_mgr := get_node_or_null("/root/MainGame/RaceManager")
        if race_mgr and race_mgr.has_method("on_checkpoint_passed"):
            race_mgr.on_checkpoint_passed(self, body)
