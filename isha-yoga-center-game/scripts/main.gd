extends Node3D

@onready var world_env: WorldEnvironment = $WorldEnvironment
@onready var sun: DirectionalLight3D = $DirectionalLight3D
@onready var plaza_visual: Node3D = $SteppedPlaza_Visual
@onready var adiyogi_statue: StaticBody3D = $Adiyogi_Statue

func _ready():
	# Configure Viewport Anti-Aliasing (TAA + MSAA + Debanding for silky-smooth, jitter-free rendering)
	var vp = get_viewport()
	if vp:
		vp.use_taa = true
		vp.use_debanding = true
		vp.msaa_3d = Viewport.MSAA_2X
		print("[Main] Viewport TAA (Temporal Anti-Aliasing) and Debanding enabled!")

	var player_cam = get_node_or_null("Player/CameraPivot/SpringArm3D/Camera3D")
	if player_cam and player_cam is Camera3D:
		var pcam = player_cam as Camera3D
		pcam.near = 0.25 # Eliminates depth buffer fighting and distant z-precision glittering
		pcam.far = 2500.0

	_setup_normal_day_lighting()
	_setup_materials()
	_setup_physics()
	_setup_mandapa_sanctum()
	_setup_landscape_and_pathway()
	_setup_malai_vasal()
	# _setup_inner_temple_complex() # Removed: Adiyogi and Malai Vasal only
	_setup_vintage_bicycle()
	_setup_suryakund_complex()
	_setup_sarpavasal_gateway()
	_setup_lingabhairavi_temple()
	_setup_dhyanalinga_temple()
	
	# Spawn player directly in front of Linga Bhairavi Temple entrance facing facade
	var player = get_node_or_null("Player")
	if player:
		player.position = _lb_pt(Vector3(0.0, 0.40, -14.0))
		player.rotation_degrees = Vector3(0, LINGABHAIRAVI_ROT_DEG + 180.0, 0)
		print("[Main] Player spawned directly in front of Linga Bhairavi Temple at: ", player.position)

	print("[Main] Normal Day HDRI atmosphere, realistic daylight, 4K materials & landscape configured successfully!")
	
	var args = OS.get_cmdline_args() + OS.get_cmdline_user_args()
	for a in args:
		if "--bake-gi" in a:
			call_deferred("_run_bake_gi_and_capture")
			return
		elif "--capture-sarpavasal" in a:
			call_deferred("_run_capture_sarpavasal_sequence")
			break
		elif "--capture-suryakund" in a:
			call_deferred("_run_capture_suryakund_sequence")
			break
		elif "--capture-lingabhairavi" in a:
			call_deferred("_run_capture_lingabhairavi_sequence")
			break
		elif "--capture-dhyanalinga" in a:
			call_deferred("_run_capture_dhyanalinga_sequence")
			break
		elif "--capture-pro-realism" in a:
			call_deferred("_run_capture_pro_realism_sequence")
			break
		elif "--capture-pillars" in a:
			call_deferred("_run_capture_sequence")
			break

func _run_bake_gi_and_capture():
	print("[VoxelGI] Preparing scene tree for fresh photorealistic VoxelGI bake...")
	for f in range(10):
		await get_tree().process_frame

	var vgi: VoxelGI = get_node_or_null("VoxelGI")
	if vgi:
		print("[VoxelGI] Baking VoxelGI with all temple geometry (Four Pillars, Naga Pillars, Mandapa Roof)...")
		vgi.bake(self)
		if vgi.data:
			ResourceSaver.save(vgi.data, "res://assets/voxel_gi_data.res")
			print("[VoxelGI] Saved fresh baked voxel_gi_data.res successfully!")

	var vgi_pathway: VoxelGI = get_node_or_null("VoxelGI_Pathway")
	if vgi_pathway:
		print("[VoxelGI] Baking VoxelGI_Pathway with pathway, curbs, terrain, and grass...")
		vgi_pathway.bake(self)
		if vgi_pathway.data:
			ResourceSaver.save(vgi_pathway.data, "res://assets/voxel_gi_pathway_data.res")
			print("[VoxelGI] Saved fresh baked voxel_gi_pathway_data.res successfully!")

	# Continue into capture sequence to verify
	_run_capture_sequence()

func _run_capture_sequence():
	print("[Capture] Starting 8ft pillar capture sequence...")
	var cam = Camera3D.new()
	cam.name = "CaptureCam"
	add_child(cam)
	cam.current = true
	cam.fov = 65.0
	cam.near = 0.25
	cam.far = 1200.0

	# Position player behind Adiyogi to demonstrate full 360 walkability behind statue
	var player = get_node_or_null("Player")
	if player:
		player.position = Vector3(1.5, 2.52, -7.5)
		player.rotation_degrees = Vector3(0, 180, 0) # Facing back of Adiyogi

	var shots = [
		{
			"name": "godot_naga_pillars_steps_overview.png",
			"pos": Vector3(0.0, 5.0, 50.0),
			"look": Vector3(0.0, 2.5, 30.0)
		},
		{
			"name": "godot_naga_pillar_closeup.png",
			"pos": Vector3(9.0, 1.75, 38.8),
			"look": Vector3(9.0, 1.65, 36.95)
		},
		{
			"name": "godot_mandapa_darker_pillars.png",
			"pos": Vector3(0.0, 3.2, 43.0),
			"look": Vector3(0.0, 2.8, 30.4)
		},
		{
			"name": "godot_mandapa_roof_aerial.png",
			"pos": Vector3(8.5, 9.5, 42.0),
			"look": Vector3(0.0, 4.2, 30.4)
		},
		{
			"name": "godot_mandapa_roof_overview.png",
			"pos": Vector3(0.0, 6.8, 46.0),
			"look": Vector3(0.0, 3.8, 30.4)
		},
		{
			"name": "godot_mandapa_under_roof_sanctum.png",
			"pos": Vector3(0.0, 2.6, 33.6),
			"look": Vector3(0.0, 1.8, 30.4)
		},
		{
			"name": "godot_mandapa_ceiling_wooden_closeup.png",
			"pos": Vector3(0.0, 2.0, 33.5),
			"look": Vector3(0.0, 3.8, 30.4)
		},
		{
			"name": "godot_plaza_grand_overview_04.png",
			"pos": Vector3(18.0, 16.0, 38.0),
			"look": Vector3(0.0, 6.0, 4.0)
		},
		{
			"name": "godot_pathway_from_malivasal.png",
			"pos": Vector3(0.0, 3.2, 540.0),
			"look": Vector3(0.0, 10.0, 100.0)
		},
		{
			"name": "godot_pathway_cobblestone_closeup.png",
			"pos": Vector3(0.0, 1.7, 300.0),
			"look": Vector3(0.0, 0.18, 292.0)
		},
		{
			"name": "godot_pathway_curb_finish_closeup.png",
			"pos": Vector3(8.9, 0.75, 260.0),
			"look": Vector3(9.9, 0.20, 263.0)
		},
		{
			"name": "godot_pathway_curb_west_view.png",
			"pos": Vector3(-8.9, 0.75, 260.0),
			"look": Vector3(-9.9, 0.20, 263.0)
		},
		{
			"name": "godot_pathway_side_extrusion_and_mud.png",
			"pos": Vector3(14.0, 1.6, 260.0),
			"look": Vector3(0.0, 0.4, 250.0)
		},
		{
			"name": "godot_landscape_birds_eye.png",
			"pos": Vector3(75.0, 65.0, 320.0),
			"look": Vector3(0.0, 5.0, 220.0)
		},
		{
			"name": "godot_trees_along_path.png",
			"pos": Vector3(5.0, 1.8, 200.0),
			"look": Vector3(0.0, 6.0, 80.0)
		},
		{
			"name": "godot_3d_grass_and_shrub_closeup.png",
			"pos": Vector3(11.2, 0.85, 238.5),
			"look": Vector3(12.5, 0.45, 240.5)
		},
		{
			"name": "godot_malai_vasal_front.png",
			"pos": Vector3(0.0, 3.2, 592.0),
			"look": Vector3(0.0, 7.2, 570.0)
		},
		{
			"name": "godot_malai_vasal_from_pathway.png",
			"pos": Vector3(0.0, 2.8, 545.0),
			"look": Vector3(0.0, 7.8, 570.0)
		},
		{
			"name": "godot_malai_vasal_boulder_closeup.png",
			"pos": Vector3(7.2, 9.5, 582.0),
			"look": Vector3(0.2, 10.5, 570.0)
		},
		{
			"name": "godot_malai_vasal_gate_and_art_panel.png",
			"pos": Vector3(-12.0, 2.0, 580.0),
			"look": Vector3(-15.2, 2.0, 570.0)
		},
		{
			"name": "godot_main_road_pathway.png",
			"pos": Vector3(0.0, 3.0, 555.0),
			"look": Vector3(0.0, 2.0, 350.0)
		}
	]

	# Let the scene settle
	for f in range(5):
		await get_tree().process_frame

	for shot in shots:
		cam.position = shot["pos"]
		cam.look_at(shot["look"], Vector3.UP)
		for f in range(3):
			await get_tree().process_frame
		await RenderingServer.frame_post_draw

		var vp = get_viewport()
		if vp:
			var img = vp.get_texture().get_image()
			if img:
				var path = "/home/mullainathan/Games/IshaGodot/" + shot["name"]
				img.save_png(path)
				var brain_dir = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures/"
				DirAccess.make_dir_recursive_absolute(brain_dir)
				img.save_png(brain_dir + shot["name"])
				print("[Capture] Successfully saved: ", path, " and brain artifact!")

	print("[Capture] All pillar screenshots captured!")
	get_tree().quit(0)

func _setup_normal_day_lighting():
	# Normal Day Sun positioned in front of the statue (shining directly onto Adiyogi's face and chest)
	if sun:
		sun.visible = true
		sun.rotation_degrees = Vector3(-36.0, -22.0, 0.0) # Natural mid-morning / afternoon solar angle illuminating Adiyogi's face & chest
		sun.light_color = Color(1.0, 0.965, 0.915) # Authentic 5600K physical solar spectrum
		sun.light_energy = 1.95 # Ultra-pro realistic physical daylight lux
		sun.light_indirect_energy = 1.65 # Rich multi-bounce indirect GI radiosity
		sun.light_bake_mode = Light3D.BAKE_DYNAMIC # Dynamic VoxelGI bounce contribution
		sun.light_angular_distance = 1.25 # Physical solar disk penumbra (sharp near contact shadows, softly blurring distant penumbra - PCSS effect)
		sun.light_specular = 0.32 # Clean, crisp specular highlights on stone facets & facial contours
		sun.shadow_enabled = true
		sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
		sun.directional_shadow_blend_splits = true # Seamless blend between cascade splits - zero visible shadow boundary lines
		sun.directional_shadow_split_1 = 0.035 # Razor-sharp near contact shadows (player, steps, water, linga)
		sun.directional_shadow_split_2 = 0.115 # Mid-range shadows (mandapa pillars, trees, naga pillars)
		sun.directional_shadow_split_3 = 0.340 # Long-range shadows (grand pathway, tree line, entrance walls)
		sun.directional_shadow_fade_start = 0.85
		sun.directional_shadow_max_distance = 1500.0 # Full scene coverage up to 1500m across entire ashram
		sun.shadow_bias = 0.006 # Razor-sharp contact without self-shadow acne
		sun.shadow_normal_bias = 0.90 # Eliminates light leaks on stone corners and edges
		sun.shadow_blur = 1.45 # Natural soft PCSS shadow filtration
		sun.shadow_opacity = 0.98
		sun.light_volumetric_fog_energy = 1.85 # Atmospheric god rays across entire map

	# VoxelGI around Adiyogi removed per user request (SDFGI and Ambient Sky provide natural outdoor global illumination)

	# Configure VoxelGI_Pathway for Photorealistic Landscape, 3D Grass & Walkway Indirect Lighting
	var vgi_pathway: VoxelGI = get_node_or_null("VoxelGI_Pathway")
	if vgi_pathway:
		vgi_pathway.size = Vector3(180.0, 48.0, 520.0)
		vgi_pathway.position = Vector3(0.0, 18.0, 360.0)
		vgi_pathway.subdiv = VoxelGI.SUBDIV_128
		if not vgi_pathway.data:
			var loaded_pdata = load("res://assets/voxel_gi_pathway_data.res")
			if loaded_pdata:
				vgi_pathway.data = loaded_pdata
		if vgi_pathway.data:
			vgi_pathway.data.propagation = 0.78 # Natural light bounce across cobblestones and grass
			vgi_pathway.data.use_two_bounces = true # Multi-bounce radiosity for lush contact shadows
			vgi_pathway.data.energy = 1.20 # Rich natural daytime bounce
			vgi_pathway.data.bias = 1.2
			vgi_pathway.data.normal_bias = 0.15
			vgi_pathway.data.dynamic_range = 3.6
			vgi_pathway.data.interior = false
			print("[Main] VoxelGI_Pathway realistic global illumination loaded and active!")

	if world_env and world_env.environment:
		var env = world_env.environment
		
		# Set Sky to Normal Day HDRI and rotate so green foothills/mountains appear behind Adiyogi
		var day_sky_tex = load("res://assets/normal_day_hills.hdr")
		if day_sky_tex:
			if not env.sky:
				env.sky = Sky.new()
			var sky_mat = PanoramaSkyMaterial.new()
			sky_mat.panorama = day_sky_tex
			env.sky.sky_material = sky_mat
		
		# Rotate HDRI by 180 degrees so the majestic mountain range stands directly behind Adiyogi
		env.sky_rotation = Vector3(0.0, deg_to_rad(180.0), 0.0)
		
		# ACES Photographic Tonemapping (Ultra pro realistic dynamic range, cinematic film response)
		env.tonemap_mode = Environment.TONE_MAPPER_ACES
		env.tonemap_exposure = 1.15
		env.tonemap_white = 6.0
		
		# Normal Day Sky Ambient (Soft, balanced, photorealistic daylight directly from HDRI sky)
		env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
		env.ambient_light_sky_contribution = 1.0 # 100% physically authentic HDRI sky lighting
		env.ambient_light_color = Color(0.92, 0.95, 1.0) # Subtle cool mountain sky tint
		env.ambient_light_energy = 1.25
		
		# Cascaded Signed-Distance Field Global Illumination (SDFGI) for expansive landscape & mountains
		env.sdfgi_enabled = true
		env.sdfgi_use_occlusion = true
		env.sdfgi_read_sky_light = true
		env.sdfgi_bounce_feedback = 0.55 # Multi-bounce radiosity
		env.sdfgi_cascades = 4
		env.sdfgi_min_cell_size = 0.20
		env.sdfgi_cascade0_distance = 20.0
		env.sdfgi_max_distance = 1500.0
		env.sdfgi_y_scale = Environment.SDFGI_Y_SCALE_100_PERCENT
		env.sdfgi_energy = 1.15
		env.sdfgi_normal_bias = 1.1

		# Natural Mountain Aerial Perspective & Atmospheric Haze (Velliangiri Foothills)
		env.volumetric_fog_enabled = true
		env.volumetric_fog_density = 0.00030 # Crystal-clear visibility across full 1.2km ashram with soft distant mountain haze
		env.volumetric_fog_albedo = Color(0.88, 0.93, 1.0) # Crisp blue sky atmospheric scattering
		env.volumetric_fog_emission = Color(0.0, 0.0, 0.0)
		env.volumetric_fog_anisotropy = 0.62 # Natural forward solar scattering creating stunning god rays
		env.volumetric_fog_length = 1600.0
		env.volumetric_fog_ambient_inject = 0.90
		env.volumetric_fog_sky_affect = 0.30
		env.volumetric_fog_temporal_reprojection_enabled = true
		env.volumetric_fog_temporal_reprojection_amount = 0.96
		
		# Screen-Space Ambient Occlusion (SSAO: deep, crisp contact shadows without noise)
		env.ssao_enabled = true
		env.ssao_radius = 2.2
		env.ssao_intensity = 2.35
		env.ssao_power = 1.45
		env.ssao_detail = 0.65 # Crisp fine-edge crevices between stone blocks
		env.ssao_horizon = 0.05
		
		# Screen-Space Indirect Lighting (SSIL: soft realistic color bleeding between materials)
		env.ssil_enabled = true
		env.ssil_radius = 4.2
		env.ssil_intensity = 1.15
		env.ssil_sharpness = 0.92
		env.ssil_normal_rejection = 1.0
		
		# Screen-Space Reflections disabled to prevent ground glare
		env.ssr_enabled = false
		
		# Natural Physical Bloom / Glow (Radiance on emissive Moon, Vibuthi & Sacred Gold)
		env.glow_enabled = true
		env.glow_intensity = 0.25
		env.glow_strength = 0.92
		env.glow_bloom = 0.10
		env.glow_blend_mode = Environment.GLOW_BLEND_MODE_SOFTLIGHT
		env.glow_hdr_threshold = 1.05 # Only bright emissive highlights bloom
		env.glow_hdr_scale = 1.8
		
		# Photographic Color Grading (Subtle film print contrast and natural saturation)
		env.adjustment_enabled = true
		env.adjustment_contrast = 1.09
		env.adjustment_saturation = 1.06
		env.adjustment_brightness = 1.01

func _setup_physics():
	var physics_body = get_node_or_null("Plaza_Physics")
	if not physics_body:
		return
	
	for child in physics_body.get_children():
		child.queue_free()
	
	# 1. Lower Courtyard: size (160, 2, 72), center (0, -1.0, 79.1) -> top Y = 0.0, Z = [43.1, 115.1]
	_add_box_col(physics_body, "Col_Courtyard", Vector3(160, 2, 72), Transform3D(Basis(), Vector3(0, -1.0, 79.1)))
	
	# 2. Landings and Terraces
	_add_box_col(physics_body, "Col_Landing1", Vector3(80, 2, 1.5), Transform3D(Basis(), Vector3(0, -0.640, 41.550)))
	_add_box_col(physics_body, "Col_Landing2", Vector3(80, 2, 1.5), Transform3D(Basis(), Vector3(0, -0.280, 39.250)))
	_add_box_col(physics_body, "Col_Landing3", Vector3(80, 2, 1.5), Transform3D(Basis(), Vector3(0,  0.080, 36.950)))
	_add_box_col(physics_body, "Col_Terrace10m", Vector3(80, 2, 10.0), Transform3D(Basis(), Vector3(0, 0.440, 30.400)))
	_add_box_col(physics_body, "Col_Landing5", Vector3(80, 2, 1.5), Transform3D(Basis(), Vector3(0,  0.800, 23.850)))
	_add_box_col(physics_body, "Col_Landing6", Vector3(80, 2, 1.5), Transform3D(Basis(), Vector3(0,  1.160, 21.550)))
	_add_box_col(physics_body, "Col_TopPlatform", Vector3(80, 2, 55.0), Transform3D(Basis(), Vector3(0, 1.520, -7.500)))
	
	# 3. Seven Stair Flight Ramps (Box size: 80, 0.4, 1.20)
	var ramp_basis = Basis.from_euler(Vector3(deg_to_rad(24.2277), 0.0, 0.0))
	var ramp_size = Vector3(80.0, 0.4, 1.20)
	
	var flight_centers = [
		Vector3(0.0, -0.002, 42.618),
		Vector3(0.0,  0.358, 40.318),
		Vector3(0.0,  0.718, 38.018),
		Vector3(0.0,  1.078, 35.718),
		Vector3(0.0,  1.438, 24.918),
		Vector3(0.0,  1.798, 22.618),
		Vector3(0.0,  2.158, 20.318),
	]
	
	for i in range(flight_centers.size()):
		_add_box_col(physics_body, "Ramp_Flight" + str(i + 1), ramp_size, Transform3D(ramp_basis, flight_centers[i]))
	
	print("[Physics] Built 100% gapless BoxShape3D physics for courtyard, 7 flight ramps, landings, 10m terrace & top platform!")

func _add_box_col(parent: Node, col_name: String, box_size: Vector3, xform: Transform3D):
	var shape = BoxShape3D.new()
	shape.size = box_size
	var col = CollisionShape3D.new()
	col.name = col_name
	col.shape = shape
	col.transform = xform
	parent.add_child(col)

func _setup_materials():
	# 1. BlendKit Ashlar Slate Pavers Material (3f98f735-59a3-43b4-9b7e-d2f1b26373c8)
	var mat_granite = StandardMaterial3D.new()
	mat_granite.resource_name = "BlendKit_Ashlar_Slate_Pavers_PBR"
	mat_granite.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_granite.albedo_texture = load("res://assets/textures/ashlar_slate_color.jpg")
	mat_granite.roughness_texture = load("res://assets/textures/ashlar_slate_roughness.jpg")
	mat_granite.normal_enabled = true
	mat_granite.normal_texture = load("res://assets/textures/ashlar_slate_normal.jpg")
	mat_granite.normal_scale = 1.0
	mat_granite.roughness = 0.90 # Natural matte paving stone
	mat_granite.metallic = 0.0 # Non-metallic natural slate
	mat_granite.metallic_specular = 0.15 # Subtle natural stone sheen without blinding glare
	mat_granite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	
	# Triplanar projection prevents any texture stretching on vertical drops / stair risers
	mat_granite.uv1_triplanar = true
	mat_granite.uv1_world_triplanar = true
	mat_granite.uv1_triplanar_sharpness = 2.0 # Smooth blending prevents distant pixel buzzing / sparkling
	mat_granite.uv1_scale = Vector3(0.28, 0.28, 0.28) # Real-world architectural paver scale
	
	# 2. BlendKit Stacked Brick Step Tiles Material (3e81764e-6d5a-422f-8a62-3316b0abae3e)
	var mat_step_bricks = StandardMaterial3D.new()
	mat_step_bricks.resource_name = "BlendKit_Stacked_Brick_PBR"
	mat_step_bricks.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_step_bricks.albedo_texture = load("res://assets/textures/stacked_brick_color.jpg")
	mat_step_bricks.roughness_texture = load("res://assets/textures/stacked_brick_roughness.jpg")
	mat_step_bricks.normal_enabled = true
	mat_step_bricks.normal_texture = load("res://assets/textures/stacked_brick_normal.png")
	mat_step_bricks.normal_scale = 1.0
	mat_step_bricks.roughness = 0.92 # Natural matte brick texture
	mat_step_bricks.metallic = 0.0
	mat_step_bricks.metallic_specular = 0.10
	mat_step_bricks.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	mat_step_bricks.uv1_triplanar = true
	mat_step_bricks.uv1_world_triplanar = true
	mat_step_bricks.uv1_triplanar_sharpness = 2.0 # Smooth blending prevents distant pixel buzzing / sparkling
	mat_step_bricks.uv1_scale = Vector3(0.55, 0.55, 0.55)
	
	# 3. Adiyogi Sculpture Material (Dignified charcoal stone/steel - visible facial features, non-shining)
	var mat_adiyogi = StandardMaterial3D.new()
	mat_adiyogi.resource_name = "Godot_Adiyogi_Black_Sculpture"
	mat_adiyogi.albedo_color = Color(0.08, 0.08, 0.085) # Rich deep charcoal/black - facial features clearly visible in daylight
	mat_adiyogi.metallic = 0.15 # Subtle dark metal/cast steel undertone
	mat_adiyogi.roughness = 0.52 # Smooth satin sheen - no harsh mirror glare
	mat_adiyogi.metallic_specular = 0.25 # Soft diffused specular definition on brow, nose & cheekbones
	mat_adiyogi.clearcoat_enabled = false # No glossy lacquer
	mat_adiyogi.rim_enabled = true # Gentle sky rim definition
	mat_adiyogi.rim = 0.25
	mat_adiyogi.rim_tint = 0.30
	
	# 4. Adiyogi Crescent Moon (Glowing White)
	var mat_moon = StandardMaterial3D.new()
	mat_moon.resource_name = "Godot_Adiyogi_Moon_GlowingWhite"
	mat_moon.albedo_color = Color(1.0, 1.0, 1.0)
	mat_moon.emission_enabled = true
	mat_moon.emission = Color(1.0, 1.0, 1.0)
	mat_moon.emission_energy_multiplier = 5.0 # Radiant celestial white glow
	mat_moon.roughness = 0.15
	
	# 5. Adiyogi Sacred Vibuthi (Glowing White, Single Vertical Stroke: Blunt bottom, sharp top)
	var mat_vibuthi = StandardMaterial3D.new()
	mat_vibuthi.resource_name = "Godot_Adiyogi_Vibuthi_GlowingWhite"
	mat_vibuthi.albedo_color = Color(1.0, 1.0, 1.0)
	mat_vibuthi.emission_enabled = true
	mat_vibuthi.emission = Color(1.0, 1.0, 1.0)
	mat_vibuthi.emission_energy_multiplier = 5.0 # Matching radiant celestial white glow
	mat_vibuthi.roughness = 0.15
	
	# 6. Adiyogi Kundala Earrings (Metallic Copper)
	var mat_earrings = StandardMaterial3D.new()
	mat_earrings.resource_name = "Godot_Adiyogi_Earrings_Copper"
	mat_earrings.albedo_color = Color(0.85, 0.45, 0.22) # Warm metallic copper
	mat_earrings.metallic = 0.96 # Highly metallic copper sheen
	mat_earrings.roughness = 0.22
	mat_earrings.rim_enabled = true
	mat_earrings.rim = 0.40
	
	# Assign materials to SteppedPlaza meshes
	_apply_material_recursive(plaza_visual, mat_granite, mat_step_bricks)
	
	# Assign materials to Adiyogi sculpture
	if adiyogi_statue:
		var visual = adiyogi_statue.get_node_or_null("Visual_Mesh")
		if visual:
			_apply_adiyogi_materials_recursive(visual, mat_adiyogi, mat_moon, mat_vibuthi, mat_earrings)

	# Authentic Naga-Stone Granite Material for Four_Pillars (matching Naga Pillars perfectly)
	var mat_pillar_granite = StandardMaterial3D.new()
	mat_pillar_granite.resource_name = "Four_Pillars_Naga_Granite_PBR"
	mat_pillar_granite.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_pillar_granite.albedo_color = Color(1.15, 1.15, 1.15) # Matches Naga pillar warm golden-buff tone
	mat_pillar_granite.albedo_texture = load("res://assets/textures/naga_stone_color.png")
	mat_pillar_granite.normal_enabled = true
	mat_pillar_granite.normal_texture = load("res://assets/textures/naga_stone_normal.png")
	mat_pillar_granite.normal_scale = 1.0
	mat_pillar_granite.roughness_texture = load("res://assets/textures/naga_stone_roughness.png")
	mat_pillar_granite.roughness = 0.88
	mat_pillar_granite.metallic = 0.0 # Non-metallic natural stone
	mat_pillar_granite.metallic_specular = 0.15 # Subtle natural stone sheen without glare
	mat_pillar_granite.uv1_triplanar = true
	mat_pillar_granite.uv1_world_triplanar = true
	mat_pillar_granite.uv1_triplanar_sharpness = 2.0
	mat_pillar_granite.uv1_scale = Vector3(0.55, 0.55, 0.55)
	mat_pillar_granite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	var pillars_node = get_node_or_null("Four_Pillars")
	if pillars_node:
		_apply_override_material_recursive(pillars_node, mat_pillar_granite)
		_set_gi_static_recursive(pillars_node)
		print("[Main] Four_Pillars assigned Naga-Stone Granite PBR Material!")

	# Dedicated authentic carved granite material for Naga Pillars using naga_granite_solid texture & normal map
	var mat_naga_granite = StandardMaterial3D.new()
	mat_naga_granite.resource_name = "Naga_Pillar_Authentic_Granite_PBR"
	mat_naga_granite.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_naga_granite.albedo_color = Color(1.15, 1.15, 1.15) # Matches approved temple granite tone
	mat_naga_granite.albedo_texture = load("res://assets/textures/naga_granite_solid.png")
	mat_naga_granite.normal_enabled = true
	mat_naga_granite.normal_texture = load("res://assets/textures/naga_normal.png")
	mat_naga_granite.normal_scale = 1.2
	mat_naga_granite.roughness = 0.88
	mat_naga_granite.metallic = 0.0
	mat_naga_granite.metallic_specular = 0.15
	mat_naga_granite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# Setup Naga Pillars distributed across the steps in geometric order with front-facing snake
	_setup_naga_pillars(mat_naga_granite)

	# Assign ashlar slate pavers granite material to Mandapa floor between pillars
	var mandapa_floor: MeshInstance3D = get_node_or_null("Mandapa_Granite_Floor")
	if mandapa_floor:
		mandapa_floor.material_override = mat_granite
		mandapa_floor.gi_mode = GeometryInstance3D.GI_MODE_STATIC
		print("[Main] Assigned Ashlar Slate Pavers Granite Material to Mandapa_Granite_Floor!")

	# Linga Decor Sacred Bronze Mandala PBR Material
	var mat_linga = StandardMaterial3D.new()
	mat_linga.resource_name = "Linga_Decor_Bronze_PBR"
	mat_linga.albedo_texture = load("res://assets/textures/linga_decor_color.png")
	mat_linga.normal_enabled = true
	mat_linga.normal_texture = load("res://assets/textures/linga_decor_normal.png")
	mat_linga.normal_scale = 1.4
	mat_linga.roughness_texture = load("res://assets/textures/linga_decor_roughness.png")
	mat_linga.metallic = 0.85
	mat_linga.metallic_specular = 0.35
	mat_linga.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	mat_linga.alpha_scissor_threshold = 0.05
	mat_linga.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_linga.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	var linga_decor = get_node_or_null("Linga_Decor")
	if linga_decor:
		_apply_override_material_recursive(linga_decor, mat_linga)
		_set_gi_static_recursive(linga_decor)
		print("[Main] Assigned Linga Decor Bronze PBR Material to Linga_Decor!")

	# Saptarishi Panel Sacred Black Granite Relief PBR Material
	var mat_saptarishi = StandardMaterial3D.new()
	mat_saptarishi.resource_name = "Saptarishi_Black_Granite_PBR"
	mat_saptarishi.albedo_texture = load("res://assets/textures/saptarishi_color.png")
	mat_saptarishi.normal_enabled = true
	mat_saptarishi.normal_texture = load("res://assets/textures/saptarishi_normal.png")
	mat_saptarishi.normal_scale = 1.6
	mat_saptarishi.roughness_texture = load("res://assets/textures/saptarishi_roughness.png")
	mat_saptarishi.metallic = 0.15
	mat_saptarishi.metallic_specular = 0.50
	mat_saptarishi.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_saptarishi.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	var saptarishi = get_node_or_null("Saptarishi_Panel")
	if saptarishi:
		_apply_override_material_recursive(saptarishi, mat_saptarishi)
		_set_gi_static_recursive(saptarishi)
		print("[Main] Assigned Saptarishi Black Granite PBR Material to Saptarishi_Panel!")

	# Barrier PBR Material (Alpha Scissor for wire mesh, solid black metallic for 3D posts)
	var mat_barrier = StandardMaterial3D.new()
	mat_barrier.resource_name = "Black_Barrier_PBR"
	mat_barrier.albedo_texture = load("res://assets/textures/barrier_color.png")
	mat_barrier.normal_enabled = true
	mat_barrier.normal_texture = load("res://assets/textures/barrier_normal.png")
	mat_barrier.normal_scale = 1.2
	mat_barrier.roughness_texture = load("res://assets/textures/barrier_roughness.png")
	mat_barrier.metallic = 0.50
	mat_barrier.metallic_specular = 0.40
	mat_barrier.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	mat_barrier.alpha_scissor_threshold = 0.08
	mat_barrier.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_barrier.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	_setup_barriers(mat_barrier)

func _setup_barriers(mat_barrier: Material):
	var barriers_parent = get_node_or_null("Barriers")
	if not barriers_parent:
		return

	for child in barriers_parent.get_children():
		child.queue_free()

	var barrier_scene: PackedScene = load("res://assets/barrier_module.glb")
	if not barrier_scene:
		print("[Main] Warning: barrier_module.glb not found!")
		return

	var barrier_col_shape = BoxShape3D.new()
	barrier_col_shape.size = Vector3(5.0, 1.25, 0.20)

	# Barrier instances: [Vector3(pos), float(yaw_deg)]
	# A. Left Step Flank (X = -39.8m) along the landings & terrace
	var barrier_configs: Array = [
		[Vector3(-39.8, 0.36, 41.55), 90.0],
		[Vector3(-39.8, 0.72, 39.25), 90.0],
		[Vector3(-39.8, 1.08, 36.95), 90.0],
		[Vector3(-39.8, 1.44, 32.90), 90.0],
		[Vector3(-39.8, 1.44, 27.90), 90.0],
		[Vector3(-39.8, 1.80, 23.85), 90.0],
		[Vector3(-39.8, 2.16, 21.55), 90.0],

		# B. Right Step Flank (X = +39.8m)
		[Vector3( 39.8, 0.36, 41.55), -90.0],
		[Vector3( 39.8, 0.72, 39.25), -90.0],
		[Vector3( 39.8, 1.08, 36.95), -90.0],
		[Vector3( 39.8, 1.44, 32.90), -90.0],
		[Vector3( 39.8, 1.44, 27.90), -90.0],
		[Vector3( 39.8, 1.80, 23.85), -90.0],
		[Vector3( 39.8, 2.16, 21.55), -90.0],
	]

	# C. Top Platform Left Edge (X = -39.8m, Y = 2.52m) from Z = 17.5 to Z = -17.5
	var z_coords_side = [17.5, 12.5, 7.5, 2.5, -2.5, -7.5, -12.5, -17.5]
	for z in z_coords_side:
		barrier_configs.append([Vector3(-39.8, 2.52, z), 90.0])
		barrier_configs.append([Vector3( 39.8, 2.52, z), -90.0])

	# D. Top Platform Rear Edge (Z = -18.5m, Y = 2.52m) spanning X from -37.5 to +37.5 (behind Adiyogi)
	var x_coords_rear = [-37.5, -32.5, -27.5, -22.5, -17.5, -12.5, -7.5, -2.5, 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5]
	for x in x_coords_rear:
		barrier_configs.append([Vector3(x, 2.52, -18.5), 0.0])

	for i in range(barrier_configs.size()):
		var cfg = barrier_configs[i]
		var pos: Vector3 = cfg[0]
		var rot_y_deg: float = cfg[1]

		var sb = StaticBody3D.new()
		sb.name = "Barrier_" + str(i + 1)
		sb.position = pos
		sb.rotation_degrees = Vector3(0.0, rot_y_deg, 0.0)

		var vis = barrier_scene.instantiate()
		vis.name = "Visual"
		sb.add_child(vis)
		_apply_override_material_recursive(vis, mat_barrier)
		_set_gi_static_recursive(vis)

		var col = CollisionShape3D.new()
		col.name = "Col"
		col.shape = barrier_col_shape
		col.position = Vector3(0.0, 0.625, 0.0)
		sb.add_child(col)

		barriers_parent.add_child(sb)

	print("[Main] Successfully spawned ", barrier_configs.size(), " 3D barrier modules enclosing perimeter except front!")

func _setup_naga_pillars(mat_naga: Material):
	var naga_parent = get_node_or_null("Naga_Pillars")
	if not naga_parent:
		naga_parent = Node3D.new()
		naga_parent.name = "Naga_Pillars"
		add_child(naga_parent)

	for child in naga_parent.get_children():
		child.queue_free()

	var naga_scene: PackedScene = load("res://assets/naga_pillar.glb")
	if not naga_scene:
		print("[Main] Warning: naga_pillar.glb not found!")
		return

	var col_shape = BoxShape3D.new()
	col_shape.size = Vector3(0.66, 1.35, 0.66)

	# Staggered geometric distribution across step landings matching Adiyogi aerial reference
	# Central corridor (X in [-6, +6]) kept clear for processional ascent
	var configs = []

	# Tier 1: Landing 1 (Y = 0.36m, Z = 41.55m) - lower steps
	for x in [-34.0, -22.0, -10.0, 10.0, 22.0, 34.0]:
		configs.append(Vector3(x, 0.36, 41.55))

	# Tier 2: Landing 2 (Y = 0.72m, Z = 39.25m) - staggered
	for x in [-28.0, -16.0, 16.0, 28.0]:
		configs.append(Vector3(x, 0.72, 39.25))

	# Tier 3: Landing 3 (Y = 1.08m, Z = 36.95m) - staggered
	for x in [-33.0, -21.0, -9.0, 9.0, 21.0, 33.0]:
		configs.append(Vector3(x, 1.08, 36.95))

	# Tier 4: Terrace Lip (Y = 1.44m, Z = 35.10m) - flanking the Mandapa approach
	for x in [-26.0, -14.0, 14.0, 26.0]:
		configs.append(Vector3(x, 1.44, 35.10))

	# Tier 5: Landing 5 (Y = 1.80m, Z = 23.85m) - behind Mandapa leading up to Adiyogi
	for x in [-22.0, -10.0, 10.0, 22.0]:
		configs.append(Vector3(x, 1.80, 23.85))

	# Tier 6: Landing 6 (Y = 2.16m, Z = 21.55m) - upper landing
	for x in [-28.0, -16.0, 16.0, 28.0]:
		configs.append(Vector3(x, 2.16, 21.55))

	for i in range(configs.size()):
		var pos = configs[i]
		var sb = StaticBody3D.new()
		sb.name = "Naga_Pillar_" + str(i + 1)
		sb.position = pos
		# Facing +Z towards climbing pilgrims/players (snake relief facing front)
		sb.rotation_degrees = Vector3(0.0, 90.0, 0.0)

		var vis = naga_scene.instantiate()
		vis.name = "Visual"
		sb.add_child(vis)
		_apply_override_material_recursive(vis, mat_naga)
		_set_gi_static_recursive(vis)

		var col = CollisionShape3D.new()
		col.name = "Col"
		col.shape = col_shape
		col.position = Vector3(0.0, 0.675, 0.0)
		sb.add_child(col)

		naga_parent.add_child(sb)

	print("[Main] Successfully spawned ", configs.size(), " darker granite Naga Pillars across the steps in geometric order!")

func _apply_override_material_recursive(node: Node, mat: Material):
	if node is MeshInstance3D:
		var mi = node as MeshInstance3D
		mi.material_override = mat
		mi.gi_mode = GeometryInstance3D.GI_MODE_STATIC
	for c in node.get_children():
		_apply_override_material_recursive(c, mat)

func _set_gi_static_recursive(node: Node):
	if node is MeshInstance3D:
		var mi = node as MeshInstance3D
		mi.gi_mode = GeometryInstance3D.GI_MODE_STATIC
	for c in node.get_children():
		_set_gi_static_recursive(c)

func _apply_adiyogi_materials_recursive(node: Node, mat_body: Material, mat_moon: Material, mat_vibuthi: Material, mat_earrings: Material):
	if node is MeshInstance3D:
		var mesh_inst = node as MeshInstance3D
		mesh_inst.gi_mode = GeometryInstance3D.GI_MODE_STATIC
		var surface_count = mesh_inst.get_surface_override_material_count()
		if surface_count == 0 and mesh_inst.mesh:
			surface_count = mesh_inst.mesh.get_surface_count()
		
		if surface_count >= 4:
			mesh_inst.set_surface_override_material(0, mat_body)
			mesh_inst.set_surface_override_material(1, mat_moon)
			mesh_inst.set_surface_override_material(2, mat_vibuthi)
			mesh_inst.set_surface_override_material(3, mat_earrings)
			# Any additional surfaces (e.g. 4) default to body
			for s in range(4, surface_count):
				mesh_inst.set_surface_override_material(s, mat_body)
			print("[Main] Assigned dedicated Adiyogi materials (Obsidian Body, Glowing Moon, Blunt-to-Sharp Glowing Vibuthi, Copper Earrings) to: ", node.name)
		elif surface_count > 1:
			mesh_inst.set_surface_override_material(0, mat_body)
			mesh_inst.set_surface_override_material(1, mat_moon)
			print("[Main] Assigned multi-surface materials to: ", node.name)
		else:
			mesh_inst.material_override = mat_body
			print("[Main] Assigned Obsidian Black Metallic to: ", node.name)
	
	for child in node.get_children():
		_apply_adiyogi_materials_recursive(child, mat_body, mat_moon, mat_vibuthi, mat_earrings)

func _apply_material_recursive(node: Node, mat_granite: Material, mat_inlay: Material):
	if node is MeshInstance3D:
		var mesh_inst = node as MeshInstance3D
		mesh_inst.gi_mode = GeometryInstance3D.GI_MODE_STATIC
		var node_name = node.name.to_lower()
		if "inlay" in node_name or "red" in node_name:
			node.material_override = mat_inlay
			print("[Main] Assigned BlendKit Stacked Brick Step Tiles Material to: ", node.name)
		else:
			node.material_override = mat_granite
			print("[Main] Assigned BlendKit Ashlar Slate Pavers Material to: ", node.name)
	
	for child in node.get_children():
		_apply_material_recursive(child, mat_granite, mat_inlay)

func _setup_mandapa_sanctum():
	print("[Main] Setting up Yogeshwar Linga Sanctum: Deep Stepped Kunda, Sacred Water, Submerged Linga & Fitted Square Panels...")

	# 1. Update Mandapa Granite Floor to 10x10m Ashlar Slate Pavers Granite with central hole
	var floor_node = get_node_or_null("Mandapa_Granite_Floor")
	if floor_node and floor_node is MeshInstance3D:
		var floor_mi = floor_node as MeshInstance3D
		floor_mi.mesh = _create_floor_with_hole_mesh(5.0, 0.92)
		floor_mi.position = Vector3(0.0, 1.446, 30.4) # Sits cleanly above underlying step treads
		var mat_granite = StandardMaterial3D.new()
		mat_granite.resource_name = "Mandapa_Ashlar_Slate_Granite"
		mat_granite.albedo_texture = load("res://assets/textures/ashlar_slate_color.jpg")
		mat_granite.normal_enabled = true
		mat_granite.normal_texture = load("res://assets/textures/ashlar_slate_normal.jpg")
		mat_granite.normal_scale = 1.0
		mat_granite.roughness_texture = load("res://assets/textures/ashlar_slate_roughness.jpg")
		mat_granite.roughness = 0.88
		mat_granite.uv1_triplanar = true
		mat_granite.uv1_world_triplanar = true
		mat_granite.uv1_triplanar_sharpness = 2.0
		mat_granite.uv1_scale = Vector3(0.28, 0.28, 0.28)
		mat_granite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
		floor_mi.material_override = mat_granite
		floor_mi.gi_mode = GeometryInstance3D.GI_MODE_STATIC

	# 2. Sanctum Hole (Deep Stepped Kunda Pit with Water Basin)
	var hole_parent = get_node_or_null("Sanctum_Hole")
	if not hole_parent:
		hole_parent = StaticBody3D.new()
		hole_parent.name = "Sanctum_Hole"
		add_child(hole_parent)
	hole_parent.position = Vector3(0.0, 1.446, 30.4)

	for c in hole_parent.get_children():
		c.queue_free()

	# Stepped Kunda Stone Pit with crisp architectural tiers
	var hole_mesh_inst = MeshInstance3D.new()
	hole_mesh_inst.name = "Visual_Kunda"
	hole_mesh_inst.mesh = _create_sanctum_hole_mesh()
	var mat_hole = StandardMaterial3D.new()
	mat_hole.resource_name = "Sanctum_Basin_Black_Granite"
	mat_hole.albedo_color = Color(0.04, 0.04, 0.05)
	mat_hole.metallic = 0.35
	mat_hole.roughness = 0.15
	mat_hole.metallic_specular = 0.70
	mat_hole.cull_mode = BaseMaterial3D.CULL_DISABLED
	hole_mesh_inst.material_override = mat_hole
	hole_mesh_inst.gi_mode = GeometryInstance3D.GI_MODE_STATIC
	hole_parent.add_child(hole_mesh_inst)

	# 3. Sacred Temple Water filling the hole (Jala Arpanam Offering Pool)
	var water_mesh_inst = MeshInstance3D.new()
	water_mesh_inst.name = "Sacred_Water"
	water_mesh_inst.mesh = _create_water_disc_mesh(0.74)
	water_mesh_inst.position = Vector3(0.0, -0.36, 0.0) # Fills 0.34m deep water in the basin

	# Ultra-realistic dynamic water shader with animated ripples, depth absorption & Fresnel reflections
	var mat_water = ShaderMaterial.new()
	var shader = load("res://shaders/water.gdshader")
	if shader:
		mat_water.shader = shader
		mat_water.set_shader_parameter("water_color", Color(0.04, 0.20, 0.24, 0.55))
		mat_water.set_shader_parameter("deep_color", Color(0.01, 0.07, 0.10, 0.88))
		mat_water.set_shader_parameter("roughness", 0.015)
		mat_water.set_shader_parameter("metallic", 0.05)

		var noise = FastNoiseLite.new()
		noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
		noise.frequency = 0.04
		noise.fractal_octaves = 3
		var noise_tex = NoiseTexture2D.new()
		noise_tex.as_normal_map = true
		noise_tex.bump_strength = 2.0
		noise_tex.seamless = true
		noise_tex.noise = noise
		mat_water.set_shader_parameter("noise_tex", noise_tex)
		water_mesh_inst.material_override = mat_water
	else:
		var mat_pbr_water = StandardMaterial3D.new()
		mat_pbr_water.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		mat_pbr_water.albedo_color = Color(0.02, 0.20, 0.28, 0.82)
		mat_pbr_water.roughness = 0.02
		water_mesh_inst.material_override = mat_pbr_water
	water_mesh_inst.gi_mode = GeometryInstance3D.GI_MODE_STATIC
	hole_parent.add_child(water_mesh_inst)

	# 4. Sacred Copper Linga (Yogeshwar Linga / Consecrated Tamra Linga)
	var linga_parent = get_node_or_null("Golden_Egg_Linga")
	if not linga_parent:
		linga_parent = StaticBody3D.new()
		linga_parent.name = "Golden_Egg_Linga"
		add_child(linga_parent)
	# Nestled on the pedestal at y = -0.58m inside the pit, submerged in water (water level is at y = -0.36m)
	linga_parent.position = Vector3(0.0, 1.446 - 0.58, 30.4)

	for c in linga_parent.get_children():
		c.queue_free()

	var linga_mesh_inst = MeshInstance3D.new()
	linga_mesh_inst.name = "Visual"
	# Sacred Yogeshwar Linga: broad cylindrical base resting in water, tapering to a majestic rounded dome apex
	linga_mesh_inst.mesh = _create_egg_linga_mesh(0.36, 0.92, 0.45)
	var mat_copper = StandardMaterial3D.new()
	mat_copper.resource_name = "Sacred_Temple_Copper_PBR"
	# Authentic burnished Indian temple copper (Tamra)
	mat_copper.albedo_color = Color(0.88, 0.52, 0.35) # Pure warm radiant copper
	mat_copper.metallic = 0.98
	mat_copper.roughness = 0.12 # Lustrous, silky burnished metal sheen
	mat_copper.metallic_specular = 0.85
	mat_copper.rim_enabled = true
	mat_copper.rim = 0.45
	mat_copper.rim_tint = 0.75
	mat_copper.clearcoat_enabled = true
	mat_copper.clearcoat = 0.40
	mat_copper.clearcoat_roughness = 0.15
	linga_mesh_inst.material_override = mat_copper
	linga_mesh_inst.gi_mode = GeometryInstance3D.GI_MODE_STATIC
	linga_parent.add_child(linga_mesh_inst)

	# Physics Collision for Linga
	var linga_col = CollisionShape3D.new()
	linga_col.name = "Col"
	var cap = CylinderShape3D.new()
	cap.radius = 0.38
	cap.height = 0.95
	linga_col.shape = cap
	linga_col.position = Vector3(0.0, 0.47, 0.0)
	linga_parent.add_child(linga_col)

	# Divine OmniLights illuminating the water and copper linga inside the hole
	var omni_water = OmniLight3D.new()
	omni_water.name = "Sanctum_Water_Glow"
	omni_water.position = Vector3(0.0, 0.15, 0.0)
	omni_water.light_color = Color(0.35, 0.82, 0.92) # Turquoise underwater luminescence
	omni_water.light_energy = 1.2
	omni_water.omni_range = 2.5
	linga_parent.add_child(omni_water)

	var omni_copper = OmniLight3D.new()
	omni_copper.name = "Sanctum_Copper_Glow"
	omni_copper.position = Vector3(0.0, 0.65, 0.0)
	omni_copper.light_color = Color(1.0, 0.76, 0.52) # Warm copper radiance
	omni_copper.light_energy = 2.0
	omni_copper.omni_range = 4.0
	omni_copper.shadow_enabled = true
	linga_parent.add_child(omni_copper)

	# 5. Square Enclosure of 36 Linga Square Panels (0.65m x 0.65m) around Circle Star
	var panels_parent = get_node_or_null("Linga_Square_Enclosure")
	if not panels_parent:
		panels_parent = Node3D.new()
		panels_parent.name = "Linga_Square_Enclosure"
		add_child(panels_parent)

	for c in panels_parent.get_children():
		c.queue_free()

	var panel_scene: PackedScene = load("res://assets/linga_square_panel.glb")
	if not panel_scene:
		print("[Main] Warning: linga_square_panel.glb not found!")
		return

	# Material for copper yantra panels
	var mat_panel = StandardMaterial3D.new()
	mat_panel.resource_name = "Linga_Square_Panel_Copper_PBR"
	mat_panel.albedo_texture = load("res://assets/textures/linga_square_panel_color.png")
	mat_panel.normal_enabled = false # Mesh does not contain tangents; disable normal map to prevent shader warnings & render hitching
	mat_panel.roughness_texture = load("res://assets/textures/linga_square_panel_roughness.png")
	mat_panel.metallic = 0.85
	mat_panel.metallic_specular = 0.65
	mat_panel.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_panel.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	var panel_col_shape = BoxShape3D.new()
	panel_col_shape.size = Vector3(0.65, 0.04, 0.65)

	var z_center = 30.4
	var panel_configs: Array = []
	# 10 panels across 6.5m (0.65m each, centers at -2.925 to +2.925)
	var coords_full = [-2.925, -2.275, -1.625, -0.975, -0.325, 0.325, 0.975, 1.625, 2.275, 2.925]
	var coords_inner = [-2.275, -1.625, -0.975, -0.325, 0.325, 0.975, 1.625, 2.275]

	# North row (pointing South toward sanctum center)
	for x in coords_full:
		panel_configs.append([Vector3(x, 1.458, z_center + 2.925), 180.0])

	# South row (pointing North toward sanctum center)
	for x in coords_full:
		panel_configs.append([Vector3(x, 1.458, z_center - 2.925), 0.0])

	# West column (pointing East toward sanctum center)
	for dz in coords_inner:
		panel_configs.append([Vector3(-2.925, 1.458, z_center + dz), -90.0])

	# East column (pointing West toward sanctum center)
	for dz in coords_inner:
		panel_configs.append([Vector3(2.925, 1.458, z_center + dz), 90.0])

	for i in range(panel_configs.size()):
		var cfg = panel_configs[i]
		var pos: Vector3 = cfg[0]
		var rot_y: float = cfg[1]

		var sb = StaticBody3D.new()
		sb.name = "Panel_" + str(i + 1)
		sb.position = pos
		sb.rotation_degrees = Vector3(0.0, rot_y, 0.0)

		var vis = panel_scene.instantiate()
		vis.name = "Visual"
		sb.add_child(vis)
		_apply_override_material_recursive(vis, mat_panel)
		_set_gi_static_recursive(vis)

		var col = CollisionShape3D.new()
		col.name = "Col"
		col.shape = panel_col_shape
		col.position = Vector3(0.0, 0.02, 0.0)
		sb.add_child(col)

		panels_parent.add_child(sb)

	print("[Main] Successfully spawned 36 fitted Linga Square Panels enclosing the Circle Star!")

	# 6. Mandapa Roof with Edge Slider and Central Dome (0.3m thick)
	_setup_mandapa_roof()

func _setup_mandapa_roof():
	print("[Main] Assembling 0.3m thick Mandapa Roof with perimeter Edge Slider & Central Dome (R=0.92m)...")
	var roof_parent = get_node_or_null("Mandapa_Roof")
	if not roof_parent:
		roof_parent = StaticBody3D.new()
		roof_parent.name = "Mandapa_Roof"
		add_child(roof_parent)

	# Pillar top is at Y = 1.44 + 2.4384 = 3.8784m.
	# Lintel beams in mandapa_roof.glb extend down by 0.24m (from Y = -0.24m to 0.0m).
	# Placing roof_parent at Y = 3.8784 + 0.24 = 4.1184m rests the beams flush on top of the pillar capitals at Y = 3.8784m!
	roof_parent.position = Vector3(0.0, 3.8784 + 0.24, 30.4)

	for c in roof_parent.get_children():
		c.queue_free()

	var roof_scene: PackedScene = load("res://assets/mandapa_roof.glb")
	if not roof_scene:
		print("[Main] Warning: mandapa_roof.glb not found!")
		return

	var vis = roof_scene.instantiate()
	vis.name = "Visual"
	roof_parent.add_child(vis)

	# Dedicated authentic PBR materials matching the real Isha temple reference image
	# 1. Roof Deck Terracotta Tile Material
	# 1. Roof Deck (Non-Edges) Darker Copper Material
	var mat_deck = StandardMaterial3D.new()
	mat_deck.resource_name = "Mandapa_Roof_Deck_Darker_Copper_PBR"
	mat_deck.albedo_color = Color(0.36, 0.17, 0.11) # Darker patinated temple copper
	mat_deck.normal_enabled = true
	mat_deck.normal_texture = load("res://assets/textures/stacked_brick_normal.png")
	mat_deck.normal_scale = 0.5
	mat_deck.roughness_texture = load("res://assets/textures/stacked_brick_roughness.jpg")
	mat_deck.roughness = 0.30
	mat_deck.metallic = 0.94
	mat_deck.metallic_specular = 0.75
	mat_deck.rim_enabled = true
	mat_deck.rim = 0.40
	mat_deck.rim_tint = 0.65
	mat_deck.clearcoat_enabled = true
	mat_deck.clearcoat = 0.20
	mat_deck.clearcoat_roughness = 0.25
	mat_deck.uv1_scale = Vector3(1.2, 1.2, 1.2)
	mat_deck.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# 2. Roof Edge Slider Dark Copper Trim Material
	var mat_slider = StandardMaterial3D.new()
	mat_slider.resource_name = "Mandapa_Roof_Slider_Dark_Copper_PBR"
	mat_slider.albedo_color = Color(0.50, 0.24, 0.16) # Deep burnished dark copper
	mat_slider.metallic = 0.94
	mat_slider.roughness = 0.26
	mat_slider.metallic_specular = 0.80
	mat_slider.rim_enabled = true
	mat_slider.rim = 0.45
	mat_slider.rim_tint = 0.65
	mat_slider.clearcoat_enabled = true
	mat_slider.clearcoat = 0.25
	mat_slider.clearcoat_roughness = 0.20
	mat_slider.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# 3. Roof Dome Dark Copper Material
	var mat_dome = StandardMaterial3D.new()
	mat_dome.resource_name = "Mandapa_Roof_Dome_Dark_Copper_PBR"
	mat_dome.albedo_color = Color(0.46, 0.22, 0.15) # Sacred dark copper dome
	mat_dome.metallic = 0.96
	mat_dome.roughness = 0.20
	mat_dome.metallic_specular = 0.85
	mat_dome.rim_enabled = true
	mat_dome.rim = 0.50
	mat_dome.rim_tint = 0.70
	mat_dome.clearcoat_enabled = true
	mat_dome.clearcoat = 0.35
	mat_dome.clearcoat_roughness = 0.15

	# 4. Roof Finial Golden Brass Kalasam Pinnacle Material
	var mat_finial = StandardMaterial3D.new()
	mat_finial.resource_name = "Mandapa_Roof_Finial_Brass_PBR"
	mat_finial.albedo_color = Color(0.95, 0.80, 0.45)
	mat_finial.roughness = 0.14
	mat_finial.metallic = 0.98
	mat_finial.metallic_specular = 0.85
	mat_finial.rim_enabled = true
	mat_finial.rim = 0.50

	# 5. Inner Roof BlenderKit Procedural Terracotta Roof Tiles (Asset 7b72cf72-3029-4550-b413-99f296e53185)
	var mat_ceiling = StandardMaterial3D.new()
	mat_ceiling.resource_name = "Mandapa_Roof_Ceiling_Terracotta_BlendKit_PBR"
	mat_ceiling.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_ceiling.albedo_color = Color(1.0, 1.0, 1.0)
	mat_ceiling.albedo_texture = load("res://assets/textures/terracotta_tiles_color.png")
	mat_ceiling.normal_enabled = true
	mat_ceiling.normal_texture = load("res://assets/textures/terracotta_tiles_normal.png")
	mat_ceiling.normal_scale = 2.0
	mat_ceiling.roughness_texture = load("res://assets/textures/terracotta_tiles_roughness.png")
	mat_ceiling.roughness = 0.80
	mat_ceiling.metallic = 0.0
	mat_ceiling.metallic_specular = 0.15
	mat_ceiling.uv1_triplanar = true
	mat_ceiling.uv1_world_triplanar = true
	mat_ceiling.uv1_triplanar_sharpness = 2.0
	mat_ceiling.uv1_scale = Vector3(0.40, 0.40, 0.40)
	mat_ceiling.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# 6. Roof Lintel Support Beams Teak Wood Material (Solid dark teak timber)
	var mat_beams = StandardMaterial3D.new()
	mat_beams.resource_name = "Mandapa_Roof_Beams_Wood_PBR"
	mat_beams.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_beams.albedo_color = Color(0.90, 0.80, 0.75)
	mat_beams.albedo_texture = load("res://assets/textures/dark_wood_diff_2k.jpg")
	mat_beams.normal_enabled = true
	mat_beams.normal_texture = load("res://assets/textures/dark_wood_nor_gl_2k.jpg")
	mat_beams.normal_scale = 1.0
	mat_beams.roughness_texture = load("res://assets/textures/dark_wood_rough_2k.jpg")
	mat_beams.roughness = 0.60
	mat_beams.metallic = 0.0
	mat_beams.metallic_specular = 0.25
	mat_beams.uv1_triplanar = true
	mat_beams.uv1_world_triplanar = true
	mat_beams.uv1_triplanar_sharpness = 2.0
	mat_beams.uv1_scale = Vector3(0.50, 0.50, 0.50)
	mat_beams.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	_apply_roof_materials(vis, mat_deck, mat_slider, mat_dome, mat_finial, mat_ceiling, mat_beams)
	_set_gi_static_recursive(vis)

	# Physics Collision for Roof Slab (11.6m x 0.30m x 10.6m)
	var col_slab = CollisionShape3D.new()
	col_slab.name = "Col_Slab"
	var slab_box = BoxShape3D.new()
	slab_box.size = Vector3(11.6, 0.30, 10.6)
	col_slab.shape = slab_box
	col_slab.position = Vector3(0.0, 0.15, 0.0)
	roof_parent.add_child(col_slab)

	# Physics Collision for Dome (radius = 0.92m matching the hole under)
	var col_dome = CollisionShape3D.new()
	col_dome.name = "Col_Dome"
	var dome_shape = CylinderShape3D.new()
	dome_shape.radius = 0.92
	dome_shape.height = 0.74
	col_dome.shape = dome_shape
	col_dome.position = Vector3(0.0, 0.30 + 0.37, 0.0)
	roof_parent.add_child(col_dome)

	print("[Main] Successfully assembled 0.3m thick Mandapa Roof with Edge Slider and central Dome (R=0.92m)!")

func _apply_roof_materials(node: Node, m_deck: Material, m_slider: Material, m_dome: Material, m_finial: Material, m_ceiling: Material, m_beams: Material):
	if node is MeshInstance3D:
		var mi = node as MeshInstance3D
		mi.gi_mode = GeometryInstance3D.GI_MODE_STATIC
		var sc = mi.get_surface_override_material_count()
		if sc == 0 and mi.mesh:
			sc = mi.mesh.get_surface_count()
		if sc >= 6:
			mi.set_surface_override_material(0, m_deck)
			mi.set_surface_override_material(1, m_slider)
			mi.set_surface_override_material(2, m_dome)
			mi.set_surface_override_material(3, m_finial)
			mi.set_surface_override_material(4, m_ceiling)
			mi.set_surface_override_material(5, m_beams)
		elif sc >= 5:
			mi.set_surface_override_material(0, m_deck)
			mi.set_surface_override_material(1, m_slider)
			mi.set_surface_override_material(2, m_dome)
			mi.set_surface_override_material(3, m_finial)
			mi.set_surface_override_material(4, m_ceiling)
		elif sc > 0:
			mi.set_surface_override_material(0, m_deck)
	for c in node.get_children():
		_apply_roof_materials(c, m_deck, m_slider, m_dome, m_finial, m_ceiling, m_beams)

func _create_floor_with_hole_mesh(half_size: float, hole_radius: float) -> ArrayMesh:
	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var sectors = 64
	for j in range(sectors):
		var phi0 = float(j) * 2.0 * PI / float(sectors)
		var phi1 = float(j + 1) * 2.0 * PI / float(sectors)
		var c0 = cos(phi0)
		var s0 = sin(phi0)
		var c1 = cos(phi1)
		var s1 = sin(phi1)

		var p_in0 = Vector3(hole_radius * c0, 0.0, hole_radius * s0)
		var p_in1 = Vector3(hole_radius * c1, 0.0, hole_radius * s1)

		var t0_x = half_size / abs(c0) if abs(c0) > 0.0001 else 10000.0
		var t0_z = half_size / abs(s0) if abs(s0) > 0.0001 else 10000.0
		var t0 = min(t0_x, t0_z)
		var p_out0 = Vector3(t0 * c0, 0.0, t0 * s0)

		var t1_x = half_size / abs(c1) if abs(c1) > 0.0001 else 10000.0
		var t1_z = half_size / abs(s1) if abs(s1) > 0.0001 else 10000.0
		var t1 = min(t1_x, t1_z)
		var p_out1 = Vector3(t1 * c1, 0.0, t1 * s1)

		st.set_normal(Vector3.UP)
		st.set_uv(Vector2(p_in0.x / 10.0 + 0.5, p_in0.z / 10.0 + 0.5))
		st.add_vertex(p_in0)

		st.set_normal(Vector3.UP)
		st.set_uv(Vector2(p_out0.x / 10.0 + 0.5, p_out0.z / 10.0 + 0.5))
		st.add_vertex(p_out0)

		st.set_normal(Vector3.UP)
		st.set_uv(Vector2(p_out1.x / 10.0 + 0.5, p_out1.z / 10.0 + 0.5))
		st.add_vertex(p_out1)

		st.set_normal(Vector3.UP)
		st.set_uv(Vector2(p_in0.x / 10.0 + 0.5, p_in0.z / 10.0 + 0.5))
		st.add_vertex(p_in0)

		st.set_normal(Vector3.UP)
		st.set_uv(Vector2(p_out1.x / 10.0 + 0.5, p_out1.z / 10.0 + 0.5))
		st.add_vertex(p_out1)

		st.set_normal(Vector3.UP)
		st.set_uv(Vector2(p_in1.x / 10.0 + 0.5, p_in1.z / 10.0 + 0.5))
		st.add_vertex(p_in1)

	st.generate_normals()
	st.generate_tangents()
	return st.commit()

func _create_water_disc_mesh(radius: float) -> ArrayMesh:
	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var sectors = 64
	st.set_normal(Vector3.UP)
	st.set_uv(Vector2(0.5, 0.5))
	st.add_vertex(Vector3.ZERO)

	for j in range(sectors + 1):
		var phi = float(j) * 2.0 * PI / float(sectors)
		var c = cos(phi)
		var s = sin(phi)
		st.set_normal(Vector3.UP)
		st.set_uv(Vector2(0.5 + 0.5 * c, 0.5 + 0.5 * s))
		st.add_vertex(Vector3(radius * c, 0.0, radius * s))

	for j in range(sectors):
		st.add_index(0)
		st.add_index(j + 1)
		st.add_index(j + 2)

	st.generate_normals()
	st.generate_tangents()
	return st.commit()

func _create_egg_linga_mesh(radius: float, height: float, _taper: float) -> ArrayMesh:
	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var rings = 48
	var sectors = 96
	for i in range(rings + 1):
		var v = float(i) / float(rings)
		var y = height * v
		var r: float = 0.0
		if v < 0.40:
			# Broad cylindrical lower base seated firmly in the water
			r = radius * (1.0 - 0.05 * (0.40 - v))
		else:
			# Sacred parabolic dome curving smoothly to the apex
			var t = (v - 0.40) / 0.60
			r = radius * sqrt(max(0.0, 1.0 - t * t))

		for j in range(sectors + 1):
			var u = float(j) / float(sectors)
			var phi = u * 2.0 * PI
			var x = r * cos(phi)
			var z = r * sin(phi)
			st.set_uv(Vector2(u, v))
			st.add_vertex(Vector3(x, y, z))

	for i in range(rings):
		for j in range(sectors):
			var p1 = i * (sectors + 1) + j
			var p2 = p1 + 1
			var p3 = (i + 1) * (sectors + 1) + j
			var p4 = p3 + 1
			st.add_index(p1)
			st.add_index(p2)
			st.add_index(p3)
			st.add_index(p2)
			st.add_index(p4)
			st.add_index(p3)

	# Bottom base cap
	var bot_idx = (rings + 1) * (sectors + 1)
	st.set_uv(Vector2(0.5, 0.5))
	st.add_vertex(Vector3.ZERO)
	for j in range(sectors):
		st.add_index(bot_idx)
		st.add_index(j + 1)
		st.add_index(j)

	st.generate_normals()
	st.generate_tangents()
	return st.commit()

func _create_sanctum_hole_mesh() -> ArrayMesh:
	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var sectors = 64

	# Helper to build vertical cylinder walls with horizontal inward/outward normals
	var add_wall = func(r: float, y_top: float, y_bot: float, inward: bool):
		var base = st.get_vertex_count() if st.has_method("get_vertex_count") else 0
		# SurfaceTool doesn't have get_vertex_count directly in all versions, we build directly with add_vertex:
		for j in range(sectors):
			var phi0 = float(j) * 2.0 * PI / float(sectors)
			var phi1 = float(j + 1) * 2.0 * PI / float(sectors)
			var c0 = cos(phi0)
			var s0 = sin(phi0)
			var c1 = cos(phi1)
			var s1 = sin(phi1)
			var n0 = Vector3(-c0, 0.0, -s0) if inward else Vector3(c0, 0.0, s0)
			var n1 = Vector3(-c1, 0.0, -s1) if inward else Vector3(c1, 0.0, s1)

			var v_top0 = Vector3(r * c0, y_top, r * s0)
			var v_bot0 = Vector3(r * c0, y_bot, r * s0)
			var v_top1 = Vector3(r * c1, y_top, r * s1)
			var v_bot1 = Vector3(r * c1, y_bot, r * s1)

			st.set_normal(n0)
			st.set_uv(Vector2(float(j)/float(sectors), 0.0))
			st.add_vertex(v_top0)

			st.set_normal(n1)
			st.set_uv(Vector2(float(j+1)/float(sectors), 1.0))
			st.add_vertex(v_bot1)

			st.set_normal(n0)
			st.set_uv(Vector2(float(j)/float(sectors), 1.0))
			st.add_vertex(v_bot0)

			st.set_normal(n0)
			st.set_uv(Vector2(float(j)/float(sectors), 0.0))
			st.add_vertex(v_top0)

			st.set_normal(n1)
			st.set_uv(Vector2(float(j+1)/float(sectors), 0.0))
			st.add_vertex(v_top1)

			st.set_normal(n1)
			st.set_uv(Vector2(float(j+1)/float(sectors), 1.0))
			st.add_vertex(v_bot1)

	var add_tread = func(r_out: float, r_in: float, y: float):
		for j in range(sectors):
			var phi0 = float(j) * 2.0 * PI / float(sectors)
			var phi1 = float(j + 1) * 2.0 * PI / float(sectors)
			var c0 = cos(phi0)
			var s0 = sin(phi0)
			var c1 = cos(phi1)
			var s1 = sin(phi1)

			var v_out0 = Vector3(r_out * c0, y, r_out * s0)
			var v_in0  = Vector3(r_in  * c0, y, r_in  * s0)
			var v_out1 = Vector3(r_out * c1, y, r_out * s1)
			var v_in1  = Vector3(r_in  * c1, y, r_in  * s1)

			st.set_normal(Vector3.UP)
			st.set_uv(Vector2(0.5 + 0.5 * c0, 0.5 + 0.5 * s0))
			st.add_vertex(v_out0)

			st.set_normal(Vector3.UP)
			st.set_uv(Vector2(0.5 + 0.5 * c1, 0.5 + 0.5 * s1))
			st.add_vertex(v_out1)

			st.set_normal(Vector3.UP)
			st.set_uv(Vector2(0.5 + 0.5 * c0, 0.5 + 0.5 * s0))
			st.add_vertex(v_in0)

			st.set_normal(Vector3.UP)
			st.set_uv(Vector2(0.5 + 0.5 * c0, 0.5 + 0.5 * s0))
			st.add_vertex(v_in0)

			st.set_normal(Vector3.UP)
			st.set_uv(Vector2(0.5 + 0.5 * c1, 0.5 + 0.5 * s1))
			st.add_vertex(v_out1)

			st.set_normal(Vector3.UP)
			st.set_uv(Vector2(0.5 + 0.5 * c1, 0.5 + 0.5 * s1))
			st.add_vertex(v_in1)

	# 1. Curb top beveled lip
	add_tread.call(0.94, 0.88, 0.015)

	# 2. Step 1: riser down to y = -0.22, tread from 0.88 to 0.74
	add_wall.call(0.88, 0.015, -0.22, true)
	add_tread.call(0.88, 0.74, -0.22)

	# 3. Step 2: riser down to y = -0.45, tread from 0.74 to 0.60
	add_wall.call(0.74, -0.22, -0.45, true)
	add_tread.call(0.74, 0.60, -0.45)

	# 4. Step 3: riser down to y = -0.70, basin floor from 0.60 to 0.40
	add_wall.call(0.60, -0.45, -0.70, true)
	add_tread.call(0.60, 0.40, -0.70)

	# 5. Lotus pedestal: riser from y = -0.70 up to y = -0.58 at r = 0.40
	add_wall.call(0.40, -0.58, -0.70, false)

	# 6. Pedestal top cap: solid disc at y = -0.58
	for j in range(sectors):
		var phi0 = float(j) * 2.0 * PI / float(sectors)
		var phi1 = float(j + 1) * 2.0 * PI / float(sectors)
		var c0 = cos(phi0)
		var s0 = sin(phi0)
		var c1 = cos(phi1)
		var s1 = sin(phi1)

		st.set_normal(Vector3.UP)
		st.set_uv(Vector2(0.5, 0.5))
		st.add_vertex(Vector3(0.0, -0.58, 0.0))

		st.set_normal(Vector3.UP)
		st.set_uv(Vector2(0.5 + 0.5 * c0, 0.5 + 0.5 * s0))
		st.add_vertex(Vector3(0.40 * c0, -0.58, 0.40 * s0))

		st.set_normal(Vector3.UP)
		st.set_uv(Vector2(0.5 + 0.5 * c1, 0.5 + 0.5 * s1))
		st.add_vertex(Vector3(0.40 * c1, -0.58, 0.40 * s1))

	st.generate_tangents()
	return st.commit()




# ==============================================================================
# LANDSCAPE, 20M EXTRUDED PATHWAY & INDIAN PALM TREES
# ==============================================================================

# ==============================================================================
# LANDSCAPE, 20M EXTRUDED PATHWAY & INDIAN PALM TREES
# ==============================================================================

func _setup_landscape_and_pathway():
	print("[Landscape] Creating uneven terrain, 20m extruded pathway, and Indian trees...")

	# --- 1. Materials ---
	# Pathway: BlenderKit Weathered Stone Grid Tiles
	var mat_path = StandardMaterial3D.new()
	mat_path.resource_name = "Weathered_Stone_Pathway"
	mat_path.albedo_texture = load("res://assets/textures/weathered_stone_BaseColor.jpg")
	mat_path.normal_enabled = true
	mat_path.normal_texture = load("res://assets/textures/weathered_stone_Normal.jpg")
	mat_path.normal_scale = 1.15
	mat_path.roughness_texture = load("res://assets/textures/weathered_stone_Roughness.jpg")
	mat_path.roughness = 0.88
	mat_path.metallic_specular = 0.18
	mat_path.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# Terrain: Red Laterite Mud & Lush Grass blended shader
	var mat_terrain = ShaderMaterial.new()
	mat_terrain.shader = load("res://shaders/terrain_blend.gdshader")
	mat_terrain.set_shader_parameter("mud_albedo", load("res://assets/textures/red_mud_diff_2k.jpg"))
	mat_terrain.set_shader_parameter("mud_normal", load("res://assets/textures/red_mud_nor_gl_2k.jpg"))
	mat_terrain.set_shader_parameter("mud_roughness", load("res://assets/textures/red_mud_rough_2k.jpg"))
	mat_terrain.set_shader_parameter("grass_albedo", load("res://assets/textures/grass_ground_diff_2k.jpg"))
	mat_terrain.set_shader_parameter("grass_normal", load("res://assets/textures/grass_ground_nor_gl_2k.jpg"))
	mat_terrain.set_shader_parameter("grass_roughness", load("res://assets/textures/grass_ground_rough_2k.jpg"))
	mat_terrain.set_shader_parameter("uv_scale", Vector2(0.22, 0.22))

	# --- 2. Build Uneven Mud/Grass Terrain Mesh ---
	var terrain_mesh = _build_terrain_mesh()
	var terrain_node = MeshInstance3D.new()
	terrain_node.name = "Terrain_MudGrass"
	terrain_node.mesh = terrain_mesh
	terrain_node.material_override = mat_terrain
	terrain_node.gi_mode = GeometryInstance3D.GI_MODE_STATIC
	terrain_node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	add_child(terrain_node)
	terrain_node.create_trimesh_collision()
	print("[Landscape] Terrain mesh built and collision generated successfully!")

	# --- 3. Build 20m Extruded Pathway ---
	var pathway_mesh = _build_pathway_mesh()
	var pathway_node = MeshInstance3D.new()
	pathway_node.name = "Pathway_20m_WeatheredStone"
	pathway_node.mesh = pathway_mesh
	pathway_node.material_override = mat_path
	pathway_node.gi_mode = GeometryInstance3D.GI_MODE_STATIC
	pathway_node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	add_child(pathway_node)

	# Pathway Physics Collision
	var physics_body = get_node_or_null("Plaza_Physics")
	if physics_body:
		# Main extruded pathway box: width 20m, height 2m, length 454.5m
		# Top surface is at Y = 0.18m, from Z = 115.5 to Z = 570.0 (center Z = 342.75)
		_add_box_col(physics_body, "Col_Pathway_Main", Vector3(20.0, 2.0, 454.5), Transform3D(Basis(), Vector3(0.0, -0.82, 342.75)))
		# Ramp connection connecting Z = 113.1 (Y=0.0) to Z = 115.5 (Y=0.18)
		_add_box_col(physics_body, "Col_Pathway_Ramp", Vector3(20.0, 0.4, 2.4), Transform3D(Basis(), Vector3(0.0, -0.09, 114.3)))
	print("[Landscape] 20m Extruded stone pathway built from Malai Vasal (Z=570) to Courtyard (Z=113.1)!")

	# --- 3b. Build Dressed Stone Road Side Edges (Curbs) ---
	var mat_curb = StandardMaterial3D.new()
	mat_curb.resource_name = "Ashlar_Slate_Curb_Edges"
	mat_curb.albedo_texture = load("res://assets/textures/ashlar_slate_color.jpg")
	mat_curb.normal_enabled = true
	mat_curb.normal_texture = load("res://assets/textures/ashlar_slate_normal.jpg")
	mat_curb.normal_scale = 1.25
	mat_curb.roughness_texture = load("res://assets/textures/ashlar_slate_roughness.jpg")
	mat_curb.roughness = 0.82
	mat_curb.metallic = 0.0
	mat_curb.metallic_specular = 0.20
	mat_curb.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	var curb_mesh = _build_pathway_curb_mesh()
	var curb_node = MeshInstance3D.new()
	curb_node.name = "Pathway_Curb_Edges"
	curb_node.mesh = curb_mesh
	curb_node.material_override = mat_curb
	curb_node.gi_mode = GeometryInstance3D.GI_MODE_STATIC
	curb_node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	add_child(curb_node)
	print("[Landscape] Built 3D dressed stone curbs along both road sides from Z=113.1 to Z=570.0!")

	# --- 4. Distribute Indian Trees & 3D Vegetation ---
	_setup_trees()
	_setup_3d_plants_and_grass()

func _get_terrain_height(x: float, z: float) -> float:
	# Real natural earth/mud undulation: rolling mounds and gentle swales
	var h = sin(x * 0.055 + 0.6) * 0.22 + cos(z * 0.042 + 1.2) * 0.18 + sin(x * 0.16 + z * 0.12) * 0.08 + cos(x * 0.24 - z * 0.17) * 0.04

	# 1. Suryakund flat precinct bounds (centered at SURYAKUND_POS, rotated by SURYAKUND_ROT_DEG)
	var rel_sk_x = x - SURYAKUND_POS.x
	var rel_sk_z = z - SURYAKUND_POS.z
	var rad_sk = -deg_to_rad(SURYAKUND_ROT_DEG)
	var l_sk_x = rel_sk_x * cos(rad_sk) - rel_sk_z * sin(rad_sk)
	var l_sk_z = rel_sk_x * sin(rad_sk) + rel_sk_z * cos(rad_sk)
	var sk_dx = abs(l_sk_x)
	var sk_dz = abs(l_sk_z)
	if sk_dx <= 46.0 * SURYAKUND_SCALE and sk_dz <= 62.0 * SURYAKUND_SCALE:
		return -0.06 # Foundation bedrock under temple floor at -0.06m (eliminates z-fighting & prevents falling into void)
	elif sk_dx <= 90.0 * SURYAKUND_SCALE and sk_dz <= 90.0 * SURYAKUND_SCALE:
		return 0.0 # Perfectly flat at temple ground level
	elif sk_dx < 135.0 * SURYAKUND_SCALE and sk_dz < 135.0 * SURYAKUND_SCALE:
		var bx = max(0.0, sk_dx - 90.0 * SURYAKUND_SCALE) / (45.0 * SURYAKUND_SCALE)
		var bz = max(0.0, sk_dz - 90.0 * SURYAKUND_SCALE) / (45.0 * SURYAKUND_SCALE)
		var b = clamp(max(bx, bz), 0.0, 1.0)
		return lerp(0.0, h, b)

	# 2. Adiyogi Stepped Plaza and Courtyard bounds: X in [-40.5, 40.5], Z in [-36.0, 113.5]
	# (Stepped plaza sits at Z in [-35.0, 41.0] from Y=0.0 to 2.52; Courtyard sits at Z in [41.0, 113.5])
	if abs(x) <= 40.5 and z >= -36.0 and z <= 113.5:
		return -0.08
	elif abs(x) < 55.0 and z >= -48.0 and z <= 122.0:
		var dx = max(0.0, abs(x) - 40.5) / 14.5
		var dz = 0.0
		if z < -36.0:
			dz = (-36.0 - z) / 12.0
		elif z > 113.5:
			dz = (z - 113.5) / 8.5
		var b = clamp(max(dx, dz), 0.0, 1.0)
		return lerp(-0.08, h, b)

	# 3. 20m Walkway bounds: X in [-10.8, 10.8], Z in [113.0, 575.0]
	if z >= 113.0 and z <= 575.0:
		var abs_x = abs(x)
		if abs_x <= 10.15:
			return -0.08 # Walkway surface (Y=0.0 at ramp to Y=0.18 on main) is safely above this, zero z-fighting!
		elif abs_x < 13.5:
			var bp = (abs_x - 10.15) / 3.35
			return lerp(-0.08, h, bp)

	# 4. Malai Vasal Forecourt & Threshold: X in [-36.0, 36.0], Z in [565.0, 595.0]
	if abs(x) <= 36.0 and z >= 565.0 and z <= 595.0:
		return -0.08

	# 5. Sarpa Vasal Gateway precinct bounds (centered at SARPAVASAL_POS = Vector3(-393.94, 0.0, -431.26))
	var sv_dx = abs(x - SARPAVASAL_POS.x)
	var sv_dz = abs(z - SARPAVASAL_POS.z)
	if sv_dx <= 14.0 * SARPAVASAL_SCALE and sv_dz <= 14.0 * SARPAVASAL_SCALE:
		return -0.05 # Firm foundation bedrock under gateway platform
	elif sv_dx < 26.0 * SARPAVASAL_SCALE and sv_dz < 26.0 * SARPAVASAL_SCALE:
		var bx = max(0.0, sv_dx - 14.0 * SARPAVASAL_SCALE) / (12.0 * SARPAVASAL_SCALE)
		var bz = max(0.0, sv_dz - 14.0 * SARPAVASAL_SCALE) / (12.0 * SARPAVASAL_SCALE)
		var b = clamp(max(bx, bz), 0.0, 1.0)
		return lerp(-0.05, h, b)

	# 6. Sacred Processional Pathway connecting Adiyogi -> Sarpa Vasal -> Suryakund -> Linga Bhairavi
	var p_pt = Vector2(x, z)
	var p_sv = Vector2(SARPAVASAL_POS.x, SARPAVASAL_POS.z)
	var p_adi = Vector2(-35.0, 25.0)
	var p_sk = Vector2(-388.61, -525.49) # Front entrance steps of Suryakund complex
	var p_lb = Vector2(LINGABHAIRAVI_POS.x, LINGABHAIRAVI_POS.z) # Linga Bhairavi Temple Entrance

	# Leg 1: Adiyogi to Sarpa Vasal (aligned directly toward Adiyogi)
	var v1 = p_sv - p_adi
	var l1_sq = v1.length_squared()
	var t1 = clamp((p_pt - p_adi).dot(v1) / l1_sq, 0.0, 1.0)
	var dist_leg1 = (p_pt - (p_adi + t1 * v1)).length()

	# Leg 2: Sarpa Vasal to Suryakund
	var v2 = p_sk - p_sv
	var l2_sq = v2.length_squared()
	var t2 = clamp((p_pt - p_sv).dot(v2) / l2_sq, 0.0, 1.0)
	var dist_leg2 = (p_pt - (p_sv + t2 * v2)).length()

	# Leg 3: Suryakund to Linga Bhairavi (connecting sacred parikrama loop)
	var v3 = p_lb - p_sk
	var l3_sq = v3.length_squared()
	var t3 = clamp((p_pt - p_sk).dot(v3) / l3_sq, 0.0, 1.0)
	var dist_leg3 = (p_pt - (p_sk + t3 * v3)).length()

	var min_path_dist = min(min(dist_leg1, dist_leg2), dist_leg3)
	if min_path_dist <= 6.5:
		return -0.05 # Flat smooth processional walkway
	elif min_path_dist < 11.0:
		var bp = (min_path_dist - 6.5) / 4.5
		return lerp(-0.05, h, bp)

	# 7. Linga Bhairavi Temple precinct bounds (centered at LINGABHAIRAVI_POS, rotated by LINGABHAIRAVI_ROT_DEG)
	var rel_lb_x = x - LINGABHAIRAVI_POS.x
	var rel_lb_z = z - LINGABHAIRAVI_POS.z
	var rad_lb = deg_to_rad(LINGABHAIRAVI_ROT_DEG)
	var l_lb_x = rel_lb_x * cos(rad_lb) - rel_lb_z * sin(rad_lb)
	var l_lb_z = rel_lb_x * sin(rad_lb) + rel_lb_z * cos(rad_lb)
	var lb_abs_x = abs(l_lb_x)
	if lb_abs_x <= 20.0 and l_lb_z >= -26.0 and l_lb_z <= 32.0:
		return -0.06 # Foundation bedrock under temple floor at -0.06m (eliminates z-fighting)
	elif lb_abs_x < 34.0 and l_lb_z > -40.0 and l_lb_z < 44.0:
		var bx = max(0.0, lb_abs_x - 20.0) / 14.0
		var bz = 0.0
		if l_lb_z < -26.0:
			bz = (-26.0 - l_lb_z) / 14.0
		elif l_lb_z > 32.0:
			bz = (l_lb_z - 32.0) / 12.0
		var b = clamp(max(bx, bz), 0.0, 1.0)
		return lerp(-0.06, h, b)

	return h

func _build_terrain_mesh() -> ArrayMesh:
	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)

	# Vast continuous terrain covering Adiyogi, Malai Vasal, and 400m beyond Suryakund (1.4km x 1.95km expanse)
	var x_min = -900.0
	var x_max =  500.0
	var z_min = -1100.0
	var z_max =  850.0

	var nx = 234
	var nz = 325
	var dx = (x_max - x_min) / float(nx) # ~5.98m
	var dz = (z_max - z_min) / float(nz) # 6.00m

	# Cutout bounds for ONLY the subterranean kund pool pit:
	# Inside these bounds, we omit the terrain quad so the pool descends cleanly into the ground
	# Evaluated in rotated local coordinates around SURYAKUND_POS:
	# Pool pit opening: X in [-24.5, +24.5], Z in [-23.0, +10.8] relative to Suryakund center, scaled by SURYAKUND_SCALE.
	var rad_cut = -deg_to_rad(SURYAKUND_ROT_DEG)
	var cos_cut = cos(rad_cut)
	var sin_cut = sin(rad_cut)
	var cut_lx_min = -24.5 * SURYAKUND_SCALE
	var cut_lx_max = 24.5 * SURYAKUND_SCALE
	var cut_lz_min = -23.0 * SURYAKUND_SCALE
	var cut_lz_max = 10.8 * SURYAKUND_SCALE

	var eps = 0.5
	for iz in range(nz):
		var z0 = z_min + float(iz) * dz
		var z1 = z_min + float(iz + 1) * dz
		for ix in range(nx):
			var x0 = x_min + float(ix) * dx
			var x1 = x_min + float(ix + 1) * dx

			var cx = 0.5 * (x0 + x1)
			var cz = 0.5 * (z0 + z1)
			var rcx = cx - SURYAKUND_POS.x
			var rcz = cz - SURYAKUND_POS.z
			var lcx = rcx * cos_cut - rcz * sin_cut
			var lcz = rcx * sin_cut + rcz * cos_cut
			if lcx >= cut_lx_min and lcx <= cut_lx_max and lcz >= cut_lz_min and lcz <= cut_lz_max:
				continue # Skip excavated subterranean kund pit!

			# Cutout for excavated subterranean Linga Bhairavi Temple hall
			var local_lb = Vector3(cx - LINGABHAIRAVI_POS.x, 0.0, cz - LINGABHAIRAVI_POS.z).rotated(Vector3.UP, -deg_to_rad(LINGABHAIRAVI_ROT_DEG))
			if local_lb.x >= -16.0 and local_lb.x <= 16.0 and local_lb.z >= -2.0 and local_lb.z <= 42.0:
				continue # Skip excavated subterranean Linga Bhairavi hall!

			var y00 = _get_terrain_height(x0, z0)
			var y10 = _get_terrain_height(x1, z0)
			var y01 = _get_terrain_height(x0, z1)
			var y11 = _get_terrain_height(x1, z1)

			var n00 = Vector3(_get_terrain_height(x0 - eps, z0) - _get_terrain_height(x0 + eps, z0), 2.0 * eps, _get_terrain_height(x0, z0 - eps) - _get_terrain_height(x0, z0 + eps)).normalized()
			var n10 = Vector3(_get_terrain_height(x1 - eps, z0) - _get_terrain_height(x1 + eps, z0), 2.0 * eps, _get_terrain_height(x1, z0 - eps) - _get_terrain_height(x1, z0 + eps)).normalized()
			var n01 = Vector3(_get_terrain_height(x0 - eps, z1) - _get_terrain_height(x0 + eps, z1), 2.0 * eps, _get_terrain_height(x0, z1 - eps) - _get_terrain_height(x0, z1 + eps)).normalized()
			var n11 = Vector3(_get_terrain_height(x1 - eps, z1) - _get_terrain_height(x1 + eps, z1), 2.0 * eps, _get_terrain_height(x1, z1 - eps) - _get_terrain_height(x1, z1 + eps)).normalized()

			# Triangle 1 (v00, v10, v01)
			st.set_normal(n00)
			st.set_uv(Vector2(x0, z0) * 0.22)
			st.add_vertex(Vector3(x0, y00, z0))

			st.set_normal(n10)
			st.set_uv(Vector2(x1, z0) * 0.22)
			st.add_vertex(Vector3(x1, y10, z0))

			st.set_normal(n01)
			st.set_uv(Vector2(x0, z1) * 0.22)
			st.add_vertex(Vector3(x0, y01, z1))

			# Triangle 2 (v10, v11, v01)
			st.set_normal(n10)
			st.set_uv(Vector2(x1, z0) * 0.22)
			st.add_vertex(Vector3(x1, y10, z0))

			st.set_normal(n11)
			st.set_uv(Vector2(x1, z1) * 0.22)
			st.add_vertex(Vector3(x1, y11, z1))

			st.set_normal(n01)
			st.set_uv(Vector2(x0, z1) * 0.22)
			st.add_vertex(Vector3(x0, y01, z1))

	st.generate_tangents()
	return st.commit()

func _build_pathway_mesh() -> ArrayMesh:
	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)

	var x_left = -10.0
	var x_right = 10.0
	var z_start = 113.1
	var z_ramp_end = 115.5
	var z_end = 570.0

	var y_top = 0.18
	var y_bottom = -0.30

	# Subdivide along Z for smooth lighting and UV mapping
	var segments_ramp = 4
	var segments_main = 180
	var dz_ramp = (z_ramp_end - z_start) / float(segments_ramp)
	var dz_main = (z_end - z_ramp_end) / float(segments_main)

	# --- Top Surface: Ramp section ---
	for i in range(segments_ramp):
		var za = z_start + float(i) * dz_ramp
		var zb = z_start + float(i + 1) * dz_ramp
		var ya = lerp(0.0, y_top, float(i) / float(segments_ramp))
		var yb = lerp(0.0, y_top, float(i + 1) / float(segments_ramp))

		var u0 = 0.0
		var u1 = (x_right - x_left) / 4.0
		var v0 = (za - z_start) / 4.0
		var v1 = (zb - z_start) / 4.0

		var norm = Vector3(0.0, 1.0, -(yb - ya) / dz_ramp).normalized()

		st.set_normal(norm); st.set_uv(Vector2(u0, v0)); st.add_vertex(Vector3(x_left, ya, za))
		st.set_normal(norm); st.set_uv(Vector2(u1, v0)); st.add_vertex(Vector3(x_right, ya, za))
		st.set_normal(norm); st.set_uv(Vector2(u0, v1)); st.add_vertex(Vector3(x_left, yb, zb))

		st.set_normal(norm); st.set_uv(Vector2(u1, v0)); st.add_vertex(Vector3(x_right, ya, za))
		st.set_normal(norm); st.set_uv(Vector2(u1, v1)); st.add_vertex(Vector3(x_right, yb, zb))
		st.set_normal(norm); st.set_uv(Vector2(u0, v1)); st.add_vertex(Vector3(x_left, yb, zb))

	# --- Top Surface: Main section ---
	for i in range(segments_main):
		var za = z_ramp_end + float(i) * dz_main
		var zb = z_ramp_end + float(i + 1) * dz_main

		var u0 = 0.0
		var u1 = (x_right - x_left) / 4.0
		var v0 = (za - z_start) / 4.0
		var v1 = (zb - z_start) / 4.0

		st.set_normal(Vector3.UP); st.set_uv(Vector2(u0, v0)); st.add_vertex(Vector3(x_left, y_top, za))
		st.set_normal(Vector3.UP); st.set_uv(Vector2(u1, v0)); st.add_vertex(Vector3(x_right, y_top, za))
		st.set_normal(Vector3.UP); st.set_uv(Vector2(u0, v1)); st.add_vertex(Vector3(x_left, y_top, zb))

		st.set_normal(Vector3.UP); st.set_uv(Vector2(u1, v0)); st.add_vertex(Vector3(x_right, y_top, za))
		st.set_normal(Vector3.UP); st.set_uv(Vector2(u1, v1)); st.add_vertex(Vector3(x_right, y_top, zb))
		st.set_normal(Vector3.UP); st.set_uv(Vector2(u0, v1)); st.add_vertex(Vector3(x_left, y_top, zb))

	# --- Kerb West (Left Side at X = -10.0, facing -X) ---
	var total_z_segs = segments_ramp + segments_main
	for i in range(total_z_segs):
		var za = z_start + float(i) * (z_end - z_start) / float(total_z_segs)
		var zb = z_start + float(i + 1) * (z_end - z_start) / float(total_z_segs)
		var ya = y_top
		var yb = y_top
		if za < z_ramp_end:
			ya = lerp(0.0, y_top, clamp((za - z_start) / (z_ramp_end - z_start), 0.0, 1.0))
		if zb < z_ramp_end:
			yb = lerp(0.0, y_top, clamp((zb - z_start) / (z_ramp_end - z_start), 0.0, 1.0))

		var u0 = (za - z_start) / 4.0
		var u1 = (zb - z_start) / 4.0
		var v_top = 0.0
		var v_bot = 0.5

		st.set_normal(Vector3.LEFT); st.set_uv(Vector2(u0, v_top)); st.add_vertex(Vector3(x_left, ya, za))
		st.set_normal(Vector3.LEFT); st.set_uv(Vector2(u0, v_bot)); st.add_vertex(Vector3(x_left, y_bottom, za))
		st.set_normal(Vector3.LEFT); st.set_uv(Vector2(u1, v_top)); st.add_vertex(Vector3(x_left, yb, zb))

		st.set_normal(Vector3.LEFT); st.set_uv(Vector2(u1, v_top)); st.add_vertex(Vector3(x_left, yb, zb))
		st.set_normal(Vector3.LEFT); st.set_uv(Vector2(u0, v_bot)); st.add_vertex(Vector3(x_left, y_bottom, za))
		st.set_normal(Vector3.LEFT); st.set_uv(Vector2(u1, v_bot)); st.add_vertex(Vector3(x_left, y_bottom, zb))

	# --- Kerb East (Right Side at X = +10.0, facing +X) ---
	for i in range(total_z_segs):
		var za = z_start + float(i) * (z_end - z_start) / float(total_z_segs)
		var zb = z_start + float(i + 1) * (z_end - z_start) / float(total_z_segs)
		var ya = y_top
		var yb = y_top
		if za < z_ramp_end:
			ya = lerp(0.0, y_top, clamp((za - z_start) / (z_ramp_end - z_start), 0.0, 1.0))
		if zb < z_ramp_end:
			yb = lerp(0.0, y_top, clamp((zb - z_start) / (z_ramp_end - z_start), 0.0, 1.0))

		var u0 = (za - z_start) / 4.0
		var u1 = (zb - z_start) / 4.0
		var v_top = 0.0
		var v_bot = 0.5

		st.set_normal(Vector3.RIGHT); st.set_uv(Vector2(u0, v_top)); st.add_vertex(Vector3(x_right, ya, za))
		st.set_normal(Vector3.RIGHT); st.set_uv(Vector2(u1, v_top)); st.add_vertex(Vector3(x_right, yb, zb))
		st.set_normal(Vector3.RIGHT); st.set_uv(Vector2(u0, v_bot)); st.add_vertex(Vector3(x_right, y_bottom, za))

		st.set_normal(Vector3.RIGHT); st.set_uv(Vector2(u1, v_top)); st.add_vertex(Vector3(x_right, yb, zb))
		st.set_normal(Vector3.RIGHT); st.set_uv(Vector2(u1, v_bot)); st.add_vertex(Vector3(x_right, y_bottom, zb))
		st.set_normal(Vector3.RIGHT); st.set_uv(Vector2(u0, v_bot)); st.add_vertex(Vector3(x_right, y_bottom, za))

	# --- South End Cap (At Malai Vasal Z = 570.0, facing +Z) ---
	var cap_u0 = 0.0
	var cap_u1 = (x_right - x_left) / 4.0
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(cap_u0, 0.0)); st.add_vertex(Vector3(x_left, y_top, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(cap_u0, 0.5)); st.add_vertex(Vector3(x_left, y_bottom, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(cap_u1, 0.0)); st.add_vertex(Vector3(x_right, y_top, z_end))

	st.set_normal(Vector3.BACK); st.set_uv(Vector2(cap_u1, 0.0)); st.add_vertex(Vector3(x_right, y_top, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(cap_u0, 0.5)); st.add_vertex(Vector3(x_left, y_bottom, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(cap_u1, 0.5)); st.add_vertex(Vector3(x_right, y_bottom, z_end))

	st.generate_tangents()
	return st.commit()

func _build_pathway_curb_mesh() -> ArrayMesh:
	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)

	var z_start = 113.1
	var z_ramp_end = 115.5
	var z_end = 570.0
	var segments_ramp = 4
	var segments_main = 180
	var dz_ramp = (z_ramp_end - z_start) / float(segments_ramp)
	var dz_main = (z_end - z_ramp_end) / float(segments_main)
	var total_z = segments_ramp + segments_main

	# Curb stone block length for UV repetition
	var block_len = 1.5

	# West profile points: (x, y_main)
	# Inner edge (flush with walkway stone), chamfer top, outer flat edge, bevel bottom, base deep skirt
	var west_profile = [
		Vector2(-9.45, 0.18),  # P0: flush with cobblestone
		Vector2(-9.55, 0.32),  # P1: top inner chamfer (raised 14cm above road)
		Vector2(-10.15, 0.32), # P2: top outer edge (60cm wide dressed curb)
		Vector2(-10.22, 0.22), # P3: outer bevel bottom
		Vector2(-10.22, -0.65) # P4: base deep in ground skirt
	]
	var west_u = [0.0, 0.12, 0.72, 0.85, 1.65]

	# East profile points: (x, y_main)
	var east_profile = [
		Vector2(9.45, 0.18),  # P0: flush with cobblestone
		Vector2(9.55, 0.32),  # P1: top inner chamfer
		Vector2(10.15, 0.32), # P2: top outer edge
		Vector2(10.22, 0.22), # P3: outer bevel bottom
		Vector2(10.22, -0.65) # P4: base deep in ground skirt
	]
	var east_u = [0.0, 0.12, 0.72, 0.85, 1.65]

	for iz in range(total_z):
		var za: float
		var zb: float
		var factor_a: float
		var factor_b: float

		if iz < segments_ramp:
			za = z_start + float(iz) * dz_ramp
			zb = z_start + float(iz + 1) * dz_ramp
			factor_a = clamp((za - z_start) / (z_ramp_end - z_start), 0.0, 1.0)
			factor_b = clamp((zb - z_start) / (z_ramp_end - z_start), 0.0, 1.0)
		else:
			var j = iz - segments_ramp
			za = z_ramp_end + float(j) * dz_main
			zb = z_ramp_end + float(j + 1) * dz_main
			factor_a = 1.0
			factor_b = 1.0

		var v0 = (za - z_start) / block_len
		var v1 = (zb - z_start) / block_len

		# Build West Curb strips
		for p in range(west_profile.size() - 1):
			var p_a = west_profile[p]
			var p_b = west_profile[p + 1]

			var ya0 = lerp(0.08 * (p_a.y / 0.32), p_a.y, factor_a) if p_a.y > 0.0 else p_a.y
			var ya1 = lerp(0.08 * (p_b.y / 0.32), p_b.y, factor_a) if p_b.y > 0.0 else p_b.y
			var yb0 = lerp(0.08 * (p_a.y / 0.32), p_a.y, factor_b) if p_a.y > 0.0 else p_a.y
			var yb1 = lerp(0.08 * (p_b.y / 0.32), p_b.y, factor_b) if p_b.y > 0.0 else p_b.y

			var v_a0 = Vector3(p_a.x, ya0, za)
			var v_b0 = Vector3(p_b.x, ya1, za)
			var v_a1 = Vector3(p_a.x, yb0, zb)
			var v_b1 = Vector3(p_b.x, yb1, zb)

			var norm = ((v_b0 - v_a0).cross(v_a1 - v_a0)).normalized()
			var ua = west_u[p]
			var ub = west_u[p + 1]

			st.set_normal(norm); st.set_uv(Vector2(ua, v0)); st.add_vertex(v_a0)
			st.set_normal(norm); st.set_uv(Vector2(ub, v0)); st.add_vertex(v_b0)
			st.set_normal(norm); st.set_uv(Vector2(ua, v1)); st.add_vertex(v_a1)

			st.set_normal(norm); st.set_uv(Vector2(ub, v0)); st.add_vertex(v_b0)
			st.set_normal(norm); st.set_uv(Vector2(ub, v1)); st.add_vertex(v_b1)
			st.set_normal(norm); st.set_uv(Vector2(ua, v1)); st.add_vertex(v_a1)

		# Build East Curb strips
		for p in range(east_profile.size() - 1):
			var p_a = east_profile[p]
			var p_b = east_profile[p + 1]

			var ya0 = lerp(0.08 * (p_a.y / 0.32), p_a.y, factor_a) if p_a.y > 0.0 else p_a.y
			var ya1 = lerp(0.08 * (p_b.y / 0.32), p_b.y, factor_a) if p_b.y > 0.0 else p_b.y
			var yb0 = lerp(0.08 * (p_a.y / 0.32), p_a.y, factor_b) if p_a.y > 0.0 else p_a.y
			var yb1 = lerp(0.08 * (p_b.y / 0.32), p_b.y, factor_b) if p_b.y > 0.0 else p_b.y

			var v_a0 = Vector3(p_a.x, ya0, za)
			var v_b0 = Vector3(p_b.x, ya1, za)
			var v_a1 = Vector3(p_a.x, yb0, zb)
			var v_b1 = Vector3(p_b.x, yb1, zb)

			var norm = ((v_a1 - v_a0).cross(v_b0 - v_a0)).normalized()
			var ua = east_u[p]
			var ub = east_u[p + 1]

			st.set_normal(norm); st.set_uv(Vector2(ua, v0)); st.add_vertex(v_a0)
			st.set_normal(norm); st.set_uv(Vector2(ua, v1)); st.add_vertex(v_a1)
			st.set_normal(norm); st.set_uv(Vector2(ub, v0)); st.add_vertex(v_b0)

			st.set_normal(norm); st.set_uv(Vector2(ub, v0)); st.add_vertex(v_b0)
			st.set_normal(norm); st.set_uv(Vector2(ua, v1)); st.add_vertex(v_a1)
			st.set_normal(norm); st.set_uv(Vector2(ub, v1)); st.add_vertex(v_b1)

	# South end caps at z_end = 570.0
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(0, 0)); st.add_vertex(Vector3(-9.45, 0.18, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(0, 1)); st.add_vertex(Vector3(-9.45, -0.65, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(1, 0)); st.add_vertex(Vector3(-10.22, 0.22, z_end))

	st.set_normal(Vector3.BACK); st.set_uv(Vector2(1, 0)); st.add_vertex(Vector3(-10.22, 0.22, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(0, 1)); st.add_vertex(Vector3(-9.45, -0.65, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(1, 1)); st.add_vertex(Vector3(-10.22, -0.65, z_end))

	st.set_normal(Vector3.BACK); st.set_uv(Vector2(0, 0)); st.add_vertex(Vector3(9.45, 0.18, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(1, 0)); st.add_vertex(Vector3(10.22, 0.22, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(0, 1)); st.add_vertex(Vector3(9.45, -0.65, z_end))

	st.set_normal(Vector3.BACK); st.set_uv(Vector2(1, 0)); st.add_vertex(Vector3(10.22, 0.22, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(1, 1)); st.add_vertex(Vector3(10.22, -0.65, z_end))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(0, 1)); st.add_vertex(Vector3(9.45, -0.65, z_end))

	# Courtyard South Border Curbs (West: X in [-40.0, -10.15], East: X in [10.15, 40.0] at Z=113.1)
	var z_c0 = 113.1
	var z_c1 = 113.65
	var y_c_top = 0.08
	var y_c_bot = -0.55

	# West courtyard curb top
	st.set_normal(Vector3.UP); st.set_uv(Vector2(-40.0, z_c0)); st.add_vertex(Vector3(-40.0, y_c_top, z_c0))
	st.set_normal(Vector3.UP); st.set_uv(Vector2(-10.15, z_c0)); st.add_vertex(Vector3(-10.15, y_c_top, z_c0))
	st.set_normal(Vector3.UP); st.set_uv(Vector2(-40.0, z_c1)); st.add_vertex(Vector3(-40.0, y_c_top, z_c1))

	st.set_normal(Vector3.UP); st.set_uv(Vector2(-10.15, z_c0)); st.add_vertex(Vector3(-10.15, y_c_top, z_c0))
	st.set_normal(Vector3.UP); st.set_uv(Vector2(-10.15, z_c1)); st.add_vertex(Vector3(-10.15, y_c_top, z_c1))
	st.set_normal(Vector3.UP); st.set_uv(Vector2(-40.0, z_c1)); st.add_vertex(Vector3(-40.0, y_c_top, z_c1))

	# West courtyard curb south skirt
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(-40.0, 0)); st.add_vertex(Vector3(-40.0, y_c_top, z_c1))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(-10.15, 0)); st.add_vertex(Vector3(-10.15, y_c_top, z_c1))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(-40.0, 1)); st.add_vertex(Vector3(-40.0, y_c_bot, z_c1))

	st.set_normal(Vector3.BACK); st.set_uv(Vector2(-10.15, 0)); st.add_vertex(Vector3(-10.15, y_c_top, z_c1))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(-10.15, 1)); st.add_vertex(Vector3(-10.15, y_c_bot, z_c1))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(-40.0, 1)); st.add_vertex(Vector3(-40.0, y_c_bot, z_c1))

	# East courtyard curb top
	st.set_normal(Vector3.UP); st.set_uv(Vector2(10.15, z_c0)); st.add_vertex(Vector3(10.15, y_c_top, z_c0))
	st.set_normal(Vector3.UP); st.set_uv(Vector2(40.0, z_c0)); st.add_vertex(Vector3(40.0, y_c_top, z_c0))
	st.set_normal(Vector3.UP); st.set_uv(Vector2(10.15, z_c1)); st.add_vertex(Vector3(10.15, y_c_top, z_c1))

	st.set_normal(Vector3.UP); st.set_uv(Vector2(40.0, z_c0)); st.add_vertex(Vector3(40.0, y_c_top, z_c0))
	st.set_normal(Vector3.UP); st.set_uv(Vector2(40.0, z_c1)); st.add_vertex(Vector3(40.0, y_c_top, z_c1))
	st.set_normal(Vector3.UP); st.set_uv(Vector2(10.15, z_c1)); st.add_vertex(Vector3(10.15, y_c_top, z_c1))

	# East courtyard curb south skirt
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(10.15, 0)); st.add_vertex(Vector3(10.15, y_c_top, z_c1))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(40.0, 0)); st.add_vertex(Vector3(40.0, y_c_top, z_c1))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(10.15, 1)); st.add_vertex(Vector3(10.15, y_c_bot, z_c1))

	st.set_normal(Vector3.BACK); st.set_uv(Vector2(40.0, 0)); st.add_vertex(Vector3(40.0, y_c_top, z_c1))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(40.0, 1)); st.add_vertex(Vector3(40.0, y_c_bot, z_c1))
	st.set_normal(Vector3.BACK); st.set_uv(Vector2(10.15, 1)); st.add_vertex(Vector3(10.15, y_c_bot, z_c1))

	st.generate_tangents()
	return st.commit()

func _setup_trees():
	var palm_scene: PackedScene = load("res://assets/models/palm_tree.glb")
	var dense_palm_scene: PackedScene = load("res://assets/models/palm_tree_dense.glb")
	var neem_scene: PackedScene = load("res://assets/models/neem_broadleaf_tree_opt.glb")

	var trees_root = Node3D.new()
	trees_root.name = "Landscape_Trees"
	add_child(trees_root)

	var rng = RandomNumberGenerator.new()
	rng.seed = 108

	# Tree configurations along avenue and in fields:
	# type: 0=Coconut Palm, 1=Neem Broadleaf Tree, 2=Dense Coconut Palm
	var tree_configs = [
		# West Avenue Tree Line (X ~ -16.0)
		{"type": 1, "pos": Vector3(-16.0, 0.0, 132.0), "s_min": 1.7, "s_max": 2.1, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3(-15.8, 0.0, 156.0), "s_min": 1.0, "s_max": 1.2, "r": 0.42, "h": 4.5},
		{"type": 2, "pos": Vector3(-15.5, 0.0, 180.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-16.2, 0.0, 206.0), "s_min": 1.8, "s_max": 2.2, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3(-15.7, 0.0, 232.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-16.0, 0.0, 258.0), "s_min": 1.75, "s_max": 2.15, "r": 0.55, "h": 4.0},
		{"type": 2, "pos": Vector3(-15.6, 0.0, 284.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-16.1, 0.0, 310.0), "s_min": 1.8, "s_max": 2.2, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3(-15.5, 0.0, 336.0), "s_min": 1.02, "s_max": 1.24, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-16.2, 0.0, 362.0), "s_min": 1.85, "s_max": 2.25, "r": 0.55, "h": 4.0},
		{"type": 2, "pos": Vector3(-15.6, 0.0, 388.0), "s_min": 0.98, "s_max": 1.22, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-15.9, 0.0, 414.0), "s_min": 1.75, "s_max": 2.15, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3(-15.7, 0.0, 440.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-16.1, 0.0, 466.0), "s_min": 1.8, "s_max": 2.2, "r": 0.55, "h": 4.0},
		{"type": 2, "pos": Vector3(-15.5, 0.0, 492.0), "s_min": 1.02, "s_max": 1.24, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-16.0, 0.0, 518.0), "s_min": 1.82, "s_max": 2.22, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3(-15.6, 0.0, 542.0), "s_min": 1.05, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-15.8, 0.0, 560.0), "s_min": 1.7, "s_max": 2.1, "r": 0.55, "h": 4.0},

		# East Avenue Tree Line (X ~ +16.0)
		{"type": 0, "pos": Vector3( 15.6, 0.0, 132.0), "s_min": 1.0, "s_max": 1.22, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3( 16.1, 0.0, 156.0), "s_min": 1.75, "s_max": 2.15, "r": 0.55, "h": 4.0},
		{"type": 2, "pos": Vector3( 15.5, 0.0, 180.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3( 16.0, 0.0, 206.0), "s_min": 1.8, "s_max": 2.2, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3( 15.7, 0.0, 232.0), "s_min": 1.02, "s_max": 1.24, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3( 16.2, 0.0, 258.0), "s_min": 1.85, "s_max": 2.25, "r": 0.55, "h": 4.0},
		{"type": 2, "pos": Vector3( 15.5, 0.0, 284.0), "s_min": 1.0, "s_max": 1.22, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3( 15.9, 0.0, 310.0), "s_min": 1.75, "s_max": 2.15, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3( 15.6, 0.0, 336.0), "s_min": 1.0, "s_max": 1.24, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3( 16.1, 0.0, 362.0), "s_min": 1.82, "s_max": 2.22, "r": 0.55, "h": 4.0},
		{"type": 2, "pos": Vector3( 15.5, 0.0, 388.0), "s_min": 1.04, "s_max": 1.26, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3( 16.0, 0.0, 414.0), "s_min": 1.78, "s_max": 2.18, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3( 15.7, 0.0, 440.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3( 16.2, 0.0, 466.0), "s_min": 1.85, "s_max": 2.25, "r": 0.55, "h": 4.0},
		{"type": 2, "pos": Vector3( 15.5, 0.0, 492.0), "s_min": 1.0, "s_max": 1.24, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3( 15.8, 0.0, 518.0), "s_min": 1.75, "s_max": 2.15, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3( 15.6, 0.0, 542.0), "s_min": 1.05, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3( 16.0, 0.0, 560.0), "s_min": 1.8, "s_max": 2.2, "r": 0.55, "h": 4.0},

		# Lateral Field Trees (Open landscape grove depth)
		{"type": 1, "pos": Vector3(-45.0, 0.0, 138.0), "s_min": 1.8, "s_max": 2.2, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3( 42.0, 0.0, 146.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-68.0, 0.0, 215.0), "s_min": 1.9, "s_max": 2.3, "r": 0.55, "h": 4.0},
		{"type": 2, "pos": Vector3( 65.0, 0.0, 245.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 0, "pos": Vector3(-52.0, 0.0, 365.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3( 56.0, 0.0, 445.0), "s_min": 1.8, "s_max": 2.2, "r": 0.55, "h": 4.0},
		{"type": 1, "pos": Vector3(-40.0, 0.0, 490.0), "s_min": 1.8, "s_max": 2.2, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3( 45.0, 0.0, 520.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5},

		# Scenic Landscape Groves between Adiyogi and Suryakund (flanking the winding pilgrimage trail)
		{"type": 1, "pos": Vector3(-92.0, 0.0, -45.0), "s_min": 1.8, "s_max": 2.2, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3(-95.0, 0.0, -105.0), "s_min": 1.05, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 2, "pos": Vector3(-178.0, 0.0, -165.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-202.0, 0.0, -255.0), "s_min": 1.85, "s_max": 2.25, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3(-288.0, 0.0, -325.0), "s_min": 1.02, "s_max": 1.24, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-312.0, 0.0, -425.0), "s_min": 1.8, "s_max": 2.2, "r": 0.55, "h": 4.0},
		{"type": 2, "pos": Vector3(-395.0, 0.0, -490.0), "s_min": 1.0, "s_max": 1.22, "r": 0.42, "h": 4.5},

		# Suryakund Perimeter Groves
		{"type": 1, "pos": Vector3(-495.0, 0.0, -535.0), "s_min": 1.8, "s_max": 2.2, "r": 0.55, "h": 4.0},
		{"type": 0, "pos": Vector3(-505.0, 0.0, -680.0), "s_min": 1.05, "s_max": 1.25, "r": 0.42, "h": 4.5},
		{"type": 1, "pos": Vector3(-320.0, 0.0, -685.0), "s_min": 1.85, "s_max": 2.25, "r": 0.55, "h": 4.0},
		{"type": 2, "pos": Vector3(-315.0, 0.0, -540.0), "s_min": 1.0, "s_max": 1.25, "r": 0.42, "h": 4.5}
	]

	for i in range(tree_configs.size()):
		var cfg = tree_configs[i]
		var scene: PackedScene = null
		var type_name = "Palm"
		match cfg["type"]:
			0:
				scene = palm_scene
				type_name = "CoconutPalm"
			1:
				scene = neem_scene if neem_scene else palm_scene
				type_name = "NeemTree"
			2:
				scene = dense_palm_scene if dense_palm_scene else palm_scene
				type_name = "DensePalm"

		if not scene:
			continue

		var base_pos: Vector3 = cfg["pos"]
		var y_ground = _get_terrain_height(base_pos.x, base_pos.z)
		var tree_inst = scene.instantiate()
		tree_inst.name = type_name + "_" + str(i + 1)

		var s = rng.randf_range(cfg["s_min"], cfg["s_max"])
		tree_inst.scale = Vector3(s, s, s)

		var rot_y = rng.randf_range(0.0, 360.0)
		var tilt_x = rng.randf_range(-1.8, 1.8)
		var tilt_z = rng.randf_range(-1.8, 1.8)
		tree_inst.rotation_degrees = Vector3(tilt_x, rot_y, tilt_z)
		tree_inst.position = Vector3(base_pos.x, y_ground, base_pos.z)

		trees_root.add_child(tree_inst)
		_set_gi_static_recursive(tree_inst)

		# Trunk collision
		var col_body = StaticBody3D.new()
		col_body.name = "Col_" + type_name + "_" + str(i + 1)
		var col_shape = CollisionShape3D.new()
		var cyl = CylinderShape3D.new()
		cyl.radius = cfg["r"] * s
		cyl.height = cfg["h"] * s
		col_shape.shape = cyl
		col_shape.position = Vector3(0.0, (cfg["h"] * 0.5) * s, 0.0)
		col_body.add_child(col_shape)
		col_body.position = Vector3(base_pos.x, y_ground, base_pos.z)
		trees_root.add_child(col_body)

	print("[Landscape] Placed ", tree_configs.size(), " authentic Indian neem shade trees and coconut palms!")

func _setup_3d_plants_and_grass():
	print("[Landscape] Scattering 3D volumetric grass tufts and realistic shrubs along road edges...")
	var root_veg = Node3D.new()
	root_veg.name = "Landscape_Vegetation"
	add_child(root_veg)

	var rng = RandomNumberGenerator.new()
	rng.seed = 2024 # Deterministic natural distribution

	# --- 1. 3D Grass Tufts along curbs and courtyard edges ---
	var grass_scene: PackedScene = load("res://assets/models/grass_tuft_3d.glb")
	if grass_scene:
		var temp_grass = grass_scene.instantiate()
		var grass_mesh: Mesh = null
		for child in temp_grass.get_children():
			if child is MeshInstance3D:
				grass_mesh = child.mesh
				break

		if grass_mesh:
			var grass_positions: Array[Vector3] = []
			var grass_scales: Array[float] = []
			var grass_rots: Array[float] = []

			# A. Along West Curb Edge: Dense 2-row strip at X in [-11.6, -10.25], Z in [116.0, 568.0]
			var cur_z = 116.0
			while cur_z <= 568.0:
				# Row 1: Right against curb
				var gx1 = rng.randf_range(-10.85, -10.28)
				var gz1 = cur_z + rng.randf_range(-0.35, 0.35)
				var gy1 = _get_terrain_height(gx1, gz1)
				grass_positions.append(Vector3(gx1, gy1, gz1))
				grass_scales.append(rng.randf_range(3.2, 5.6))
				grass_rots.append(rng.randf_range(0.0, TAU))

				# Row 2: Slightly outward for plush natural grass verge
				var gx2 = rng.randf_range(-11.55, -10.90)
				var gz2 = cur_z + rng.randf_range(-0.5, 0.5)
				var gy2 = _get_terrain_height(gx2, gz2)
				grass_positions.append(Vector3(gx2, gy2, gz2))
				grass_scales.append(rng.randf_range(3.0, 5.2))
				grass_rots.append(rng.randf_range(0.0, TAU))

				cur_z += rng.randf_range(1.0, 1.6)

			# B. Along East Curb Edge: Dense 2-row strip at X in [10.28, 11.6], Z in [116.0, 568.0]
			cur_z = 116.0
			while cur_z <= 568.0:
				# Row 1: Right against curb
				var gx1 = rng.randf_range(10.28, 10.85)
				var gz1 = cur_z + rng.randf_range(-0.35, 0.35)
				var gy1 = _get_terrain_height(gx1, gz1)
				grass_positions.append(Vector3(gx1, gy1, gz1))
				grass_scales.append(rng.randf_range(3.2, 5.6))
				grass_rots.append(rng.randf_range(0.0, TAU))

				# Row 2: Slightly outward
				var gx2 = rng.randf_range(10.90, 11.55)
				var gz2 = cur_z + rng.randf_range(-0.5, 0.5)
				var gy2 = _get_terrain_height(gx2, gz2)
				grass_positions.append(Vector3(gx2, gy2, gz2))
				grass_scales.append(rng.randf_range(3.0, 5.2))
				grass_rots.append(rng.randf_range(0.0, TAU))

				cur_z += rng.randf_range(1.0, 1.6)

			# C. Along Courtyard South Edge: Z in [113.8, 115.5], X in [-40.0, -11.0] and [11.0, 40.0]
			for step_x in range(45):
				var wx = -40.0 + float(step_x) * 0.65
				var wz = rng.randf_range(113.8, 115.5)
				grass_positions.append(Vector3(wx, _get_terrain_height(wx, wz), wz))
				grass_scales.append(rng.randf_range(3.0, 5.0))
				grass_rots.append(rng.randf_range(0.0, TAU))

				var ex = 11.0 + float(step_x) * 0.65
				var ez = rng.randf_range(113.8, 115.5)
				grass_positions.append(Vector3(ex, _get_terrain_height(ex, ez), ez))
				grass_scales.append(rng.randf_range(3.0, 5.0))
				grass_rots.append(rng.randf_range(0.0, TAU))

			# Create MultiMesh for grass
			var mm_grass = MultiMesh.new()
			mm_grass.transform_format = MultiMesh.TRANSFORM_3D
			mm_grass.mesh = grass_mesh
			mm_grass.instance_count = grass_positions.size()

			for i in range(grass_positions.size()):
				var pos = grass_positions[i]
				var sc = grass_scales[i]
				var ry = grass_rots[i]
				var b = Basis(Vector3.UP, ry).scaled(Vector3(sc, sc, sc))
				mm_grass.set_instance_transform(i, Transform3D(b, pos))

			var mmi_grass = MultiMeshInstance3D.new()
			mmi_grass.name = "Pathway_3D_Grass_Tufts"
			mmi_grass.multimesh = mm_grass
			mmi_grass.gi_mode = GeometryInstance3D.GI_MODE_STATIC
			mmi_grass.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
			root_veg.add_child(mmi_grass)
			print("[Landscape] Placed ", grass_positions.size(), " 3D grass tufts via MultiMeshInstance3D!")
		temp_grass.free()

	# --- 2. 3D Realistic Green Foliage Shrubs along avenue green belts and courtyard ---
	var shrub_scene: PackedScene = load("res://assets/models/realistic_shrub.glb")
	if shrub_scene:
		var temp_shrub = shrub_scene.instantiate()
		var shrub_child = temp_shrub.get_node_or_null("shrub_01_a_LOD0")
		var shrub_mesh: Mesh = null
		if shrub_child is MeshInstance3D:
			shrub_mesh = shrub_child.mesh

		if shrub_mesh:
			var shrub_positions: Array[Vector3] = []
			var shrub_scales: Array[float] = []
			var shrub_rots: Array[float] = []

			# A. West Avenue Green Belt: X in [-14.5, -11.8], Z in [118.0, 560.0]
			var sz = 118.0
			while sz <= 560.0:
				var sx = rng.randf_range(-14.5, -11.8)
				var z_pos = sz + rng.randf_range(-1.0, 1.0)
				var sy = _get_terrain_height(sx, z_pos)
				shrub_positions.append(Vector3(sx, sy, z_pos))
				shrub_scales.append(rng.randf_range(4.5, 7.5))
				shrub_rots.append(rng.randf_range(0.0, TAU))
				sz += rng.randf_range(6.5, 10.5)

			# B. East Avenue Green Belt: X in [11.8, 14.5], Z in [118.0, 560.0]
			sz = 122.0
			while sz <= 560.0:
				var sx = rng.randf_range(11.8, 14.5)
				var z_pos = sz + rng.randf_range(-1.0, 1.0)
				var sy = _get_terrain_height(sx, z_pos)
				shrub_positions.append(Vector3(sx, sy, z_pos))
				shrub_scales.append(rng.randf_range(4.5, 7.5))
				shrub_rots.append(rng.randf_range(0.0, TAU))
				sz += rng.randf_range(6.5, 10.5)

			# C. Courtyard Front Entrance Garden Beds: X in [-38.0, -12.0] & [12.0, 38.0], Z in [114.5, 118.5]
			for step_x in range(16):
				var wx = -38.0 + float(step_x) * 1.6
				var wz = rng.randf_range(114.5, 118.5)
				shrub_positions.append(Vector3(wx, _get_terrain_height(wx, wz), wz))
				shrub_scales.append(rng.randf_range(4.2, 6.8))
				shrub_rots.append(rng.randf_range(0.0, TAU))

				var ex = 12.5 + float(step_x) * 1.6
				var ez = rng.randf_range(114.5, 118.5)
				shrub_positions.append(Vector3(ex, _get_terrain_height(ex, ez), ez))
				shrub_scales.append(rng.randf_range(4.2, 6.8))
				shrub_rots.append(rng.randf_range(0.0, TAU))

			# D. Malai Vasal Entrance Garden Beds: X in [-22.0, -12.5] & [12.5, 22.0], Z in [556.0, 568.0]
			for k in range(8):
				var mx_w = rng.randf_range(-22.0, -12.5)
				var mz_w = rng.randf_range(556.0, 568.0)
				shrub_positions.append(Vector3(mx_w, _get_terrain_height(mx_w, mz_w), mz_w))
				shrub_scales.append(rng.randf_range(4.5, 7.2))
				shrub_rots.append(rng.randf_range(0.0, TAU))

				var mx_e = rng.randf_range(12.5, 22.0)
				var mz_e = rng.randf_range(556.0, 568.0)
				shrub_positions.append(Vector3(mx_e, _get_terrain_height(mx_e, mz_e), mz_e))
				shrub_scales.append(rng.randf_range(4.5, 7.2))
				shrub_rots.append(rng.randf_range(0.0, TAU))

			var mm_shrub = MultiMesh.new()
			mm_shrub.transform_format = MultiMesh.TRANSFORM_3D
			mm_shrub.mesh = shrub_mesh
			mm_shrub.instance_count = shrub_positions.size()

			for i in range(shrub_positions.size()):
				var pos = shrub_positions[i]
				var sc = shrub_scales[i]
				var ry = shrub_rots[i]
				var b = Basis(Vector3.UP, ry).scaled(Vector3(sc, sc, sc))
				mm_shrub.set_instance_transform(i, Transform3D(b, pos))

			var mmi_shrub = MultiMeshInstance3D.new()
			mmi_shrub.name = "Pathway_3D_Shrubs"
			mmi_shrub.multimesh = mm_shrub
			mmi_shrub.gi_mode = GeometryInstance3D.GI_MODE_STATIC
			mmi_shrub.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
			root_veg.add_child(mmi_shrub)
			print("[Landscape] Placed ", shrub_positions.size(), " 3D dense foliage shrubs via MultiMeshInstance3D!")
		temp_shrub.free()

func _setup_malai_vasal():
	print("[MalaiVasal] Constructing monumental Malai Vasal gateway with 235-ton boulder...")

	var mv_root = Node3D.new()
	mv_root.name = "Malai_Vasal_Complex"
	add_child(mv_root)

	# --- 1. Authentic Materials ---
	# 235-ton Granite Monolith Boulder Material
	var mat_boulder = StandardMaterial3D.new()
	mat_boulder.resource_name = "MalaiVasal_235Ton_Boulder"
	mat_boulder.albedo_texture = load("res://assets/textures/weathered_stone_BaseColor.jpg")
	mat_boulder.normal_enabled = true
	mat_boulder.normal_texture = load("res://assets/textures/weathered_stone_Normal.jpg")
	mat_boulder.normal_scale = 1.15
	mat_boulder.roughness_texture = load("res://assets/textures/weathered_stone_Roughness.jpg")
	mat_boulder.roughness = 0.95
	mat_boulder.albedo_color = Color(0.96, 0.94, 0.92)
	mat_boulder.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# Consecrated Golden Kalasha / Pinnacle Dome Material
	var mat_kalasha = StandardMaterial3D.new()
	mat_kalasha.resource_name = "MalaiVasal_Golden_Kalasha"
	mat_kalasha.albedo_color = Color(0.98, 0.78, 0.16)
	mat_kalasha.metallic = 0.92
	mat_kalasha.roughness = 0.22
	mat_kalasha.metallic_specular = 0.90

	# Ashlar Dressed Megalithic Granite Piers & Lintels Material
	var mat_piers = StandardMaterial3D.new()
	mat_piers.resource_name = "MalaiVasal_Ashlar_Granite"
	mat_piers.albedo_texture = load("res://assets/textures/ashlar_slate_color.jpg")
	mat_piers.normal_enabled = true
	mat_piers.normal_texture = load("res://assets/textures/ashlar_slate_normal.jpg")
	mat_piers.normal_scale = 0.85
	mat_piers.roughness_texture = load("res://assets/textures/ashlar_slate_roughness.jpg")
	mat_piers.roughness = 0.90
	mat_piers.albedo_color = Color(0.95, 0.95, 0.93)
	mat_piers.uv1_triplanar = true
	mat_piers.uv1_scale = Vector3(0.35, 0.35, 0.35)
	mat_piers.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# Warm Terracotta Red Laterite Brick Walls Material
	var mat_wall_laterite = StandardMaterial3D.new()
	mat_wall_laterite.resource_name = "MalaiVasal_Red_Laterite"
	mat_wall_laterite.albedo_texture = load("res://assets/textures/stacked_brick_color.jpg")
	mat_wall_laterite.normal_enabled = true
	mat_wall_laterite.normal_texture = load("res://assets/textures/stacked_brick_normal.png")
	mat_wall_laterite.normal_scale = 0.85
	mat_wall_laterite.roughness_texture = load("res://assets/textures/stacked_brick_roughness.jpg")
	mat_wall_laterite.roughness = 0.92
	mat_wall_laterite.albedo_color = Color(1.15, 0.95, 0.88)
	mat_wall_laterite.uv1_triplanar = true
	mat_wall_laterite.uv1_scale = Vector3(0.40, 0.40, 0.40)
	mat_wall_laterite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# Embedded White Rough Granite Relief Panels Material
	var mat_relief = StandardMaterial3D.new()
	mat_relief.resource_name = "MalaiVasal_White_Relief_Granite"
	mat_relief.albedo_texture = load("res://assets/textures/ashlar_slate_color.jpg")
	mat_relief.normal_enabled = true
	mat_relief.normal_texture = load("res://assets/textures/ashlar_slate_normal.jpg")
	mat_relief.albedo_color = Color(1.28, 1.28, 1.25)
	mat_relief.roughness = 0.92
	mat_relief.uv1_triplanar = true
	mat_relief.uv1_scale = Vector3(0.45, 0.45, 0.45)
	mat_relief.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# Traditional Indigenous Tribal Art (Bulls & Dancers) Panel Material
	var mat_tribal_art = StandardMaterial3D.new()
	mat_tribal_art.resource_name = "MalaiVasal_Tribal_Art"
	mat_tribal_art.albedo_texture = load("res://assets/textures/malai_vasal_tribal_art.png")
	mat_tribal_art.roughness = 0.90
	mat_tribal_art.metallic_specular = 0.04
	mat_tribal_art.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# Matte Wrought Iron Security Gates & Trishula Cresting Material
	var mat_iron = StandardMaterial3D.new()
	mat_iron.resource_name = "MalaiVasal_Wrought_Iron"
	mat_iron.albedo_color = Color(0.12, 0.12, 0.13)
	mat_iron.metallic = 0.85
	mat_iron.roughness = 0.40
	mat_iron.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_iron.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# Forecourt Arrival Paving Material
	var mat_forecourt = StandardMaterial3D.new()
	mat_forecourt.resource_name = "MalaiVasal_Forecourt_Cobbles"
	mat_forecourt.albedo_texture = load("res://assets/textures/fan_cobblestone_color.jpg")
	mat_forecourt.normal_enabled = true
	mat_forecourt.normal_texture = load("res://assets/textures/fan_cobblestone_normal.jpg")
	mat_forecourt.normal_scale = 0.65
	mat_forecourt.roughness_texture = load("res://assets/textures/fan_cobblestone_roughness.jpg")
	mat_forecourt.roughness = 0.95
	mat_forecourt.uv1_triplanar = true
	mat_forecourt.uv1_scale = Vector3(0.35, 0.35, 0.35)
	mat_forecourt.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# Helper to create styled BoxMesh nodes
	var make_box = func(b_name: String, size: Vector3, pos: Vector3, mat: Material) -> MeshInstance3D:
		var bm = BoxMesh.new()
		bm.size = size
		var mi = MeshInstance3D.new()
		mi.name = b_name
		mi.mesh = bm
		mi.material_override = mat
		mi.position = pos
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		mi.gi_mode = GeometryInstance3D.GI_MODE_STATIC
		mv_root.add_child(mi)
		return mi

	# --- 2. Raised Ground Plinth & Forecourt Arrival Apron ---
	# Main threshold plinth: width 72m, height 0.22m, depth 10m at Z = 570.0
	make_box.call("MV_Plinth_Threshold", Vector3(72.0, 0.22, 10.0), Vector3(0.0, 0.11, 570.0), mat_forecourt)
	# Forecourt arrival plaza extending south towards Z = 595.0
	make_box.call("MV_Plinth_Forecourt", Vector3(64.0, 0.18, 25.0), Vector3(0.0, 0.09, 582.5), mat_forecourt)

	# --- 3. Colossal Megalithic Main Piers (Frames 12.2m central roadway) ---
	# Left Mega-Pier (Centered at X = -7.5, Z = 570.0)
	make_box.call("MV_Pier_L_Base", Vector3(3.0, 2.8, 4.4), Vector3(-7.5, 1.4, 570.0), mat_piers)
	make_box.call("MV_Pier_L_Shaft", Vector3(2.6, 3.2, 4.0), Vector3(-7.5, 4.4, 570.0), mat_piers)
	make_box.call("MV_Pier_L_Capital", Vector3(2.8, 2.8, 4.2), Vector3(-7.5, 7.4, 570.0), mat_piers)

	# Right Mega-Pier (Centered at X = +7.5, Z = 570.0)
	make_box.call("MV_Pier_R_Base", Vector3(3.0, 2.8, 4.4), Vector3(7.5, 1.4, 570.0), mat_piers)
	make_box.call("MV_Pier_R_Shaft", Vector3(2.6, 3.2, 4.0), Vector3(7.5, 4.4, 570.0), mat_piers)
	make_box.call("MV_Pier_R_Capital", Vector3(2.8, 2.8, 4.2), Vector3(7.5, 7.4, 570.0), mat_piers)

	# --- 4. Pedestrian Portals, Outer Jambs & Mega-Lintel Beams ---
	# Left Pedestrian Outer Pier (X = -12.7)
	make_box.call("MV_Outer_Pier_L", Vector3(1.4, 5.2, 2.6), Vector3(-12.7, 2.6, 570.0), mat_piers)
	# Right Pedestrian Outer Pier (X = +12.7)
	make_box.call("MV_Outer_Pier_R", Vector3(1.4, 5.2, 2.6), Vector3(12.7, 2.6, 570.0), mat_piers)

	# Heavy Monolithic Granite Lintel Beams spanning above pedestrian gates
	make_box.call("MV_Lintel_L", Vector3(4.8, 0.8, 2.4), Vector3(-10.8, 4.8, 570.0), mat_piers)
	make_box.call("MV_Lintel_R", Vector3(4.8, 0.8, 2.4), Vector3(10.8, 4.8, 570.0), mat_piers)

	# Wrought Iron Lattice Security Gates inside pedestrian portals
	var sc_gate = load("res://assets/models/malai_vasal_gate_grille.glb")
	if sc_gate:
		var gate_l = sc_gate.instantiate()
		gate_l.name = "MV_Gate_Grille_Left"
		gate_l.position = Vector3(-10.7, 0.22, 570.0)
		_apply_override_recursive(gate_l, mat_iron)
		mv_root.add_child(gate_l)

		var gate_r = sc_gate.instantiate()
		gate_r.name = "MV_Gate_Grille_Right"
		gate_r.position = Vector3(10.7, 0.22, 570.0)
		_apply_override_recursive(gate_r, mat_iron)
		mv_root.add_child(gate_r)

	# --- 5. Flanking Red Laterite Walls with Embedded White Granite Panels ---
	# Left Laterite Wall (Main & Stepped Outer)
	make_box.call("MV_Wall_L_Main", Vector3(16.6, 5.2, 1.3), Vector3(-21.7, 2.6, 570.0), mat_wall_laterite)
	make_box.call("MV_Wall_L_Step", Vector3(4.5, 4.6, 1.3), Vector3(-32.25, 2.3, 570.0), mat_wall_laterite)

	# Right Laterite Wall (Main & Stepped Outer)
	make_box.call("MV_Wall_R_Main", Vector3(16.6, 5.2, 1.3), Vector3(21.7, 2.6, 570.0), mat_wall_laterite)
	make_box.call("MV_Wall_R_Step", Vector3(4.5, 4.6, 1.3), Vector3(32.25, 2.3, 570.0), mat_wall_laterite)

	# Embedded White Granite Panels on Left Wall (Front Z = 569.30, Back Z = 570.70)
	# Lower Art Panel: Ancient Nandi Bulls & Dancers Petroglyphs
	make_box.call("MV_Panel_L_Art_Front", Vector3(6.5, 2.0, 0.12), Vector3(-19.5, 1.4, 569.30), mat_tribal_art)
	make_box.call("MV_Panel_L_Art_Back", Vector3(6.5, 2.0, 0.12), Vector3(-19.5, 1.4, 570.70), mat_tribal_art)
	# Upper Inscription Panel
	make_box.call("MV_Panel_L_Upper_Front", Vector3(8.5, 1.9, 0.12), Vector3(-23.0, 3.75, 569.30), mat_relief)
	make_box.call("MV_Panel_L_Upper_Back", Vector3(8.5, 1.9, 0.12), Vector3(-23.0, 3.75, 570.70), mat_relief)
	# Outer Stepped Panel
	make_box.call("MV_Panel_L_Outer_Front", Vector3(3.2, 2.5, 0.12), Vector3(-31.5, 2.2, 569.30), mat_relief)
	make_box.call("MV_Panel_L_Outer_Back", Vector3(3.2, 2.5, 0.12), Vector3(-31.5, 2.2, 570.70), mat_relief)

	# Embedded White Granite Panels on Right Wall
	make_box.call("MV_Panel_R_Lower_Front", Vector3(5.5, 1.8, 0.12), Vector3(18.0, 1.3, 569.30), mat_relief)
	make_box.call("MV_Panel_R_Lower_Back", Vector3(5.5, 1.8, 0.12), Vector3(18.0, 1.3, 570.70), mat_relief)
	make_box.call("MV_Panel_R_Upper_Front", Vector3(9.5, 2.1, 0.12), Vector3(23.5, 3.65, 569.30), mat_relief)
	make_box.call("MV_Panel_R_Upper_Back", Vector3(9.5, 2.1, 0.12), Vector3(23.5, 3.65, 570.70), mat_relief)
	make_box.call("MV_Panel_R_Outer_Front", Vector3(3.2, 2.5, 0.12), Vector3(31.5, 2.2, 569.30), mat_relief)
	make_box.call("MV_Panel_R_Outer_Back", Vector3(3.2, 2.5, 0.12), Vector3(31.5, 2.2, 570.70), mat_relief)

	# --- 6. Ornamental Wrought Iron Trishula (Trident) Parapet Cresting ---
	var sc_trident = load("res://assets/models/malai_vasal_trident.glb")
	if sc_trident:
		var trident_inst = sc_trident.instantiate()
		var trident_mesh: Mesh = null
		if trident_inst.has_node("geometry_0"):
			trident_mesh = (trident_inst.get_node("geometry_0") as MeshInstance3D).mesh
		
		if trident_mesh:
			var mm = MultiMesh.new()
			mm.transform_format = MultiMesh.TRANSFORM_3D
			var trident_positions = []
			# Left wall tridents
			var x_curr = -33.5
			while x_curr <= -13.6:
				var y_h = 5.2 if x_curr > -30.0 else 4.6
				trident_positions.append(Vector3(x_curr, y_h, 570.0))
				x_curr += 1.15
			# Right wall tridents
			x_curr = 13.6
			while x_curr <= 33.5:
				var y_h = 5.2 if x_curr < 30.0 else 4.6
				trident_positions.append(Vector3(x_curr, y_h, 570.0))
				x_curr += 1.15

			mm.mesh = trident_mesh
			mm.instance_count = trident_positions.size()
			for idx in range(trident_positions.size()):
				var tr = Transform3D(Basis(), trident_positions[idx])
				mm.set_instance_transform(idx, tr)

			var mm_node = MultiMeshInstance3D.new()
			mm_node.name = "MV_Trishula_Parapet_Cresting"
			mm_node.multimesh = mm
			mm_node.material_override = mat_iron
			mm_node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
			mm_node.gi_mode = GeometryInstance3D.GI_MODE_STATIC
			mv_root.add_child(mm_node)
		trident_inst.free()

	# --- 7. The 235-Ton Monolithic Granite Boulder & Golden Kalasha ---
	var sc_boulder = load("res://assets/models/malai_vasal_boulder.glb")
	if sc_boulder:
		var boulder_inst = sc_boulder.instantiate()
		boulder_inst.name = "MV_235Ton_Monolith_Boulder"
		boulder_inst.position = Vector3(0.0, 8.8, 570.0)
		_apply_override_recursive(boulder_inst, mat_boulder)
		mv_root.add_child(boulder_inst)

	var sc_kalasha = load("res://assets/models/malai_vasal_kalasha.glb")
	if sc_kalasha:
		var kalasha_inst = sc_kalasha.instantiate()
		kalasha_inst.name = "MV_Sacred_Golden_Kalasha"
		kalasha_inst.position = Vector3(0.0, 8.8, 570.0)
		_apply_override_recursive(kalasha_inst, mat_kalasha)
		mv_root.add_child(kalasha_inst)

	# --- 8. Physics Collisions ---
	var phys = get_node_or_null("Plaza_Physics")
	if phys:
		# Main mega-piers
		_add_box_col(phys, "Col_MV_Pier_L", Vector3(3.0, 8.8, 4.4), Transform3D(Basis(), Vector3(-7.5, 4.4, 570.0)))
		_add_box_col(phys, "Col_MV_Pier_R", Vector3(3.0, 8.8, 4.4), Transform3D(Basis(), Vector3(7.5, 4.4, 570.0)))
		# Outer jamb piers
		_add_box_col(phys, "Col_MV_Outer_L", Vector3(1.4, 5.2, 2.6), Transform3D(Basis(), Vector3(-12.7, 2.6, 570.0)))
		_add_box_col(phys, "Col_MV_Outer_R", Vector3(1.4, 5.2, 2.6), Transform3D(Basis(), Vector3(12.7, 2.6, 570.0)))
		# Flanking laterite walls
		_add_box_col(phys, "Col_MV_Wall_L", Vector3(21.5, 5.2, 1.4), Transform3D(Basis(), Vector3(-23.95, 2.6, 570.0)))
		_add_box_col(phys, "Col_MV_Wall_R", Vector3(21.5, 5.2, 1.4), Transform3D(Basis(), Vector3(23.95, 2.6, 570.0)))
		# 235-ton boulder upper collision
		_add_box_col(phys, "Col_MV_Boulder", Vector3(19.2, 6.4, 7.0), Transform3D(Basis(), Vector3(0.0, 12.0, 570.0)))
		# Gateway threshold plinth & apron
		_add_box_col(phys, "Col_MV_Plinth", Vector3(72.0, 0.4, 30.0), Transform3D(Basis(), Vector3(0.0, -0.05, 577.0)))

	print("[MalaiVasal] Successfully built Malai Vasal gateway with 235-ton boulder, ashlar granite piers, and tribal laterite walls!")

func _apply_override_recursive(node: Node, mat: Material):
	if node is MeshInstance3D:
		var mi = node as MeshInstance3D
		mi.material_override = mat
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		mi.gi_mode = GeometryInstance3D.GI_MODE_STATIC
	for c in node.get_children():
		_apply_override_recursive(c, mat)

func _setup_vintage_bicycle():
	var bike_scene = load("res://scenes/bicycle.tscn")
	if not bike_scene:
		push_error("[Main] Failed to load res://scenes/bicycle.tscn!")
		return

	var bike = bike_scene.instantiate()
	bike.name = "Vintage_Bicycle"
	bike.position = Vector3(2.2, 0.05, 52.5) # Near player start in front of Adiyogi
	add_child(bike)
	print("[Main] Successfully spawned Vintage Yellow Bicycle at (2.2, 0.05, 52.5) near player start!")

# ==============================================================================
# SACRED TEMPLE PRECINCT: DHYANALINGA, LINGA BHAIRAVI, SURYAKUND & CHANDRAKUND
# BASE FOUNDATIONS & REAL GEOGRAPHIC LANDMARK MARKINGS BEHIND ADIYOGI
# ==============================================================================

# ==============================================================================
# SACRED TEMPLE PRECINCT: SURYAKUND SUBTERRANEAN KUND & MANDAPAM COMPLEX
# Exact Geographic Location from Adiyogi:
# Adiyogi Shiva Statue: 10.9723887 N, 76.7404636 E
# Suryakund:            10.9779108 N, 76.7367188 E
# Geodesic Delta:       North +610.82m, East -409.30m (735.28m, bearing 326.2 deg NNW)
# Godot World Frame:    X = -409.30m, Y = 0.0m, Z = -610.82m
# ==============================================================================

const ADIYOGI_LAT: float = 10.9723887
const ADIYOGI_LON: float = 76.7404636
const SURYAKUND_LAT: float = 10.9778181
const SURYAKUND_LON: float = 76.7370055

# Authentic Real-World Geographic Location:
# Latitude:  10.9778181 N (10 deg 58 min 40.1 sec N)
# Longitude: 76.7370055 E (76 deg 44 min 13.2 sec E)
# Godot World Frame: X = -377.30m, Y = 0.0m, Z = -603.42m
# Distance from Adiyogi: 711.75m NNW (bearing 327.97 deg)
# Distance from Sarpa Vasal: 172.96m North along sacred processional pilgrimage axis
# Orientation: Rotated -8.26 deg around Y (aligned with real OpenStreetMap building polygon Way 1570138922)
const SURYAKUND_POS: Vector3 = Vector3(-377.30, 0.0, -603.42)
const SURYAKUND_ROT_DEG: float = -8.26
const SURYAKUND_SCALE: float = 1.75 # Monumental scale fitting Adiyogi's majestic presence

# ------------------------------------------------------------------------------
# SARPA VASAL (THE SACRED SNAKE GATEWAY ENTRANCE)
# Authentic Real-World Geographic Location:
# Latitude:  10.9762875 N (10 deg 58 min 34.6 sec N)
# Longitude: 76.7368594 E (76 deg 44 min 12.7 sec E)
# Plus Code: 7J2RXPGP+GP9 (Semmedu, Coimbatore, Tamil Nadu, India)
# Geodesic Delta from Adiyogi: North +431.26m, West -393.94m (584.10m NNW, bearing 317.6 deg)
# Distance to Suryakund: 180.22m South along the sacred entry axis
# Godot World Frame: X = -393.94m, Y = 0.0m, Z = -431.26m
# ------------------------------------------------------------------------------
const SARPAVASAL_LAT: float = 10.9762875
const SARPAVASAL_LON: float = 76.7368594
const SARPAVASAL_POS: Vector3 = Vector3(-393.94, 0.0, -431.26)
const SARPAVASAL_SCALE: float = 3.0 # Monumental sacred gateway scale (25.2m wide x 19.4m tall)

# ------------------------------------------------------------------------------
# LINGA BHAIRAVI TEMPLE (SACRED DEVI TEMPLE)
# Authentic Real-World Geographic Ground Truth (OpenStreetMap Way 640475174 / Node 14303949453):
# Latitude:  10.9777424 N (10 deg 58 min 39.87 sec N)
# Longitude: 76.7349250 E (76 deg 44 min 05.73 sec E)
# Plus Code: 7J2RXPMN+3X (Isha Yoga Center, Velliangiri Foothills, Coimbatore, Tamil Nadu, India)
# Geodesic Delta from Adiyogi (10.9723887 N, 76.7404636 E):
#   Distance: 846.85m NNW (bearing 314.37 deg)
#   Delta North: +592.20m -> Godot Z = -592.20m
#   Delta East:  -605.35m -> Godot X = -605.35m
# Distance to Suryakund: 228.33m due West (-228.05m X, +11.22m Z)
# Distance to Sarpa Vasal: 265.70m WNW (-211.41m X, -160.94m Z)
# Orientation & Facing Angle:
#   Front Facade wall spans OpenStreetMap Node 6033564238 (-612.90, -602.04) to Node 6033564239 (-598.28, -582.93)
#   Length: 24.07m (matches 24.6m 3D model facade 1:1)
#   Outward normal vector from entrance through colonnade: Vector3(+0.7943, 0.0, -0.6076)
#   Compass Bearing: 52.59 deg (East-North-East / ENE, facing directly into the inner parikrama path towards Dhyanalinga)
#   Godot Y-Rotation: -52.59 deg (Basis local -Z forward aligns with (+0.7943, -0.6076))
# ------------------------------------------------------------------------------
const LINGABHAIRAVI_LAT: float = 10.9777424
const LINGABHAIRAVI_LON: float = 76.7349250
const LINGABHAIRAVI_POS: Vector3 = Vector3(-605.35, 0.0, -592.20)
const LINGABHAIRAVI_ROT_DEG: float = -52.59
const LINGABHAIRAVI_SCALE: float = 1.0

func _lb_pt(offset: Vector3) -> Vector3:
	return LINGABHAIRAVI_POS + offset.rotated(Vector3.UP, deg_to_rad(LINGABHAIRAVI_ROT_DEG))

# ------------------------------------------------------------------------------
# DHYANALINGA TEMPLE (SACRED ELLIPTICAL BRICK DOME & MEDITATION SANCTUM)
# Authentic Real-World Geographic Ground Truth (OpenStreetMap Way 155640705):
# Latitude:  10.9780347 N (10 deg 58 min 40.93 sec N)
# Longitude: 76.7353093 E (76 deg 44 min 07.11 sec E)
# Plus Code: 7J2RXPMQ+64 (Isha Yoga Center, Velliangiri Foothills, Coimbatore, Tamil Nadu, India)
# Geodesic Delta from Adiyogi (10.9723887 N, 76.7404636 E):
#   Distance: 841.07m NNW (bearing 317.95 deg)
#   Delta North: +624.53m -> Godot Z = -624.53m
#   Delta East:  -563.35m -> Godot X = -563.35m
# Distance to Linga Bhairavi: 53.00m ENE
# Distance to Suryakund: 187.25m due West
# Orientation & Facing Angle:
#   Entrance Vestibule and Sunken Reception Court face EAST (+X in Godot).
#   Godot Y-Rotation: -90.0 deg (aligns local entrance with +X East)
# ------------------------------------------------------------------------------
const DHYANALINGA_LAT: float = 10.9780347
const DHYANALINGA_LON: float = 76.7353093
const DHYANALINGA_POS: Vector3 = Vector3(-563.35, 0.0, -624.53)
const DHYANALINGA_ROT_DEG: float = -90.0
const DHYANALINGA_SCALE: float = 1.0

func _dl_pt(offset: Vector3) -> Vector3:
	return DHYANALINGA_POS + offset.rotated(Vector3.UP, deg_to_rad(DHYANALINGA_ROT_DEG))

func _sk_pt(offset: Vector3) -> Vector3:
	return SURYAKUND_POS + offset.rotated(Vector3.UP, deg_to_rad(SURYAKUND_ROT_DEG))

func _setup_suryakund_complex():
	print("[Suryakund] Initializing Suryakund at exact real-world coordinates...")
	print("[Suryakund] Adiyogi: (", ADIYOGI_LAT, ", ", ADIYOGI_LON, ") -> Suryakund: (", SURYAKUND_LAT, ", ", SURYAKUND_LON, ")")
	print("[Suryakund] Godot world offset: ", SURYAKUND_POS, " (distance: 735.28m NNW, scale: ", SURYAKUND_SCALE, "x)")

	var sk_root = Node3D.new()
	sk_root.name = "Suryakund_Precinct"
	add_child(sk_root)

	# --- 1. Vast Continuous Terrain Integration ---
	print("[Suryakund] Unified continuous terrain covers Suryakund precinct with trimesh collision!")

	# --- 2. Instantiate Suryakund Complex Architecture ---
	var sk_scene = load("res://assets/models/suryakund_complex.glb")
	if not sk_scene:
		push_error("[Suryakund] Failed to load res://assets/models/suryakund_complex.glb!")
		return

	var sk_inst = sk_scene.instantiate()
	sk_inst.name = "Suryakund_Complex"
	sk_inst.position = SURYAKUND_POS
	sk_inst.rotation_degrees = Vector3(0.0, SURYAKUND_ROT_DEG, 0.0)
	sk_inst.scale = Vector3(SURYAKUND_SCALE, SURYAKUND_SCALE, SURYAKUND_SCALE)
	sk_root.add_child(sk_inst)

	# --- 3. Material Refinements & PBR Polish ---
	_refine_suryakund_materials(sk_inst)

	# --- 4. Setup Complete Physics Collision & Smooth Stair Ramps for Suryakund ---
	_setup_suryakund_physics(sk_root, sk_inst)

	# --- 5. Indoor Photorealistic VoxelGI Node ---
	print("[Suryakund] Setting up indoor VoxelGI node with multi-bounce radiosity...")
	var vgi_sk = VoxelGI.new()
	vgi_sk.name = "VoxelGI_Suryakund_Indoor"
	vgi_sk.position = SURYAKUND_POS + Vector3(0.0, 9.0 * SURYAKUND_SCALE, 0.0)
	vgi_sk.rotation_degrees = Vector3(0.0, SURYAKUND_ROT_DEG, 0.0)
	vgi_sk.size = Vector3(135.0 * SURYAKUND_SCALE, 55.0 * SURYAKUND_SCALE, 165.0 * SURYAKUND_SCALE)
	vgi_sk.subdiv = VoxelGI.SUBDIV_128

	var vdata = VoxelGIData.new()
	vdata.interior = true # Pure indoor mode - eliminates exterior sky leaking into underground sanctum
	vdata.use_two_bounces = true # Multi-bounce radiosity for deep stone contact bounce
	vdata.propagation = 0.88 # Rich natural light bounce across stone & copper surfaces
	vdata.energy = 2.40 # Deeply illuminated sacred temple bounce ambiance
	vdata.bias = 1.1 # Clean artifact-free flat surfaces
	vdata.normal_bias = 0.1 # Prevents light leaking on step edges
	vdata.dynamic_range = 3.5 # HDR headroom for intense brass sun highlights
	vgi_sk.data = vdata
	sk_root.add_child(vgi_sk)

	# --- 6. Subterranean & Interior Temple Sacred Lighting (Bright, Luminous, Divine) ---
	# 6a. 20-Foot Brass Sun Sculpture Radiant Luminescence (Central Overhead Sun Disc)
	var sun_omni = OmniLight3D.new()
	sun_omni.name = "Suryakund_Sun_Radiance_Omni"
	sun_omni.position = _sk_pt(Vector3(0.0, 7.40 * SURYAKUND_SCALE, 0.0))
	sun_omni.omni_range = 65.0 * SURYAKUND_SCALE
	sun_omni.omni_attenuation = 0.90
	sun_omni.light_energy = 9.8
	sun_omni.light_color = Color(1.0, 0.93, 0.78) # Divine warm solar radiance
	sun_omni.shadow_enabled = true
	sun_omni.light_bake_mode = Light3D.BAKE_DYNAMIC
	sk_root.add_child(sun_omni)

	# 6b. Downward Solar Spotlight beaming directly from Sun Sculpture into water and 3 Rasalingas
	var sun_down_spot = SpotLight3D.new()
	sun_down_spot.name = "Suryakund_Sun_Downward_Spot"
	sun_down_spot.position = _sk_pt(Vector3(0.0, 7.20 * SURYAKUND_SCALE, 0.0))
	sun_down_spot.spot_angle = 62.0
	sun_down_spot.spot_range = 45.0 * SURYAKUND_SCALE
	sun_down_spot.light_energy = 11.5
	sun_down_spot.light_color = Color(1.0, 0.96, 0.84) # Brilliant golden sun beam
	sun_down_spot.shadow_enabled = true
	sun_down_spot.light_bake_mode = Light3D.BAKE_DYNAMIC
	sk_root.add_child(sun_down_spot)
	sun_down_spot.look_at(_sk_pt(Vector3(0.0, -6.5 * SURYAKUND_SCALE, 0.0)), Vector3.FORWARD.rotated(Vector3.UP, deg_to_rad(SURYAKUND_ROT_DEG)))

	# 6c. Upward Ceiling Floodlight illuminating the soaring vaulted dome & steel trusses
	var sun_up_spot = SpotLight3D.new()
	sun_up_spot.name = "Suryakund_Vault_Upward_Spot"
	sun_up_spot.position = _sk_pt(Vector3(0.0, 7.80 * SURYAKUND_SCALE, 0.0))
	sun_up_spot.spot_angle = 75.0
	sun_up_spot.spot_range = 40.0 * SURYAKUND_SCALE
	sun_up_spot.light_energy = 9.5
	sun_up_spot.light_color = Color(1.0, 0.94, 0.82) # Warm ceiling wash
	sun_up_spot.shadow_enabled = false # Soft bounce fill without harsh ceiling shadow lines
	sun_up_spot.light_bake_mode = Light3D.BAKE_DYNAMIC
	sk_root.add_child(sun_up_spot)
	sun_up_spot.look_at(_sk_pt(Vector3(0.0, 16.0 * SURYAKUND_SCALE, 0.0)), Vector3.FORWARD.rotated(Vector3.UP, deg_to_rad(SURYAKUND_ROT_DEG)))

	# 6d. Sacred Energized Water Glow (3 Underwater Teal/Cyan Translucent Lights around 3 Rasalingas)
	var underwater_positions = [
		Vector3(0.0, -6.2 * SURYAKUND_SCALE, 0.0), # Center Rasalinga
		Vector3(12.0 * SURYAKUND_SCALE, -6.2 * SURYAKUND_SCALE, 0.0), # East Rasalinga
		Vector3(-12.0 * SURYAKUND_SCALE, -6.2 * SURYAKUND_SCALE, 0.0), # West Rasalinga
	]
	for u_idx in range(underwater_positions.size()):
		var u_light = OmniLight3D.new()
		u_light.name = "Suryakund_Underwater_Light_" + str(u_idx)
		u_light.position = _sk_pt(underwater_positions[u_idx])
		u_light.omni_range = 35.0 * SURYAKUND_SCALE
		u_light.omni_attenuation = 0.85
		u_light.light_energy = 8.5
		u_light.light_color = Color(0.15, 0.88, 0.85) # Luminous sacred theerthakund turquoise water glow
		u_light.shadow_enabled = false
		u_light.light_bake_mode = Light3D.BAKE_DYNAMIC
		sk_root.add_child(u_light)

	# 6e. Subterranean Cavern Wall Washes (Illuminates 8m tall megalithic stone walls & eliminates cave darkness)
	var cavern_wall_positions = [
		Vector3(-22.0 * SURYAKUND_SCALE, -2.5 * SURYAKUND_SCALE, -5.0 * SURYAKUND_SCALE), # West Wall North
		Vector3(-22.0 * SURYAKUND_SCALE, -2.5 * SURYAKUND_SCALE, 5.0 * SURYAKUND_SCALE),  # West Wall South
		Vector3(22.0 * SURYAKUND_SCALE, -2.5 * SURYAKUND_SCALE, -5.0 * SURYAKUND_SCALE),  # East Wall North
		Vector3(22.0 * SURYAKUND_SCALE, -2.5 * SURYAKUND_SCALE, 5.0 * SURYAKUND_SCALE),   # East Wall South
		Vector3(-12.0 * SURYAKUND_SCALE, -2.5 * SURYAKUND_SCALE, 9.8 * SURYAKUND_SCALE),  # South Wall West
		Vector3(12.0 * SURYAKUND_SCALE, -2.5 * SURYAKUND_SCALE, 9.8 * SURYAKUND_SCALE),   # South Wall East
	]
	for cw_idx in range(cavern_wall_positions.size()):
		var cw_light = OmniLight3D.new()
		cw_light.name = "Cavern_Wall_Light_" + str(cw_idx)
		cw_light.position = _sk_pt(cavern_wall_positions[cw_idx])
		cw_light.omni_range = 35.0 * SURYAKUND_SCALE
		cw_light.omni_attenuation = 0.85
		cw_light.light_energy = 6.5
		cw_light.light_color = Color(1.0, 0.90, 0.74) # Warm golden megalithic stone illumination
		cw_light.shadow_enabled = true
		cw_light.light_bake_mode = Light3D.BAKE_DYNAMIC
		sk_root.add_child(cw_light)

	# 6f. Megalithic Waterfall Lights (2 wide spotlights shining directly onto the 14m wide waterfall)
	for side_sign in [-1.0, 1.0]:
		var wf_spot = SpotLight3D.new()
		wf_spot.name = "Suryakund_Waterfall_Spot_" + ("W" if side_sign < 0 else "E")
		wf_spot.position = _sk_pt(Vector3(side_sign * 7.0 * SURYAKUND_SCALE, -2.5 * SURYAKUND_SCALE, 4.0 * SURYAKUND_SCALE))
		wf_spot.spot_angle = 60.0
		wf_spot.spot_range = 38.0 * SURYAKUND_SCALE
		wf_spot.light_energy = 9.2
		wf_spot.light_color = Color(0.20, 0.90, 0.85) # Sacred turquoise illumination matching pool
		wf_spot.shadow_enabled = false
		wf_spot.light_bake_mode = Light3D.BAKE_DYNAMIC
		sk_root.add_child(wf_spot)
		wf_spot.look_at(_sk_pt(Vector3(side_sign * 3.5 * SURYAKUND_SCALE, -1.0 * SURYAKUND_SCALE, 8.92 * SURYAKUND_SCALE)), Vector3.UP)

	# 6g. Colonnade Temple Brass Diya Lamps (10 warm sconce lights along side ambulatories)
	var lamp_z_offsets = [-35.0, -20.0, -5.0, 10.0, 25.0]
	for side_x in [-18.5, 18.5]:
		for idx in range(lamp_z_offsets.size()):
			var lz = lamp_z_offsets[idx]
			var diya = OmniLight3D.new()
			diya.name = "Diya_" + ("W" if side_x < 0 else "E") + "_" + str(idx)
			diya.position = _sk_pt(Vector3(side_x * SURYAKUND_SCALE, 3.8 * SURYAKUND_SCALE, lz * SURYAKUND_SCALE))
			diya.omni_range = 28.0 * SURYAKUND_SCALE
			diya.omni_attenuation = 0.85
			diya.light_energy = 5.2
			diya.light_color = Color(1.0, 0.86, 0.65) # Warm 2800K brass temple oil lamp glow
			diya.shadow_enabled = true
			diya.light_bake_mode = Light3D.BAKE_DYNAMIC
			sk_root.add_child(diya)

	# 6h. Grand Descent Stair Flight Wash Lights
	var stair_z_levels = [
		Vector3(0.0, 1.8, -25.0), # Top flight entrance
		Vector3(0.0, -0.8, -19.5), # Intermediate landing
		Vector3(0.0, -3.2, -13.0), # Lower flight landing
		Vector3(0.0, -4.8, -6.5), # Pool step threshold
	]
	for idx in range(stair_z_levels.size()):
		var spos = stair_z_levels[idx]
		var step_light = OmniLight3D.new()
		step_light.name = "Stair_Step_Light_" + str(idx)
		step_light.position = _sk_pt(spos * SURYAKUND_SCALE)
		step_light.omni_range = 26.0 * SURYAKUND_SCALE
		step_light.omni_attenuation = 0.90
		step_light.light_energy = 4.8
		step_light.light_color = Color(1.0, 0.91, 0.74) # Soft granite stair wash
		step_light.shadow_enabled = true
		step_light.light_bake_mode = Light3D.BAKE_DYNAMIC
		sk_root.add_child(step_light)

	# 6i. Grand Descent Hall Sconces (Illuminates intermediate staircase landings)
	var hall_sconces = [
		Vector3(-12.0 * SURYAKUND_SCALE, 1.5 * SURYAKUND_SCALE, -22.0 * SURYAKUND_SCALE),
		Vector3( 12.0 * SURYAKUND_SCALE, 1.5 * SURYAKUND_SCALE, -22.0 * SURYAKUND_SCALE),
		Vector3(-12.0 * SURYAKUND_SCALE, -1.0 * SURYAKUND_SCALE, -15.0 * SURYAKUND_SCALE),
		Vector3( 12.0 * SURYAKUND_SCALE, -1.0 * SURYAKUND_SCALE, -15.0 * SURYAKUND_SCALE),
	]
	for h_idx in range(hall_sconces.size()):
		var hl = OmniLight3D.new()
		hl.name = "Hall_Sconce_" + str(h_idx)
		hl.position = _sk_pt(hall_sconces[h_idx])
		hl.omni_range = 30.0 * SURYAKUND_SCALE
		hl.omni_attenuation = 0.85
		hl.light_energy = 5.5
		hl.light_color = Color(1.0, 0.92, 0.78)
		hl.shadow_enabled = true
		hl.light_bake_mode = Light3D.BAKE_DYNAMIC
		sk_root.add_child(hl)

	# 6j. Dedicated Mandapam Hall & Colonnade Architectural Downlights ("and in the mandapam also give lighting")
	# South Mandapam Platform Lights (elevated arrival terrace Z in [12, 24] * SCALE)
	var mandapam_south_lights = [
		Vector3(-32.0 * SURYAKUND_SCALE, 5.2 * SURYAKUND_SCALE, 18.0 * SURYAKUND_SCALE),
		Vector3(-16.0 * SURYAKUND_SCALE, 5.2 * SURYAKUND_SCALE, 18.0 * SURYAKUND_SCALE),
		Vector3(  0.0 * SURYAKUND_SCALE, 5.2 * SURYAKUND_SCALE, 18.0 * SURYAKUND_SCALE),
		Vector3( 16.0 * SURYAKUND_SCALE, 5.2 * SURYAKUND_SCALE, 18.0 * SURYAKUND_SCALE),
		Vector3( 32.0 * SURYAKUND_SCALE, 5.2 * SURYAKUND_SCALE, 18.0 * SURYAKUND_SCALE),
	]
	for ms_idx in range(mandapam_south_lights.size()):
		var msl = OmniLight3D.new()
		msl.name = "Mandapam_South_Light_" + str(ms_idx)
		msl.position = _sk_pt(mandapam_south_lights[ms_idx])
		msl.omni_range = 35.0 * SURYAKUND_SCALE
		msl.omni_attenuation = 0.85
		msl.light_energy = 6.8
		msl.light_color = Color(1.0, 0.90, 0.74) # Radiant warm Indian temple illumination
		msl.shadow_enabled = true
		msl.light_bake_mode = Light3D.BAKE_DYNAMIC
		sk_root.add_child(msl)

	# Side Colonnades Mandapam Aisle Lights (illuminating West and East ambulatories)
	var side_mandapam_z = [-15.0, 0.0, 15.0, 30.0, 45.0]
	for side_x in [-33.5, 33.5]:
		for sz_idx in range(side_mandapam_z.size()):
			var sml = OmniLight3D.new()
			sml.name = "Side_Mandapam_Light_" + ("W" if side_x < 0 else "E") + "_" + str(sz_idx)
			sml.position = _sk_pt(Vector3(side_x * SURYAKUND_SCALE, 4.8 * SURYAKUND_SCALE, side_mandapam_z[sz_idx] * SURYAKUND_SCALE))
			sml.omni_range = 32.0 * SURYAKUND_SCALE
			sml.omni_attenuation = 0.85
			sml.light_energy = 5.8
			sml.light_color = Color(1.0, 0.91, 0.76)
			sml.shadow_enabled = true
			sml.light_bake_mode = Light3D.BAKE_DYNAMIC
			sk_root.add_child(sml)

	# North Arrival Hall Mandapam Lights (Z in [-55, -30] * SCALE)
	var north_mandapam_x = [-24.0, 0.0, 24.0]
	for nm_idx in range(north_mandapam_x.size()):
		var nml = OmniLight3D.new()
		nml.name = "North_Mandapam_Light_" + str(nm_idx)
		nml.position = _sk_pt(Vector3(north_mandapam_x[nm_idx] * SURYAKUND_SCALE, 4.5 * SURYAKUND_SCALE, -42.0 * SURYAKUND_SCALE))
		nml.omni_range = 34.0 * SURYAKUND_SCALE
		nml.omni_attenuation = 0.85
		nml.light_energy = 6.2
		nml.light_color = Color(1.0, 0.92, 0.78)
		nml.shadow_enabled = true
		nml.light_bake_mode = Light3D.BAKE_DYNAMIC
		sk_root.add_child(nml)

	# --- 7. Setup Adiyogi Border Barriers around the Entire Suryakund Outer Perimeter ---
	_setup_suryakund_barriers(sk_root)

	print("[Suryakund] Suryakund Complex successfully imported and placed at ", SURYAKUND_POS, " with monumental scale ", SURYAKUND_SCALE, "x and vibrant indoor lighting!")

var _suryakund_waterfall_mat: StandardMaterial3D = null
var _sun_drift_time: float = 0.0
const _SUN_BASE_ROT: Vector3 = Vector3(-36.0, -22.0, 0.0)

func _process(delta: float):
	if _suryakund_waterfall_mat:
		_suryakund_waterfall_mat.uv1_offset.y += delta * 1.35

	# Pro-realistic dynamic solar drift: subtle, living sunlight and dynamic moving shadows across the entire map
	if sun and sun.visible:
		_sun_drift_time += delta * 0.035
		var solar_drift_pitch = sin(_sun_drift_time * 0.35) * 1.8
		var solar_drift_yaw = cos(_sun_drift_time * 0.25) * 2.5
		sun.rotation_degrees = Vector3(_SUN_BASE_ROT.x + solar_drift_pitch, _SUN_BASE_ROT.y + solar_drift_yaw, 0.0)

var _suryakund_pillar_shared_mat: StandardMaterial3D = null

func _get_suryakund_pillar_shared_material() -> StandardMaterial3D:
	if _suryakund_pillar_shared_mat != null:
		return _suryakund_pillar_shared_mat
	var mat = StandardMaterial3D.new()
	mat.resource_name = "Suryakund_Dravidian_Pillars_PBR"
	mat.albedo_color = Color(1.55, 1.50, 1.42) # Bright radiant sacred granite tone
	mat.albedo_texture = load("res://assets/textures/naga_stone_color.png")
	mat.normal_enabled = true
	mat.normal_texture = load("res://assets/textures/naga_stone_normal.png")
	mat.normal_scale = 1.25
	mat.roughness_texture = load("res://assets/textures/naga_stone_roughness.png")
	mat.roughness = 0.65
	mat.metallic = 0.0
	mat.metallic_specular = 0.30
	mat.uv1_triplanar = true
	mat.uv1_world_triplanar = true
	mat.uv1_triplanar_sharpness = 2.0
	mat.uv1_scale = Vector3(0.45, 0.45, 0.45)
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	_suryakund_pillar_shared_mat = mat
	return mat

func _refine_suryakund_materials(node: Node):
	print("[Suryakund] Applying authentic photorealistic 2K PBR materials matching real Suryakund...")

	# 1. Authentic Ashlar Granite Paving Stones (Floor, Plinths & Architraves)
	var mat_granite_floor = StandardMaterial3D.new()
	mat_granite_floor.resource_name = "Suryakund_Ashlar_Granite_PBR"
	mat_granite_floor.albedo_texture = load("res://assets/textures/ashlar_slate_color.jpg")
	mat_granite_floor.normal_enabled = true
	mat_granite_floor.normal_texture = load("res://assets/textures/ashlar_slate_normal.jpg")
	mat_granite_floor.normal_scale = 1.15
	mat_granite_floor.roughness_texture = load("res://assets/textures/ashlar_slate_roughness.jpg")
	mat_granite_floor.roughness = 0.88
	mat_granite_floor.metallic = 0.0
	mat_granite_floor.metallic_specular = 0.15
	mat_granite_floor.uv1_triplanar = true
	mat_granite_floor.uv1_world_triplanar = true
	mat_granite_floor.uv1_triplanar_sharpness = 6.0
	mat_granite_floor.uv1_scale = Vector3(0.28, 0.28, 0.28)
	mat_granite_floor.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_granite_floor.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# 1b. Dedicated Ashlar Granite Step Material (Native baked per-block UVs, no triplanar edge-bleeding)
	var mat_granite_steps = StandardMaterial3D.new()
	mat_granite_steps.resource_name = "Suryakund_Ashlar_Granite_Steps_PBR"
	mat_granite_steps.albedo_texture = load("res://assets/textures/ashlar_slate_color.jpg")
	mat_granite_steps.normal_enabled = true
	mat_granite_steps.normal_texture = load("res://assets/textures/ashlar_slate_normal.jpg")
	mat_granite_steps.normal_scale = 1.20
	mat_granite_steps.roughness_texture = load("res://assets/textures/ashlar_slate_roughness.jpg")
	mat_granite_steps.roughness = 0.88
	mat_granite_steps.metallic = 0.0
	mat_granite_steps.metallic_specular = 0.15
	mat_granite_steps.uv1_triplanar = false
	mat_granite_steps.uv1_scale = Vector3(1.0, 1.0, 1.0)
	mat_granite_steps.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_granite_steps.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# 2. Authentic Megalithic Dressed Stone Block Walls (Retaining Walls & 8m Waterfall Backdrop)
	var mat_megalithic_wall = StandardMaterial3D.new()
	mat_megalithic_wall.resource_name = "Suryakund_Megalithic_Wall_PBR"
	mat_megalithic_wall.albedo_texture = load("res://assets/textures/stone_block_wall_diff_2k.jpg")
	mat_megalithic_wall.normal_enabled = true
	mat_megalithic_wall.normal_texture = load("res://assets/textures/stone_block_wall_nor_gl_2k.jpg")
	mat_megalithic_wall.normal_scale = 1.85
	mat_megalithic_wall.roughness_texture = load("res://assets/textures/stone_block_wall_rough_2k.jpg")
	mat_megalithic_wall.roughness = 0.82
	mat_megalithic_wall.ao_enabled = true
	mat_megalithic_wall.ao_texture = load("res://assets/textures/stone_block_wall_ao_2k.jpg")
	mat_megalithic_wall.metallic = 0.0
	mat_megalithic_wall.metallic_specular = 0.18
	mat_megalithic_wall.uv1_triplanar = true
	mat_megalithic_wall.uv1_world_triplanar = true
	mat_megalithic_wall.uv1_triplanar_sharpness = 4.0
	mat_megalithic_wall.uv1_scale = Vector3(0.08, 0.12, 0.08) # Massive rectangular dressed rock blocks
	mat_megalithic_wall.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_megalithic_wall.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# 2b. Authentic Isha Bright Monolithic Rock Blocks (Pool Edge Coping & Mandapam Megaliths)
	var mat_bright_rock = StandardMaterial3D.new()
	mat_bright_rock.resource_name = "Suryakund_Bright_Granite_Rock_PBR"
	mat_bright_rock.albedo_color = Color(1.68, 1.62, 1.50) # Bright radiant sunlit granite tone
	mat_bright_rock.albedo_texture = load("res://assets/textures/naga_stone_color.png")
	mat_bright_rock.normal_enabled = true
	mat_bright_rock.normal_texture = load("res://assets/textures/naga_stone_normal.png")
	mat_bright_rock.normal_scale = 1.35
	mat_bright_rock.roughness_texture = load("res://assets/textures/naga_stone_roughness.png")
	mat_bright_rock.roughness = 0.72
	mat_bright_rock.metallic = 0.0
	mat_bright_rock.metallic_specular = 0.25
	mat_bright_rock.uv1_triplanar = true
	mat_bright_rock.uv1_world_triplanar = true
	mat_bright_rock.uv1_triplanar_sharpness = 3.0
	mat_bright_rock.uv1_scale = Vector3(0.35, 0.35, 0.35)
	mat_bright_rock.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_bright_rock.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# 3. Authentic Carved Dravidian Temple Stone Pillars (All 99 Colonnade Columns & Dome Pillar)
	var mat_dravidian_pillar = _get_suryakund_pillar_shared_material()

	# 4. Authentic Dark Monolithic Rock Base (Carved Central Monolith)
	var mat_rock_monolith = StandardMaterial3D.new()
	mat_rock_monolith.resource_name = "Suryakund_Dark_Rock_Monolith_PBR"
	mat_rock_monolith.albedo_texture = load("res://assets/textures/dark_rock_02_diff_2k.jpg")
	mat_rock_monolith.normal_enabled = true
	mat_rock_monolith.normal_texture = load("res://assets/textures/dark_rock_02_nor_gl_2k.jpg")
	mat_rock_monolith.normal_scale = 1.45
	mat_rock_monolith.roughness_texture = load("res://assets/textures/dark_rock_02_rough_2k.jpg")
	mat_rock_monolith.roughness = 0.82
	mat_rock_monolith.metallic = 0.0
	mat_rock_monolith.metallic_specular = 0.20
	mat_rock_monolith.uv1_triplanar = true
	mat_rock_monolith.uv1_world_triplanar = true
	mat_rock_monolith.uv1_triplanar_sharpness = 2.5
	mat_rock_monolith.uv1_scale = Vector3(0.35, 0.35, 0.35)
	mat_rock_monolith.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_rock_monolith.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# 5. Authentic Indian Terracotta Fluted Barrel Roof Tiles (Domes, Vaults & Inner Ceilings)
	var mat_terracotta = StandardMaterial3D.new()
	mat_terracotta.resource_name = "Suryakund_Terracotta_Roof_PBR"
	mat_terracotta.albedo_color = Color(1.18, 0.96, 0.82) # Radiant warm baked terracotta tile
	mat_terracotta.albedo_texture = load("res://assets/textures/terracotta_tiles_color.png")
	mat_terracotta.normal_enabled = true
	mat_terracotta.normal_texture = load("res://assets/textures/terracotta_tiles_normal.png")
	mat_terracotta.normal_scale = 1.35
	mat_terracotta.roughness_texture = load("res://assets/textures/terracotta_tiles_roughness.png")
	mat_terracotta.roughness = 0.72
	mat_terracotta.metallic = 0.0
	mat_terracotta.metallic_specular = 0.18
	mat_terracotta.uv1_triplanar = true
	mat_terracotta.uv1_world_triplanar = true
	mat_terracotta.uv1_triplanar_sharpness = 2.5
	mat_terracotta.uv1_scale = Vector3(0.35, 0.35, 0.35)
	mat_terracotta.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat_terracotta.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC

	# 6. Industrial Structural Steel Arches & Girders
	var mat_steel = StandardMaterial3D.new()
	mat_steel.resource_name = "Suryakund_Steel_Framework_PBR"
	mat_steel.albedo_color = Color(0.12, 0.12, 0.13)
	mat_steel.metallic = 0.92
	mat_steel.roughness = 0.32
	mat_steel.metallic_specular = 0.50
	mat_steel.cull_mode = BaseMaterial3D.CULL_DISABLED

	# 7. 20-Foot Consecrated Radiant Brass & Copper Sun Sculpture
	var mat_brass_sun = StandardMaterial3D.new()
	mat_brass_sun.resource_name = "Suryakund_Brass_Sun_PBR"
	mat_brass_sun.albedo_color = Color(1.0, 0.92, 0.78)
	if ResourceLoader.exists("res://assets/textures/suryakund_sun_albedo.png"):
		mat_brass_sun.albedo_texture = load("res://assets/textures/suryakund_sun_albedo.png")
	mat_brass_sun.metallic = 0.92
	mat_brass_sun.roughness = 0.20
	mat_brass_sun.metallic_specular = 0.85
	mat_brass_sun.emission_enabled = true
	mat_brass_sun.emission = Color(0.95, 0.72, 0.20)
	mat_brass_sun.emission_energy_multiplier = 0.35
	mat_brass_sun.rim_enabled = true
	mat_brass_sun.rim = 0.45
	mat_brass_sun.rim_tint = 0.50
	mat_brass_sun.cull_mode = BaseMaterial3D.CULL_DISABLED

	# 7b. Dedicated 24K Sacred Temple Gold for Dome Golden Lingas (Master Linga & Zigzag Lingas)
	var mat_golden_linga = StandardMaterial3D.new()
	mat_golden_linga.resource_name = "Suryakund_Golden_Linga_24K_PBR"
	mat_golden_linga.albedo_color = Color(0.96, 0.78, 0.22) # Radiant 24K Temple Gold
	mat_golden_linga.metallic = 0.95
	mat_golden_linga.roughness = 0.16
	mat_golden_linga.metallic_specular = 0.90
	mat_golden_linga.cull_mode = BaseMaterial3D.CULL_DISABLED

	# 8. Consecrated Solidified Mercury Rasalingas (Deep Obsidian/Mercury Liquid Metal Sheen)
	var mat_rasalinga = StandardMaterial3D.new()
	mat_rasalinga.resource_name = "Rasalinga_Solidified_Mercury_PBR"
	mat_rasalinga.albedo_color = Color(0.14, 0.15, 0.17) # Deep dark alchemical mercury
	mat_rasalinga.metallic = 0.98
	mat_rasalinga.roughness = 0.08 # Mirror-like liquid metal surface
	mat_rasalinga.metallic_specular = 1.00
	mat_rasalinga.clearcoat_enabled = true
	mat_rasalinga.clearcoat = 0.70
	mat_rasalinga.clearcoat_roughness = 0.05
	mat_rasalinga.cull_mode = BaseMaterial3D.CULL_DISABLED

	# 9. Sacred Mineral Energized Pool Water
	var mat_water = StandardMaterial3D.new()
	mat_water.resource_name = "Suryakund_Sacred_Water_PBR"
	mat_water.albedo_color = Color(0.05, 0.35, 0.33, 0.82) # Sacred deep mineral turquoise/aquamarine
	mat_water.roughness = 0.03 # Glass-calm reflective pool
	mat_water.metallic = 0.06
	mat_water.metallic_specular = 0.85
	mat_water.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat_water.cull_mode = BaseMaterial3D.CULL_DISABLED

	# 10. Cascading Waterfall Sheet & Splash Foam (Matching Sacred Turquoise Pool Water)
	var mat_waterfall = ShaderMaterial.new()
	mat_waterfall.resource_name = "Suryakund_Waterfall_Sheet_PBR"
	mat_waterfall.shader = load("res://shaders/waterfall.gdshader")
	mat_waterfall.set_shader_parameter("albedo_tex", load("res://assets/textures/waterfall_albedo.png"))
	mat_waterfall.set_shader_parameter("normal_tex", load("res://assets/textures/waterfall_normal.png"))
	mat_waterfall.set_shader_parameter("roughness_tex", load("res://assets/textures/waterfall_roughness.png"))
	mat_waterfall.set_shader_parameter("flow_speed", 3.0)
	mat_waterfall.set_shader_parameter("secondary_speed", 4.5)
	mat_waterfall.set_shader_parameter("normal_depth", 1.75)
	mat_waterfall.set_shader_parameter("wave_amplitude", 0.05)
	mat_waterfall.set_shader_parameter("water_color", Color(0.08, 0.58, 0.54, 0.95)) # Luminous sacred turquoise matching pool
	mat_waterfall.set_shader_parameter("foam_color", Color(0.90, 0.98, 0.96, 0.95))  # White-water mineral froth
	_suryakund_waterfall_mat = null

	var mat_waterfall_foam = StandardMaterial3D.new()
	mat_waterfall_foam.resource_name = "Suryakund_Waterfall_Foam_PBR"
	mat_waterfall_foam.albedo_texture = load("res://assets/textures/waterfall_foam.png")
	mat_waterfall_foam.albedo_color = Color(0.90, 0.98, 0.96, 0.85)
	mat_waterfall_foam.roughness = 0.22
	mat_waterfall_foam.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat_waterfall_foam.cull_mode = BaseMaterial3D.CULL_DISABLED

	# 11. Consecrated Subterranean Pure Copper Basin Floor & Submerged Central Plinth
	var mat_copper_basin = StandardMaterial3D.new()
	mat_copper_basin.resource_name = "Suryakund_Copper_Basin_PBR"
	mat_copper_basin.albedo_color = Color(0.98, 0.58, 0.38) # Radiant hammered temple copper
	mat_copper_basin.metallic = 0.98
	mat_copper_basin.roughness = 0.16
	mat_copper_basin.metallic_specular = 0.90
	mat_copper_basin.cull_mode = BaseMaterial3D.CULL_DISABLED

	var mats = {
		"granite_floor": mat_granite_floor,
		"granite_steps": mat_granite_steps,
		"megalithic_wall": mat_megalithic_wall,
		"bright_rock": mat_bright_rock,
		"dravidian_pillar": mat_dravidian_pillar,
		"rock_monolith": mat_rock_monolith,
		"terracotta": mat_terracotta,
		"steel": mat_steel,
		"brass_sun": mat_brass_sun,
		"rasalinga": mat_rasalinga,
		"water": mat_water,
		"waterfall": mat_waterfall,
		"waterfall_foam": mat_waterfall_foam,
		"copper_basin": mat_copper_basin,
		"golden_linga": mat_golden_linga
	}

	_apply_suryakund_mats_recursive(node, mats)
	print("[Suryakund] All dedicated PBR materials assigned successfully across the complex!")

func _apply_suryakund_mats_recursive(node: Node, mats: Dictionary):
	if node is MeshInstance3D:
		var mi = node as MeshInstance3D
		var mname = mi.name.to_lower()
		mi.gi_mode = GeometryInstance3D.GI_MODE_STATIC
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON

		if "outside_plaza" in mname:
			# Hide duplicate flat plaza plane to eliminate z-fighting glitch with the flat mud terrain
			mi.visible = false
		elif "waterfall_foam" in mname or "foam" in mname:
			mi.material_override = mats["waterfall_foam"]
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif "waterfall_sheet" in mname or "waterfall" in mname or "falls" in mname:
			mi.material_override = mats["waterfall"]
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif "water" in mname:
			mi.material_override = mats["water"]
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		elif "golden_linga" in mname or "master_golden" in mname or "zigzag_golden" in mname or ("golden" in mname and "linga" in mname):
			mi.material_override = mats["golden_linga"]
		elif "rasalinga" in mname or ("linga" in mname and not "panel" in mname and not "golden" in mname):
			# "and the linga alone should be in coper and not the basement of the linga"
			mi.material_override = mats["copper_basin"]
		elif "sun_sculpture" in mname or ("sun" in mname and "sculpture" in mname):
			# Outer radiating brass/gold sun rays on surface 0, consecrated copper center medallion on surface 1
			if mi.mesh and mi.mesh.get_surface_count() > 1:
				mi.set_surface_override_material(0, mats["brass_sun"])
				mi.set_surface_override_material(1, mats["copper_basin"])
			else:
				mi.material_override = mats["brass_sun"]
		elif "pillar_naga" in mname or "naga_sculpture" in mname:
			# High-poly 3D King Cobra carved in Dravidian granite
			mi.material_override = mats["dravidian_pillar"]
		elif "sun_cables" in mname or "cable" in mname:
			mi.material_override = mats["brass_sun"]
		elif "kalasha" in mname or "cupola" in mname:
			mi.material_override = mats["brass_sun"]
		elif "side_roof" in mname or "flat_roof" in mname:
			# Above side mandapams flat roof exterior deck & parapet
			mi.material_override = mats["granite_floor"]
		elif "ceiling" in mname or "roof" in mname or "vault" in mname or "dome" in mname:
			# Mandapam inner ceilings and vaulted roofs in authentic terracotta tile texture
			mi.material_override = mats["terracotta"]
		elif "exterior_front_fascia" in mname or "exterior_back_fascia" in mname or "fascia" in mname:
			# Exterior stone frieze hiding any beams from outside
			mi.material_override = mats["dravidian_pillar"]
		elif "truss" in mname or "arch_rib" in mname or "purlin" in mname or "transverse_beam" in mname or "beam" in mname:
			mi.material_override = mats["steel"]
		elif "pediment" in mname:
			mi.material_override = mats["megalithic_wall"]
		elif "pillar" in mname and not "central" in mname:
			mi.material_override = mats["dravidian_pillar"]
		elif "central_pillar" in mname:
			mi.material_override = mats["dravidian_pillar"]
		elif "naga_monolith" in mname or "monolith" in mname:
			# Apply dark rock to plain faces (surface 1) while preserving King Cobra relief
			if mi.mesh and mi.mesh.get_surface_count() >= 2:
				mi.set_surface_override_material(1, mats["rock_monolith"])
			else:
				mi.material_override = mats["rock_monolith"]
		elif "rock_blocks" in mname or "edge_rock" in mname or "pool_edge" in mname:
			mi.material_override = mats["bright_rock"]
		elif "retaining_wall" in mname or "retaining" in mname or "wall" in mname:
			mi.material_override = mats["megalithic_wall"]
		elif "basin_floor" in mname or "pool_floor" in mname:
			# Pool basin underwater floor is consecrated pure copper!
			mi.material_override = mats["copper_basin"]
		elif "central_plinth" in mname:
			# Plinth/pedestal of the linga is authentic Ashlar granite stone ("not the basement of the linga")
			mi.material_override = mats["granite_floor"]
		elif "steps" in mname or "stairs" in mname:
			# Use dedicated ashlar step material with baked per-block UV mapping (no triplanar edge bleed or swimming)
			mi.material_override = mats["granite_steps"]
		elif "floor" in mname or "plinth" in mname or "architrave" in mname:
			mi.material_override = mats["granite_floor"]

	for child in node.get_children():
		_apply_suryakund_mats_recursive(child, mats)

func _setup_suryakund_physics(sk_root: Node3D, sk_inst: Node):
	print("[Suryakund] Setting up complete physics, smooth stair collision ramps & solid boundaries...")
	var sk_physics = StaticBody3D.new()
	sk_physics.name = "Suryakund_Physics"
	sk_physics.position = SURYAKUND_POS
	sk_physics.rotation_degrees = Vector3(0.0, SURYAKUND_ROT_DEG, 0.0)
	sk_physics.scale = Vector3(SURYAKUND_SCALE, SURYAKUND_SCALE, SURYAKUND_SCALE)
	sk_root.add_child(sk_physics)

	# 1. Smooth Stair Slope Ramps (Mathematically calibrated so top surface aligns flush with landing & floor levels)
	# Exterior Grand Steps (South Arrival): ascends from Z = 45 (Y = 0.00) to Z = 25 (Y = 3.50)
	# Angle: +9.932 deg. Center Y = 1.56m (offset by half-box thickness so top surface is at 0.01m to 3.51m)
	_add_box_col(sk_physics, "Ramp_Exterior_Grand_Steps", Vector3(48.0, 0.4, 20.35), Transform3D(Basis.from_euler(Vector3(deg_to_rad(9.932), 0, 0)), Vector3(0.0, 1.56, 35.0)))
	
	# Compact Side Mandapam Steps (West & East): ascends from Z = -28 (Y = 0.00) to Z = -21 (Y = 3.50)
	# Angle: -26.565 deg. Center Y = 1.53m (top surface is at 0.01m to 3.51m)
	_add_box_col(sk_physics, "Ramp_Side_Steps_West", Vector3(19.0, 0.4, 7.83), Transform3D(Basis.from_euler(Vector3(-deg_to_rad(26.565), 0, 0)), Vector3(-33.5, 1.53, -24.5)))
	_add_box_col(sk_physics, "Ramp_Side_Steps_East", Vector3(19.0, 0.4, 7.83), Transform3D(Basis.from_euler(Vector3(-deg_to_rad(26.565), 0, 0)), Vector3(33.5, 1.53, -24.5)))

	# Inner Grand Descent Steps into Subterranean Pool:
	# Top Flat Landing: from Z = -28.0 to Z = -22.5 at Y = 0.00m (connects North Hall to stair descent)
	_add_box_col(sk_physics, "Landing_Pool_Top", Vector3(48.0, 0.4, 5.5), Transform3D(Basis(), Vector3(0.0, -0.20, -25.25)))
	# Flight 1: descends from Z = -22.5 (Y = 0.00) to Z = -16.5 (Y = -2.25). Center Y = -1.33m
	_add_box_col(sk_physics, "Ramp_Pool_Flight_1", Vector3(48.0, 0.4, 6.41), Transform3D(Basis.from_euler(Vector3(deg_to_rad(20.556), 0, 0)), Vector3(0.0, -1.33, -19.5)))
	# Intermediate Landing at Y = -2.25m: from Z = -16.5 to Z = -14.5
	_add_box_col(sk_physics, "Landing_Pool_Intermediate", Vector3(48.0, 0.4, 2.0), Transform3D(Basis(), Vector3(0.0, -2.44, -15.5)))
	# Flight 2: descends from Z = -14.5 (Y = -2.25) to Z = -7.5 (Y = -4.50). Center Y = -3.58m
	_add_box_col(sk_physics, "Ramp_Pool_Flight_2", Vector3(48.0, 0.4, 7.35), Transform3D(Basis.from_euler(Vector3(deg_to_rad(17.820), 0, 0)), Vector3(0.0, -3.58, -11.0)))
	# North Pool Steps into Water: descends from Z = -7.5 (Y = -4.50) to Z = -3.5 (Y = -6.10). Center Y = -5.51m
	_add_box_col(sk_physics, "Ramp_Pool_Lower_Steps", Vector3(48.0, 0.4, 4.31), Transform3D(Basis.from_euler(Vector3(deg_to_rad(21.800), 0, 0)), Vector3(0.0, -5.51, -5.5)))

	# 2. Solid Mandapam Floors, Basin Floor & Outside Arrival Plaza
	_add_box_col(sk_physics, "Plaza_Arrival_Outside", Vector3(144.0, 0.4, 23.0), Transform3D(Basis(), Vector3(0.0, -0.20, 56.5)))
	_add_box_col(sk_physics, "Floor_Pool_Basin", Vector3(48.0, 0.4, 18.0), Transform3D(Basis(), Vector3(0.0, -6.30, 1.5)))
	_add_box_col(sk_physics, "Floor_North_Hall", Vector3(86.0, 0.4, 31.0), Transform3D(Basis(), Vector3(0.0, -0.20, -43.5)))
	_add_box_col(sk_physics, "Floor_South_Platform", Vector3(86.0, 0.4, 14.5), Transform3D(Basis(), Vector3(0.0, 3.30, 17.75)))
	_add_box_col(sk_physics, "Floor_West_Aisle", Vector3(19.0, 0.4, 31.5), Transform3D(Basis(), Vector3(-33.5, 3.30, -5.25)))
	_add_box_col(sk_physics, "Floor_East_Aisle", Vector3(19.0, 0.4, 31.5), Transform3D(Basis(), Vector3(33.5, 3.30, -5.25)))

	# 3. Solid Retaining Walls, Plinths, Central Naga Monolith & Supporting Pillar
	# Central 4-Faced Rock Monolith at Z = -14.40m: base firmly seated on steps down to Z = -3.20m, top at 2.65m (height 5.85m, center -0.275m)
	_add_box_col(sk_physics, "Rock_Base", Vector3(2.9, 5.85, 2.9), Transform3D(Basis(), Vector3(0.0, -0.275, -14.40)))
	# Central Pillar reaching dome at Z = -14.40m: 1.2m x 1.2m, 12m tall touching top of Naga rock (from Y=2.65m to Y=14.65m)
	_add_box_col(sk_physics, "Pillar_Center", Vector3(1.2, 12.0, 1.2), Transform3D(Basis(), Vector3(0.0, 8.65, -14.40)))
	# South Megalithic Retaining Wall behind Waterfall: 48m wide, 9.6m tall at Z = 10.9m
	_add_box_col(sk_physics, "Wall_South_Megalithic", Vector3(48.0, 9.6, 0.8), Transform3D(Basis(), Vector3(0.0, -1.30, 10.9)))
	# West Inner Retaining Wall: 34m long, 9.6m tall at X = -24.4m
	_add_box_col(sk_physics, "Wall_West_Inner", Vector3(0.8, 9.6, 34.0), Transform3D(Basis(), Vector3(-24.4, -1.30, -6.0)))
	# East Inner Retaining Wall: 34m long, 9.6m tall at X = 24.4m
	_add_box_col(sk_physics, "Wall_East_Inner", Vector3(0.8, 9.6, 34.0), Transform3D(Basis(), Vector3(24.4, -1.30, -6.0)))
	# West Exterior Foundation Plinth Wall: 46m long, 3.5m tall
	_add_box_col(sk_physics, "Wall_West_Plinth", Vector3(0.8, 3.5, 46.0), Transform3D(Basis(), Vector3(-43.4, 1.75, 2.0)))
	# East Exterior Foundation Plinth Wall: 46m long, 3.5m tall
	_add_box_col(sk_physics, "Wall_East_Plinth", Vector3(0.8, 3.5, 46.0), Transform3D(Basis(), Vector3(43.4, 1.75, 2.0)))

	# 4. Trimesh collision on solid architectural features, excluding stairs/steps (handled by smooth ramps) and liquids
	_setup_suryakund_mesh_collision(sk_inst)
	print("[Suryakund] All solid architecture, floors, walls, steps & smooth collision ramps active!")

func _setup_suryakund_mesh_collision(node: Node):
	if node is MeshInstance3D:
		var mi = node as MeshInstance3D
		var mname = mi.name.to_lower()
		# Add trimesh collision to solid architecture (pillars, roofs, walls, monolith, floor)
		# Skip liquid water, waterfall visual sheets, duplicate outside plaza, and stairs/steps (which have smooth physics ramps)
		var skip = false
		for k in ["water", "waterfall", "outside_plaza", "stairs", "steps"]:
			if k in mname:
				skip = true
				break
		if not skip:
			mi.create_trimesh_collision()
			mi.gi_mode = GeometryInstance3D.GI_MODE_STATIC
	for child in node.get_children():
		_setup_suryakund_mesh_collision(child)

func _setup_suryakund_barriers(sk_root: Node3D):
	print("[Suryakund] Setting up Adiyogi Border Barriers exclusively on high-level mandapam platform edges...")
	var barrier_scene: PackedScene = load("res://assets/barrier_module.glb")
	if not barrier_scene:
		print("[Suryakund] Warning: barrier_module.glb not found!")
		return

	var barriers_group = Node3D.new()
	barriers_group.name = "Suryakund_High_Platform_Barriers"
	barriers_group.position = SURYAKUND_POS
	barriers_group.rotation_degrees = Vector3(0.0, SURYAKUND_ROT_DEG, 0.0)
	sk_root.add_child(barriers_group)

	var barrier_col_shape = BoxShape3D.new()
	barrier_col_shape.size = Vector3(5.0, 1.25, 0.20)

	# Barriers are placed ONLY on top elevated edges of the high-level mandapam platform (Y = 3.48m * SCALE = 6.09m)
	# Lower levels (North Hall at Y = 0) and the entire Grand Front Steps (Z in [25.0, 59.0]) remain completely barrier-free!
	var y_platform = 3.48 * SURYAKUND_SCALE
	var b_configs: Array = []
	var z_step = 4.95
	var x_step = 4.95

	# 1. West Mandapam high outer edge at X = -43.0 * SURYAKUND_SCALE (Z from -21.0 to 25.0 * SCALE)
	var x_west = -43.0 * SURYAKUND_SCALE
	var z_curr = -21.0 * SURYAKUND_SCALE + 2.5
	while z_curr <= 25.0 * SURYAKUND_SCALE - 1.0:
		b_configs.append([Vector3(x_west, y_platform, z_curr), 90.0])
		z_curr += z_step

	# 2. East Mandapam high outer edge at X = +43.0 * SURYAKUND_SCALE (Z from -21.0 to 25.0 * SCALE)
	var x_east = 43.0 * SURYAKUND_SCALE
	z_curr = -21.0 * SURYAKUND_SCALE + 2.5
	while z_curr <= 25.0 * SURYAKUND_SCALE - 1.0:
		b_configs.append([Vector3(x_east, y_platform, z_curr), -90.0])
		z_curr += z_step

	# 3. South Mandapam high platform outer wings flanking the Grand Steps at Z = 25.0 * SURYAKUND_SCALE
	# Grand steps in the center (X in [-24.8, 24.8] * SCALE) are 100% barrier-free!
	var z_south = 25.0 * SURYAKUND_SCALE
	# West Wing: X from -43.0 to -24.8 * SCALE
	var x_w = -43.0 * SURYAKUND_SCALE + 2.5
	while x_w <= -24.8 * SURYAKUND_SCALE - 1.5:
		b_configs.append([Vector3(x_w, y_platform, z_south), 0.0])
		x_w += x_step

	# East Wing: X from 24.8 to 43.0 * SCALE
	var x_e = 24.8 * SURYAKUND_SCALE + 2.5
	while x_e <= 43.0 * SURYAKUND_SCALE - 1.5:
		b_configs.append([Vector3(x_e, y_platform, z_south), 0.0])
		x_e += x_step

	# 4. North Mandapam return edges overlooking lower North Hall at Z = -21.0 * SURYAKUND_SCALE
	var z_north = -21.0 * SURYAKUND_SCALE
	# West Wing North edge: X from -43.0 to -24.8 * SCALE
	x_w = -43.0 * SURYAKUND_SCALE + 2.5
	while x_w <= -24.8 * SURYAKUND_SCALE - 1.5:
		b_configs.append([Vector3(x_w, y_platform, z_north), 180.0])
		x_w += x_step

	# East Wing North edge: X from 24.8 to 43.0 * SCALE
	x_e = 24.8 * SURYAKUND_SCALE + 2.5
	while x_e <= 43.0 * SURYAKUND_SCALE - 1.5:
		b_configs.append([Vector3(x_e, y_platform, z_north), 180.0])
		x_e += x_step

	for i in range(b_configs.size()):
		var cfg = b_configs[i]
		var local_pos: Vector3 = cfg[0]
		var rot_deg: float = cfg[1]

		var sb = StaticBody3D.new()
		sb.name = "SK_High_Barrier_" + str(i + 1)
		sb.position = local_pos
		sb.rotation_degrees.y = rot_deg

		var col = CollisionShape3D.new()
		col.shape = barrier_col_shape
		col.position = Vector3(0.0, 0.625, 0.0)
		sb.add_child(col)

		var inst = barrier_scene.instantiate()
		sb.add_child(inst)
		barriers_group.add_child(sb)

	print("[Suryakund] Successfully placed ", b_configs.size(), " Adiyogi Border Barriers exclusively along high-level mandapam platform edges!")

func _run_capture_suryakund_sequence():
	print("[Capture] Starting Suryakund verification capture sequence...")
	var cam = Camera3D.new()
	cam.name = "SuryakundCaptureCam"
	add_child(cam)
	cam.current = true
	cam.fov = 65.0
	cam.near = 0.25
	cam.far = 2500.0

	var player = get_node_or_null("Player")
	if player:
		player.position = _sk_pt(Vector3(0.0, 0.1, 45.0 * SURYAKUND_SCALE))
		player.rotation_degrees = Vector3(0, SURYAKUND_ROT_DEG + 180.0, 0)

	var shots = [
		{
			"name": "godot_suryakund_01_landscape_overview.png",
			"pos": Vector3(-140.0, 140.0, -110.0),
			"look": SURYAKUND_POS + Vector3(0.0, 10.0, 0.0),
			"fov": 62.0
		},
		{
			"name": "godot_suryakund_02_view_towards_adiyogi.png",
			"pos": _sk_pt(Vector3(20.0 * SURYAKUND_SCALE, 6.0 * SURYAKUND_SCALE, 75.0 * SURYAKUND_SCALE)),
			"look": Vector3(0.0, 18.0, 0.0),
			"fov": 55.0
		},
		{
			"name": "godot_suryakund_03_aerial_complex_mud_terrain.png",
			"pos": _sk_pt(Vector3(95.0 * SURYAKUND_SCALE, 75.0 * SURYAKUND_SCALE, 105.0 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(0.0, 6.0 * SURYAKUND_SCALE, 0.0)),
			"fov": 58.0
		},
		{
			"name": "godot_suryakund_04_flat_mud_approach.png",
			"pos": _sk_pt(Vector3(0.0, 2.0, 72.0 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(0.0, 5.5 * SURYAKUND_SCALE, 0.0)),
			"fov": 65.0
		},
		{
			"name": "godot_suryakund_05_grand_stairs_naga_pillar.png",
			"pos": _sk_pt(Vector3(0.0, 2.2, -26.5 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(0.0, 4.8 * SURYAKUND_SCALE, -12.0 * SURYAKUND_SCALE)),
			"fov": 70.0
		},
		{
			"name": "godot_suryakund_06_subterranean_pool_linga_waterfall.png",
			"pos": _sk_pt(Vector3(0.0, -3.8 * SURYAKUND_SCALE, -6.5 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(0.0, -5.2 * SURYAKUND_SCALE, 6.0 * SURYAKUND_SCALE)),
			"fov": 75.0
		},
		{
			"name": "godot_suryakund_07_indoor_vault_voxelgi.png",
			"pos": _sk_pt(Vector3(0.0, -3.2 * SURYAKUND_SCALE, 2.0 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(0.0, 14.0 * SURYAKUND_SCALE, -2.0 * SURYAKUND_SCALE)),
			"fov": 75.0
		},
		{
			"name": "godot_suryakund_08_roof_golden_lingas_zigzag.png",
			"pos": _sk_pt(Vector3(32.0 * SURYAKUND_SCALE, 26.0 * SURYAKUND_SCALE, 52.0 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(0.0, 15.0 * SURYAKUND_SCALE, 20.0 * SURYAKUND_SCALE)),
			"fov": 65.0
		},
		{
			"name": "godot_suryakund_09_naga_step_seating_closeup.png",
			"pos": _sk_pt(Vector3(0.0, -1.2, -18.0 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(0.0, -1.8, -14.4 * SURYAKUND_SCALE)),
			"fov": 55.0
		},
		{
			"name": "godot_suryakund_10_stair_sidewall_rock_blocks.png",
			"pos": _sk_pt(Vector3(-12.0 * SURYAKUND_SCALE, 0.5, -24.0 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(-23.6 * SURYAKUND_SCALE, -1.0, -14.0 * SURYAKUND_SCALE)),
			"fov": 65.0
		},
		{
			"name": "godot_suryakund_11_outer_steps_ceiling_alignment.png",
			"pos": _sk_pt(Vector3(0.0, 1.8, 42.0 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(0.0, 9.0 * SURYAKUND_SCALE, 22.0 * SURYAKUND_SCALE)),
			"fov": 68.0
		},
		{
			"name": "godot_suryakund_12_straight_sun_copper_center.png",
			"pos": _sk_pt(Vector3(0.0, 7.8 * SURYAKUND_SCALE, -4.0 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(0.0, 7.8 * SURYAKUND_SCALE, 3.0 * SURYAKUND_SCALE)),
			"fov": 60.0
		},
		{
			"name": "godot_suryakund_13_stepped_321_rock_cascade.png",
			"pos": _sk_pt(Vector3(-12.0 * SURYAKUND_SCALE, 1.8 * SURYAKUND_SCALE, -22.0 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(-23.6 * SURYAKUND_SCALE, 1.8 * SURYAKUND_SCALE, -26.0 * SURYAKUND_SCALE)),
			"fov": 65.0
		},
		{
			"name": "godot_suryakund_14_sculpted_naga_pillar_closeup.png",
			"pos": _sk_pt(Vector3(0.0, 3.8 * SURYAKUND_SCALE, -20.0 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(0.0, 3.8 * SURYAKUND_SCALE, -14.85 * SURYAKUND_SCALE)),
			"fov": 50.0
		},
		{
			"name": "godot_suryakund_15_sarpa_vasal_pilgrimage_approach.png",
			"pos": SARPAVASAL_POS + Vector3(0.0, 3.5, -15.0),
			"look": _sk_pt(Vector3(0.0, 4.0 * SURYAKUND_SCALE, 35.0 * SURYAKUND_SCALE)),
			"fov": 65.0
		},
		{
			"name": "godot_suryakund_16_arrival_plaza_grand_steps_facade.png",
			"pos": _sk_pt(Vector3(0.0, 1.8, 62.0 * SURYAKUND_SCALE)),
			"look": _sk_pt(Vector3(0.0, 6.0 * SURYAKUND_SCALE, 10.0 * SURYAKUND_SCALE)),
			"fov": 68.0
		}
	]

	for f in range(5):
		await get_tree().process_frame

	for shot in shots:
		cam.position = shot["pos"]
		cam.fov = shot["fov"]
		cam.look_at(shot["look"], Vector3.UP)
		for f in range(3):
			await get_tree().process_frame
		await RenderingServer.frame_post_draw

		var vp = get_viewport()
		if vp:
			var img = vp.get_texture().get_image()
			if img:
				var path = "/home/mullainathan/Games/IshaGodot/" + shot["name"]
				img.save_png(path)
				var brain_dir = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures/"
				DirAccess.make_dir_recursive_absolute(brain_dir)
				img.save_png(brain_dir + shot["name"])
				print("[Capture] Successfully saved: ", path, " and brain artifact!")

	print("[Capture] All Suryakund screenshots captured!")
	get_tree().quit(0)

# ==============================================================================
# SARPA VASAL GATEWAY SETUP & AUTHENTIC REAL-WORLD PLACEMENT
# ==============================================================================
func _setup_sarpavasal_gateway():
	print("[SarpaVasal] Initializing Sarpa Vasal (The Sacred Snake Entrance Gateway)...")
	print("[SarpaVasal] GPS Coordinates: (", SARPAVASAL_LAT, " N, ", SARPAVASAL_LON, " E)")
	print("[SarpaVasal] Godot World Offset: ", SARPAVASAL_POS, " (bearing 317.6 deg NNW from Adiyogi, scale: ", SARPAVASAL_SCALE, "x)")

	var sv_root = Node3D.new()
	sv_root.name = "SarpaVasal_Precinct"
	add_child(sv_root)

	# --- 1. Instantiate Watertight 3D Rebuilt Sarpa Vasal Gateway GLB ---
	var sv_scene = load("res://assets/models/sarpavasal.glb")
	if not sv_scene:
		push_error("[SarpaVasal] Failed to load res://assets/models/sarpavasal.glb!")
		return

	var sv_inst = sv_scene.instantiate()
	sv_inst.name = "SarpaVasal_Gateway_Model"
	sv_inst.position = SARPAVASAL_POS # Sits directly on natural ground at Y = 0.0m
	sv_inst.rotation_degrees = Vector3(0.0, 42.42, 0.0) # Aligned straight toward Adiyogi along the sacred approach axis
	sv_inst.scale = Vector3(SARPAVASAL_SCALE, SARPAVASAL_SCALE, SARPAVASAL_SCALE)
	sv_root.add_child(sv_inst)

	# --- 2. Gateway Static Collision (Passable Dual Portals) ---
	var gate_body = StaticBody3D.new()
	gate_body.name = "SarpaVasal_Collision"
	gate_body.position = sv_inst.position
	gate_body.rotation_degrees = sv_inst.rotation_degrees
	sv_root.add_child(gate_body)

	var S = SARPAVASAL_SCALE
	# Central sculpted Naga column
	var center_col = CollisionShape3D.new()
	var center_shape = BoxShape3D.new()
	center_shape.size = Vector3(1.10 * S, 4.00 * S, 1.70 * S)
	center_col.shape = center_shape
	center_col.position = Vector3(0.0, 2.00 * S, 0.0)
	gate_body.add_child(center_col)

	# West (Left) flank pillar / wall
	var west_col = CollisionShape3D.new()
	var west_shape = BoxShape3D.new()
	west_shape.size = Vector3(1.10 * S, 4.00 * S, 1.70 * S)
	west_col.shape = west_shape
	west_col.position = Vector3(-3.55 * S, 2.00 * S, 0.0)
	gate_body.add_child(west_col)

	# East (Right) flank pillar / wall
	var east_col = CollisionShape3D.new()
	var east_shape = BoxShape3D.new()
	east_shape.size = Vector3(1.10 * S, 4.00 * S, 1.70 * S)
	east_col.shape = east_shape
	east_col.position = Vector3(3.55 * S, 2.00 * S, 0.0)
	gate_body.add_child(east_col)

	# Top frieze / lintel header & cornice
	var top_col = CollisionShape3D.new()
	var top_shape = BoxShape3D.new()
	top_shape.size = Vector3(8.40 * S, 1.25 * S, 1.90 * S)
	top_col.shape = top_shape
	top_col.position = Vector3(0.0, 3.65 * S, 0.0)
	gate_body.add_child(top_col)

	var dome_col = CollisionShape3D.new()
	var dome_shape = BoxShape3D.new()
	dome_shape.size = Vector3(8.40 * S, 2.20 * S, 1.80 * S)
	dome_col.shape = dome_shape
	dome_col.position = Vector3(0.0, 5.25 * S, 0.0)
	gate_body.add_child(dome_col)

	print("[SarpaVasal] Rebuilt Sarpa Vasal gateway standing directly on terrain with temple dome and passable dual portals!")

func _run_capture_sarpavasal_sequence():
	print("[Capture] Starting Sarpa Vasal gateway capture sequence...")
	var cam = Camera3D.new()
	cam.name = "CaptureCam"
	add_child(cam)
	cam.current = true
	cam.near = 0.25
	cam.far = 2500.0

	var S = SARPAVASAL_SCALE
	var rot_rad = deg_to_rad(42.42)
	var fwd = Vector3(sin(rot_rad), 0.0, cos(rot_rad)) # Directly toward Adiyogi
	var right = Vector3(cos(rot_rad), 0.0, -sin(rot_rad))
	var up = Vector3.UP

	var player = get_node_or_null("Player")
	if player:
		player.position = SARPAVASAL_POS + fwd * (18.0 * S) + Vector3(0.0, 0.35, 0.0)
		player.rotation_degrees = Vector3(0, 42.42 + 180.0, 0) # Facing toward Sarpa Vasal entrance

	var shots = [
		{
			"name": "godot_sarpavasal_01_monument_front_view.png",
			"pos": SARPAVASAL_POS + fwd * (16.0 * S) + up * (3.2 * S),
			"look": SARPAVASAL_POS + up * (3.2 * S),
			"fov": 55.0
		},
		{
			"name": "godot_sarpavasal_02_portal_pass_through.png",
			"pos": SARPAVASAL_POS + right * (-1.65 * S) - fwd * (6.0 * S) + up * (2.2 * S),
			"look": SARPAVASAL_POS + right * (-1.65 * S) + fwd * (60.0 * S) + up * (2.2 * S),
			"fov": 68.0
		},
		{
			"name": "godot_sarpavasal_03_side_extrusion_granite.png",
			"pos": SARPAVASAL_POS + right * (10.0 * S) + fwd * (8.0 * S) + up * (3.5 * S),
			"look": SARPAVASAL_POS + up * (3.2 * S),
			"fov": 56.0
		},
		{
			"name": "godot_sarpavasal_04_rear_facade_view.png",
			"pos": SARPAVASAL_POS - fwd * (13.0 * S) + up * (3.5 * S),
			"look": SARPAVASAL_POS + up * (3.2 * S),
			"fov": 60.0
		},
		{
			"name": "godot_sarpavasal_05_aerial_geographic_axis.png",
			"pos": SARPAVASAL_POS + right * (20.0 * S) + fwd * (30.0 * S) + up * (38.0 * S),
			"look": SARPAVASAL_POS - fwd * (15.0 * S) + up * (5.0 * S),
			"fov": 60.0
		},
		{
			"name": "godot_sarpavasal_06_sculpted_naga_closeup.png",
			"pos": SARPAVASAL_POS + fwd * (4.5 * S) + up * (2.0 * S),
			"look": SARPAVASAL_POS + up * (2.0 * S),
			"fov": 42.0
		}
	]

	for f in range(5):
		await get_tree().process_frame

	for shot in shots:
		cam.position = shot["pos"]
		cam.fov = shot["fov"]
		cam.look_at(shot["look"], Vector3.UP)
		for f in range(3):
			await get_tree().process_frame
		await RenderingServer.frame_post_draw

		var vp = get_viewport()
		if vp:
			var img = vp.get_texture().get_image()
			if img:
				var path = "/home/mullainathan/Games/IshaGodot/" + shot["name"]
				img.save_png(path)
				var brain_dir = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures/"
				DirAccess.make_dir_recursive_absolute(brain_dir)
				img.save_png(brain_dir + shot["name"])
				print("[Capture] Successfully saved: ", path, " and brain artifact!")

	print("[Capture] All Sarpa Vasal screenshots captured!")
	get_tree().quit(0)

# ==============================================================================
# LINGA BHAIRAVI TEMPLE COMPLEX INITIALIZATION & CAPTURE
# ==============================================================================

func _setup_lingabhairavi_temple():
	print("[LingaBhairavi] Initializing Linga Bhairavi Temple at exact real-world coordinates...")
	print("[LingaBhairavi] GPS Coordinates: (", LINGABHAIRAVI_LAT, " N, ", LINGABHAIRAVI_LON, " E)")
	print("[LingaBhairavi] Godot World Offset: ", LINGABHAIRAVI_POS, " (distance: 846.85m NNW from Adiyogi, bearing: 314.37 deg)")
	print("[LingaBhairavi] Entrance Facing Bearing: 52.59 deg ENE (Godot Y-Rotation: ", LINGABHAIRAVI_ROT_DEG, " deg)")
	print("[LingaBhairavi] Distance to Suryakund: 228.33m due West; Distance to Sarpa Vasal: 265.70m WNW")

	var lb_root = Node3D.new()
	lb_root.name = "LingaBhairavi_Precinct"
	add_child(lb_root)

	var lb_scene = load("res://assets/models/lingabhairavi_temple.glb")
	if not lb_scene:
		push_error("[LingaBhairavi] Failed to load res://assets/models/lingabhairavi_temple.glb!")
		return

	var lb_inst = lb_scene.instantiate()
	lb_inst.name = "LingaBhairavi_Temple"
	lb_inst.position = LINGABHAIRAVI_POS
	lb_inst.rotation_degrees = Vector3(0.0, LINGABHAIRAVI_ROT_DEG, 0.0)
	lb_inst.scale = Vector3(LINGABHAIRAVI_SCALE, LINGABHAIRAVI_SCALE, LINGABHAIRAVI_SCALE)
	lb_root.add_child(lb_inst)

	_cleanup_imported_nodes_recursive(lb_inst)
	_calibrate_lingabhairavi_materials_recursive(lb_inst)
	_set_gi_static_recursive(lb_inst)
	_setup_lingabhairavi_physics(lb_root, lb_inst)
	_setup_lingabhairavi_lighting(lb_root)
	print("[LingaBhairavi] Linga Bhairavi Temple successfully loaded and placed at exact real-world location!")

func _cleanup_imported_nodes_recursive(node: Node):
	var to_remove = []
	for child in node.get_children():
		if child is Light3D or child is Camera3D:
			to_remove.append(child)
		else:
			_cleanup_imported_nodes_recursive(child)
	for r in to_remove:
		if r.get_parent():
			r.get_parent().remove_child(r)
		r.queue_free()

func _calibrate_lingabhairavi_materials_recursive(node: Node):
	if node is MeshInstance3D:
		var mi = node as MeshInstance3D
		var mname = mi.name.to_lower()
		if "col_suryakund_pillar" in mname or "pillar_front" in mname or ("col_" in mname and "front" in mname) or "suryakund_pillar" in mname:
			mi.material_override = _get_suryakund_pillar_shared_material()
		elif mi.mesh:
			for i in range(mi.mesh.get_surface_count()):
				var mat = mi.get_surface_override_material(i)
				if not mat:
					mat = mi.mesh.surface_get_material(i)
				if mat is StandardMaterial3D:
					var sm = mat as StandardMaterial3D
					if sm.emission_enabled:
						sm.emission_energy_multiplier = min(sm.emission_energy_multiplier, 0.8)
						sm.emission = Color(1.0, 0.65, 0.2)
	for child in node.get_children():
		_calibrate_lingabhairavi_materials_recursive(child)

func _setup_lingabhairavi_physics(lb_root: Node3D, lb_inst: Node):
	print("[LingaBhairavi] Generating precision trimesh static collision for temple floors, steps, dais & walls...")
	_add_trimesh_collision_recursive(lb_inst)

func _add_trimesh_collision_recursive(node: Node):
	if node is MeshInstance3D:
		var n_low = node.name.to_lower()
		# Create collision for structural architectural elements
		if "plinth" in n_low or "step" in n_low or "floor" in n_low or "wall" in n_low or "portal" in n_low or "sanctum" in n_low or "dais" in n_low or "col_" in n_low or "court" in n_low or "curb" in n_low:
			node.create_trimesh_collision()
	for child in node.get_children():
		_add_trimesh_collision_recursive(child)

func _setup_lingabhairavi_lighting(lb_root: Node3D):
	# Sacred architectural illumination for the vast subterranean hall & Devi sanctum
	# 1. Front Forecourt Hall Ceiling Downlight (Above upper forecourt floor)
	var omni_front = OmniLight3D.new()
	omni_front.name = "Omni_Hall_Front"
	omni_front.position = _lb_pt(Vector3(0.0, 2.8, 5.0))
	omni_front.light_color = Color(1.0, 0.86, 0.60)
	omni_front.light_energy = 2.0
	omni_front.omni_range = 14.0
	omni_front.shadow_enabled = false
	lb_root.add_child(omni_front)

	# 2. Central Trishul Dedicated Golden Spotlight (At Z = 10.0m)
	var spot_trishul = SpotLight3D.new()
	spot_trishul.name = "Spot_Trishul_Center"
	spot_trishul.position = _lb_pt(Vector3(0.0, 4.6, 7.2))
	spot_trishul.light_color = Color(1.0, 0.92, 0.72)
	spot_trishul.light_energy = 4.5
	spot_trishul.spot_range = 10.0
	spot_trishul.spot_angle = 38.0
	spot_trishul.spot_attenuation = 1.0
	spot_trishul.shadow_enabled = true
	lb_root.add_child(spot_trishul)
	spot_trishul.look_at(_lb_pt(Vector3(0.0, 2.77, 10.0)), Vector3.UP)

	var omni_trishul = OmniLight3D.new()
	omni_trishul.name = "Omni_Trishul_Glow"
	omni_trishul.position = _lb_pt(Vector3(0.0, 2.2, 10.0))
	omni_trishul.light_color = Color(1.0, 0.88, 0.60)
	omni_trishul.light_energy = 1.8
	omni_trishul.omni_range = 8.0
	omni_trishul.shadow_enabled = false
	lb_root.add_child(omni_trishul)

	# 3. Mid Approach Hall Downlight (Between Trishul and Big Pillars)
	var omni_mid = OmniLight3D.new()
	omni_mid.name = "Omni_Hall_Mid"
	omni_mid.position = _lb_pt(Vector3(0.0, 2.8, 15.0))
	omni_mid.light_color = Color(1.0, 0.86, 0.60)
	omni_mid.light_energy = 2.0
	omni_mid.omni_range = 14.0
	omni_mid.shadow_enabled = false
	lb_root.add_child(omni_mid)

	# 4. Big Pillars Naga Architrave Accent Spotlight (At Z = 20.0m, Brightly illuminating Patched Naga Panel)
	var spot_arch = SpotLight3D.new()
	spot_arch.name = "Spot_Pillar_Arch"
	spot_arch.position = _lb_pt(Vector3(0.0, 4.8, 16.5))
	spot_arch.light_color = Color(1.0, 0.94, 0.78)
	spot_arch.light_energy = 5.5
	spot_arch.spot_range = 10.0
	spot_arch.spot_angle = 48.0
	spot_arch.spot_attenuation = 1.0
	spot_arch.shadow_enabled = true
	lb_root.add_child(spot_arch)
	spot_arch.look_at(_lb_pt(Vector3(0.0, 5.50, 20.0)), Vector3.UP)

	var omni_arch = OmniLight3D.new()
	omni_arch.name = "Omni_Pillar_Arch_Accent"
	omni_arch.position = _lb_pt(Vector3(0.0, 5.50, 19.6))
	omni_arch.light_color = Color(1.0, 0.92, 0.75)
	omni_arch.light_energy = 2.5
	omni_arch.omni_range = 6.0
	omni_arch.shadow_enabled = false
	lb_root.add_child(omni_arch)

	# 5. Far Sanctum Dais Focal Light (Above Expanded Sunken Gap)
	var omni_dais = OmniLight3D.new()
	omni_dais.name = "Omni_Sanctum_Dais"
	omni_dais.position = _lb_pt(Vector3(0.0, 2.8, 29.5))
	omni_dais.light_color = Color(1.0, 0.82, 0.50)
	omni_dais.light_energy = 2.6
	omni_dais.omni_range = 14.0
	omni_dais.shadow_enabled = true
	lb_root.add_child(omni_dais)

	# Corridor lighting removed per user request: "remove the lighting which is in the coridoor"
	# The expanded entrance colonnade corridor is naturally illuminated by ambient open-sky daylight.

	# 8. Focused Warm Spotlight directly on the Devi Sanctum Bas-Relief Panel (Z = 30.00m)
	var spot_devi = SpotLight3D.new()
	spot_devi.name = "Spot_Devi_Sanctum"
	spot_devi.position = _lb_pt(Vector3(0.0, 3.8, 27.5))
	spot_devi.light_color = Color(1.0, 0.90, 0.70)
	spot_devi.light_energy = 5.5
	spot_devi.spot_range = 10.0
	spot_devi.spot_angle = 35.0
	spot_devi.spot_attenuation = 1.0
	spot_devi.shadow_enabled = true
	lb_root.add_child(spot_devi)
	spot_devi.look_at(_lb_pt(Vector3(0.0, 1.30, 30.00)), Vector3.UP)

func _run_capture_lingabhairavi_sequence():
	print("[Capture] Starting Linga Bhairavi Temple capture sequence at exact real-world coordinates...")
	var cam = Camera3D.new()
	cam.name = "CaptureCam_LingaBhairavi"
	add_child(cam)
	cam.current = true
	cam.near = 0.25
	cam.far = 2500.0

	var player = get_node_or_null("Player")
	if player:
		player.position = _lb_pt(Vector3(0.0, 0.1, -15.0))
		player.rotation_degrees = Vector3(0, LINGABHAIRAVI_ROT_DEG, 0)

	var shots = [
		{
			"name": "godot_lingabhairavi_01_monumental_front_facade.png",
			"pos": _lb_pt(Vector3(0.0, 3.2, -24.0)),
			"look": _lb_pt(Vector3(0.0, 2.5, -6.0)),
			"fov": 65.0
		},
		{
			"name": "godot_lingabhairavi_02_front_perspective_water_reflect.png",
			"pos": _lb_pt(Vector3(18.0, 3.0, -20.0)),
			"look": _lb_pt(Vector3(0.0, 2.5, -6.0)),
			"fov": 60.0
		},
		{
			"name": "godot_lingabhairavi_03_entrance_porch_and_diya_niches.png",
			"pos": _lb_pt(Vector3(5.5, 1.8, -9.5)),
			"look": _lb_pt(Vector3(0.0, 2.2, 0.0)),
			"fov": 65.0
		},
		{
			"name": "godot_lingabhairavi_03b_door_naga_panel_and_copper_niches.png",
			"pos": _lb_pt(Vector3(0.0, 2.8, -5.5)),
			"look": _lb_pt(Vector3(0.0, 3.6, 0.0)),
			"fov": 60.0
		},
		{
			"name": "godot_lingabhairavi_04_interior_through_portal.png",
			"pos": _lb_pt(Vector3(0.0, 1.68, -0.35)),
			"look": _lb_pt(Vector3(0.0, 2.50, 10.0)),
			"fov": 65.0
		},
		{
			"name": "godot_lingabhairavi_05_interior_sunken_hall_and_seating.png",
			"pos": _lb_pt(Vector3(-2.8, 1.80, 6.0)),
			"look": _lb_pt(Vector3(0.0, 2.70, 10.0)),
			"fov": 65.0
		},
		{
			"name": "godot_lingabhairavi_06_interior_devi_garbhagriha_closeup.png",
			"pos": _lb_pt(Vector3(0.0, 1.65, 27.00)),
			"look": _lb_pt(Vector3(0.0, 1.30, 30.00)),
			"fov": 52.0
		},
		{
			"name": "godot_lingabhairavi_07_exterior_triangular_rear_sanctum.png",
			"pos": _lb_pt(Vector3(22.0, 10.0, 28.0)),
			"look": _lb_pt(Vector3(0.0, 4.0, 15.0)),
			"fov": 55.0
		},
		{
			"name": "godot_lingabhairavi_08_pilgrimage_approach_from_suryakund.png",
			"pos": Vector3(-495.0, 2.2, -560.0),
			"look": LINGABHAIRAVI_POS + Vector3(0.0, 3.0, 0.0),
			"fov": 62.0
		},
		{
			"name": "godot_lingabhairavi_09_aerial_geographic_orientation.png",
			"pos": Vector3(-480.0, 150.0, -360.0),
			"look": LINGABHAIRAVI_POS + Vector3(0.0, 5.0, 0.0),
			"fov": 60.0
		},
		{
			"name": "godot_lingabhairavi_10_devi_interior_replica.png",
			"pos": _lb_pt(Vector3(0.0, 1.95, 1.50)),
			"look": _lb_pt(Vector3(0.0, 2.75, 22.00)),
			"fov": 75.0
		},
		{
			"name": "godot_lingabhairavi_11_forecourt_metal_chains_sky_up.png",
			"pos": _lb_pt(Vector3(0.0, 1.45, 9.50)),
			"look": _lb_pt(Vector3(0.0, 7.50, 9.80)),
			"fov": 84.0
		},
		{
			"name": "godot_lingabhairavi_12_sanctum_raised_flat_roof_exterior.png",
			"pos": _lb_pt(Vector3(18.0, 11.5, 32.0)),
			"look": _lb_pt(Vector3(0.0, 7.8, 28.0)),
			"fov": 58.0
		}
	]

	for f in range(5):
		await get_tree().process_frame

	for shot in shots:
		cam.position = shot["pos"]
		cam.fov = shot["fov"]
		var look_dir = (shot["look"] - shot["pos"]).normalized()
		var up_vec = Vector3.UP
		if abs(look_dir.dot(Vector3.UP)) > 0.95:
			up_vec = Vector3.FORWARD.rotated(Vector3.UP, deg_to_rad(LINGABHAIRAVI_ROT_DEG))
		cam.look_at(shot["look"], up_vec)
		for f in range(3):
			await get_tree().process_frame
		await RenderingServer.frame_post_draw

		var vp = get_viewport()
		if vp:
			var img = vp.get_texture().get_image()
			if img:
				var path = "/home/mullainathan/Games/IshaGodot/" + shot["name"]
				img.save_png(path)
				var brain_dir = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures/"
				DirAccess.make_dir_recursive_absolute(brain_dir)
				img.save_png(brain_dir + shot["name"])
				print("[Capture] Successfully saved: ", path, " and brain artifact!")

	print("[Capture] All Linga Bhairavi screenshots captured successfully!")
	get_tree().quit(0)

func _run_capture_pro_realism_sequence():
	print("[Capture] Starting Pro Realistic Lighting & Full Map showcase sequence...")
	var cam = Camera3D.new()
	cam.name = "CaptureCam_ProRealism"
	add_child(cam)
	cam.current = true
	cam.near = 0.25
	cam.far = 2500.0

	var shots = [
		{
			"name": "godot_pro_01_adiyogi_monumental_daylight.png",
			"pos": Vector3(0.0, 4.5, 75.0),
			"look": Vector3(0.0, 22.0, 0.0),
			"fov": 64.0
		},
		{
			"name": "godot_pro_02_grand_ceremonial_avenue.png",
			"pos": Vector3(0.0, 3.5, 240.0),
			"look": Vector3(0.0, 2.2, 440.0),
			"fov": 68.0
		},
		{
			"name": "godot_pro_03_suryakund_dravidian_colonnade.png",
			"pos": Vector3(-409.30, 4.2, -532.0),
			"look": Vector3(-409.30, 2.2, -562.0),
			"fov": 65.0
		},
		{
			"name": "godot_pro_04_lingabhairavi_front_pillars_and_facade.png",
			"pos": _lb_pt(Vector3(0.0, 2.6, -17.5)),
			"look": _lb_pt(Vector3(0.0, 2.4, -4.0)),
			"fov": 64.0
		},
		{
			"name": "godot_pro_05_lingabhairavi_corridor_perspective.png",
			"pos": _lb_pt(Vector3(9.2, 2.1, -9.5)),
			"look": _lb_pt(Vector3(-4.5, 2.2, -7.0)),
			"fov": 65.0
		},
		{
			"name": "godot_pro_06_malai_vasal_monumental_gate.png",
			"pos": Vector3(0.0, 3.5, 520.0),
			"look": Vector3(0.0, 5.0, 570.0),
			"fov": 62.0
		}
	]

	for f in range(8):
		await get_tree().process_frame

	for shot in shots:
		cam.position = shot["pos"]
		cam.fov = shot["fov"]
		cam.look_at(shot["look"], Vector3.UP)
		for f in range(4):
			await get_tree().process_frame
		await RenderingServer.frame_post_draw

		var vp = get_viewport()
		if vp:
			var img = vp.get_texture().get_image()
			if img:
				var path = "/home/mullainathan/Games/IshaGodot/" + shot["name"]
				img.save_png(path)
				var brain_dir = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures/"
				DirAccess.make_dir_recursive_absolute(brain_dir)
				img.save_png(brain_dir + shot["name"])
				print("[Capture] Successfully saved: ", path, " and brain artifact!")

	print("[Capture] All Pro-Realistic map showcase screenshots captured successfully!")
	get_tree().quit(0)

# ==============================================================================
# DHYANALINGA TEMPLE COMPLEX INITIALIZATION, LIGHTING & SHOWCASE CAPTURE
# ==============================================================================

func _setup_dhyanalinga_temple():
	print("[Dhyanalinga] Initializing Dhyanalinga Temple at exact real-world coordinates...")
	print("[Dhyanalinga] GPS Coordinates: (", DHYANALINGA_LAT, " N, ", DHYANALINGA_LON, " E)")
	print("[Dhyanalinga] Godot World Offset: ", DHYANALINGA_POS, " (distance: 841.07m NNW from Adiyogi, bearing: 317.95 deg)")
	print("[Dhyanalinga] Entrance Facing East (Godot Y-Rotation: ", DHYANALINGA_ROT_DEG, " deg)")
	print("[Dhyanalinga] Distance to Linga Bhairavi: 53.00m ENE; Distance to Suryakund: 187.25m due West")

	var dl_root = Node3D.new()
	dl_root.name = "Dhyanalinga_Precinct"
	add_child(dl_root)

	var dl_scene = load("res://assets/models/dhyanalinga_temple.glb")
	if not dl_scene:
		push_error("[Dhyanalinga] Failed to load res://assets/models/dhyanalinga_temple.glb!")
		return

	var dl_inst = dl_scene.instantiate()
	dl_inst.name = "Dhyanalinga_Temple"
	dl_inst.position = DHYANALINGA_POS
	dl_inst.rotation_degrees = Vector3(0.0, DHYANALINGA_ROT_DEG, 0.0)
	dl_inst.scale = Vector3(DHYANALINGA_SCALE, DHYANALINGA_SCALE, DHYANALINGA_SCALE)
	dl_root.add_child(dl_inst)

	_cleanup_imported_nodes_recursive(dl_inst)
	_calibrate_dhyanalinga_materials_recursive(dl_inst)
	_set_gi_static_recursive(dl_inst)
	_setup_dhyanalinga_physics(dl_root, dl_inst)
	_setup_dhyanalinga_lighting(dl_root)
	print("[Dhyanalinga] Dhyanalinga Temple successfully loaded and placed at exact real-world location!")

func _calibrate_dhyanalinga_materials_recursive(node: Node):
	if node is MeshInstance3D:
		var mi = node as MeshInstance3D
		if mi.mesh:
			for i in range(mi.mesh.get_surface_count()):
				var mat = mi.get_surface_override_material(i)
				if not mat:
					mat = mi.mesh.surface_get_material(i)
				if mat is StandardMaterial3D:
					var sm = mat as StandardMaterial3D
					if sm.emission_enabled:
						sm.emission_energy_multiplier = min(sm.emission_energy_multiplier, 1.2)
						sm.emission = Color(1.0, 0.70, 0.25)
	for child in node.get_children():
		_calibrate_dhyanalinga_materials_recursive(child)

func _setup_dhyanalinga_physics(dl_root: Node3D, dl_inst: Node):
	print("[Dhyanalinga] Generating precision trimesh static collision for Dhyanalinga architecture...")
	_add_trimesh_collision_recursive(dl_inst)

func _setup_dhyanalinga_lighting(dl_root: Node3D):
	print("[Dhyanalinga] Configuring authentic sacred architectural lighting & VoxelGI...")

	# 1. Crown Oculus Natural Light Beam
	# Powerful natural downlight streaming from the oculus cupola directly onto the Linga
	var spot_oculus = SpotLight3D.new()
	spot_oculus.name = "SpotLight_Oculus_Ray"
	spot_oculus.position = _dl_pt(Vector3(0.0, 10.4, 0.0))
	spot_oculus.rotation_degrees = Vector3(-90.0, 0.0, 0.0)
	spot_oculus.spot_angle = 24.0
	spot_oculus.spot_attenuation = 0.8
	spot_oculus.spot_range = 14.0
	spot_oculus.light_color = Color(1.0, 0.96, 0.90)
	spot_oculus.light_energy = 4.2
	spot_oculus.shadow_enabled = true
	dl_root.add_child(spot_oculus)

	# 2. Sacred Sanctum Spotlights (Highlighting Dhyanalinga Monolith & Seven-Coiled Serpent)
	for side_i in [-1.0, 1.0]:
		var spot_linga = SpotLight3D.new()
		spot_linga.name = "SpotLight_Linga_" + ("Left" if side_i < 0 else "Right")
		dl_root.add_child(spot_linga)
		spot_linga.position = _dl_pt(Vector3(side_i * 4.5, 4.2, -4.5))
		spot_linga.look_at(_dl_pt(Vector3(0.0, 2.2, 0.0)), Vector3.UP)
		spot_linga.spot_angle = 38.0
		spot_linga.spot_range = 9.5
		spot_linga.light_color = Color(1.0, 0.84, 0.65)
		spot_linga.light_energy = 2.0
		spot_linga.shadow_enabled = true

	# 3. Soft Sanctum Warm Ambient Fill (Subtle reverent interior radiance)
	var omni_sanctum = OmniLight3D.new()
	omni_sanctum.name = "Omni_Sanctum_Radiance"
	dl_root.add_child(omni_sanctum)
	omni_sanctum.position = _dl_pt(Vector3(0.0, 4.5, 0.0))
	omni_sanctum.omni_range = 14.0
	omni_sanctum.omni_attenuation = 1.2
	omni_sanctum.light_color = Color(1.0, 0.72, 0.42)
	omni_sanctum.light_energy = 0.9
	omni_sanctum.shadow_enabled = false

	# 4. Vaulted Entrance Tunnel Deepams (Warm golden illumination in corridor)
	for t_y in [-13.0, -16.0, -19.0]:
		var omni_tun = OmniLight3D.new()
		omni_tun.name = "Omni_Vestibule_Diya_" + str(abs(round(t_y)))
		dl_root.add_child(omni_tun)
		omni_tun.position = _dl_pt(Vector3(0.0, 2.4, t_y))
		omni_tun.omni_range = 5.5
		omni_tun.omni_attenuation = 1.0
		omni_tun.light_color = Color(1.0, 0.68, 0.28)
		omni_tun.light_energy = 1.1
		omni_tun.shadow_enabled = false

	# 5. Sarva Dharma Sthambha Dedicated Uplights
	for sd_angle in [0.0, 90.0, 180.0, 270.0]:
		var rad_a = deg_to_rad(sd_angle)
		var lx = 2.4 * cos(rad_a)
		var lz = -33.5 + 2.4 * sin(rad_a)
		var spot_sd = SpotLight3D.new()
		spot_sd.name = "SpotLight_SarvaDharma_" + str(int(sd_angle))
		dl_root.add_child(spot_sd)
		spot_sd.position = _dl_pt(Vector3(lx, -0.6, lz))
		spot_sd.look_at(_dl_pt(Vector3(0.0, 3.2, -33.5)), Vector3.UP)
		spot_sd.spot_angle = 32.0
		spot_sd.spot_range = 7.5
		spot_sd.light_color = Color(1.0, 0.92, 0.82)
		spot_sd.light_energy = 1.8
		spot_sd.shadow_enabled = true

func _run_capture_dhyanalinga_sequence():
	print("[Capture] Starting Dhyanalinga Temple multi-angle inspection capture sequence...")
	var cam = Camera3D.new()
	cam.name = "CaptureCam_Dhyanalinga"
	add_child(cam)
	cam.current = true
	cam.near = 0.25
	cam.far = 2500.0

	var shots = [
		{
			"name": "godot_dhyanalinga_01_elliptical_dome_exterior_facade.png",
			"pos": _dl_pt(Vector3(0.0, 4.5, -28.0)),
			"look": _dl_pt(Vector3(0.0, 5.0, 0.0)),
			"fov": 68.0
		},
		{
			"name": "godot_dhyanalinga_02_sarva_dharma_sthambha_monolith.png",
			"pos": _dl_pt(Vector3(3.5, 0.8, -38.5)),
			"look": _dl_pt(Vector3(0.0, 2.5, -33.5)),
			"fov": 58.0
		},
		{
			"name": "godot_dhyanalinga_03_thorana_gateway_and_pebble_steps.png",
			"pos": _dl_pt(Vector3(0.0, 0.4, -26.0)),
			"look": _dl_pt(Vector3(0.0, 1.8, -19.0)),
			"fov": 62.0
		},
		{
			"name": "godot_dhyanalinga_04_vaulted_entrance_vestibule.png",
			"pos": _dl_pt(Vector3(0.0, 1.6, -17.5)),
			"look": _dl_pt(Vector3(0.0, 1.8, -2.0)),
			"fov": 65.0
		},
		{
			"name": "godot_dhyanalinga_05_inner_sanctum_wide_pillarless_dome.png",
			"pos": _dl_pt(Vector3(0.0, 1.6, -8.5)),
			"look": _dl_pt(Vector3(0.0, 2.8, 0.0)),
			"fov": 75.0
		},
		{
			"name": "godot_dhyanalinga_06_dhyanalinga_monolith_closeup.png",
			"pos": _dl_pt(Vector3(0.0, 1.6, -4.8)),
			"look": _dl_pt(Vector3(0.0, 2.2, 0.0)),
			"fov": 55.0
		},
		{
			"name": "godot_dhyanalinga_07_seven_coiled_serpent_prabhavali.png",
			"pos": _dl_pt(Vector3(1.8, 2.2, 1.8)),
			"look": _dl_pt(Vector3(0.0, 2.6, 0.4)),
			"fov": 50.0
		},
		{
			"name": "godot_dhyanalinga_08_jalaseema_water_pool_and_lotuses.png",
			"pos": _dl_pt(Vector3(-2.8, 1.8, -4.2)),
			"look": _dl_pt(Vector3(-0.8, -0.1, -1.5)),
			"fov": 62.0
		},
		{
			"name": "godot_dhyanalinga_09_aura_cells_meditation_cubicles.png",
			"pos": _dl_pt(Vector3(7.5, 1.5, -4.0)),
			"look": _dl_pt(Vector3(9.2, 1.6, 2.5)),
			"fov": 65.0
		},
		{
			"name": "godot_dhyanalinga_10_aerial_elliptical_dome_complex.png",
			"pos": _dl_pt(Vector3(18.0, 26.0, -52.0)),
			"look": _dl_pt(Vector3(0.0, 4.0, -10.0)),
			"fov": 62.0
		},
		{
			"name": "godot_dhyanalinga_11_pilgrimage_approach_from_suryakund.png",
			"pos": _dl_pt(Vector3(0.0, 2.2, -65.0)),
			"look": _dl_pt(Vector3(0.0, 3.5, -20.0)),
			"fov": 65.0
		},
		{
			"name": "godot_dhyanalinga_12_sunken_reception_lily_ponds.png",
			"pos": _dl_pt(Vector3(-7.5, 0.2, -31.0)),
			"look": _dl_pt(Vector3(0.0, 2.2, -33.5)),
			"fov": 60.0
		}
	]

	for f in range(4):
		await get_tree().process_frame

	for shot in shots:
		cam.position = shot["pos"]
		cam.fov = shot["fov"]
		cam.look_at(shot["look"], Vector3.UP)
		for f in range(2):
			await get_tree().process_frame
		await RenderingServer.frame_post_draw

		var vp = get_viewport()
		if vp:
			var img = vp.get_texture().get_image()
			if img:
				var path = "/home/mullainathan/Games/IshaGodot/" + shot["name"]
				img.save_png(path)
				var brain_dir = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures/"
				DirAccess.make_dir_recursive_absolute(brain_dir)
				img.save_png(brain_dir + shot["name"])
				print("[Capture] Successfully saved: ", path, " and brain artifact!")

	print("[Capture] All Dhyanalinga screenshots captured successfully!")
	get_tree().quit(0)
