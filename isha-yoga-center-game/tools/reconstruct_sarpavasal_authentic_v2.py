import bpy
import bmesh
import math
import os
import numpy as np

def rebuild_clean_sarpavasal():
    source_blend = "/home/mullainathan/Downloads/sarpavasal.blend.bak"
    out_blend = "/home/mullainathan/Downloads/sarpavasal.blend"
    out_glb = "/home/mullainathan/Games/IshaGodot/assets/models/sarpavasal.glb"
    tex_dir = "/home/mullainathan/Games/IshaGodot/assets/textures"

    print(f"[SarpaVasal Rebuild V2] Loading clean source: {source_blend}...")
    bpy.ops.wm.open_mainfile(filepath=source_blend)

    obj = bpy.data.objects.get("Plane")
    if not obj:
        raise ValueError("Could not find object 'Plane' in source blend!")

    # 1. Apply scale and evaluate modifiers (Subdivision 3 + Displace + Smooth)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Store scale
    sx = obj.scale.x
    sy = obj.scale.y
    sz = obj.scale.z
    
    # Apply transform so modifiers evaluate in true metric coordinates
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    eval_mesh = eval_obj.to_mesh()

    print(f"[SarpaVasal Rebuild V2] Evaluated mesh has {len(eval_mesh.vertices)} vertices, {len(eval_mesh.polygons)} faces")

    bm = bmesh.new()
    bm.from_mesh(eval_mesh)
    eval_obj.to_mesh_clear()

    # 2. Prune unwanted vertices:
    # - Outside lateral fringes: x < -3.97 or x > 4.00
    # - Outside top roof air: y > 2.68
    # - Basement pavement, flared sidewalk, and curb: y < -2.34
    # - Left Door Opening: x in [-2.85, -0.55] and y <= 0.81 (deletes photo interior perspective wall & floor ramps!)
    # - Right Door Opening: x in [0.55, 2.85] and y <= 0.81 (deletes photo interior perspective wall & floor ramps!)
    
    verts_to_delete = []
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        
        # Lateral fringes (background sky)
        if x < -3.970 or x > 4.000:
            verts_to_delete.append(v)
        # Roof top sky
        elif y > 2.682:
            verts_to_delete.append(v)
        # Basement rocks, flared sidewalk, ground pavement
        elif y < -2.340:
            verts_to_delete.append(v)
        # Left Door Portal Opening (clean rectangular opening)
        elif -2.850 <= x <= -0.550 and y <= 0.810:
            verts_to_delete.append(v)
        # Right Door Portal Opening (clean rectangular opening)
        elif 0.550 <= x <= 2.850 and y <= 0.810:
            verts_to_delete.append(v)

    print(f"[SarpaVasal Rebuild V2] Deleting {len(verts_to_delete)} vertices (basement rocks, photo door interior walls, sky)...")
    bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')

    # Remove loose wire edges / degenerate faces
    wire_edges = [e for e in bm.edges if len(e.link_faces) == 0]
    if wire_edges:
        bmesh.ops.delete(bm, geom=wire_edges, context='EDGES')

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    print(f"[SarpaVasal Rebuild V2] Clean front facade: {len(bm.verts)} verts, {len(bm.faces)} faces")

    # 3. Clean Boundary Edge Snapping
    # Snap bottom edge vertices (y <= -2.31) to exactly y = -2.340
    # Snap outer lateral boundaries to clean vertical lines
    # Snap door portal perimeter edges to crisp rectangular lines
    for v in bm.verts:
        # Ground base
        if v.co.y <= -2.310:
            v.co.y = -2.340
        # West outer wall
        if v.co.x <= -3.940:
            v.co.x = -3.970
        # East outer wall
        elif v.co.x >= 3.970:
            v.co.x = 4.000

        # West door outer jamb (x approx -2.85, y <= 0.81)
        if -2.880 <= v.co.x <= -2.820 and v.co.y <= 0.810:
            v.co.x = -2.850
        # West door lintel soffit (y approx 0.81, x in [-2.85, -0.55])
        if 0.780 <= v.co.y <= 0.840 and -2.850 <= v.co.x <= -0.550:
            v.co.y = 0.810
        # Center pillar West jamb (x approx -0.55, y <= 0.81)
        if -0.580 <= v.co.x <= -0.520 and v.co.y <= 0.810:
            v.co.x = -0.550

        # Center pillar East jamb (x approx 0.55, y <= 0.81)
        if 0.520 <= v.co.x <= 0.580 and v.co.y <= 0.810:
            v.co.x = 0.550
        # East door lintel soffit (y approx 0.81, x in [0.55, 2.85])
        if 0.780 <= v.co.y <= 0.840 and 0.550 <= v.co.x <= 2.850:
            v.co.y = 0.810
        # East door outer jamb (x approx 2.85, y <= 0.81)
        if 2.820 <= v.co.x <= 2.880 and v.co.y <= 0.810:
            v.co.x = 2.850

    # 4. Record front boundary edges BEFORE adding back faces
    boundary_edges = [e for e in bm.edges if e.is_boundary]
    print(f"[SarpaVasal Rebuild V2] Identified {len(boundary_edges)} boundary edges")

    # 5. Build Solid Architectural Depth (Depth T = 1.60m)
    # Extrude boundary to rear plane at z = -1.60m
    t_depth = 1.60
    front_verts = list(bm.verts)
    vert_map_back = {}

    for v in front_verts:
        # Create corresponding back vertex
        # Naga column and relief: back is flat architectural granite pier at z = -t_depth
        z_back = -t_depth
        vb = bm.verts.new((v.co.x, v.co.y, z_back))
        vert_map_back[v] = vb

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # 6. Create back faces with reversed winding (normals point outward toward -Z)
    uv_layer = bm.loops.layers.uv.active
    front_faces = list(bm.faces)
    for f in front_faces:
        f.material_index = 0 # Front uses Material.001
        back_f_verts = [vert_map_back[v] for v in reversed(f.verts)]
        fb = bm.faces.new(back_f_verts)
        fb.material_index = 1 # Back uses Material_SarpaVasal_Granite
        if uv_layer:
            for idx, l in enumerate(fb.loops):
                orig_uv = f.loops[len(f.loops) - 1 - idx][uv_layer].uv
                l[uv_layer].uv = (1.0 - orig_uv.x, orig_uv.y)

    # 7. Create side quads connecting front boundary edges to back boundary edges
    # This seals:
    # - Outer West wall (x = -3.97)
    # - Outer East wall (x = +4.00)
    # - Base at ground level (y = -2.34)
    # - Left door outer jamb (x = -2.85)
    # - Left door lintel ceiling (y = 0.81)
    # - Center pillar West face (x = -0.55)
    # - Center pillar East face (x = +0.55)
    # - Right door lintel ceiling (y = 0.81)
    # - Right door outer jamb (x = +2.85)
    # - Roof curved perimeter
    for e in boundary_edges:
        v1, v2 = e.verts
        v1_back = vert_map_back[v1]
        v2_back = vert_map_back[v2]

        lf = e.link_faces[0]
        v_order = [v.index for v in lf.verts]
        i1 = v_order.index(v1.index)
        i2 = (i1 + 1) % len(v_order)

        if v_order[i2] == v2.index:
            side_f = bm.faces.new([v2, v1, v1_back, v2_back])
        else:
            side_f = bm.faces.new([v1, v2, v2_back, v1_back])

        side_f.material_index = 1 # Material_SarpaVasal_Granite

        if uv_layer:
            # Planar UV mapping for granite block masonry
            for l in side_f.loops:
                co = l.vert.co
                if abs(side_f.normal.x) > 0.7:
                    l[uv_layer].uv = (co.y * 0.40, co.z * 0.40)
                elif abs(side_f.normal.y) > 0.7:
                    l[uv_layer].uv = (co.x * 0.40, co.z * 0.40)
                else:
                    l[uv_layer].uv = (co.x * 0.40, co.y * 0.40)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # 8. Shift everything so ground level is exactly Y = 0.000m
    # Current ground base is at y = -2.340m
    y_offset = 2.340
    # Also center depth Z: shift forward by t_depth/2 so gateway is centered at Z = 0
    z_offset = t_depth * 0.5 # +0.80m
    
    for v in bm.verts:
        v.co.y += y_offset
        v.co.z += z_offset

    # Verify Watertight 2-Manifold
    open_edges = [e for e in bm.edges if e.is_boundary]
    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    print(f"[SarpaVasal Rebuild V2] Watertight verification:")
    print(f"  Open boundary edges: {len(open_edges)} (Expected: 0)")
    print(f"  Non-manifold edges:  {len(non_manifold_edges)} (Expected: 0)")
    print(f"  Total Vertices: {len(bm.verts)}, Total Faces: {len(bm.faces)}")

    # 9. Setup PBR Materials
    mat_granite = bpy.data.materials.get("Material_SarpaVasal_Granite")
    if not mat_granite:
        mat_granite = bpy.data.materials.new(name="Material_SarpaVasal_Granite")
    mat_granite.use_nodes = True
    gnodes = mat_granite.node_tree.nodes
    glinks = mat_granite.node_tree.links
    gnodes.clear()

    gout = gnodes.new(type='ShaderNodeOutputMaterial')
    gbsdf = gnodes.new(type='ShaderNodeBsdfPrincipled')
    gbsdf.inputs['Roughness'].default_value = 0.80
    gbsdf.inputs['Metallic'].default_value = 0.0
    glinks.new(gbsdf.outputs['BSDF'], gout.inputs['Surface'])

    diff_p = os.path.join(tex_dir, "stone_block_wall_diff_2k.jpg")
    nor_p = os.path.join(tex_dir, "stone_block_wall_nor_gl_2k.jpg")
    rough_p = os.path.join(tex_dir, "stone_block_wall_rough_2k.jpg")

    if os.path.exists(diff_p):
        idiff = bpy.data.images.load(diff_p)
        tdiff = gnodes.new(type='ShaderNodeTexImage')
        tdiff.image = idiff
        glinks.new(tdiff.outputs['Color'], gbsdf.inputs['Base Color'])
    else:
        gbsdf.inputs['Base Color'].default_value = (0.55, 0.54, 0.52, 1.0)

    if os.path.exists(nor_p):
        inor = bpy.data.images.load(nor_p)
        inor.colorspace_settings.name = 'Non-Color'
        tnor = gnodes.new(type='ShaderNodeTexImage')
        tnor.image = inor
        nmap = gnodes.new(type='ShaderNodeNormalMap')
        nmap.inputs['Strength'].default_value = 1.0
        glinks.new(tnor.outputs['Color'], nmap.inputs['Color'])
        glinks.new(nmap.outputs['Normal'], gbsdf.inputs['Normal'])

    if os.path.exists(rough_p):
        irough = bpy.data.images.load(rough_p)
        irough.colorspace_settings.name = 'Non-Color'
        trough = gnodes.new(type='ShaderNodeTexImage')
        trough.image = irough
        glinks.new(trough.outputs['Color'], gbsdf.inputs['Roughness'])

    # 10. Update Mesh & Object
    new_mesh = bpy.data.meshes.new("SarpaVasal_Clean_Solid_Mesh")
    bm.to_mesh(new_mesh)
    bm.free()

    mat_front = bpy.data.materials.get("Material.001")
    new_mesh.materials.append(mat_front)
    new_mesh.materials.append(mat_granite)

    # Remove old objects
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    final_obj = bpy.data.objects.new("SarpaVasal_Gateway", new_mesh)
    bpy.context.collection.objects.link(final_obj)
    bpy.context.view_layer.objects.active = final_obj
    final_obj.select_set(True)

    # Calculate and print final bounding box
    bbox_xs = [v.co.x for v in final_obj.data.vertices]
    bbox_ys = [v.co.y for v in final_obj.data.vertices]
    bbox_zs = [v.co.z for v in final_obj.data.vertices]
    print(f"[SarpaVasal Rebuild V2] Final Bounding Box:")
    print(f"  X: {min(bbox_xs):.4f}m to {max(bbox_xs):.4f}m (Width: {max(bbox_xs)-min(bbox_xs):.4f}m)")
    print(f"  Y: {min(bbox_ys):.4f}m to {max(bbox_ys):.4f}m (Height: {max(bbox_ys)-min(bbox_ys):.4f}m)")
    print(f"  Z: {min(bbox_zs):.4f}m to {max(bbox_zs):.4f}m (Depth: {max(bbox_zs)-min(bbox_zs):.4f}m)")

    # Save Blend
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"[SarpaVasal Rebuild V2] Saved updated {out_blend}")

    # Export to GLB
    # Godot uses Y-up, Z-front (-Z or +Z). Standard export_scene.gltf uses Y-up.
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    print(f"[SarpaVasal Rebuild V2] Exported GLB to {out_glb} (Size: {os.path.getsize(out_glb)/1024/1024:.2f} MB)")

if __name__ == "__main__":
    rebuild_clean_sarpavasal()
