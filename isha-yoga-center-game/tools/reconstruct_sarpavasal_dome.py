import bpy
import bmesh
import math
import os
import numpy as np

def build_sarpavasal_with_dome():
    source_blend = "/home/mullainathan/Downloads/sarpavasal.blend.bak"
    out_blend = "/home/mullainathan/Downloads/sarpavasal.blend"
    out_glb = "/home/mullainathan/Games/IshaGodot/assets/models/sarpavasal.glb"
    tex_dir = "/home/mullainathan/Games/IshaGodot/assets/textures"

    print(f"[SarpaVasal Dome Rebuild] Loading source: {source_blend}...")
    bpy.ops.wm.open_mainfile(filepath=source_blend)

    obj = bpy.data.objects.get("Plane")
    if not obj:
        raise ValueError("Could not find object 'Plane' in source blend!")

    # Apply transform so modifiers evaluate in true metric units
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    eval_mesh = eval_obj.to_mesh()

    print(f"[SarpaVasal Dome Rebuild] Evaluated mesh: {len(eval_mesh.vertices)} verts, {len(eval_mesh.polygons)} faces")

    bm = bmesh.new()
    bm.from_mesh(eval_mesh)
    eval_obj.to_mesh_clear()

    # 1. Prune unwanted vertices:
    # - Outside lateral fringes: x < -3.97 or x > 4.00
    # - CUT THE BROWN THING: y > 1.85 (removes all the curved brown roof above the stone cornice!)
    # - Basement pavement, flared sidewalk, and curb: y < -2.34
    # - Left Door Opening: x in [-2.85, -0.55] and y <= 0.81
    # - Right Door Opening: x in [0.55, 2.85] and y <= 0.81
    verts_to_delete = []
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        
        # Lateral air fringes
        if x < -3.970 or x > 4.000:
            verts_to_delete.append(v)
        # CUT THE BROWN THING: all geometry above stone cornice
        elif y > 1.850:
            verts_to_delete.append(v)
        # Basement pavement, flared sidewalk, ramps
        elif y < -2.340:
            verts_to_delete.append(v)
        # Left door portal opening
        elif -2.850 <= x <= -0.550 and y <= 0.810:
            verts_to_delete.append(v)
        # Right door portal opening
        elif 0.550 <= x <= 2.850 and y <= 0.810:
            verts_to_delete.append(v)

    print(f"[SarpaVasal Dome Rebuild] Deleting {len(verts_to_delete)} vertices (brown roof, basement rocks, door interior walls)...")
    bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')

    # Remove loose wire edges
    wire_edges = [e for e in bm.edges if len(e.link_faces) == 0]
    if wire_edges:
        bmesh.ops.delete(bm, geom=wire_edges, context='EDGES')

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    print(f"[SarpaVasal Dome Rebuild] Clean front facade: {len(bm.verts)} verts, {len(bm.faces)} faces")

    # 2. Snap boundary edges to clean architectural lines
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
        # Cornice top boundary (where brown roof was cut off)
        if v.co.y >= 1.820:
            v.co.y = 1.850

        # West door outer jamb (x = -2.85, y <= 0.81)
        if -2.880 <= v.co.x <= -2.820 and v.co.y <= 0.810:
            v.co.x = -2.850
        # West door lintel soffit (y = 0.81, x in [-2.85, -0.55])
        if 0.780 <= v.co.y <= 0.840 and -2.850 <= v.co.x <= -0.550:
            v.co.y = 0.810
        # Center pillar West jamb (x = -0.55, y <= 0.81)
        if -0.580 <= v.co.x <= -0.520 and v.co.y <= 0.810:
            v.co.x = -0.550

        # Center pillar East jamb (x = 0.55, y <= 0.81)
        if 0.520 <= v.co.x <= 0.580 and v.co.y <= 0.810:
            v.co.x = 0.550
        # East door lintel soffit (y = 0.81, x in [0.55, 2.85])
        if 0.780 <= v.co.y <= 0.840 and 0.550 <= v.co.x <= 2.850:
            v.co.y = 0.810
        # East door outer jamb (x = 2.85, y <= 0.81)
        if 2.820 <= v.co.x <= 2.880 and v.co.y <= 0.810:
            v.co.x = 2.850

    # 3. Record front boundary edges BEFORE adding back faces
    boundary_edges = [e for e in bm.edges if e.is_boundary]
    print(f"[SarpaVasal Dome Rebuild] Identified {len(boundary_edges)} boundary edges")

    # 4. Build Solid Architectural Depth (Depth T = 1.60m)
    t_depth = 1.60
    front_verts = list(bm.verts)
    vert_map_back = {}

    for v in front_verts:
        vb = bm.verts.new((v.co.x, v.co.y, -t_depth))
        vert_map_back[v] = vb

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # 5. Create back faces with matching similar granite texture
    uv_layer = bm.loops.layers.uv.active
    front_faces = list(bm.faces)
    for f in front_faces:
        f.material_index = 0 # Front uses Material.001
        back_f_verts = [vert_map_back[v] for v in reversed(f.verts)]
        fb = bm.faces.new(back_f_verts)
        fb.material_index = 1 # Back uses Material_SarpaVasal_Granite (matching granite!)
        if uv_layer:
            for idx, l in enumerate(fb.loops):
                orig_uv = f.loops[len(f.loops) - 1 - idx][uv_layer].uv
                l[uv_layer].uv = (1.0 - orig_uv.x, orig_uv.y)

    # 6. Create side quads connecting front boundary to back boundary
    # (Outer West/East walls, base at ground level, inner door jambs, lintel ceilings, cornice top)
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
            for l in side_f.loops:
                co = l.vert.co
                if abs(side_f.normal.x) > 0.7:
                    l[uv_layer].uv = (co.y * 0.45, co.z * 0.45)
                elif abs(side_f.normal.y) > 0.7:
                    l[uv_layer].uv = (co.x * 0.45, co.z * 0.45)
                else:
                    l[uv_layer].uv = (co.x * 0.45, co.y * 0.45)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # 7. Shift Gateway so ground level is Y = 0.000m and depth centered around Z = 0
    y_offset = 2.340 # Shifts base from -2.34 to 0.00
    z_offset = t_depth * 0.5 # Shifts depth from [-1.60, 0] to [-0.80, +0.80]
    for v in bm.verts:
        v.co.y += y_offset
        v.co.z += z_offset

    # Cornice top is now at Y = 1.850 + 2.340 = 4.190m
    y_cornice_top = 4.190

    # 8. BUILD THE SACRED TEMPLE DOME ON TOP OF THE GATEWAY
    # Placed centrally on the roof terrace:
    # - Stepped Dravidian stone drum base
    # - Vaulted / ellipsoidal temple dome in matching granite
    # - Three crowning sacred golden Kalashas (Stupis) along the dome ridge!
    print(f"[SarpaVasal Dome Rebuild] Constructing Sacred Temple Dome at Y={y_cornice_top:.3f}m...")

    # Drum base: 2 tiers of dressed stone plinth
    # Tier 1 (Wide plinth): X in [-2.60, 2.60], Z in [-0.72, 0.72], Y from 4.19 to 4.34 (height 0.15m)
    # Tier 2 (Molded drum): X in [-2.35, 2.35], Z in [-0.62, 0.62], Y from 4.34 to 4.49 (height 0.15m)
    def add_box_geometry(min_pt, max_pt, mat_idx, uv_scale=0.45):
        x0, y0, z0 = min_pt
        x1, y1, z1 = max_pt
        verts = [
            bm.verts.new((x0, y0, z0)), # 0
            bm.verts.new((x1, y0, z0)), # 1
            bm.verts.new((x1, y1, z0)), # 2
            bm.verts.new((x0, y1, z0)), # 3
            bm.verts.new((x0, y0, z1)), # 4
            bm.verts.new((x1, y0, z1)), # 5
            bm.verts.new((x1, y1, z1)), # 6
            bm.verts.new((x0, y1, z1)), # 7
        ]
        faces_def = [
            [0, 3, 2, 1], # -Z (Rear)
            [4, 5, 6, 7], # +Z (Front)
            [0, 1, 5, 4], # -Y (Bottom)
            [3, 7, 6, 2], # +Y (Top)
            [0, 4, 7, 3], # -X (West)
            [1, 2, 6, 5], # +X (East)
        ]
        for f_indices in faces_def:
            f = bm.faces.new([verts[i] for i in f_indices])
            f.material_index = mat_idx
            if uv_layer:
                for l in f.loops:
                    co = l.vert.co
                    if abs(f.normal.x) > 0.7:
                        l[uv_layer].uv = (co.y * uv_scale, co.z * uv_scale)
                    elif abs(f.normal.y) > 0.7:
                        l[uv_layer].uv = (co.x * uv_scale, co.z * uv_scale)
                    else:
                        l[uv_layer].uv = (co.x * uv_scale, co.y * uv_scale)

    # Add lower drum plinth
    add_box_geometry((-2.60, y_cornice_top, -0.72), (2.60, y_cornice_top + 0.15, 0.72), mat_idx=1)
    # Add upper drum cornice
    add_box_geometry((-2.35, y_cornice_top + 0.15, -0.62), (2.35, y_cornice_top + 0.30, 0.62), mat_idx=1)

    # 9. VAULTED STONE DOME (Sala Shikhara Dome)
    # Smooth curved vaulted temple dome in matching granite stone
    # Spans X in [-2.25, 2.25] (width 4.50m), Z in [-0.58, 0.58] (depth 1.16m), height 1.10m (apex Y = 5.59m)
    y_dome_base = y_cornice_top + 0.30 # 4.49m
    dome_rx = 2.25
    dome_rz = 0.58
    dome_h = 1.10

    n_u = 24 # along length
    n_v = 12 # along vertical arc
    dome_grid = []

    for iv in range(n_v + 1):
        v_frac = float(iv) / float(n_v) # 0 to 1
        phi = v_frac * (math.pi / 2.0) # 0 to 90 deg
        cur_y = y_dome_base + dome_h * math.sin(phi)
        cos_phi = math.cos(phi)

        row = []
        for iu in range(n_u):
            theta = float(iu) / float(n_u) * 2.0 * math.pi
            # Super-ellipsoidal curvature for authentic Dravidian barrel-dome profile
            cur_x = dome_rx * cos_phi * math.cos(theta)
            cur_z = dome_rz * cos_phi * math.sin(theta)
            v = bm.verts.new((cur_x, cur_y, cur_z))
            row.append(v)
        dome_grid.append(row)

    # Apex vertex at center top
    v_apex = bm.verts.new((0.0, y_dome_base + dome_h, 0.0))

    # Connect dome quads
    for iv in range(n_v - 1):
        for iu in range(n_u):
            iu_next = (iu + 1) % n_u
            v00 = dome_grid[iv][iu]
            v01 = dome_grid[iv][iu_next]
            v11 = dome_grid[iv + 1][iu_next]
            v10 = dome_grid[iv + 1][iu]
            # Normal points outwards
            df = bm.faces.new([v00, v01, v11, v10])
            df.material_index = 1 # Material_SarpaVasal_Granite
            if uv_layer:
                for l in df.loops:
                    co = l.vert.co
                    l[uv_layer].uv = (co.x * 0.40, (co.y - y_dome_base) * 0.50 + co.z * 0.20)

    # Connect top row to apex
    for iu in range(n_u):
        iu_next = (iu + 1) % n_u
        v0 = dome_grid[n_v - 1][iu]
        v1 = dome_grid[n_v - 1][iu_next]
        tf = bm.faces.new([v0, v1, v_apex])
        tf.material_index = 1
        if uv_layer:
            for l in tf.loops:
                co = l.vert.co
                l[uv_layer].uv = (co.x * 0.40, (co.y - y_dome_base) * 0.50)

    # 10. SACRED TEMPLE KALASHAS (3 Golden Stupis along Dome Ridge)
    # Center Grand Kalasha at X = 0.0, and 2 flanking Kalashas at X = -1.25m and +1.25m
    def add_golden_kalasha(pos_x, pos_z, base_y, scale_k=1.0):
        # Traditional Stupi / Kalasha profile: pot base + flared rim + conical spire finial
        k_segs = 12
        radii_heights = [
            (0.12 * scale_k, 0.00 * scale_k), # Base ring
            (0.20 * scale_k, 0.12 * scale_k), # Bulbous body
            (0.14 * scale_k, 0.24 * scale_k), # Neck
            (0.18 * scale_k, 0.30 * scale_k), # Flared rim
            (0.08 * scale_k, 0.42 * scale_k), # Spire cone base
            (0.01 * scale_k, 0.58 * scale_k), # Sharp golden needle tip
        ]
        k_rings = []
        for r, h in radii_heights:
            ring = []
            for iseg in range(k_segs):
                ang = float(iseg) / float(k_segs) * 2.0 * math.pi
                kx = pos_x + r * math.cos(ang)
                kz = pos_z + r * math.sin(ang)
                ky = base_y + h
                ring.append(bm.verts.new((kx, ky, kz)))
            k_rings.append(ring)

        v_tip = bm.verts.new((pos_x, base_y + 0.62 * scale_k, pos_z))

        # Build quad bands
        for iring in range(len(radii_heights) - 1):
            for iseg in range(k_segs):
                iseg_next = (iseg + 1) % k_segs
                v00 = k_rings[iring][iseg]
                v01 = k_rings[iring][iseg_next]
                v11 = k_rings[iring + 1][iseg_next]
                v10 = k_rings[iring + 1][iseg]
                kf = bm.faces.new([v00, v01, v11, v10])
                kf.material_index = 2 # Material_Gold_Kalasha
                if uv_layer:
                    for l in kf.loops:
                        l[uv_layer].uv = (float(iseg)/float(k_segs), float(iring)/float(len(radii_heights)))

        # Tip cap
        top_ring = k_rings[-1]
        for iseg in range(k_segs):
            iseg_next = (iseg + 1) % k_segs
            tf = bm.faces.new([top_ring[iseg], top_ring[iseg_next], v_tip])
            tf.material_index = 2
            if uv_layer:
                for l in tf.loops:
                    l[uv_layer].uv = (float(iseg)/float(k_segs), 1.0)

    # Place 3 Golden Kalashas:
    apex_y = y_dome_base + dome_h # 5.59m
    # Center Grand Kalasha (Scale 1.15x)
    add_golden_kalasha(0.0, 0.0, apex_y - 0.04, scale_k=1.15)
    # West Kalasha
    add_golden_kalasha(-1.30, 0.0, y_dome_base + dome_h * 0.88, scale_k=0.90)
    # East Kalasha
    add_golden_kalasha(1.30, 0.0, y_dome_base + dome_h * 0.88, scale_k=0.90)

    # 11. ROOF PARAPET (Balustrade along roof edges flanking the dome)
    # Adds finished temple coping on roof terrace flanking dome (X < -2.60 and X > 2.60)
    add_box_geometry((-3.97, y_cornice_top, -0.80), (-2.60, y_cornice_top + 0.22, -0.65), mat_idx=1) # West rear parapet
    add_box_geometry((-3.97, y_cornice_top, 0.65), (-2.60, y_cornice_top + 0.22, 0.80), mat_idx=1)  # West front parapet
    add_box_geometry((-3.97, y_cornice_top, -0.80), (-3.82, y_cornice_top + 0.22, 0.80), mat_idx=1) # West end parapet

    add_box_geometry((2.60, y_cornice_top, -0.80), (4.00, y_cornice_top + 0.22, -0.65), mat_idx=1)  # East rear parapet
    add_box_geometry((2.60, y_cornice_top, 0.65), (4.00, y_cornice_top + 0.22, 0.80), mat_idx=1)   # East front parapet
    add_box_geometry((3.85, y_cornice_top, -0.80), (4.00, y_cornice_top + 0.22, 0.80), mat_idx=1)  # East end parapet

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    print(f"[SarpaVasal Dome Rebuild] Completed complete model geometry: {len(bm.verts)} verts, {len(bm.faces)} faces")

    # 12. PBR MATERIALS SETUP
    # Material 0: Front Facade (Material.001)
    mat_front = bpy.data.materials.get("Material.001")

    # Material 1: Temple Granite Material (matching the front stone!)
    mat_granite = bpy.data.materials.get("Material_SarpaVasal_Granite")
    if not mat_granite:
        mat_granite = bpy.data.materials.new(name="Material_SarpaVasal_Granite")
    mat_granite.use_nodes = True
    gnodes = mat_granite.node_tree.nodes
    glinks = mat_granite.node_tree.links
    gnodes.clear()

    gout = gnodes.new(type='ShaderNodeOutputMaterial')
    gbsdf = gnodes.new(type='ShaderNodeBsdfPrincipled')
    gbsdf.inputs['Roughness'].default_value = 0.78
    gbsdf.inputs['Metallic'].default_value = 0.0
    glinks.new(gbsdf.outputs['BSDF'], gout.inputs['Surface'])

    # Use the color-balanced light temple granite diffuse texture
    match_diff_p = os.path.join(tex_dir, "sarpavasal_temple_granite_diff.png")
    nor_p = os.path.join(tex_dir, "granite_wall_nor_gl_2k.jpg")
    rough_p = os.path.join(tex_dir, "granite_wall_rough_2k.jpg")

    if os.path.exists(match_diff_p):
        idiff = bpy.data.images.load(match_diff_p)
        tdiff = gnodes.new(type='ShaderNodeTexImage')
        tdiff.image = idiff
        glinks.new(tdiff.outputs['Color'], gbsdf.inputs['Base Color'])
    else:
        gbsdf.inputs['Base Color'].default_value = (0.60, 0.58, 0.56, 1.0)

    if os.path.exists(nor_p):
        inor = bpy.data.images.load(nor_p)
        inor.colorspace_settings.name = 'Non-Color'
        tnor = gnodes.new(type='ShaderNodeTexImage')
        tnor.image = inor
        nmap = gnodes.new(type='ShaderNodeNormalMap')
        nmap.inputs['Strength'].default_value = 0.85
        glinks.new(tnor.outputs['Color'], nmap.inputs['Color'])
        glinks.new(nmap.outputs['Normal'], gbsdf.inputs['Normal'])

    if os.path.exists(rough_p):
        irough = bpy.data.images.load(rough_p)
        irough.colorspace_settings.name = 'Non-Color'
        trough = gnodes.new(type='ShaderNodeTexImage')
        trough.image = irough
        glinks.new(trough.outputs['Color'], gbsdf.inputs['Roughness'])

    # Material 2: Temple Gold Kalasha Material
    mat_gold = bpy.data.materials.get("Material_Gold_Kalasha")
    if not mat_gold:
        mat_gold = bpy.data.materials.new(name="Material_Gold_Kalasha")
    mat_gold.use_nodes = True
    knodes = mat_gold.node_tree.nodes
    klinks = mat_gold.node_tree.links
    knodes.clear()

    kout = knodes.new(type='ShaderNodeOutputMaterial')
    kbsdf = knodes.new(type='ShaderNodeBsdfPrincipled')
    kbsdf.inputs['Base Color'].default_value = (1.0, 0.82, 0.36, 1.0) # Sacred brass temple gold
    kbsdf.inputs['Metallic'].default_value = 0.95
    kbsdf.inputs['Roughness'].default_value = 0.22
    klinks.new(kbsdf.outputs['BSDF'], kout.inputs['Surface'])

    # 13. Create Object & Export
    new_mesh = bpy.data.meshes.new("SarpaVasal_Dome_Solid_Mesh")
    bm.to_mesh(new_mesh)
    bm.free()

    new_mesh.materials.append(mat_front)   # slot 0
    new_mesh.materials.append(mat_granite) # slot 1
    new_mesh.materials.append(mat_gold)    # slot 2

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    final_obj = bpy.data.objects.new("SarpaVasal_Gateway", new_mesh)
    bpy.context.collection.objects.link(final_obj)
    bpy.context.view_layer.objects.active = final_obj
    final_obj.select_set(True)

    # Calculate final bounding box
    xs = [v.co.x for v in final_obj.data.vertices]
    ys = [v.co.y for v in final_obj.data.vertices]
    zs = [v.co.z for v in final_obj.data.vertices]
    print(f"[SarpaVasal Dome Rebuild] Final Dimensions:")
    print(f"  X: {min(xs):.4f}m to {max(xs):.4f}m (Width: {max(xs)-min(xs):.4f}m)")
    print(f"  Y: {min(ys):.4f}m to {max(ys):.4f}m (Height: {max(ys)-min(ys):.4f}m)")
    print(f"  Z: {min(zs):.4f}m to {max(zs):.4f}m (Depth: {max(zs)-min(zs):.4f}m)")

    # Save Blend
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"[SarpaVasal Dome Rebuild] Saved updated {out_blend}")

    # Export to GLB
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    print(f"[SarpaVasal Dome Rebuild] Exported GLB to {out_glb} (Size: {os.path.getsize(out_glb)/1024/1024:.2f} MB)")

if __name__ == "__main__":
    build_sarpavasal_with_dome()
