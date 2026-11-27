"""Reconstruct Authentic 3D Watertight Sarpa Vasal Gateway

Removes:
- All basement rocks, flared concrete sidewalk slabs, and ground wedges
- All doorway floor ramps (door portals are 100% open, clear, and walkable from front to back)
- Outside wall perimeter fringes

Preserves:
- Central Naga Pillar: 100% of the authentic sculpted Cobra displacement relief, hood, scales, and coils
- Left & Right stone wall pilasters, stepped architraves, and red brick inlay panels
- Lotus petal cornice frieze and curved barrel vault roof

Adds:
- Clean 1.20m solid architectural depth (vertical side walls, inner door jambs, lintel soffits)
- Structural Dravidian stone masonry back facade
- 100% watertight 2-manifold solid geometry (0 non-manifold edges, 0 boundary holes)
- Automatic export to assets/models/sarpavasal.glb in proper Godot coordinates
"""
import bpy
import bmesh
import math
import os
import numpy as np

def rebuild_sarpavasal():
    blend_path = "/home/mullainathan/Downloads/sarpavasal.blend"
    out_glb = "/home/mullainathan/Games/IshaGodot/assets/models/sarpavasal.glb"
    tex_dir = "/home/mullainathan/Games/IshaGodot/assets/textures"
    brain_captures = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures"
    os.makedirs(brain_captures, exist_ok=True)

    print(f"[SarpaVasal Rebuild] Opening {blend_path}...")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    obj = bpy.data.objects.get("Plane")
    if not obj:
        raise ValueError("Could not find object 'Plane' in sarpavasal.blend")

    # 1. Apply transforms so geometry is in metric units
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    print(f"[SarpaVasal Rebuild] Loaded mesh with {len(bm.verts)} verts, {len(bm.faces)} faces")

    # 2. Filter out basement rocks, door floors, perimeter fringes, and old back faces
    verts_to_delete = []
    for v in bm.verts:
        x = v.co.x
        y = v.co.y
        z = v.co.z
        if z < -0.5: # Old back/side vertices
            verts_to_delete.append(v)
        elif y < -2.34: # ALL basement rocks, flared sidewalk, and ground pavement
            verts_to_delete.append(v)
        elif -1.85 <= x <= -0.48 and y <= 0.39: # Left door opening & ground floor
            verts_to_delete.append(v)
        elif 0.50 <= x <= 1.99 and y <= 0.39: # Right door opening & ground floor
            verts_to_delete.append(v)
        elif x < -3.97 or x > 4.00: # Outside wall fringes
            verts_to_delete.append(v)

    print(f"[SarpaVasal Rebuild] Deleting {len(verts_to_delete)} vertices (basement rocks, door floor ramps, fringes)...")
    bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')

    # Remove loose wire edges
    wire_edges = [e for e in bm.edges if len(e.link_faces) == 0]
    if wire_edges:
        bmesh.ops.delete(bm, geom=wire_edges, context='EDGES')

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    print(f"[SarpaVasal Rebuild] Clean front facade: {len(bm.verts)} verts, {len(bm.faces)} faces")

    # 3. Level bottom edge to perfectly flat ground line y = -2.340
    # and snap outer lateral edges to straight vertical lines
    for v in bm.verts:
        if v.co.y <= -2.31:
            v.co.y = -2.340
        if v.co.x <= -3.94:
            v.co.x = -3.970
        elif v.co.x >= 3.97:
            v.co.x = 4.000

    # 4. Record front boundary edges BEFORE adding back faces
    boundary_edges = [e for e in bm.edges if e.is_boundary]
    print(f"[SarpaVasal Rebuild] Identified {len(boundary_edges)} boundary edges (perimeter + 2 inner archways)")

    # 5. Build Back Face by analyzing front face depth
    # Solid architectural gateway thickness: depth T = 1.20m
    t_depth = 1.20
    front_verts = list(bm.verts)
    vert_map_back = {}

    for v in front_verts:
        # Back face projects outward slightly matching front architectural prominence
        z_back = -t_depth - (v.co.z + 0.46) * 0.25
        vb = bm.verts.new((v.co.x, v.co.y, z_back))
        vert_map_back[v] = vb

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # 6. Create back faces with reversed winding (normals point outward towards -Z)
    uv_layer = bm.loops.layers.uv.active
    front_faces = list(bm.faces)
    for f in front_faces:
        f.material_index = 0 # Front face uses original temple texture Material.001
        back_f_verts = [vert_map_back[v] for v in reversed(f.verts)]
        fb = bm.faces.new(back_f_verts)
        fb.material_index = 1 # Back face uses Material_SarpaVasal_Granite
        if uv_layer:
            for idx, l in enumerate(fb.loops):
                orig_uv = f.loops[len(f.loops) - 1 - idx][uv_layer].uv
                l[uv_layer].uv = (1.0 - orig_uv.x, orig_uv.y)

    # 7. Create side quads connecting front boundary edges to back boundary edges
    # Connects outer perimeter walls AND inner door jambs/archways
    for e in boundary_edges:
        v1, v2 = e.verts
        v1_back = vert_map_back[v1]
        v2_back = vert_map_back[v2]

        lf = e.link_faces[0]
        v_order = [v.index for v in lf.verts]
        i1 = v_order.index(v1.index)
        i2 = (i1 + 1) % len(v_order)

        if v_order[i2] == v2.index:
            # Front face winds v1 -> v2, so side quad winds v2 -> v1 -> v1_back -> v2_back
            side_f = bm.faces.new([v2, v1, v1_back, v2_back])
        else:
            side_f = bm.faces.new([v1, v2, v2_back, v1_back])

        side_f.material_index = 1 # Material_SarpaVasal_Granite

        if uv_layer:
            # Box-projected UVs for granite blocks
            for l in side_f.loops:
                co = l.vert.co
                if abs(side_f.normal.x) > 0.7:
                    l[uv_layer].uv = (co.y * 0.35, co.z * 0.35)
                elif abs(side_f.normal.y) > 0.7:
                    l[uv_layer].uv = (co.x * 0.35, co.z * 0.35)
                else:
                    l[uv_layer].uv = (co.x * 0.35, co.y * 0.35)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Verify 2-manifold watertight solid
    open_edges = [e for e in bm.edges if e.is_boundary]
    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    print(f"[SarpaVasal Rebuild] Watertight verification:")
    print(f"  Open boundary edges: {len(open_edges)} (Expected: 0)")
    print(f"  Non-manifold edges:  {len(non_manifold_edges)} (Expected: 0)")
    print(f"  Total Vertices: {len(bm.verts)}, Total Faces: {len(bm.faces)}")

    # 8. Setup PBR Materials
    mat_granite = bpy.data.materials.get("Material_SarpaVasal_Granite")
    if not mat_granite:
        mat_granite = bpy.data.materials.new(name="Material_SarpaVasal_Granite")
    mat_granite.use_nodes = True
    gnodes = mat_granite.node_tree.nodes
    glinks = mat_granite.node_tree.links
    gnodes.clear()

    gout = gnodes.new(type='ShaderNodeOutputMaterial')
    gbsdf = gnodes.new(type='ShaderNodeBsdfPrincipled')
    gbsdf.inputs['Roughness'].default_value = 0.82
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
        gbsdf.inputs['Base Color'].default_value = (0.28, 0.27, 0.26, 1.0)

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

    # 9. Update mesh in Blender
    new_mesh = bpy.data.meshes.new("SarpaVasal_Solid_Mesh")
    bm.to_mesh(new_mesh)
    bm.free()

    mat_front = bpy.data.materials.get("Material.001")
    new_mesh.materials.append(mat_front)
    new_mesh.materials.append(mat_granite)

    obj.data = new_mesh
    obj.name = "SarpaVasal_Gateway"

    # Save clean blend
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[SarpaVasal Rebuild] Saved clean {blend_path}")

    # 10. Transform for Godot Export
    # Godot frame:
    # Width is X
    # Height is Y (sitting at 0.0)
    # Depth is Z (front face facing +Z)
    bm_export = bmesh.new()
    bm_export.from_mesh(new_mesh)

    min_y = min(v.co.y for v in bm_export.verts)
    for v in bm_export.verts:
        x = v.co.x
        y = v.co.y - min_y
        z = v.co.z
        v.co.x = x
        v.co.y = -z
        v.co.z = y

    mesh_godot = bpy.data.meshes.new("SarpaVasal_Godot_Mesh")
    bm_export.to_mesh(mesh_godot)
    bm_export.free()

    mesh_godot.materials.append(mat_front)
    mesh_godot.materials.append(mat_granite)
    obj.data = mesh_godot

    # Export GLB
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO'
    )
    print(f"[SarpaVasal Rebuild] Successfully exported to {out_glb} ({os.path.getsize(out_glb)} bytes)")

if __name__ == "__main__":
    rebuild_sarpavasal()
