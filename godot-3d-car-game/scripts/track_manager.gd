extends Node
class_name TrackManager

signal track_load_started(track_name: String)
signal track_loaded(track_info: Dictionary)
signal track_list_ready(tracks: Array)

var available_tracks: Array[Dictionary] = []
var current_track_index: int = 0

var main_game: Node3D
var player_car: Node3D
var chase_camera: Camera3D
var original_track_node: Node3D
var loaded_track_instance: Node3D = null
var current_finish_gate: Area3D = null

const DOWNLOADS_DIR = "/home/mullainathan/Downloads/Sketchfab_Racetracks"
const TRACKS_DIR = "res://assets/sketchfab_tracks"

func _ready() -> void:
    main_game = get_parent() as Node3D
    player_car = get_node_or_null("/root/MainGame/PlayerCar")
    chase_camera = get_node_or_null("/root/MainGame/ChaseCamera")
    original_track_node = get_node_or_null("/root/MainGame/Track")
    
    refresh_track_catalog()

func refresh_track_catalog() -> void:
    available_tracks.clear()
    
    # 0. Built-in Grand Prix Track
    available_tracks.append({
        "id": 0,
        "name": "Grand Prix Arena (Original)",
        "author": "Nitro Drift Team",
        "description": "Custom arcade circuit with hairpins, jumps, boost pads & coins",
        "folder": "",
        "path": "",
        "is_default": true,
        "vertex_count": 0
    })
    
    var search_dirs = [DOWNLOADS_DIR, TRACKS_DIR]
    var seen_folders: Dictionary = {}
    for base in search_dirs:
        var dir = DirAccess.open(base)
        if dir:
            dir.list_dir_begin()
            var f = dir.get_next()
            while f != "":
                if dir.current_is_dir() and not f.begins_with(".") and not seen_folders.has(f):
                    var candidate_gltf = base.path_join(f).path_join("scene.gltf")
                    if FileAccess.file_exists(candidate_gltf):
                        seen_folders[f] = candidate_gltf
                f = dir.get_next()
            dir.list_dir_end()

    var folder_keys: Array = seen_folders.keys()
    folder_keys.sort()
    for f in folder_keys:
        var gltf_path: String = seen_folders[f]
        var track_data := {
            "id": available_tracks.size(),
            "name": _format_folder_name(f),
            "author": "Dave Love SketchFab",
            "description": "Authentic real-world racing circuit",
            "folder": f,
            "path": gltf_path,
            "is_default": false,
            "vertex_count": 0
        }
        
        var meta_path = gltf_path.get_base_dir().path_join("metadata.json")
        if FileAccess.file_exists(meta_path):
            var file = FileAccess.open(meta_path, FileAccess.READ)
            if file:
                var json = JSON.new()
                if json.parse(file.get_as_text()) == OK and json.data is Dictionary:
                    var d: Dictionary = json.data
                    track_data["name"] = d.get("name", track_data["name"])
                    track_data["author"] = d.get("user", track_data["author"])
                    track_data["vertex_count"] = d.get("vertexCount", 0)
                    track_data["face_count"] = d.get("faceCount", 0)

        available_tracks.append(track_data)

    track_list_ready.emit(available_tracks)

func _format_folder_name(folder: String) -> String:
    var clean = folder
    if clean.length() > 3 and clean[2] == '_':
        clean = clean.substr(3)
    return clean.replace("_", " ").strip_edges()

func get_track_count() -> int:
    return available_tracks.size()

func get_current_track_info() -> Dictionary:
    if current_track_index >= 0 and current_track_index < available_tracks.size():
        return available_tracks[current_track_index]
    return {}

func next_track() -> void:
    if available_tracks.is_empty():
        return
    var next_idx = (current_track_index + 1) % available_tracks.size()
    load_track(next_idx)

func prev_track() -> void:
    if available_tracks.is_empty():
        return
    var prev_idx = (current_track_index - 1 + available_tracks.size()) % available_tracks.size()
    load_track(prev_idx)

func load_track(index: int) -> void:
    if index < 0 or index >= available_tracks.size():
        return
    
    current_track_index = index
    var info = available_tracks[index]
    track_load_started.emit(info.get("name", "Track"))
    
    # Defer execution to allow HUD to show loading banner
    call_deferred("_execute_load_track", info)

func _execute_load_track(info: Dictionary) -> void:
    if info.get("is_default", false):
        _load_default_track()
    else:
        _load_sketchfab_track(info)
    
    track_loaded.emit(info)

func _load_default_track() -> void:
    # 1. Clean up external track
    if is_instance_valid(loaded_track_instance):
        loaded_track_instance.queue_free()
        loaded_track_instance = null
        
    if is_instance_valid(current_finish_gate):
        current_finish_gate.queue_free()
        current_finish_gate = null
        
    # 2. Show original track and enable collision
    if is_instance_valid(original_track_node):
        original_track_node.visible = true
        _set_node_collisions_enabled(original_track_node, true)
        
    # 3. Reset car position to start
    if is_instance_valid(player_car):
        player_car.global_position = Vector3(0, 0.4, 0)
        player_car.global_rotation = Vector3.ZERO
        player_car.velocity = Vector3.ZERO
        if "current_forward_speed" in player_car:
            player_car.current_forward_speed = 0.0
        if "last_checkpoint_transform" in player_car:
            player_car.last_checkpoint_transform = player_car.global_transform
            
    # 4. Snap chase camera
    if is_instance_valid(chase_camera):
        chase_camera.global_position = Vector3(0, 2.5, 6.0)
        chase_camera.look_at(Vector3(0, 1.0, 0))
        
    # 5. Reset race manager for default track
    var race_mgr = get_node_or_null("/root/MainGame/RaceManager")
    if race_mgr and race_mgr.has_method("_start_countdown"):
        race_mgr.current_lap = 1
        race_mgr.next_checkpoint = 1
        race_mgr.current_lap_time = 0.0
        race_mgr.total_race_time = 0.0
        race_mgr._start_countdown()

func _load_sketchfab_track(info: Dictionary) -> void:
    var gltf_path: String = info.get("path", "")
    if not FileAccess.file_exists(gltf_path):
        push_error("Track glTF file not found: " + gltf_path)
        return

    # 1. Hide default track and disable its collisions
    if is_instance_valid(original_track_node):
        original_track_node.visible = false
        _set_node_collisions_enabled(original_track_node, false)

    # 2. Remove previously loaded track
    if is_instance_valid(loaded_track_instance):
        loaded_track_instance.queue_free()
        loaded_track_instance = null
        
    if is_instance_valid(current_finish_gate):
        current_finish_gate.queue_free()
        current_finish_gate = null

    # 3. Load GLTF model
    var gltf = GLTFDocument.new()
    var state = GLTFState.new()
    var err = gltf.append_from_file(gltf_path, state)
    if err != OK:
        push_error("Failed to parse GLTF: " + gltf_path)
        return

    var track_scene: Node3D = gltf.generate_scene(state) as Node3D
    if not track_scene:
        push_error("Failed to generate scene from GLTF")
        return

    track_scene.name = "LoadedSketchfabTrack"
    # Convert CAD / GIS Z-up orientation to Godot Y-up
    track_scene.rotation_degrees = Vector3(-90, 0, 0)
    
    main_game.add_child(track_scene)
    loaded_track_instance = track_scene
    track_scene.force_update_transform()
    
    # 4. Generate 3D static collision for every mesh
    _generate_trimesh_collisions(track_scene)

    # 5. Calculate optimal spawn point on track surface
    var spawn_pos: Vector3 = _calculate_track_spawn(track_scene)

    # 6. Place car at spawn
    if is_instance_valid(player_car):
        player_car.global_position = spawn_pos + Vector3(0, 1.5, 0)
        player_car.global_rotation = Vector3.ZERO
        player_car.velocity = Vector3.ZERO
        if "current_forward_speed" in player_car:
            player_car.current_forward_speed = 0.0
        if "lateral_velocity" in player_car:
            player_car.lateral_velocity = Vector3.ZERO
        if "last_checkpoint_transform" in player_car:
            player_car.last_checkpoint_transform = player_car.global_transform

    # 7. Snap camera
    if is_instance_valid(chase_camera) and is_instance_valid(player_car):
        chase_camera.global_position = player_car.global_position + Vector3(0, 2.5, 6.0)
        chase_camera.look_at(player_car.global_position + Vector3(0, 1.0, 0))

    # 8. Create a Start / Finish Line arch at spawn point
    _create_finish_line_gate(spawn_pos)

    # 9. Reset RaceManager for circuit time trial
    var race_mgr = get_node_or_null("/root/MainGame/RaceManager")
    if race_mgr:
        race_mgr.current_lap = 1
        race_mgr.next_checkpoint = 0
        race_mgr.current_lap_time = 0.0
        race_mgr.total_race_time = 0.0
        race_mgr.total_laps = 5
        race_mgr._start_countdown()

func _generate_trimesh_collisions(root: Node) -> void:
    var meshes: Array[MeshInstance3D] = []
    _collect_mesh_instances(root, meshes)
    for m in meshes:
        if m.mesh:
            var shape = m.mesh.create_trimesh_shape()
            if shape:
                var sb = StaticBody3D.new()
                sb.name = "Collision"
                var col = CollisionShape3D.new()
                col.shape = shape
                sb.add_child(col)
                m.add_child(sb)

func _collect_mesh_instances(node: Node, out: Array[MeshInstance3D]) -> void:
    if node is MeshInstance3D:
        out.append(node)
    for c in node.get_children():
        _collect_mesh_instances(c, out)

func _set_node_collisions_enabled(root: Node, enabled: bool) -> void:
    if root is CollisionShape3D:
        root.disabled = not enabled
    for c in root.get_children():
        _set_node_collisions_enabled(c, enabled)

func _calculate_track_spawn(root: Node3D) -> Vector3:
    var meshes: Array[MeshInstance3D] = []
    _collect_mesh_instances(root, meshes)
    if meshes.is_empty():
        return Vector3(0, 5, 0)

    # Compute bounding box
    var total_aabb = AABB()
    var first = true
    for m in meshes:
        var box = m.global_transform * m.mesh.get_aabb()
        if first:
            total_aabb = box
            first = false
        else:
            total_aabb = total_aabb.merge(box)

    var center_xz = Vector2(total_aabb.position.x + total_aabb.size.x * 0.5, total_aabb.position.z + total_aabb.size.z * 0.5)
    var best_vert = Vector3.ZERO
    var min_dist = 1e9

    for m in meshes:
        var mesh: Mesh = m.mesh
        for s in range(mesh.get_surface_count()):
            var arrays = mesh.surface_get_arrays(s)
            var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
            var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL] if arrays.size() > Mesh.ARRAY_NORMAL else []

            var step = maxi(1, verts.size() / 120)
            for i in range(0, verts.size(), step):
                var v = m.global_transform * verts[i]
                var n = (m.global_transform.basis * normals[i]).normalized() if i < normals.size() else Vector3.UP
                # Favor upward surface (tarmac/road)
                if n.y > 0.65:
                    var d = center_xz.distance_to(Vector2(v.x, v.z))
                    if d < min_dist:
                        min_dist = d
                        best_vert = v

    if min_dist < 1e8:
        return best_vert
    return total_aabb.get_center()

func _create_finish_line_gate(spawn_pos: Vector3) -> void:
    var gate = Area3D.new()
    gate.name = "FinishLineGate"
    gate.global_position = spawn_pos + Vector3(0, 1.0, 0)
    
    var col = CollisionShape3D.new()
    var box = BoxShape3D.new()
    box.size = Vector3(25.0, 8.0, 6.0)
    col.shape = box
    gate.add_child(col)
    
    # Checkered banner visual
    var banner = MeshInstance3D.new()
    var b_mesh = BoxMesh.new()
    b_mesh.size = Vector3(25.0, 1.2, 0.4)
    banner.mesh = b_mesh
    banner.position = Vector3(0, 5.0, 0)
    var mat = StandardMaterial3D.new()
    mat.albedo_color = Color(1.0, 0.85, 0.1)
    banner.material_override = mat
    gate.add_child(banner)
    
    gate.set_script(load("res://scripts/checkpoint.gd"))
    gate.set("is_finish_line", true)
    gate.set("checkpoint_index", 0)
    
    main_game.add_child(gate)
    current_finish_gate = gate
