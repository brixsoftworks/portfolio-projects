"""
Suryakund Mandapam Superstructure Builder (v11 - World Floor Z = 0.0m, Subterranean Pool & Solid Plinths)
Authentic Sacred Architecture:
- 250 ft x 230 ft footprint (84m length x 73m width, 66.6 ft / 20.3m height)
- Front Side (North) is at World Floor Level Z = 0.0m:
  * North Mandapam Hall: Y in [28.0, 59.0m], X in [-35.5, +35.5m] at Z = 0.0m (World Floor)
  * Connects directly and flush with the top of central 48m pool staircase (Suryakund_Grand_Stairs) at Y = 28.0m, Z = 0.0m
- Subterranean Pool Pit (Under Base Line Z = 0.0m):
  * Central Pool Grand Stairs: Y in [7.5, 28.0m], descends from Z = 0.0m down to Z = -4.50m (promenade level)
  * Pool Water at Z = -4.75m, Basin Floor at Z = -6.10m (20 feet below ground)
  * 3 Solidified Mercury Rasalingas at Z = -4.95m on central plinth
  * Megalithic 8-meter South retaining wall behind Rasalingas: Y = -10.50m, Z from -4.50m to +3.50m
- Elevated South Mandapam (Z = +3.50m, 12 feet above ground):
  * South Mandapam Hall: Y in [-25.0, -10.5m], X in [-35.5, +35.5m] at Z = +3.50m
  * 48m Full-Width Exterior Grand Steps: Starts at Y = -25.0m (Z = +3.50m) and descends OUTWARD to outside arrival plaza at Y = -45.0m (Z = 0.0m)
- Side Mandapam Ascending Steps (Y in [7.5m, 28.0m]):
  * From the point the pool steps start at Y = 28.0m, side mandapam steps go UP from Z = 0.0m to Z = +3.50m at Y = 7.5m
  * West Side Mandapam Steps (X in [-35.5, -24.5m], 11m wide gallery)
  * East Side Mandapam Steps (X in [24.5, 35.5m], 11m wide gallery)
- Solid Foundation Plinth Walls ("fill the side empties to the ground"):
  * Solid ashlar granite foundation walls along West (X = -35.5m) and East (X = +35.5m) and South (Y = -25.0m) from Z = 0.0m up to the elevated floor
- Monolithic Dravidian Pillars ("dont scale the pillers up just make them in hight up and add it"):
  * Width scale Sx = Sy = 0.5085 everywhere (original slender Dravidian column width, NOT scaled up)
  * North Lower Mandapam (Z = 0.0m): H = 8.38m (27.5 ft), Sz = 0.8729, base at Z = 0.0m
  * South Mandapam (Z = +3.50m): H = 4.88m (16 ft), Sz = 0.5085, base at Z = +3.50m
  * Stepped Side Mandapams: Pillar bases sit on step landings, Sz = (8.38 - z_base) / 9.60
  * ALL pillars touch architrave underside at Z = 8.38m with ZERO gap
- 6 Grand Central Vaulted Domes arching along Y-AXIS (Y in [-25.0, +59.0m], apex at Z = 14.20m)
- 20-Foot Brass Sun Sculpture suspended at (0.0, 0.0, 7.40m) directly over the 3 Rasalingas
"""

import bpy
import bmesh
import math
import os
import numpy as np
from mathutils import Vector
import build_suryakund_exterior_steps

def build_suryakund_mandapam():
    print("=== Building Suryakund Complex (v11 - World Floor Z = 0.0m, Pool Under Base Line) ===")

    col_name = "Suryakund_Complex"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

    # 1. Clean up ALL old mandapam, roof, arch, or pillar objects FIRST
    objects_to_remove = [
        obj for obj in bpy.data.objects
        if (obj.name.startswith("Mandapam_") or 
            obj.name.startswith("Pillar_") or 
            obj.name.startswith("Suryakund_Naga_Monolith") or
            obj.name.startswith("Suryakund_Central_Pillar") or
            obj.name == "Plane" or
            "roof" in obj.name.lower() or 
            "arch" in obj.name.lower() or
            "purlin" in obj.name.lower())
    ]
    for obj in objects_to_remove:
        bpy.data.objects.remove(obj, do_unlink=True)

    # Clean up unlinked meshes
    for mesh in list(bpy.data.meshes):
        if ("mandapam" in mesh.name.lower() or 
            "roof" in mesh.name.lower() or 
            "arch" in mesh.name.lower() or 
            "purlin" in mesh.name.lower() or
            (mesh.users == 0 and "pillar" in mesh.name.lower() and mesh.name != "piller")):
            try:
                bpy.data.meshes.remove(mesh, do_unlink=True)
            except Exception:
                pass

    # 2. Build Exterior Grand Steps, Plinths & Subterranean Pool Walls
    build_suryakund_exterior_steps.build_exterior_steps()

    # -------------------------------------------------------------
    # 3. PBR Materials
    # -------------------------------------------------------------
    mat_granite = bpy.data.materials.get("Mat_SarpaVasal_Granite")
    mat_copper = bpy.data.materials.get("Mat_Suryakund_Copper")

    mat_roof = bpy.data.materials.get("Mat_Suryakund_Roof")
    if not mat_roof:
        mat_roof = bpy.data.materials.new(name="Mat_Suryakund_Roof")
    mat_roof.use_nodes = True
    r_nodes = mat_roof.node_tree.nodes
    r_links = mat_roof.node_tree.links
    r_nodes.clear()

    r_out = r_nodes.new(type='ShaderNodeOutputMaterial')
    r_bsdf = r_nodes.new(type='ShaderNodeBsdfPrincipled')
    r_bsdf.inputs['Base Color'].default_value = (0.42, 0.16, 0.08, 1.0)
    r_bsdf.inputs['Roughness'].default_value = 0.65
    r_bsdf.inputs['Specular IOR Level'].default_value = 0.35

    r_tex_coord = r_nodes.new(type='ShaderNodeTexCoord')
    r_mapping = r_nodes.new(type='ShaderNodeMapping')
    r_mapping.inputs['Scale'].default_value = (6.0, 1.0, 1.0)

    r_wave = r_nodes.new(type='ShaderNodeTexWave')
    r_wave.wave_type = 'BANDS'
    r_wave.inputs['Scale'].default_value = 32.0
    r_wave.inputs['Distortion'].default_value = 0.15
    r_wave.inputs['Detail'].default_value = 3.0

    r_noise = r_nodes.new(type='ShaderNodeTexNoise')
    r_noise.inputs['Scale'].default_value = 16.0
    r_noise.inputs['Detail'].default_value = 4.0

    r_mix = r_nodes.new(type='ShaderNodeMix')
    r_mix.data_type = 'RGBA'
    r_mix.inputs['Factor'].default_value = 0.28
    r_mix.inputs['A'].default_value = (0.44, 0.17, 0.08, 1.0)
    r_mix.inputs['B'].default_value = (0.30, 0.11, 0.05, 1.0)

    r_bump = r_nodes.new(type='ShaderNodeBump')
    r_bump.inputs['Strength'].default_value = 0.15
    r_bump.inputs['Distance'].default_value = 0.08

    r_links.new(r_tex_coord.outputs['UV'], r_mapping.inputs['Vector'])
    r_links.new(r_mapping.outputs['Vector'], r_wave.inputs['Vector'])
    r_links.new(r_tex_coord.outputs['Object'], r_noise.inputs['Vector'])
    r_links.new(r_noise.outputs['Fac'], r_mix.inputs['Factor'])
    r_links.new(r_wave.outputs['Color'], r_bump.inputs['Height'])
    r_links.new(r_mix.outputs['Result'], r_bsdf.inputs['Base Color'])
    r_links.new(r_bump.outputs['Normal'], r_bsdf.inputs['Normal'])
    r_links.new(r_bsdf.outputs['BSDF'], r_out.inputs['Surface'])

    mat_steel = bpy.data.materials.get("Mat_Suryakund_SteelGirder")
    if not mat_steel:
        mat_steel = bpy.data.materials.new(name="Mat_Suryakund_SteelGirder")
    mat_steel.use_nodes = True
    st_nodes = mat_steel.node_tree.nodes
    st_links = mat_steel.node_tree.links
    st_nodes.clear()

    st_out = st_nodes.new(type='ShaderNodeOutputMaterial')
    st_bsdf = st_nodes.new(type='ShaderNodeBsdfPrincipled')
    st_bsdf.inputs['Base Color'].default_value = (0.12, 0.11, 0.10, 1.0)
    st_bsdf.inputs['Metallic'].default_value = 0.90
    st_bsdf.inputs['Roughness'].default_value = 0.28
    st_links.new(st_bsdf.outputs['BSDF'], st_out.inputs['Surface'])

    # -------------------------------------------------------------
    # 4. Mandapam Floor Geometry
    # - North Mandapam Hall: Z = 0.0m (World Floor Level, Y in [28.0, 59.0m])
    # - South Mandapam Hall: Z = +3.50m (Elevated terrace, Y in [-25.0, -10.5m])
    # - South Side Mandapams: Z = +3.50m (Y in [-10.5, 7.5m])
    # - Side Mandapam Steps: Y in [7.5m, 28.0m], Z descends from +3.50m down to 0.0m
    # -------------------------------------------------------------
    bm_plat = bmesh.new()
    uv_plat = bm_plat.loops.layers.uv.new("UVMap")

    z_south = 3.50
    z_north = 0.00

    # Section 1: South Mandapam Hall Platform (Y in [-25.0, -10.5], X in [-43.0, 43.0]) at Z = +3.50m
    v_s0 = bm_plat.verts.new((-43.0, -25.0, z_south))
    v_s1 = bm_plat.verts.new((43.0, -25.0, z_south))
    v_s2 = bm_plat.verts.new((43.0, -10.5, z_south))
    v_s3 = bm_plat.verts.new((-43.0, -10.5, z_south))
    bm_plat.faces.new((v_s0, v_s1, v_s2, v_s3))

    # Section 2: West Side Mandapam Elevated Platform (Y in [-10.5, 21.0m], X in [-43.0, -24.0]) at Z = +3.50m
    # Extends continuously from South hall all the way to Y = 21.0m where compact steps begin
    v_w0 = bm_plat.verts.new((-43.0, -10.5, z_south))
    v_w1 = bm_plat.verts.new((-24.0, -10.5, z_south))
    v_w2 = bm_plat.verts.new((-24.0, 21.0, z_south))
    v_w3 = bm_plat.verts.new((-43.0, 21.0, z_south))
    bm_plat.faces.new((v_w0, v_w1, v_w2, v_w3))

    # Section 3: East Side Mandapam Elevated Platform (Y in [-10.5, 21.0m], X in [24.0, 43.0]) at Z = +3.50m
    v_e0 = bm_plat.verts.new((24.0, -10.5, z_south))
    v_e1 = bm_plat.verts.new((43.0, -10.5, z_south))
    v_e2 = bm_plat.verts.new((43.0, 21.0, z_south))
    v_e3 = bm_plat.verts.new((24.0, 21.0, z_south))
    bm_plat.faces.new((v_e0, v_e1, v_e2, v_e3))

    # Section 4: Compact Side Mandapam Steps (Small Step Size, Y in [21.0m, 28.0m])
    # Total rise: Delta Z = 3.50m. Number of steps = 20.
    # Tread depth T = 0.35m (compact 35cm step size so it is NOT long, total flight = 7.0m!)
    # Riser height R = 0.175m (17.5cm comfortable authentic temple riser)
    # Starts at Y = 28.0m (where pool grand stairs start at Z = 0.0m) and goes UP to Z = 3.50m at Y = 21.0m!
    n_side_steps = 20
    y_step_pts = np.linspace(21.0, 28.0, n_side_steps + 1) # from top (21.0m) to bottom (28.0m)
    z_step_pts = np.linspace(z_south, z_north, n_side_steps + 1) # from 3.50m down to 0.00m

    n_blk_side = 8
    x_w_blks = np.linspace(-43.0, -24.0, n_blk_side + 1)
    x_e_blks = np.linspace(24.0, 43.0, n_blk_side + 1)

    for s in range(n_side_steps):
        # Step s goes between y_step_pts[s] (higher/south) and y_step_pts[s+1] (lower/north)
        sy_top = y_step_pts[s]
        sy_bot = y_step_pts[s + 1]
        sz_tread = z_step_pts[s]
        sz_lower = z_step_pts[s + 1]

        # West Side Steps
        for b in range(n_blk_side):
            xb0 = x_w_blks[b]
            xb1 = x_w_blks[b + 1]
            # Horizontal tread
            vt0 = bm_plat.verts.new((xb0, sy_top, sz_tread))
            vt1 = bm_plat.verts.new((xb1, sy_top, sz_tread))
            vt2 = bm_plat.verts.new((xb1, sy_bot, sz_tread))
            vt3 = bm_plat.verts.new((xb0, sy_bot, sz_tread))
            bm_plat.faces.new((vt0, vt1, vt2, vt3))

            # Vertical riser (facing North toward arrival hall)
            vr0 = bm_plat.verts.new((xb0, sy_bot, sz_lower))
            vr1 = bm_plat.verts.new((xb1, sy_bot, sz_lower))
            vr2 = bm_plat.verts.new((xb1, sy_bot, sz_tread))
            vr3 = bm_plat.verts.new((xb0, sy_bot, sz_tread))
            bm_plat.faces.new((vr0, vr1, vr2, vr3))

        # East Side Steps
        for b in range(n_blk_side):
            xb0 = x_e_blks[b]
            xb1 = x_e_blks[b + 1]
            # Horizontal tread
            vt0 = bm_plat.verts.new((xb0, sy_top, sz_tread))
            vt1 = bm_plat.verts.new((xb1, sy_top, sz_tread))
            vt2 = bm_plat.verts.new((xb1, sy_bot, sz_tread))
            vt3 = bm_plat.verts.new((xb0, sy_bot, sz_tread))
            bm_plat.faces.new((vt0, vt1, vt2, vt3))

            # Vertical riser
            vr0 = bm_plat.verts.new((xb0, sy_bot, sz_lower))
            vr1 = bm_plat.verts.new((xb1, sy_bot, sz_lower))
            vr2 = bm_plat.verts.new((xb1, sy_bot, sz_tread))
            vr3 = bm_plat.verts.new((xb0, sy_bot, sz_tread))
            bm_plat.faces.new((vr0, vr1, vr2, vr3))

    # Section 5: North Mandapam Hall Platform (Y in [28.0, 59.0], X in [-43.0, 43.0]) at World Floor Z = 0.0m
    # Seamlessly connects to the top landing of Suryakund_Grand_Stairs at Z = 0.0m!
    v_n0 = bm_plat.verts.new((-43.0, 28.0, z_north))
    v_n1 = bm_plat.verts.new((43.0, 28.0, z_north))
    v_n2 = bm_plat.verts.new((43.0, 59.0, z_north))
    v_n3 = bm_plat.verts.new((-43.0, 59.0, z_north))
    bm_plat.faces.new((v_n0, v_n1, v_n2, v_n3))

    for f in bm_plat.faces:
        for loop in f.loops:
            loop[uv_plat].uv = (loop.vert.co.x * 0.20, loop.vert.co.y * 0.20)

    bmesh.ops.recalc_face_normals(bm_plat, faces=bm_plat.faces)
    mesh_plat = bpy.data.meshes.new("Mandapam_Granite_Floor")
    bm_plat.to_mesh(mesh_plat)
    bm_plat.free()
    if mat_granite:
        mesh_plat.materials.append(mat_granite)
    obj_plat = bpy.data.objects.new("Mandapam_Granite_Floor", mesh_plat)
    col.objects.link(obj_plat)
    print("Constructed Mandapam floor: North at World Floor Z = 0.0m, side steps, South at Z = +3.50m (X = +-43.0m)!")

    # -------------------------------------------------------------
    # 5. Monolithic Dravidian Columns (3 Pillars Across Side Mandapams!)
    # Width scale: Sx = Sy = 0.5085 everywhere (original slender proportion, NOT scaled up in width)
    # Height scale Sz: Made in height up to span from floor to architrave underside (Z = 8.38m)
    # - North Mandapam (Z = 0.0m): H = 8.38m, Sz = 0.8729
    # - South Mandapam (Z = +3.50m): H = 4.88m, Sz = 0.5085
    # - Stepped Side Mandapams: Sz = (8.38 - z_step) / 9.60
    # 3 Pillars across West gallery: X = -25.0m, -33.5m, -42.0m
    # 3 Pillars across East gallery: X = +25.0m, +33.5m, +42.0m
    # ALL pillars sit 100% FLUSH on their respective floor planes!
    # -------------------------------------------------------------
    piller_orig = bpy.data.objects.get("piller")
    if piller_orig:
        piller_mesh = piller_orig.data
        z_arch_bot = 8.38
        scale_xy = 0.5085

        def get_pillar_base_and_sz(x, y):
            if y <= 21.0:
                # South Mandapam and Elevated Side Galleries (Z = +3.50m)
                z_b = 3.50
            elif y >= 28.0:
                # North Mandapam (World Floor Level Z = 0.0m)
                z_b = 0.00
            else:
                # Along compact side mandapam steps (Y in [21.0, 28.0m])
                # Descends from Z = 3.50m at Y = 21.0m to Z = 0.00m at Y = 28.0m
                step_idx = int(math.floor((y - 21.0) / 0.35))
                step_idx = min(max(step_idx, 0), n_side_steps - 1)
                z_b = z_step_pts[step_idx]
            
            h = z_arch_bot - z_b
            sz = h / 9.60
            return z_b, sz

        col_ys = list(np.linspace(-23.0, 59.0, 15))
        col_count = 0

        # West Inner Colonnade (X = -25.5m, safely clear of pool edge at X = -24.0m)
        for y in col_ys:
            zb, sz = get_pillar_base_and_sz(-25.5, y)
            obj_p = bpy.data.objects.new(f"Pillar_W_Inner_{col_count}", piller_mesh)
            obj_p.location = (-25.5, y, zb)
            obj_p.scale = (scale_xy, scale_xy, sz)
            col.objects.link(obj_p)
            col_count += 1

        # West Middle Colonnade (X = -33.35m)
        for y in col_ys:
            zb, sz = get_pillar_base_and_sz(-33.35, y)
            obj_p = bpy.data.objects.new(f"Pillar_W_Mid_{col_count}", piller_mesh)
            obj_p.location = (-33.35, y, zb)
            obj_p.scale = (scale_xy, scale_xy, sz)
            col.objects.link(obj_p)
            col_count += 1

        # West Outer Colonnade (X = -41.2m, safely clear of outer plinth wall at X = -42.2m)
        for y in col_ys:
            zb, sz = get_pillar_base_and_sz(-41.2, y)
            obj_p = bpy.data.objects.new(f"Pillar_W_Outer_{col_count}", piller_mesh)
            obj_p.location = (-41.2, y, zb)
            obj_p.scale = (scale_xy, scale_xy, sz)
            col.objects.link(obj_p)
            col_count += 1

        # East Inner Colonnade (X = +25.5m, clear of pool edge at X = +24.0m)
        for y in col_ys:
            zb, sz = get_pillar_base_and_sz(25.5, y)
            obj_p = bpy.data.objects.new(f"Pillar_E_Inner_{col_count}", piller_mesh)
            obj_p.location = (25.5, y, zb)
            obj_p.scale = (scale_xy, scale_xy, sz)
            col.objects.link(obj_p)
            col_count += 1

        # East Middle Colonnade (X = +33.35m)
        for y in col_ys:
            zb, sz = get_pillar_base_and_sz(33.35, y)
            obj_p = bpy.data.objects.new(f"Pillar_E_Mid_{col_count}", piller_mesh)
            obj_p.location = (33.35, y, zb)
            obj_p.scale = (scale_xy, scale_xy, sz)
            col.objects.link(obj_p)
            col_count += 1

        # East Outer Colonnade (X = +41.2m, clear of outer plinth wall at X = +42.2m)
        for y in col_ys:
            zb, sz = get_pillar_base_and_sz(41.2, y)
            obj_p = bpy.data.objects.new(f"Pillar_E_Outer_{col_count}", piller_mesh)
            obj_p.location = (41.2, y, zb)
            obj_p.scale = (scale_xy, scale_xy, sz)
            col.objects.link(obj_p)
            col_count += 1

        # South Portal Colonnade (Y = -23.0m, clear of South wall at Y = -24.2m)
        south_xs = [-18.0, -9.0, 0.0, 9.0, 18.0]
        for x in south_xs:
            zb, sz = get_pillar_base_and_sz(x, -23.0)
            obj_p = bpy.data.objects.new(f"Pillar_S_{col_count}", piller_mesh)
            obj_p.location = (x, -23.0, zb)
            obj_p.scale = (scale_xy, scale_xy, sz)
            col.objects.link(obj_p)
            col_count += 1

        # North Entrance Colonnade (Y = +59.0m, at World Floor Z = 0.0m, height 8.38m)
        # Open central ceremonial passage (no pillar at X = 0.0m)
        north_xs = [-18.0, -9.0, 9.0, 18.0]
        for x in north_xs:
            zb, sz = get_pillar_base_and_sz(x, 59.0)
            obj_p = bpy.data.objects.new(f"Pillar_N_{col_count}", piller_mesh)
            obj_p.location = (x, 59.0, zb)
            obj_p.scale = (scale_xy, scale_xy, sz)
            col.objects.link(obj_p)
            col_count += 1

        print(f"Placed {col_count} Dravidian monolithic columns (3 PILLARS WIDE on side mandapams) FLUSH on their floor planes!")

    # -------------------------------------------------------------
    # 6. Continuous Dressed Granite Architraves & Transverse Gallery Beams
    # Z = 8.38m to 8.98m
    # -------------------------------------------------------------
    bm_arch = bmesh.new()
    uv_arch = bm_arch.loops.layers.uv.new("UVMap")

    z_bot = 8.38
    z_top = 8.98

    def add_beam_box(bm, uv, p1, p2, z0, z1, width):
        v_dir = Vector((p2[0] - p1[0], p2[1] - p1[1])).normalized()
        v_perp = Vector((-v_dir.y, v_dir.x)) * (width / 2.0)
        c0 = (p1[0] - v_perp.x, p1[1] - v_perp.y)
        c1 = (p1[0] + v_perp.x, p1[1] + v_perp.y)
        c2 = (p2[0] + v_perp.x, p2[1] + v_perp.y)
        c3 = (p2[0] - v_perp.x, p2[1] - v_perp.y)

        v_b = [
            bm.verts.new((c0[0], c0[1], z0)),
            bm.verts.new((c1[0], c1[1], z0)),
            bm.verts.new((c2[0], c2[1], z0)),
            bm.verts.new((c3[0], c3[1], z0)),
            bm.verts.new((c0[0], c0[1], z1)),
            bm.verts.new((c1[0], c1[1], z1)),
            bm.verts.new((c2[0], c2[1], z1)),
            bm.verts.new((c3[0], c3[1], z1)),
        ]
        bm.faces.new((v_b[0], v_b[1], v_b[2], v_b[3]))
        bm.faces.new((v_b[4], v_b[7], v_b[6], v_b[5]))
        bm.faces.new((v_b[0], v_b[4], v_b[5], v_b[1]))
        bm.faces.new((v_b[1], v_b[5], v_b[6], v_b[2]))
        bm.faces.new((v_b[2], v_b[6], v_b[7], v_b[3]))
        bm.faces.new((v_b[3], v_b[7], v_b[4], v_b[0]))

    beam_w = 0.90
    # 6 Longitudinal Architrave Beams along Y (aligned with pillars at +-41.2, +-33.35, +-25.5)
    add_beam_box(bm_arch, uv_arch, (-41.2, -25.5), (-41.2, 59.5), z_bot, z_top, beam_w)
    add_beam_box(bm_arch, uv_arch, (-33.35, -25.5), (-33.35, 59.5), z_bot, z_top, beam_w)
    add_beam_box(bm_arch, uv_arch, (-25.5, -25.5), (-25.5, 59.5), z_bot, z_top, beam_w)
    add_beam_box(bm_arch, uv_arch, (25.5, -25.5), (25.5, 59.5), z_bot, z_top, beam_w)
    add_beam_box(bm_arch, uv_arch, (33.35, -25.5), (33.35, 59.5), z_bot, z_top, beam_w)
    add_beam_box(bm_arch, uv_arch, (41.2, -25.5), (41.2, 59.5), z_bot, z_top, beam_w)

    # South and North Facade Cross Architraves
    add_beam_box(bm_arch, uv_arch, (-41.8, -23.0), (41.8, -23.0), z_bot, z_top, beam_w)
    add_beam_box(bm_arch, uv_arch, (-41.8, 59.0), (41.8, 59.0), z_bot, z_top, beam_w)

    # Transverse Gallery Beams at each Y station spanning across all 3 pillars
    for y in col_ys:
        add_beam_box(bm_arch, uv_arch, (-41.2, y), (-25.5, y), z_bot, z_top, 0.70)
        add_beam_box(bm_arch, uv_arch, (25.5, y), (41.2, y), z_bot, z_top, 0.70)

    for f in bm_arch.faces:
        for loop in f.loops:
            loop[uv_arch].uv = (loop.vert.co.x * 0.25 + loop.vert.co.y * 0.25, loop.vert.co.z * 0.5)

    mesh_arch = bpy.data.meshes.new("Mandapam_Architraves")
    bm_arch.to_mesh(mesh_arch)
    bm_arch.free()
    if mat_granite:
        mesh_arch.materials.append(mat_granite)
    obj_arch = bpy.data.objects.new("Mandapam_Architraves", mesh_arch)
    col.objects.link(obj_arch)

    # -------------------------------------------------------------
    # 7. Heavy Transverse Steel Valley Girders Supporting Central Domes
    # Z = 8.70m to 9.80m
    # -------------------------------------------------------------
    bm_girder = bmesh.new()
    uv_girder = bm_girder.loops.layers.uv.new("UVMap")

    valley_ys = [-25.0, -11.0, 3.0, 17.0, 31.0, 45.0, 59.0]
    gw = 0.90
    gh = 1.10
    gz0 = 8.70
    gz1 = gz0 + gh

    for vy in valley_ys:
        v_g = [
            bm_girder.verts.new((-25.5, vy - gw/2, gz0)),
            bm_girder.verts.new((25.5, vy - gw/2, gz0)),
            bm_girder.verts.new((25.5, vy + gw/2, gz0)),
            bm_girder.verts.new((-25.5, vy + gw/2, gz0)),
            bm_girder.verts.new((-25.5, vy - gw/2, gz1)),
            bm_girder.verts.new((25.5, vy - gw/2, gz1)),
            bm_girder.verts.new((25.5, vy + gw/2, gz1)),
            bm_girder.verts.new((-25.5, vy + gw/2, gz1)),
        ]
        bm_girder.faces.new((v_g[0], v_g[1], v_g[2], v_g[3]))
        bm_girder.faces.new((v_g[4], v_g[7], v_g[6], v_g[5]))
        bm_girder.faces.new((v_g[0], v_g[4], v_g[5], v_g[1]))
        bm_girder.faces.new((v_g[1], v_g[5], v_g[6], v_g[2]))
        bm_girder.faces.new((v_g[2], v_g[6], v_g[7], v_g[3]))
        bm_girder.faces.new((v_g[3], v_g[7], v_g[4], v_g[0]))

    for f in bm_girder.faces:
        for loop in f.loops:
            loop[uv_girder].uv = (loop.vert.co.x * 0.15, loop.vert.co.z * 0.25)

    mesh_girder = bpy.data.meshes.new("Mandapam_Transverse_Beams")
    bm_girder.to_mesh(mesh_girder)
    bm_girder.free()
    if mat_steel:
        mesh_girder.materials.append(mat_steel)
    obj_girder = bpy.data.objects.new("Mandapam_Transverse_Beams", mesh_girder)
    col.objects.link(obj_girder)

    # -------------------------------------------------------------
    # 8. 6 Grand Central Vaulted Domes Arching along Y-Axis
    # Base Z = 8.70m, Rise = 5.50m (Apex at Z = 14.20m)
    # -------------------------------------------------------------
    bm_domes = bmesh.new()
    uv_domes = bm_domes.loops.layers.uv.new("UVMap")

    domes_def = [
        {"name": "Dome_1_South_Portico", "y0": -25.0, "y1": -11.0},
        {"name": "Dome_2_Pool_Rasalingas", "y0": -11.0, "y1": 3.0},
        {"name": "Dome_3_Lower_Steps", "y0": 3.0, "y1": 17.0},
        {"name": "Dome_4_Upper_Steps", "y0": 17.0, "y1": 31.0},
        {"name": "Dome_5_Arrival_Hall", "y0": 31.0, "y1": 45.0},
        {"name": "Dome_6_North_Portico", "y0": 45.0, "y1": 59.0},
    ]

    z_base = 8.70
    arch_rise = 5.50

    nx_d = 28
    ny_d = 20
    x_d_pts = np.linspace(-25.5, 25.5, nx_d + 1)

    for d_info in domes_def:
        y0, y1 = d_info["y0"], d_info["y1"]
        yc = (y0 + y1) / 2.0
        ry = (y1 - y0) / 2.0

        y_pts = np.linspace(y0, y1, ny_d + 1)
        grid_v = {}

        for j in range(ny_d + 1):
            yj = y_pts[j]
            y_norm = abs(yj - yc) / ry
            y_ratio = min(y_norm, 1.0)
            zj_arch = z_base + arch_rise * (1.0 - y_ratio**2)

            for i in range(nx_d + 1):
                xi = x_d_pts[i]
                x_crown = 0.35 * (1.0 - (xi / 25.5)**2)
                v = bm_domes.verts.new((xi, yj, zj_arch + x_crown))
                grid_v[(i, j)] = v

        for j in range(ny_d):
            for i in range(nx_d):
                f = bm_domes.faces.new((
                    grid_v[(i, j)],
                    grid_v[(i + 1, j)],
                    grid_v[(i + 1, j + 1)],
                    grid_v[(i, j + 1)]
                ))
                f.loops[0][uv_domes].uv = (i * 0.25, j * 0.25)
                f.loops[1][uv_domes].uv = ((i + 1) * 0.25, j * 0.25)
                f.loops[2][uv_domes].uv = ((i + 1) * 0.25, (j + 1) * 0.25)
                f.loops[3][uv_domes].uv = (i * 0.25, (j + 1) * 0.25)

        # Central Light Monitor Clerestory
        nx_mon = 6
        x_mon_pts = np.linspace(-3.0, 3.0, nx_mon + 1)
        y_mon_pts = np.linspace(yc - 3.5, yc + 3.5, 6)
        mon_v = {}
        for mj in range(len(y_mon_pts)):
            my = y_mon_pts[mj]
            for mi in range(nx_mon + 1):
                mx = x_mon_pts[mi]
                mz = z_base + arch_rise + 0.85 - 0.20 * (abs(mx) / 3.0)
                mon_v[(mi, mj)] = bm_domes.verts.new((mx, my, mz))

        for mj in range(len(y_mon_pts) - 1):
            for mi in range(nx_mon):
                f_mon = bm_domes.faces.new((
                    mon_v[(mi, mj)],
                    mon_v[(mi + 1, mj)],
                    mon_v[(mi + 1, mj + 1)],
                    mon_v[(mi, mj + 1)]
                ))
                f_mon.loops[0][uv_domes].uv = (mi * 0.5, mj * 0.5)
                f_mon.loops[1][uv_domes].uv = ((mi + 1) * 0.5, mj * 0.5)
                f_mon.loops[2][uv_domes].uv = ((mi + 1) * 0.5, (mj + 1) * 0.5)
                f_mon.loops[3][uv_domes].uv = (mi * 0.5, (mj + 1) * 0.5)

    mesh_domes = bpy.data.meshes.new("Mandapam_Multi_Domes_Roof")
    bm_domes.to_mesh(mesh_domes)
    bm_domes.free()
    if mat_roof:
        mesh_domes.materials.append(mat_roof)
    obj_domes = bpy.data.objects.new("Mandapam_Multi_Domes_Roof", mesh_domes)
    col.objects.link(obj_domes)

    # -------------------------------------------------------------
    # 9. Structural Curved Steel Arch Ribs (along Y) on Central Domes
    # -------------------------------------------------------------
    bm_ribs = bmesh.new()
    uv_ribs = bm_ribs.loops.layers.uv.new("UVMap")

    rib_xs = [-24.0, -16.0, -8.0, 0.0, 8.0, 16.0, 24.0]
    rib_w = 0.55
    rib_d = 0.75

    for d_info in domes_def:
        y0, y1 = d_info["y0"], d_info["y1"]
        yc = (y0 + y1) / 2.0
        ry = (y1 - y0) / 2.0
        n_rib_pts = 20
        y_r = np.linspace(y0, y1, n_rib_pts)

        for rx in rib_xs:
            rings = []
            for j in range(n_rib_pts):
                yj = y_r[j]
                y_norm = (yj - yc) / ry
                zj = z_base + arch_rise * (1.0 - y_norm**2)
                
                dz_dy = -2.0 * arch_rise * y_norm / ry
                norm_vec = Vector((0.0, -dz_dy, 1.0)).normalized()

                p0 = Vector((rx - rib_w/2, yj, zj)) - norm_vec * (rib_d/2)
                p1 = Vector((rx + rib_w/2, yj, zj)) - norm_vec * (rib_d/2)
                p2 = Vector((rx + rib_w/2, yj, zj)) + norm_vec * (rib_d/2)
                p3 = Vector((rx - rib_w/2, yj, zj)) + norm_vec * (rib_d/2)

                rings.append([
                    bm_ribs.verts.new(p0),
                    bm_ribs.verts.new(p1),
                    bm_ribs.verts.new(p2),
                    bm_ribs.verts.new(p3),
                ])

            for j in range(n_rib_pts - 1):
                r0 = rings[j]
                r1 = rings[j + 1]
                for k in range(4):
                    k_next = (k + 1) % 4
                    bm_ribs.faces.new((r0[k], r0[k_next], r1[k_next], r1[k]))

    for f in bm_ribs.faces:
        for loop in f.loops:
            loop[uv_ribs].uv = (loop.vert.co.y * 0.20, loop.vert.co.z * 0.30)

    mesh_ribs = bpy.data.meshes.new("Mandapam_Arch_Ribs_Y")
    bm_ribs.to_mesh(mesh_ribs)
    bm_ribs.free()
    if mat_steel:
        mesh_ribs.materials.append(mat_steel)
    obj_ribs = bpy.data.objects.new("Mandapam_Arch_Ribs_Y", mesh_ribs)
    col.objects.link(obj_ribs)

    # -------------------------------------------------------------
    # 10. Longitudinal Purlins Running East-West (X-Axis)
    # -------------------------------------------------------------
    bm_purl = bmesh.new()
    uv_purl = bm_purl.loops.layers.uv.new("UVMap")

    pw, ph = 0.30, 0.40
    for d_info in domes_def:
        y0, y1 = d_info["y0"], d_info["y1"]
        yc = (y0 + y1) / 2.0
        ry = (y1 - y0) / 2.0
        purl_y_offsets = [-0.75 * ry, -0.40 * ry, 0.0, 0.40 * ry, 0.75 * ry]

        for py_off in purl_y_offsets:
            py = yc + py_off
            pz = z_base + arch_rise * (1.0 - (py_off / ry)**2) + 0.25

            v_p = [
                bm_purl.verts.new((-25.5, py - pw/2, pz - ph/2)),
                bm_purl.verts.new((25.5, py - pw/2, pz - ph/2)),
                bm_purl.verts.new((25.5, py + pw/2, pz - ph/2)),
                bm_purl.verts.new((-25.5, py + pw/2, pz - ph/2)),
                bm_purl.verts.new((-25.5, py - pw/2, pz + ph/2)),
                bm_purl.verts.new((25.5, py - pw/2, pz + ph/2)),
                bm_purl.verts.new((25.5, py + pw/2, pz + ph/2)),
                bm_purl.verts.new((-25.5, py + pw/2, pz + ph/2)),
            ]
            bm_purl.faces.new((v_p[0], v_p[1], v_p[2], v_p[3]))
            bm_purl.faces.new((v_p[4], v_p[7], v_p[6], v_p[5]))
            bm_purl.faces.new((v_p[0], v_p[4], v_p[5], v_p[1]))
            bm_purl.faces.new((v_p[1], v_p[5], v_p[6], v_p[2]))
            bm_purl.faces.new((v_p[2], v_p[6], v_p[7], v_p[3]))
            bm_purl.faces.new((v_p[3], v_p[7], v_p[4], v_p[0]))

    for f in bm_purl.faces:
        for loop in f.loops:
            loop[uv_purl].uv = (loop.vert.co.x * 0.15, loop.vert.co.z * 0.25)

    mesh_purl = bpy.data.meshes.new("Mandapam_Purlins_X")
    bm_purl.to_mesh(mesh_purl)
    bm_purl.free()
    if mat_steel:
        mesh_purl.materials.append(mat_steel)
    obj_purl = bpy.data.objects.new("Mandapam_Purlins_X", mesh_purl)
    col.objects.link(obj_purl)

    # -------------------------------------------------------------
    # 11. SIDE MANDAPAM ROOFS (West & East Galleries)
    # Spanning X in [-36.5, -24.8] and X in [24.8, 36.5], Y in [-25.5, 59.5]
    # -------------------------------------------------------------
    bm_side_roof = bmesh.new()
    uv_side_roof = bm_side_roof.loops.layers.uv.new("UVMap")

    ny_side = 28
    y_side_pts = np.linspace(-25.5, 59.5, ny_side + 1)
    nx_side = 8

    # West Side Roof
    w_grid = {}
    x_w_pts = np.linspace(-24.8, -44.0, nx_side + 1)
    for j in range(ny_side + 1):
        sy = y_side_pts[j]
        for i in range(nx_side + 1):
            sx = x_w_pts[i]
            u = (sx - (-24.8)) / (-44.0 - (-24.8))
            sz = 8.98 + 1.80 * math.sin(u * math.pi) - 1.65 * u
            w_grid[(i, j)] = bm_side_roof.verts.new((sx, sy, sz))

    for j in range(ny_side):
        for i in range(nx_side):
            f_w = bm_side_roof.faces.new((
                w_grid[(i, j)],
                w_grid[(i, j + 1)],
                w_grid[(i + 1, j + 1)],
                w_grid[(i + 1, j)]
            ))
            f_w.loops[0][uv_side_roof].uv = (i * 0.35, j * 0.25)
            f_w.loops[1][uv_side_roof].uv = (i * 0.35, (j + 1) * 0.25)
            f_w.loops[2][uv_side_roof].uv = ((i + 1) * 0.35, (j + 1) * 0.25)
            f_w.loops[3][uv_side_roof].uv = ((i + 1) * 0.35, j * 0.25)

    # East Side Roof
    e_grid = {}
    x_e_pts = np.linspace(24.8, 44.0, nx_side + 1)
    for j in range(ny_side + 1):
        sy = y_side_pts[j]
        for i in range(nx_side + 1):
            sx = x_e_pts[i]
            u = (sx - 24.8) / (44.0 - 24.8)
            sz = 8.98 + 1.80 * math.sin(u * math.pi) - 1.65 * u
            e_grid[(i, j)] = bm_side_roof.verts.new((sx, sy, sz))

    for j in range(ny_side):
        for i in range(nx_side):
            f_e = bm_side_roof.faces.new((
                e_grid[(i, j)],
                e_grid[(i + 1, j)],
                e_grid[(i + 1, j + 1)],
                e_grid[(i, j + 1)]
            ))
            f_e.loops[0][uv_side_roof].uv = (i * 0.35, j * 0.25)
            f_e.loops[1][uv_side_roof].uv = ((i + 1) * 0.35, j * 0.25)
            f_e.loops[2][uv_side_roof].uv = ((i + 1) * 0.35, (j + 1) * 0.25)
            f_e.loops[3][uv_side_roof].uv = (i * 0.35, (j + 1) * 0.25)

    # South Facade Eaves & North Facade Eaves
    v_se0 = bm_side_roof.verts.new((-44.0, -25.0, 8.70))
    v_se1 = bm_side_roof.verts.new((44.0, -25.0, 8.70))
    v_se2 = bm_side_roof.verts.new((45.5, -27.5, 7.10))
    v_se3 = bm_side_roof.verts.new((-45.5, -27.5, 7.10))
    bm_side_roof.faces.new((v_se0, v_se1, v_se2, v_se3))

    v_ne0 = bm_side_roof.verts.new((44.0, 59.0, 8.70))
    v_ne1 = bm_side_roof.verts.new((-44.0, 59.0, 8.70))
    v_ne2 = bm_side_roof.verts.new((-45.5, 61.5, 7.10))
    v_ne3 = bm_side_roof.verts.new((45.5, 61.5, 7.10))
    bm_side_roof.faces.new((v_ne0, v_ne1, v_ne2, v_ne3))

    bmesh.ops.recalc_face_normals(bm_side_roof, faces=bm_side_roof.faces)
    mesh_side_roof = bpy.data.meshes.new("Mandapam_Side_Roofs")
    bm_side_roof.to_mesh(mesh_side_roof)
    bm_side_roof.free()
    if mat_roof:
        mesh_side_roof.materials.append(mat_roof)
    obj_side_roof = bpy.data.objects.new("Mandapam_Side_Roofs", mesh_side_roof)
    col.objects.link(obj_side_roof)

    # -------------------------------------------------------------
    # 12. 20-Foot Brass Sun Sculpture Placement & Suspension Cables
    # Positioned at (0.0, 0.0, 7.40m) directly over pool center & Rasalingas
    # -------------------------------------------------------------
    old_para = bpy.data.objects.get("Mandapam_Parapet_Balustrade")
    if old_para:
        bpy.data.objects.remove(old_para, do_unlink=True)
    obj_sun = bpy.data.objects.get("Suryakund_Sun_Sculpture")
    if obj_sun:
        obj_sun.location = (0.0, 0.0, 7.40)
        obj_sun.rotation_euler = (0.0, 0.0, 0.0)

    # 4 Brass Suspension Cables connecting Sun to Dome 2 structure
    bm_cables = bmesh.new()
    uv_cables = bm_cables.loops.layers.uv.new("UVMap")

    yc2, ry2 = -4.0, 7.0
    cable_angles = [0.0, math.pi/2, math.pi, 3*math.pi/2]
    cable_r = 2.8

    for ang in cable_angles:
        cx = cable_r * math.cos(ang)
        cy = cable_r * math.sin(ang)
        cz_bot = 7.45
        y_norm = abs(cy - yc2) / ry2
        cz_top = z_base + arch_rise * (1.0 - min(y_norm, 1.0)**2) - 0.40
        
        v0 = bm_cables.verts.new((cx - 0.03, cy - 0.03, cz_bot))
        v1 = bm_cables.verts.new((cx + 0.03, cy - 0.03, cz_bot))
        v2 = bm_cables.verts.new((cx + 0.03, cy + 0.03, cz_bot))
        v3 = bm_cables.verts.new((cx - 0.03, cy + 0.03, cz_bot))
        v4 = bm_cables.verts.new((cx - 0.03, cy - 0.03, cz_top))
        v5 = bm_cables.verts.new((cx + 0.03, cy - 0.03, cz_top))
        v6 = bm_cables.verts.new((cx + 0.03, cy + 0.03, cz_top))
        v7 = bm_cables.verts.new((cx - 0.03, cy + 0.03, cz_top))

        bm_cables.faces.new((v0, v4, v5, v1))
        bm_cables.faces.new((v1, v5, v6, v2))
        bm_cables.faces.new((v2, v6, v7, v3))
        bm_cables.faces.new((v3, v7, v4, v0))

    mesh_cables = bpy.data.meshes.new("Mandapam_Sun_Cables")
    bm_cables.to_mesh(mesh_cables)
    bm_cables.free()
    if mat_copper:
        mesh_cables.materials.append(mat_copper)
    obj_cables = bpy.data.objects.new("Mandapam_Sun_Cables", mesh_cables)
    col.objects.link(obj_cables)

# -------------------------------------------------------------
    # 13. Square 4.2m x 4.2m Monolithic Rock & Soaring 11.15m Central Pillar
    # - Width W = 4.2m, Thickness D = 4.2m (square plan: 'as thick as the width of the front face')
    # - Height H = 4.5m: Authentic human-proportional monolithic altar pedestal matching imagesm.jpg
    # - Leaves >21.5m of wide cascading open stairs on both sides across the 48m grand staircase
    # - Front face: Displaced 3D King Cobra Naga sculpture with authentic black granite relief
    # - Side & Back faces: Solid monolithic dressed granite WITHOUT the Naga
    # - Base grounded to Z = -4.50m on pool side, Z = -2.25m on front landing
    # - Top cornice at Z = 2.65m
    # - Central Pillar on top of rock at (0.0, 14.40m, 2.65m) soaring 11.15m to dome apex at Z = 13.80m
    # -------------------------------------------------------------
    mat_naga = bpy.data.materials.get("Mat_Naga_Front_Relief")
    if not mat_naga:
        mat_naga = bpy.data.materials.new("Mat_Naga_Front_Relief")
        mat_naga.use_nodes = True
    
    n_nodes = mat_naga.node_tree.nodes
    n_links = mat_naga.node_tree.links
    n_nodes.clear()
    
    node_out = n_nodes.new("ShaderNodeOutputMaterial")
    node_bsdf = n_nodes.new("ShaderNodeBsdfPrincipled")
    node_tex = n_nodes.new("ShaderNodeTexImage")
    tex_path = "/home/mullainathan/Games/IshaGodot/assets/textures/naga_stone_relief_albedo.png"
    node_tex.image = bpy.data.images.load(tex_path, check_existing=True)
    
    node_bump = n_nodes.new("ShaderNodeBump")
    node_bump.inputs['Strength'].default_value = 0.60
    node_bump.inputs['Distance'].default_value = 0.05
    node_hm = n_nodes.new("ShaderNodeTexImage")
    hm_path = "/home/mullainathan/Games/IshaGodot/assets/textures/naga_stone_relief_height.png"
    node_hm.image = bpy.data.images.load(hm_path, check_existing=True)
    node_hm.image.colorspace_settings.name = 'Non-Color'
    
    n_links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
    n_links.new(node_hm.outputs['Color'], node_bump.inputs['Height'])
    n_links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])
    node_bsdf.inputs['Roughness'].default_value = 0.55
    n_links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    # Load heightmap via bpy.data.images
    img = bpy.data.images.load(hm_path, check_existing=True)
    w_cols, h_rows = img.size[0], img.size[1]
    raw_pixels = np.array(img.pixels[:]).reshape((h_rows, w_cols, 4))
    hm_arr = raw_pixels[:, :, 0]
    
    W = 4.2
    D = 4.2 # As thick as the width of the front face!
    H = 4.5 # Proportional monolithic altar height matching imagesm.jpg
    disp_amp = 0.50
    
    y_front_base = 16.5 - disp_amp # Front relief reaches Y = 16.5m
    y_back = y_front_base + disp_amp - D # Exactly 4.2m thick -> Y = 12.30m
    z_landing = -2.25 # Landing level at North front
    z_foundation = -4.50 # Lowest stair / floor level at South back
    z_top = z_landing + H # 2.25m
    
    nx = 100
    nz = 100
    
    x_pts = np.linspace(-W / 2.0, W / 2.0, nx + 1)
    z_front_pts = np.linspace(z_landing, z_top, nz + 1)
    z_back_pts = np.linspace(z_foundation, z_top, nz + 1)
    
    u_pts = np.linspace(1.0, 0.0, nx + 1)
    v_pts = np.linspace(0.0, 1.0, nz + 1)
    
    row_indices = (v_pts * (h_rows - 1)).astype(np.int32)
    col_indices = (u_pts * (w_cols - 1)).astype(np.int32)
    disp_grid = hm_arr[np.ix_(row_indices, col_indices)]
    
    bm_naga = bmesh.new()
    uv_naga = bm_naga.loops.layers.uv.verify()
    
    # 1. Front grid vertices (at Y = 16.5m, Z from -2.25m to 2.25m)
    front_v = {}
    for j in range(nz + 1):
        for i in range(nx + 1):
            x = x_pts[i]
            z = z_front_pts[j]
            y = y_front_base + disp_amp * disp_grid[j, i]
            v = bm_naga.verts.new((x, y, z))
            front_v[(i, j)] = v
    
    for j in range(nz):
        for i in range(nx):
            v0 = front_v[(i, j)]
            v1 = front_v[(i, j + 1)]
            v2 = front_v[(i + 1, j + 1)]
            v3 = front_v[(i + 1, j)]
            f = bm_naga.faces.new((v0, v1, v2, v3))
            f.material_index = 0 # Naga relief material
            f.loops[0][uv_naga].uv = (u_pts[i], v_pts[j])
            f.loops[1][uv_naga].uv = (u_pts[i], v_pts[j + 1])
            f.loops[2][uv_naga].uv = (u_pts[i + 1], v_pts[j + 1])
            f.loops[3][uv_naga].uv = (u_pts[i + 1], v_pts[j])
    
    # 2. Back face vertices at Y = y_back (12.30m), extending down to z_foundation (-4.50m)!
    back_v = {}
    for j in range(nz + 1):
        for i in range(nx + 1):
            x = x_pts[i]
            z = z_back_pts[j]
            v = bm_naga.verts.new((x, y_back, z))
            back_v[(i, j)] = v
    
    for j in range(nz):
        for i in range(nx):
            v0 = back_v[(i, j)]
            v1 = back_v[(i + 1, j)]
            v2 = back_v[(i + 1, j + 1)]
            v3 = back_v[(i, j + 1)]
            f = bm_naga.faces.new((v0, v1, v2, v3))
            f.material_index = 1 # Granite (NO NAGA!)
            f.loops[0][uv_naga].uv = (x_pts[i] * 0.25, z_back_pts[j] * 0.25)
            f.loops[1][uv_naga].uv = (x_pts[i + 1] * 0.25, z_back_pts[j] * 0.25)
            f.loops[2][uv_naga].uv = (x_pts[i + 1] * 0.25, z_back_pts[j + 1] * 0.25)
            f.loops[3][uv_naga].uv = (x_pts[i] * 0.25, z_back_pts[j + 1] * 0.25)
    
    # 3. West side wall (normal -X) - 4.2m deep!
    for j in range(nz):
        vf0 = front_v[(0, j)]
        vb0 = back_v[(0, j)]
        vb1 = back_v[(0, j + 1)]
        vf1 = front_v[(0, j + 1)]
        f = bm_naga.faces.new((vf0, vb0, vb1, vf1))
        f.material_index = 1 # Granite (NO NAGA!)
        f.loops[0][uv_naga].uv = (vf0.co.y * 0.25, vf0.co.z * 0.25)
        f.loops[1][uv_naga].uv = (vb0.co.y * 0.25, vb0.co.z * 0.25)
        f.loops[2][uv_naga].uv = (vb1.co.y * 0.25, vb1.co.z * 0.25)
        f.loops[3][uv_naga].uv = (vf1.co.y * 0.25, vf1.co.z * 0.25)
    
    # 4. East side wall (normal +X) - 4.2m deep!
    for j in range(nz):
        vf0 = front_v[(nx, j)]
        vf1 = front_v[(nx, j + 1)]
        vb1 = back_v[(nx, j + 1)]
        vb0 = back_v[(nx, j)]
        f = bm_naga.faces.new((vf0, vf1, vb1, vb0))
        f.material_index = 1 # Granite (NO NAGA!)
        f.loops[0][uv_naga].uv = (vf0.co.y * 0.25, vf0.co.y * 0.25)
        f.loops[1][uv_naga].uv = (vf1.co.y * 0.25, vf1.co.y * 0.25)
        f.loops[2][uv_naga].uv = (vb1.co.y * 0.25, vb1.co.z * 0.25)
        f.loops[3][uv_naga].uv = (vb0.co.y * 0.25, vb0.co.y * 0.25)
    
    # 5. Bottom face: connects front bottom (Z = -2.25) to back bottom (Z = -4.50)
    for i in range(nx):
        vf0 = front_v[(i, 0)]
        vf1 = front_v[(i + 1, 0)]
        vb1 = back_v[(i + 1, 0)]
        vb0 = back_v[(i, 0)]
        f = bm_naga.faces.new((vf0, vf1, vb1, vb0))
        f.material_index = 1 # Granite
        f.loops[0][uv_naga].uv = (vf0.co.x * 0.25, vf0.co.y * 0.25)
        f.loops[1][uv_naga].uv = (vf1.co.x * 0.25, vf1.co.y * 0.25)
        f.loops[2][uv_naga].uv = (vb1.co.x * 0.25, vb1.co.y * 0.25)
        f.loops[3][uv_naga].uv = (vb0.co.x * 0.25, vb0.co.y * 0.25)
    
    # 6. Top face (normal +Z) at Z = z_top (2.25m)
    for i in range(nx):
        vf0 = front_v[(i, nz)]
        vb0 = back_v[(i, nz)]
        vb1 = back_v[(i + 1, nz)]
        vf1 = front_v[(i + 1, nz)]
        f = bm_naga.faces.new((vf0, vb0, vb1, vf1))
        f.material_index = 1 # Granite
        f.loops[0][uv_naga].uv = (vf0.co.x * 0.25, vf0.co.y * 0.25)
        f.loops[1][uv_naga].uv = (vb0.co.x * 0.25, vb0.co.y * 0.25)
        f.loops[2][uv_naga].uv = (vb1.co.x * 0.25, vb1.co.y * 0.25)
        f.loops[3][uv_naga].uv = (vf1.co.x * 0.25, vf1.co.y * 0.25)
    
    # 7. Stepped Dravidian Base Plinth & Top Cornice for 4.2x4.2m footprint
    def add_molded_box(bm, x0, x1, y0, y1, z0, z1, mat_idx, uv_l):
        v = [
            bm.verts.new((x0, y0, z0)),
            bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)),
            bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)),
            bm.verts.new((x1, y0, z1)),
            bm.verts.new((x1, y1, z1)),
            bm.verts.new((x0, y1, z1)),
        ]
        quads = [
            (v[0], v[3], v[2], v[1]),
            (v[4], v[5], v[6], v[7]),
            (v[0], v[1], v[5], v[4]),
            (v[2], v[3], v[7], v[6]),
            (v[3], v[0], v[4], v[7]),
            (v[1], v[2], v[6], v[5]),
        ]
        for q in quads:
            f = bm.faces.new(q)
            f.material_index = mat_idx
            for loop in f.loops:
                loop[uv_l].uv = (loop.vert.co.x * 0.25 + loop.vert.co.y * 0.25, loop.vert.co.z * 0.25)
    
    # Front landing base plinth
    add_molded_box(bm_naga, -2.25, 2.25, 16.3, 16.6, -2.25, -2.05, 1, uv_naga)
    add_molded_box(bm_naga, -2.20, 2.20, 16.35, 16.55, -2.05, -1.90, 1, uv_naga)
    
    # South lower stairs base plinth (grounding down to Z = -4.50m)
    add_molded_box(bm_naga, -2.25, 2.25, 12.15, 12.45, -4.50, -4.25, 1, uv_naga)
    add_molded_box(bm_naga, -2.20, 2.20, 12.20, 12.40, -4.25, -4.05, 1, uv_naga)
    
    # Top cornice tiers
    add_molded_box(bm_naga, -2.20, 2.20, 12.20, 16.60, z_top, z_top + 0.18, 1, uv_naga)
    add_molded_box(bm_naga, -2.25, 2.25, 12.15, 16.65, z_top + 0.18, z_top + 0.40, 1, uv_naga)
    
    bmesh.ops.recalc_face_normals(bm_naga, faces=bm_naga.faces)
    
    mesh_naga = bpy.data.meshes.new("Suryakund_Naga_Monolith")
    bm_naga.to_mesh(mesh_naga)
    bm_naga.free()
    
    mesh_naga.materials.append(mat_naga)
    mesh_naga.materials.append(bpy.data.materials.get("Mat_SarpaVasal_Granite"))
    
    obj_naga = bpy.data.objects.new("Suryakund_Naga_Monolith", mesh_naga)
    col.objects.link(obj_naga)
    print("Constructed proportional 4.2x4.2m Suryakund_Naga_Monolith on grand stairs landing!")
    
    # 8. Place Central Pillar on Top of Rock Reaching Dome (11.15m Soaring Column)
    piller_orig = bpy.data.objects.get("piller")
    if piller_orig:
        piller_mesh = piller_orig.data
        z_rock_top = z_top + 0.40 # 2.65m (surface of rock cornice)
        z_dome = 13.80 # underside of central arch rib & dome at X=0, Y=14.40m
        h_pillar = z_dome - z_rock_top # 11.15m
        sz_pillar = h_pillar / 9.597 # native piller height is 9.597m -> 1.1618
        
        pillar_center_y = 14.40 # centered on the 4.2x4.2m rock (Y in [12.3, 16.5])
        scale_xy = 0.70 # monumental 1.83m column width
        
        obj_cen_pillar = bpy.data.objects.new("Suryakund_Central_Pillar", piller_mesh)
        obj_cen_pillar.location = (0.0, pillar_center_y, z_rock_top)
        obj_cen_pillar.scale = (scale_xy, scale_xy, sz_pillar)
        col.objects.link(obj_cen_pillar)
        print(f"Placed central pillar on top of rock at Z={z_rock_top:.2f}m reaching dome at Z={z_dome:.2f}m (H={h_pillar:.2f}m)!")

    # Save mainfile
    blend_path = "/home/mullainathan/Downloads/Untitled.blend"
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print("Suryakund Complex (v11) successfully built and saved!")

if __name__ == "__main__":
    build_suryakund_mandapam()
