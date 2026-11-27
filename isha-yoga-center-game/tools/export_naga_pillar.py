import bpy
import bmesh
import math
import mathutils

blend_file = "/home/mullainathan/Downloads/naga_pillar_complete.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

naga = bpy.data.objects.get("naga")
if not naga:
    print("Error: naga object not found!")
    exit(1)

bpy.ops.object.select_all(action='DESELECT')
naga.select_set(True)
bpy.context.view_layer.objects.active = naga

# Apply modifiers
bpy.ops.object.convert(target='MESH')

me = naga.data
min_y = min(v.co.y for v in me.vertices)
max_y = max(v.co.y for v in me.vertices)
orig_h = max_y - min_y

center_x = (min(v.co.x for v in me.vertices) + max(v.co.x for v in me.vertices)) / 2.0
center_z = (min(v.co.z for v in me.vertices) + max(v.co.z for v in me.vertices)) / 2.0

target_h = 1.35 # 1.35m tall (authentic waist/chest high temple sthamba)
scale_factor = target_h / orig_h

# Use a proper 3D rigid rotation (+90 deg around X) to keep positive volume and outward face normals
T1 = mathutils.Matrix.Translation((-center_x, -min_y, -center_z))
R = mathutils.Euler((math.radians(90.0), 0.0, 0.0), "XYZ").to_matrix().to_4x4()
S = mathutils.Matrix.Diagonal((scale_factor, scale_factor, scale_factor, 1.0))
M = S @ R @ T1
me.transform(M)

naga.matrix_world = mathutils.Matrix.Identity(4)

# Ensure original Material.003 is preserved and uses the granite texture
orig_mat = bpy.data.materials.get("Material.003")
if orig_mat and orig_mat.use_nodes:
    bsdf = orig_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Roughness"].default_value = 0.88
        bsdf.inputs["Metallic"].default_value = 0.0
    naga.data.materials.clear()
    naga.data.materials.append(orig_mat)

# Export to GLB
out_path = "/home/mullainathan/Games/IshaGodot/assets/naga_pillar.glb"
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',
    use_selection=True,
    export_apply=True
)
print(f"Successfully exported capped watertight {out_path} with target height {target_h}m!")
