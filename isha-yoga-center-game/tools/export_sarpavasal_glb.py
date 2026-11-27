"""Export Watertight 3D Sarpa Vasal Gateway from sarpavasal.blend to assets/models/sarpavasal.glb

Features:
- Proper Godot orientation (Y is UP, X is width, Z is depth)
- Gateway base touches the ground exactly at Y = 0.0m
- Front face (Naga relief) faces forward (+Z)
- Surface 0: Front face with original high-res temple displacement relief
- Surface 1: Side walls, arch reveals, and back facade with 2K Dravidian stone masonry PBR textures
"""
import bpy
import bmesh
import math
import os

def export_sarpavasal():
    blend_path = "/home/mullainathan/Downloads/sarpavasal.blend"
    out_glb = "/home/mullainathan/Games/IshaGodot/assets/models/sarpavasal.glb"
    tex_dir = "/home/mullainathan/Games/IshaGodot/assets/textures"
    
    print(f"[Export SarpaVasal] Opening {blend_path}...")
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    
    obj = bpy.data.objects.get("Plane")
    if not obj:
        raise ValueError("Could not find object 'Plane' in sarpavasal.blend")
        
    obj.name = "SarpaVasal_Gateway"
    
    # Apply current object scale so geometry is in true metric dimensions
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # Setup PBR Material_SarpaVasal_Granite with 2K stone textures
    mat_granite = bpy.data.materials.get("Material_SarpaVasal_Granite")
    if not mat_granite:
        mat_granite = bpy.data.materials.new(name="Material_SarpaVasal_Granite")
    mat_granite.use_nodes = True
    nodes = mat_granite.node_tree.nodes
    links = mat_granite.node_tree.links
    nodes.clear()
    
    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.82
    bsdf.inputs['Metallic'].default_value = 0.0
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    
    diff_path = os.path.join(tex_dir, "stone_block_wall_diff_2k.jpg")
    nor_path = os.path.join(tex_dir, "stone_block_wall_nor_gl_2k.jpg")
    rough_path = os.path.join(tex_dir, "stone_block_wall_rough_2k.jpg")
    
    if os.path.exists(diff_path):
        img_diff = bpy.data.images.load(diff_path)
        tex_diff = nodes.new(type='ShaderNodeTexImage')
        tex_diff.image = img_diff
        links.new(tex_diff.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.28, 0.27, 0.25, 1.0)
        
    if os.path.exists(rough_path):
        img_rough = bpy.data.images.load(rough_path)
        img_rough.colorspace_settings.name = 'Non-Color'
        tex_rough = nodes.new(type='ShaderNodeTexImage')
        tex_rough.image = img_rough
        links.new(tex_rough.outputs['Color'], bsdf.inputs['Roughness'])
        
    if os.path.exists(nor_path):
        img_nor = bpy.data.images.load(nor_path)
        img_nor.colorspace_settings.name = 'Non-Color'
        tex_nor = nodes.new(type='ShaderNodeTexImage')
        tex_nor.image = img_nor
        norm_map = nodes.new(type='ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 1.0
        links.new(tex_nor.outputs['Color'], norm_map.inputs['Color'])
        links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    uv_layer = bm.loops.layers.uv.verify()
    
    # Identify non-front faces (sides, jambs, back) and assign material_index = 1
    # Front vertices in local space before rotation have z > 0.0 (or z >= -0.2)
    # Extruded back vertices are at z <= -0.9m
    # Faces pointing mostly backward (normal.z < -0.6) or sideways (|normal.z| < 0.6)
    front_count = 0
    granite_count = 0
    for f in bm.faces:
        # Check normal and vertex Z
        nz = f.normal.z
        avg_z = sum(v.co.z for v in f.verts) / len(f.verts)
        if avg_z < -0.8 or nz < -0.5 or abs(nz) < 0.6:
            f.material_index = 1
            granite_count += 1
            # Generate triplanar-like clean box UVs for granite
            for l in f.loops:
                co = l.vert.co
                if abs(f.normal.x) > 0.7:
                    l[uv_layer].uv = (co.y * 0.4, co.z * 0.4)
                elif abs(f.normal.y) > 0.7:
                    l[uv_layer].uv = (co.x * 0.4, co.z * 0.4)
                else:
                    l[uv_layer].uv = (co.x * 0.4, co.y * 0.4)
        else:
            f.material_index = 0
            front_count += 1
            
    print(f"[Export SarpaVasal] Face materials assigned: Front relief: {front_count}, Granite sides/back: {granite_count}")
    
    # Find min Y (bottom of gateway)
    min_y = min(v.co.y for v in bm.verts)
    
    # Transform vertices so:
    # Width is X
    # Height is Z in Blender (becomes Y in glTF/Godot, starting at 0.0)
    # Depth is Y in Blender (becomes Z in glTF/Godot, front face facing +Z)
    for v in bm.verts:
        x = v.co.x
        y = v.co.y - min_y
        z = v.co.z
        v.co.x = x
        v.co.y = -z
        v.co.z = y
        
    bm.to_mesh(obj.data)
    bm.free()
    
    obj.data.update()
    
    # Verify bounds in Blender:
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    print(f"[Export SarpaVasal] Transformed metric dimensions:")
    print(f"  Width (X):  {min(xs):.3f}m to {max(xs):.3f}m (span: {max(xs)-min(xs):.3f}m)")
    print(f"  Depth (Y):  {min(ys):.3f}m to {max(ys):.3f}m (span: {max(ys)-min(ys):.3f}m)")
    print(f"  Height (Z): {min(zs):.3f}m to {max(zs):.3f}m (span: {max(zs)-min(zs):.3f}m)")
    
    os.makedirs(os.path.dirname(out_glb), exist_ok=True)
    
    # Export glTF binary (.glb)
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO'
    )
    print(f"[Export SarpaVasal] Successfully exported to {out_glb} ({os.path.getsize(out_glb)} bytes)")

if __name__ == "__main__":
    export_sarpavasal()
