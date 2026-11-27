import bpy
import os

print("[Bake] Loading blend file and material...")
blend_path = "/home/mullainathan/Games/IshaGodot/assets/terracotta_roof_tiles.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

mat = bpy.data.materials.get("Procedural Terracotta Roof Tiles")
if not mat:
    print("[Bake] ERROR: Material not found!")
    exit(1)

# Ensure Cycles
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 1
scene.cycles.bake_type = 'DIFFUSE'

# Create a simple UV plane (1m x 1m, UV 0 to 1)
bpy.ops.mesh.primitive_plane_add(size=2.0, enter_editmode=False, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "Bake_Plane"

# Ensure UV map is (0,0) to (1,1)
me = plane.data
uv_layer = me.uv_layers.active
if not uv_layer:
    uv_layer = me.uv_layers.new(name="UVMap")

plane.data.materials.clear()
plane.data.materials.append(mat)

# Setup Image Texture node in mat.node_tree for baking target
tex_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
tex_node.name = "BakeTargetNode"
mat.node_tree.nodes.active = tex_node
tex_node.select = True

out_dir = "/home/mullainathan/Games/IshaGodot/assets/textures"
os.makedirs(out_dir, exist_ok=True)

res = 2048

# 1. Bake Color (Albedo / Diffuse)
print("[Bake] Baking 2K Albedo / Color...")
img_color = bpy.data.images.new("Terracotta_Color", width=res, height=res, alpha=False)
tex_node.image = img_color

# Connect Base Color to Emission for fast clean bake without lighting
bsdf = mat.node_tree.nodes.get("Principled BSDF")
output = mat.node_tree.nodes.get("Material Output")

emit_node = mat.node_tree.nodes.new(type="ShaderNodeEmission")
mix_color = mat.node_tree.nodes.get("Mix.002")
if mix_color:
    mat.node_tree.links.new(mix_color.outputs["Result"], emit_node.inputs["Color"])
    mat.node_tree.links.new(emit_node.outputs["Emission"], output.inputs["Surface"])

scene.cycles.bake_type = 'EMIT'
bpy.ops.object.bake(type='EMIT')
color_path = os.path.join(out_dir, "terracotta_tiles_color.png")
img_color.filepath_raw = color_path
img_color.file_format = 'PNG'
img_color.save()
print(f"[Bake] Saved Color to: {color_path}")

# 2. Bake Normal Map
print("[Bake] Baking 2K Normal Map...")
img_normal = bpy.data.images.new("Terracotta_Normal", width=res, height=res, alpha=False)
tex_node.image = img_normal

# Restore BSDF to output surface
mat.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
scene.cycles.bake_type = 'NORMAL'
scene.render.bake.normal_space = 'TANGENT'
bpy.ops.object.bake(type='NORMAL')
normal_path = os.path.join(out_dir, "terracotta_tiles_normal.png")
img_normal.filepath_raw = normal_path
img_normal.file_format = 'PNG'
img_normal.save()
print(f"[Bake] Saved Normal to: {normal_path}")

# 3. Bake Roughness Map
print("[Bake] Baking 2K Roughness Map...")
img_rough = bpy.data.images.new("Terracotta_Roughness", width=res, height=res, alpha=False)
tex_node.image = img_rough
scene.cycles.bake_type = 'ROUGHNESS'
bpy.ops.object.bake(type='ROUGHNESS')
rough_path = os.path.join(out_dir, "terracotta_tiles_roughness.png")
img_rough.filepath_raw = rough_path
img_rough.file_format = 'PNG'
img_rough.save()
print(f"[Bake] Saved Roughness to: {rough_path}")

print("[Bake] ALL PROCEDURAL TERRACOTTA MAPS BAKED SUCCESSFULLY!")
