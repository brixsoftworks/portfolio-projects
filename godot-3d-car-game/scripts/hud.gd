extends Control

var speed_label: Label
var speed_bar: ProgressBar
var nitro_bar: ProgressBar
var lap_label: Label
var time_label: Label
var best_label: Label
var score_label: Label
var sector_label: Label
var car_name_label: Label

var countdown_label: Label
var drift_panel: Control
var drift_label: Label

var victory_panel: Control
var victory_time: Label
var victory_best: Label
var victory_score: Label
var restart_button: Button

var race_mgr: Node
var car_controller: Node
var track_mgr: Node

# Track Selection UI elements
var track_name_label: Label
var track_select_button: Button
var track_modal: PanelContainer
var track_search_input: LineEdit
var track_list_container: VBoxContainer
var track_loading_overlay: PanelContainer
var track_loading_label: Label
var all_tracks_cache: Array = []

func _ready() -> void:
	speed_label = find_child("SpeedValue", true, false) as Label
	speed_bar = find_child("SpeedBar", true, false) as ProgressBar
	nitro_bar = find_child("NitroBar", true, false) as ProgressBar
	lap_label = find_child("LapLabel", true, false) as Label
	time_label = find_child("TimeLabel", true, false) as Label
	best_label = find_child("BestLabel", true, false) as Label
	score_label = find_child("ScoreLabel", true, false) as Label
	sector_label = find_child("SectorLabel", true, false) as Label
	car_name_label = find_child("CarNameLabel", true, false) as Label

	countdown_label = find_child("CountdownLabel", true, false) as Label
	drift_panel = find_child("DriftContainer", true, false) as Control
	drift_label = find_child("DriftLabel", true, false) as Label

	victory_panel = find_child("VictoryOverlay", true, false) as Control
	victory_time = find_child("TimeResult", true, false) as Label
	victory_best = find_child("BestResult", true, false) as Label
	victory_score = find_child("ScoreResult", true, false) as Label
	restart_button = find_child("RestartBtn", true, false) as Button

	if drift_panel:
		drift_panel.visible = false
	if victory_panel:
		victory_panel.visible = false
	if restart_button:
		restart_button.pressed.connect(_on_restart_pressed)

	race_mgr = get_node_or_null("/root/MainGame/RaceManager")
	car_controller = get_node_or_null("/root/MainGame/PlayerCar")
	track_mgr = get_node_or_null("/root/MainGame/TrackManager")

	if car_controller:
		if car_controller.has_signal("speed_changed"):
			car_controller.connect("speed_changed", _on_speed_changed)
		if car_controller.has_signal("nitro_changed"):
			car_controller.connect("nitro_changed", _on_nitro_changed)
		if car_controller.has_signal("drift_started"):
			car_controller.connect("drift_started", _on_drift_started)
		if car_controller.has_signal("drift_updated"):
			car_controller.connect("drift_updated", _on_drift_updated)
		if car_controller.has_signal("drift_ended"):
			car_controller.connect("drift_ended", _on_drift_ended)
		if car_controller.has_signal("car_model_changed"):
			car_controller.connect("car_model_changed", _on_car_model_changed)
			_on_car_model_changed(car_controller.car_names[car_controller.current_car_index])

	if race_mgr:
		if race_mgr.has_signal("countdown_updated"):
			race_mgr.connect("countdown_updated", _on_countdown_updated)
		if race_mgr.has_signal("lap_updated"):
			race_mgr.connect("lap_updated", _on_lap_updated)
		if race_mgr.has_signal("time_updated"):
			race_mgr.connect("time_updated", _on_time_updated)
		if race_mgr.has_signal("checkpoint_updated"):
			race_mgr.connect("checkpoint_updated", _on_checkpoint_updated)
		if race_mgr.has_signal("score_updated"):
			race_mgr.connect("score_updated", _on_score_updated)
		if race_mgr.has_signal("race_finished"):
			race_mgr.connect("race_finished", _on_race_finished)

	_build_track_ui()

	if track_mgr:
		if track_mgr.has_signal("track_load_started"):
			track_mgr.connect("track_load_started", _on_track_load_started)
		if track_mgr.has_signal("track_loaded"):
			track_mgr.connect("track_loaded", _on_track_loaded)
		if track_mgr.has_signal("track_list_ready"):
			track_mgr.connect("track_list_ready", _on_track_list_ready)
		if track_mgr.has_method("refresh_track_catalog"):
			track_mgr.refresh_track_catalog()

func _build_track_ui() -> void:
	# 1. Add Track info in BottomBar
	var bottom_bar = find_child("BottomBar", true, false)
	if bottom_bar:
		var track_hbox = HBoxContainer.new()
		track_hbox.name = "TrackHBox"
		
		track_name_label = Label.new()
		track_name_label.name = "TrackNameLabel"
		track_name_label.text = "TRACK: Grand Prix Arena (Original)"
		track_name_label.add_theme_font_size_override("font_size", 18)
		track_name_label.add_theme_color_override("font_color", Color(1.0, 0.85, 0.3))
		track_hbox.add_child(track_name_label)
		
		track_select_button = Button.new()
		track_select_button.name = "SelectTrackButton"
		track_select_button.text = "SELECT TRACK [T]"
		track_select_button.custom_minimum_size = Vector2(160, 28)
		track_select_button.pressed.connect(toggle_track_menu)
		track_hbox.add_child(track_select_button)
		
		bottom_bar.add_child(track_hbox)
		bottom_bar.move_child(track_hbox, 1)

	# 2. Build Track Selector Modal
	track_modal = PanelContainer.new()
	track_modal.name = "TrackModal"
	track_modal.anchors_preset = PRESET_CENTER
	track_modal.anchor_left = 0.5
	track_modal.anchor_top = 0.5
	track_modal.anchor_right = 0.5
	track_modal.anchor_bottom = 0.5
	track_modal.offset_left = -340.0
	track_modal.offset_top = -260.0
	track_modal.offset_right = 340.0
	track_modal.offset_bottom = 260.0
	track_modal.visible = false

	var modal_box = VBoxContainer.new()
	modal_box.set("theme_override_constants/separation", 10)
	
	# Header
	var header_bar = HBoxContainer.new()
	var title = Label.new()
	title.text = "RACETRACK SELECTOR"
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title.add_theme_font_size_override("font_size", 22)
	title.add_theme_color_override("font_color", Color(0.2, 0.8, 1.0))
	header_bar.add_child(title)
	
	var close_btn = Button.new()
	close_btn.text = " [X] "
	close_btn.pressed.connect(func(): track_modal.visible = false)
	header_bar.add_child(close_btn)
	modal_box.add_child(header_bar)

	var sub_info = Label.new()
	sub_info.text = "Choose from 41 Real-World Circuits (Hotkeys: [T] menu, [ / ] cycle tracks)"
	sub_info.add_theme_font_size_override("font_size", 13)
	sub_info.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7))
	modal_box.add_child(sub_info)

	# Search input
	track_search_input = LineEdit.new()
	track_search_input.placeholder_text = " Search circuits (e.g. Monza, Nurburgring, Zolder, Spa)..."
	track_search_input.text_changed.connect(_on_search_text_changed)
	modal_box.add_child(track_search_input)

	# Scroll Container for Tracks
	var scroll = ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(660, 370)
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL

	track_list_container = VBoxContainer.new()
	track_list_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	track_list_container.set("theme_override_constants/separation", 6)
	scroll.add_child(track_list_container)
	modal_box.add_child(scroll)

	track_modal.add_child(modal_box)
	add_child(track_modal)

	# 3. Loading Indicator Overlay
	track_loading_overlay = PanelContainer.new()
	track_loading_overlay.anchors_preset = PRESET_CENTER
	track_loading_overlay.anchor_left = 0.5
	track_loading_overlay.anchor_top = 0.5
	track_loading_overlay.anchor_right = 0.5
	track_loading_overlay.anchor_bottom = 0.5
	track_loading_overlay.offset_left = -250.0
	track_loading_overlay.offset_top = -60.0
	track_loading_overlay.offset_right = 250.0
	track_loading_overlay.offset_bottom = 60.0
	track_loading_overlay.visible = false

	var load_vbox = VBoxContainer.new()
	load_vbox.alignment = BoxContainer.ALIGNMENT_CENTER
	track_loading_label = Label.new()
	track_loading_label.text = "⏳ Loading Circuit..."
	track_loading_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	track_loading_label.add_theme_font_size_override("font_size", 22)
	track_loading_label.add_theme_color_override("font_color", Color(1.0, 0.8, 0.2))
	load_vbox.add_child(track_loading_label)

	var sub_load = Label.new()
	sub_load.text = "Generating 3D Trimesh Collisions & Positioning Car..."
	sub_load.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub_load.add_theme_font_size_override("font_size", 14)
	load_vbox.add_child(sub_load)

	track_loading_overlay.add_child(load_vbox)
	add_child(track_loading_overlay)

func toggle_track_menu() -> void:
	if not track_modal:
		return
	track_modal.visible = not track_modal.visible
	if track_modal.visible and track_mgr and track_mgr.has_method("refresh_track_catalog"):
		track_mgr.refresh_track_catalog()
		if track_search_input:
			track_search_input.grab_focus()

func _on_search_text_changed(query: String) -> void:
	_populate_track_buttons(query)

func _on_track_list_ready(tracks: Array) -> void:
	all_tracks_cache = tracks
	var query = track_search_input.text if track_search_input else ""
	_populate_track_buttons(query)

func _populate_track_buttons(filter_query: String = "") -> void:
	if not track_list_container:
		return
	
	for child in track_list_container.get_children():
		child.queue_free()

	var q = filter_query.strip_edges().to_lower()
	var current_idx = track_mgr.current_track_index if track_mgr else 0

	for t in all_tracks_cache:
		var name: String = t.get("name", "Unknown Track")
		var author: String = t.get("author", "Sketchfab")
		var idx: int = t.get("id", 0)
		var is_cur: bool = (idx == current_idx)

		if q != "" and not q in name.to_lower() and not q in author.to_lower():
			continue

		var btn = Button.new()
		btn.custom_minimum_size = Vector2(0, 48)
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		
		var prefix = "* [ACTIVE] " if is_cur else "▶ "
		btn.text = "%s%s  (by %s)" % [prefix, name, author]
		
		if is_cur:
			btn.add_theme_color_override("font_color", Color(0.3, 1.0, 0.4))
		
		btn.pressed.connect(func():
			if track_mgr and track_mgr.has_method("load_track"):
				track_modal.visible = false
				track_mgr.load_track(idx)
		)
		track_list_container.add_child(btn)

func _on_track_load_started(track_name: String) -> void:
	if track_loading_overlay and track_loading_label:
		track_loading_label.text = "⏳ Loading: " + track_name
		track_loading_overlay.visible = true

func _on_track_loaded(track_info: Dictionary) -> void:
	if track_loading_overlay:
		track_loading_overlay.visible = false
	if track_name_label:
		var name = track_info.get("name", "Grand Prix Arena")
		track_name_label.text = "TRACK: " + name
	_populate_track_buttons(track_search_input.text if track_search_input else "")

func _on_speed_changed(kmh: float, speed_ratio: float) -> void:
	if speed_label:
		speed_label.text = str(int(kmh))
	if speed_bar:
		speed_bar.value = speed_ratio * 100.0

func _on_nitro_changed(current: float, maximum: float) -> void:
	if nitro_bar:
		nitro_bar.value = (current / maximum) * 100.0

func _on_drift_started() -> void:
	if drift_panel:
		drift_panel.visible = true
	if drift_label:
		drift_label.text = "DRIFT!"

func _on_drift_updated(score: int, multiplier: float) -> void:
	if drift_panel:
		drift_panel.visible = true
	if drift_label:
		drift_label.text = "DRIFT! +%d (x%.1f)" % [score, multiplier]

func _on_drift_ended(final_score: int) -> void:
	if not drift_label or not drift_panel:
		return
	if final_score > 0:
		drift_label.text = "NICE DRIFT! +%d" % final_score
		var tween := create_tween()
		tween.tween_interval(1.0)
		tween.tween_callback(func(): drift_panel.visible = false)
	else:
		drift_panel.visible = false

func _on_countdown_updated(text: String) -> void:
	if countdown_label:
		countdown_label.text = text
		countdown_label.visible = (text != "")

func _on_lap_updated(current: int, total: int) -> void:
	if lap_label:
		lap_label.text = "LAP %d / %d" % [current, total]

func _on_time_updated(current_time: float, best_time: float) -> void:
	if race_mgr and time_label and best_label:
		time_label.text = "TIME " + race_mgr.format_time(current_time)
		best_label.text = "BEST " + race_mgr.format_time(best_time)

func _on_checkpoint_updated(current: int, total: int) -> void:
	if sector_label:
		sector_label.text = "SECTOR %d / %d" % [current, total]

func _on_score_updated(total: int) -> void:
	if score_label:
		score_label.text = "SCORE: %d" % total

func _on_car_model_changed(car_name: String) -> void:
	if car_name_label:
		car_name_label.text = "CAR: " + car_name + " [Press 1-4 to change]"

func _on_race_finished(results: Dictionary) -> void:
	if victory_panel:
		victory_panel.visible = true
	if victory_time and race_mgr:
		victory_time.text = "Total Time: " + race_mgr.format_time(results["total_time"])
	if victory_best and race_mgr:
		victory_best.text = "Best Lap: " + race_mgr.format_time(results["best_lap"])
	if victory_score:
		victory_score.text = "Final Score: %d (Drift: %d)" % [results["total_score"], results["drift_score"]]

func _on_restart_pressed() -> void:
	get_tree().reload_current_scene()
