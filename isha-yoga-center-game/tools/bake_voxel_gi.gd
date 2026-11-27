extends SceneTree

func _init():
	print("[VoxelGI] Loading main scene for test bake...")
	var main_res = load("res://scenes/main.tscn")
	if not main_res:
		print("[VoxelGI] Error loading main.tscn")
		quit(1)
		return
	var main = main_res.instantiate()
	root.add_child(main)
	
	# Wait for ready and frames
	for f in range(5):
		await process_frame
	
	var vgi: VoxelGI = main.get_node_or_null("VoxelGI")
	if vgi:
		print("[VoxelGI] Found VoxelGI node! Calling bake()...")
		vgi.bake(main)
		print("[VoxelGI] Bake finished! vgi.data = ", vgi.data)
		if vgi.data:
			ResourceSaver.save(vgi.data, "res://assets/voxel_gi_data.res")
			print("[VoxelGI] Saved voxel_gi_data.res successfully!")
	else:
		print("[VoxelGI] VoxelGI node not found!")
	quit(0)
