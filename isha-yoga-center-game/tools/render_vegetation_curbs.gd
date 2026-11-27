extends SceneTree

func _init():
	print(">>> Rendering 3D Curbs, Plants, Trees & Grass verification views...")
	var main_scene = load("res://scenes/main.tscn")
	if not main_scene:
		print("Error: Could not load main.tscn")
		quit(1)
		return

	var root = main_scene.instantiate()
	get_root().add_child(root)

	var cam = Camera3D.new()
	cam.name = "RenderCam"
	cam.fov = 68.0
	root.add_child(cam)
	cam.current = true

	var output_dir = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures/"

	var views = [
		{
			"name": "curb_and_vegetation_01_road_curb_closeup.png",
			"pos": Vector3(8.8, 0.75, 136.0),
			"look": Vector3(10.2, 0.35, 160.0),
			"desc": "Close-up of East dressed stone road curb, 3D grass tufts, shrubs and trees"
		},
		{
			"name": "curb_and_vegetation_02_courtyard_edge_transition.png",
			"pos": Vector3(0.0, 1.8, 110.0),
			"look": Vector3(0.0, 1.5, 180.0),
			"desc": "Courtyard to avenue transition showing road curbs, 3D grass, shrubs, and tree lines"
		},
		{
			"name": "curb_and_vegetation_03_midway_avenue_vista.png",
			"pos": Vector3(-3.5, 1.8, 280.0),
			"look": Vector3(0.0, 1.8, 420.0),
			"desc": "Mid-avenue view showing curbs, shrubs, neem trees, palms, and Malai Vasal ahead"
		},
		{
			"name": "curb_and_vegetation_04_looking_back_to_adiyogi.png",
			"pos": Vector3(4.0, 1.8, 480.0),
			"look": Vector3(0.0, 18.0, 15.0),
			"desc": "Looking North along tree-lined, curb-edged avenue towards Adiyogi"
		},
		{
			"name": "curb_and_vegetation_05_elevated_landscape_overview.png",
			"pos": Vector3(38.0, 26.0, 210.0),
			"look": Vector3(0.0, 4.0, 170.0),
			"desc": "Elevated view showing road curbs, neem trees, areca palms, shrubs, and grass beds"
		}
	]

	# Allow initial scene warm-up and shaders to load
	await create_timer(1.5).timeout

	for v in views:
		cam.position = v["pos"]
		cam.look_at(v["look"], Vector3.UP)
		print("Rendering: ", v["name"], " - ", v["desc"])

		await create_timer(0.5).timeout
		await RenderingServer.frame_post_draw

		var vp = root.get_viewport()
		if vp:
			var tex = vp.get_texture()
			if tex:
				var img = tex.get_image()
				if img:
					var out_path = output_dir + v["name"]
					img.save_png(out_path)
					print("Successfully saved: ", out_path)

	print(">>> All verification views rendered successfully!")
	quit(0)
