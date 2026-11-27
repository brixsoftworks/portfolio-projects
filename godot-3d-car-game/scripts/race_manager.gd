extends Node

signal countdown_updated(text: String)
signal lap_updated(current: int, total: int)
signal time_updated(current_time: float, best_time: float)
signal checkpoint_updated(current: int, total: int)
signal score_updated(total: int)
signal race_finished(results: Dictionary)

enum RaceState { COUNTDOWN, RACING, FINISHED }
var state: RaceState = RaceState.COUNTDOWN

@export var total_laps: int = 3
@export var total_checkpoints: int = 8
var current_lap: int = 1
var next_checkpoint: int = 1 # 0 is start/finish

var countdown_timer: float = 3.5
var current_lap_time: float = 0.0
var best_lap_time: float = 99999.0
var total_race_time: float = 0.0

var total_score: int = 0
var drift_score: int = 0
var coins_count: int = 0

var sound_go_played: bool = false
var last_countdown_sec: int = 4

var car_ref: Node

func _get_sound() -> Node:
    return get_node_or_null("/root/SoundManager")

func _ready() -> void:
    car_ref = get_node_or_null("/root/MainGame/PlayerCar")
    if car_ref and car_ref.has_signal("drift_ended"):
        car_ref.connect("drift_ended", _on_drift_ended)
    _start_countdown()

func _start_countdown() -> void:
    state = RaceState.COUNTDOWN
    countdown_timer = 3.99

func _process(delta: float) -> void:
    if state == RaceState.COUNTDOWN:
        countdown_timer -= delta
        if countdown_timer > 3.0:
            countdown_updated.emit("3")
        elif countdown_timer > 2.0:
            countdown_updated.emit("2")
        elif countdown_timer > 1.0:
            countdown_updated.emit("1")
        elif countdown_timer > 0.0:
            countdown_updated.emit("GO!")
            var snd = _get_sound()
            if snd and not sound_go_played and snd.has_method("play_countdown_beep"):
                snd.play_countdown_beep(true)
                sound_go_played = true
        else:
            state = RaceState.RACING
            countdown_updated.emit("")
            lap_updated.emit(current_lap, total_laps)
            checkpoint_updated.emit(0, total_checkpoints)

    elif state == RaceState.RACING:
        current_lap_time += delta
        total_race_time += delta
        time_updated.emit(current_lap_time, best_lap_time)

func on_checkpoint_passed(checkpoint: Area3D, car: Node) -> void:
    if state != RaceState.RACING:
        return

    if "last_checkpoint_transform" in car:
        car.last_checkpoint_transform = checkpoint.global_transform

    var is_finish: bool = checkpoint.get("is_finish_line")
    var cp_idx: int = checkpoint.get("checkpoint_index")

    if is_finish:
        if next_checkpoint >= total_checkpoints:
            _on_lap_completed()
    else:
        if cp_idx == next_checkpoint:
            var snd = _get_sound()
            if snd and snd.has_method("play_checkpoint"):
                snd.play_checkpoint()
            next_checkpoint += 1
            checkpoint_updated.emit(next_checkpoint, total_checkpoints)
            add_score(150)

func _on_lap_completed() -> void:
    var is_best: bool = (current_lap_time < best_lap_time)
    if is_best:
        best_lap_time = current_lap_time

    var snd = _get_sound()
    if snd and snd.has_method("play_finish"):
        snd.play_finish()

    add_score(1000)

    if current_lap >= total_laps:
        _finish_race()
    else:
        current_lap += 1
        next_checkpoint = 1
        current_lap_time = 0.0
        lap_updated.emit(current_lap, total_laps)
        checkpoint_updated.emit(0, total_checkpoints)

func _finish_race() -> void:
    state = RaceState.FINISHED
    var results := {
        "total_time": total_race_time,
        "best_lap": best_lap_time,
        "total_score": total_score + drift_score,
        "drift_score": drift_score,
        "coins": coins_count
    }
    race_finished.emit(results)
    var snd = _get_sound()
    if snd and snd.has_method("play_finish"):
        snd.play_finish()

func add_score(amount: int) -> void:
    total_score += amount
    coins_count += 1
    score_updated.emit(total_score + drift_score)

func _on_drift_ended(score: int) -> void:
    drift_score += score
    score_updated.emit(total_score + drift_score)

func format_time(seconds: float) -> String:
    if seconds >= 99990.0:
        return "--:--.--"
    var mins := int(seconds / 60.0)
    var secs := int(seconds) % 60
    var msecs := int((seconds - int(seconds)) * 100.0)
    return "%02d:%02d.%02d" % [mins, secs, msecs]
