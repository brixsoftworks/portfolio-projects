extends Area3D

enum Type { COIN, NITRO, BOOST_PAD }
@export var item_type: Type = Type.COIN
@export var value: int = 250

var is_active: bool = true
var respawn_timer: float = 0.0

@onready var visual_mesh: Node3D = get_node_or_null("MeshInstance3D")

func _get_sound() -> Node:
    return get_node_or_null("/root/SoundManager")

func _ready() -> void:
    body_entered.connect(_on_body_entered)

func _process(delta: float) -> void:
    if not is_active:
        respawn_timer -= delta
        if respawn_timer <= 0.0:
            is_active = true
            visible = true
        return

    # Idle bobbing and spinning
    if visual_mesh and item_type != Type.BOOST_PAD:
        visual_mesh.rotate_y(2.5 * delta)
        visual_mesh.position.y = sin(Time.get_ticks_msec() * 0.004) * 0.15 + 0.8

func _on_body_entered(body: Node3D) -> void:
    if not is_active:
        return

    if not body.has_method("apply_speed_boost"):
        return

    var snd = _get_sound()

    match item_type:
        Type.COIN:
            if snd and snd.has_method("play_coin"):
                snd.play_coin()
            var race_mgr := get_node_or_null("/root/MainGame/RaceManager")
            if race_mgr and race_mgr.has_method("add_score"):
                race_mgr.add_score(value)
            _consume(8.0)

        Type.NITRO:
            if snd and snd.has_method("play_checkpoint"):
                snd.play_checkpoint()
            if body.has_method("add_nitro"):
                body.add_nitro(45.0)
            _consume(10.0)

        Type.BOOST_PAD:
            body.apply_speed_boost(1.4, 2.2)

func _consume(respawn_time: float) -> void:
    is_active = false
    visible = false
    respawn_timer = respawn_time
