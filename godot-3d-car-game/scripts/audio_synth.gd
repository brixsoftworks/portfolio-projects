extends Node


static var instance: Node

var engine_player: AudioStreamPlayer
var skid_player: AudioStreamPlayer
var nitro_player: AudioStreamPlayer
var sfx_player: AudioStreamPlayer

var sample_rate: int = 22050

func _init() -> void:
    instance = self

func _ready() -> void:
    engine_player = AudioStreamPlayer.new()
    skid_player = AudioStreamPlayer.new()
    nitro_player = AudioStreamPlayer.new()
    sfx_player = AudioStreamPlayer.new()

    add_child(engine_player)
    add_child(skid_player)
    add_child(nitro_player)
    add_child(sfx_player)

    _setup_engine_audio()
    _setup_skid_audio()
    _setup_nitro_audio()

func _generate_wav(samples: Array, mix_rate: int, loop: bool = false) -> AudioStreamWAV:
    var wav := AudioStreamWAV.new()
    wav.format = AudioStreamWAV.FORMAT_16_BITS
    wav.mix_rate = mix_rate
    if loop:
        wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
        wav.loop_begin = 0
        wav.loop_end = samples.size()

    var byte_array := PackedByteArray()
    byte_array.resize(samples.size() * 2)
    for i in range(samples.size()):
        var s: float = clampf(samples[i], -1.0, 1.0)
        var val: int = int(s * 31000.0)
        byte_array.encode_s16(i * 2, val)
    wav.data = byte_array
    return wav

func _setup_engine_audio() -> void:
    # 0.4 seconds looping harmonic engine wave
    var duration := 0.4
    var count := int(sample_rate * duration)
    var samples := []
    samples.resize(count)
    var f0 := 65.0 # Low rumble fundamental frequency
    for i in range(count):
        var t := float(i) / float(sample_rate)
        # Rich engine harmonics (fundamental + 2nd, 3rd, 4th harmonics + slight distortion)
        var wave := 0.45 * sin(2.0 * PI * f0 * t)
        wave += 0.30 * sin(2.0 * PI * f0 * 2.0 * t)
        wave += 0.15 * sin(2.0 * PI * f0 * 3.0 * t)
        wave += 0.10 * sin(2.0 * PI * f0 * 4.0 * t)
        # Add slight cylinder pulse saturation
        samples[i] = tanh(wave * 1.5)

    engine_player.stream = _generate_wav(samples, sample_rate, true)
    engine_player.volume_db = -10.0
    engine_player.pitch_scale = 0.85
    engine_player.play()

func _setup_skid_audio() -> void:
    # 0.5s looping noise with resonant bandpass
    var duration := 0.5
    var count := int(sample_rate * duration)
    var samples := []
    samples.resize(count)
    var prev := 0.0
    for i in range(count):
        var noise := randf_range(-1.0, 1.0)
        # Lowpass smoothing for tire screech
        prev = prev * 0.75 + noise * 0.25
        samples[i] = prev * 0.8

    skid_player.stream = _generate_wav(samples, sample_rate, true)
    skid_player.volume_db = -80.0 # Muted initially
    skid_player.play()

func _setup_nitro_audio() -> void:
    # Looping roar/hiss
    var duration := 0.6
    var count := int(sample_rate * duration)
    var samples := []
    samples.resize(count)
    for i in range(count):
        var t := float(i) / float(sample_rate)
        var noise := randf_range(-0.5, 0.5)
        var tone := sin(2.0 * PI * 180.0 * t) * 0.3
        samples[i] = (noise + tone) * 0.8

    nitro_player.stream = _generate_wav(samples, sample_rate, true)
    nitro_player.volume_db = -80.0
    nitro_player.play()

func update_car_sound(speed_ratio: float, is_drifting: float, is_boosting: bool) -> void:
    # Engine pitch scales with speed: 0.7 at idle to 2.4 at max speed
    var target_pitch := lerpf(0.75, 2.3, clampf(speed_ratio, 0.0, 1.0))
    if is_boosting:
        target_pitch *= 1.2
    engine_player.pitch_scale = lerpf(engine_player.pitch_scale, target_pitch, 0.15)

    # Skid volume
    if is_drifting > 0.15:
        var target_skid_db := lerpf(-24.0, -4.0, clampf(is_drifting, 0.0, 1.0))
        skid_player.volume_db = lerpf(skid_player.volume_db, target_skid_db, 0.25)
    else:
        skid_player.volume_db = lerpf(skid_player.volume_db, -80.0, 0.3)

    # Nitro volume
    if is_boosting:
        nitro_player.volume_db = lerpf(nitro_player.volume_db, -6.0, 0.3)
    else:
        nitro_player.volume_db = lerpf(nitro_player.volume_db, -80.0, 0.3)

func play_checkpoint() -> void:
    # Ascending high chimes (587Hz -> 880Hz)
    var count := int(sample_rate * 0.3)
    var samples := []
    samples.resize(count)
    for i in range(count):
        var t := float(i) / float(sample_rate)
        var freq := 587.0 if t < 0.15 else 880.0
        var env := 1.0 - (t / 0.3)
        samples[i] = sin(2.0 * PI * freq * t) * env * 0.6
    sfx_player.stream = _generate_wav(samples, sample_rate, false)
    sfx_player.volume_db = -4.0
    sfx_player.play()

func play_coin() -> void:
    # Crisp high-frequency coin blip (987Hz -> 1318Hz)
    var count := int(sample_rate * 0.2)
    var samples := []
    samples.resize(count)
    for i in range(count):
        var t := float(i) / float(sample_rate)
        var freq := 987.0 if t < 0.1 else 1318.0
        var env := (1.0 - (t / 0.2)) * (1.0 - (t / 0.2))
        samples[i] = sin(2.0 * PI * freq * t) * env * 0.5
    sfx_player.stream = _generate_wav(samples, sample_rate, false)
    sfx_player.volume_db = -6.0
    sfx_player.play()

func play_boost_pad() -> void:
    # Swoosh up effect (200Hz sweep up to 900Hz)
    var count := int(sample_rate * 0.35)
    var samples := []
    samples.resize(count)
    for i in range(count):
        var t := float(i) / float(sample_rate)
        var freq := lerpf(200.0, 900.0, t / 0.35)
        var env := sin(PI * (t / 0.35))
        samples[i] = sin(2.0 * PI * freq * t) * env * 0.7
    sfx_player.stream = _generate_wav(samples, sample_rate, false)
    sfx_player.volume_db = -5.0
    sfx_player.play()

func play_countdown_beep(is_go: bool) -> void:
    var count := int(sample_rate * (0.4 if is_go else 0.25))
    var samples := []
    samples.resize(count)
    var freq := 880.0 if is_go else 440.0
    for i in range(count):
        var t := float(i) / float(sample_rate)
        var env := 1.0 - (t / (0.4 if is_go else 0.25))
        samples[i] = sin(2.0 * PI * freq * t) * env * 0.7
    sfx_player.stream = _generate_wav(samples, sample_rate, false)
    sfx_player.volume_db = -3.0
    sfx_player.play()

func play_finish() -> void:
    # Victory arpeggio (C5 -> E5 -> G5 -> C6)
    var count := int(sample_rate * 1.0)
    var samples := []
    samples.resize(count)
    var notes := [523.25, 659.25, 783.99, 1046.50]
    for i in range(count):
        var t := float(i) / float(sample_rate)
        var note_idx := clampi(int(t / 0.2), 0, 3)
        var freq: float = notes[note_idx]
        var env := 1.0 - (t / 1.0)
        samples[i] = sin(2.0 * PI * freq * t) * env * 0.7
    sfx_player.stream = _generate_wav(samples, sample_rate, false)
    sfx_player.volume_db = -2.0
    sfx_player.play()
