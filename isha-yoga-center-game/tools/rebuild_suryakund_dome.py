#!/usr/bin/env python3
"""
Rebuild Suryakund Stepped Vaulted Domes, Authentic User Sun Sculpture & Sacred Golden Lingas
- Matches authentic Isha Foundation Suryakund reference architecture (WhatsApp Image 2026-11-25 at 10.26.46 PM.jpeg):
    1. Horizontal barrel vaults running East-West (X-axis), stepping monotonically UPWARDS from front arrival to back sanctuary:
       - Bay 6 (North Arrival Entrance Canopy): Y in [45, 59m], Base Z = 7.60m, Rise 1.30m -> Apex Z = 8.90m (LOWEST)
       - Bay 5 (Upper Mandapam): Y in [31, 45m], Base Z = 8.70m, Rise 1.60m -> Apex Z = 10.30m
       - Bay 4 (Grand Descent Stairs): Y in [17, 31m], Base Z = 9.90m, Rise 2.00m -> Apex Z = 11.90m
       - Bay 3 (Pool Steps & Naga Monolith): Y in [6, 17m], Base Z = 11.20m, Rise 2.50m -> Apex Z = 13.70m
       - Bay 2 (Master Pool Sanctuary): Y in [-12, 6m], Base Z = 12.60m, Rise 4.20m -> Apex Z = 16.80m (HIGHEST MASTER DOME)
       - Bay 1 (South Portico): Y in [-25, -12m], Base Z = 9.90m, Rise 2.50m -> Apex Z = 12.40m
    2. Straight horizontal cylindrical ridges across full width (East-West), with vertical riser steps connecting each tier.
    3. BIGGEST DOME (Bay 2): ONE MASTER GOLDEN LINGA on lotus plinth at apex (Z = 16.80m), NO GOPURAM / CUPOLA.
    4. LOWER TWO DOMES (Bay 6 & Bay 5): 4 AND 4 GOLDEN LINGAS in staggered ZIGZAG pattern along the horizontal ridges.
    5. Mandapam inner ceilings (both vaulted roofs and side mandapams) textured with authentic Terracotta tiles.
    6. Naga Monolith base firmly seated into the stair treads down to Z = -2.75m (zero daylight gap), top at Z = 2.650m touching central pillar.
    7. Volumetric 3D Cascading Waterfall (14m Wide x 8.81m Drop x 0.45m Thickness) with ballistic drop physics.
    8. Exports complete GLB to assets/models/suryakund_complex.glb and updates Untitled.blend.
"""

import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
import math
import numpy as np
import os

def create_linga_geometry(bm, uv_layer, cx, cy, base_z, total_height=2.2, r_body=0.42, n_circ=16):
    """Generates a sacred sculpted Linga with lotus plinth, cylindrical shaft, and rounded dome apex."""
    h_plinth = total_height * 0.25
    r_plinth = r_body * 1.85
    h_body = total_height * 0.45
    h_dome = total_height * 0.30

    profile = [
        (base_z + 0.0, r_plinth),
        (base_z + h_plinth * 0.35, r_plinth * 1.12),
        (base_z + h_plinth * 0.70, r_plinth * 0.85),
        (base_z + h_plinth, r_plinth * 0.95),
    ]

    n_body = 4
    for i in range(1, n_body + 1):
        z = base_z + h_plinth + (h_body * i / n_body)
        profile.append((z, r_body))

    n_dome = 6
    for i in range(1, n_dome):
        phi = (math.pi / 2.0) * (i / n_dome)
        z = base_z + h_plinth + h_body + h_dome * math.sin(phi)
        r = r_body * math.cos(phi)
        profile.append((z, r))

    angles = np.linspace(0, 2 * math.pi, n_circ, endpoint=False)
    rings = []
    for z_lvl, r_lvl in profile:
        ring = []
        for a in angles:
            vx = cx + r_lvl * math.cos(a)
            vy = cy + r_lvl * math.sin(a)
            ring.append(bm.verts.new((vx, vy, z_lvl)))
        rings.append(ring)

    # Apex vertex
    v_apex = bm.verts.new((cx, cy, base_z + total_height))

    # Base cap
    v_base = bm.verts.new((cx, cy, base_z))
    r_bot = rings[0]
    for s in range(n_circ):
        s_next = (s + 1) % n_circ
        f = bm.faces.new((v_base, r_bot[s_next], r_bot[s]))
        if uv_layer:
            f.loops[0][uv_layer].uv = (0.5, 0.5)
            f.loops[1][uv_layer].uv = (0.5 + 0.5 * math.cos(angles[s_next]), 0.5 + 0.5 * math.sin(angles[s_next]))
            f.loops[2][uv_layer].uv = (0.5 + 0.5 * math.cos(angles[s]), 0.5 + 0.5 * math.sin(angles[s]))

    # Wall quad rings
    for lvl in range(len(rings) - 1):
        r0 = rings[lvl]
        r1 = rings[lvl + 1]
        for s in range(n_circ):
            s_next = (s + 1) % n_circ
            f = bm.faces.new((r0[s], r0[s_next], r1[s_next], r1[s]))
            if uv_layer:
                f.loops[0][uv_layer].uv = (s / float(n_circ), lvl / float(len(rings)))
                f.loops[1][uv_layer].uv = ((s + 1) / float(n_circ), lvl / float(len(rings)))
                f.loops[2][uv_layer].uv = ((s + 1) / float(n_circ), (lvl + 1) / float(len(rings)))
                f.loops[3][uv_layer].uv = (s / float(n_circ), (lvl + 1) / float(len(rings)))

    # Dome apex cap
    r_top = rings[-1]
    for s in range(n_circ):
        s_next = (s + 1) % n_circ
        f = bm.faces.new((r_top[s], r_top[s_next], v_apex))
        if uv_layer:
            f.loops[0][uv_layer].uv = (s / float(n_circ), 0.9)
            f.loops[1][uv_layer].uv = ((s + 1) / float(n_circ), 0.9)
            f.loops[2][uv_layer].uv = ((s + 0.5) / float(n_circ), 1.0)


def rebuild_suryakund_6domes_and_lingas():
    blend_path = "/home/mullainathan/Downloads/Untitled.blend"
    blend_bak_path = "/home/mullainathan/Downloads/Untitled.blend.bak"
    glb_export_path = "/home/mullainathan/Games/IshaGodot/assets/models/suryakund_complex.glb"

    print(f"[Dome Rebuild] Opening {blend_path}...")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    col = bpy.data.collections.get("Suryakund_Complex")
    if not col:
        print("[Dome Rebuild] Error: Collection 'Suryakund_Complex' not found!")
        return

    # -------------------------------------------------------------
    # 1. Rotate the 3 Rasalingas 180 degrees & Widen Evenly Across Pool
    # -------------------------------------------------------------
    linga_positions = {
        "Rasalinga_Center": Vector((0.0, 0.0, -7.263)),
        "Rasalinga_West": Vector((-12.0, 0.0, -7.263)),
        "Rasalinga_East": Vector((12.0, 0.0, -7.263)),
    }
    for lname, lpos in linga_positions.items():
        obj = bpy.data.objects.get(lname)
        if obj:
            obj.location = lpos
            obj.rotation_euler = Euler((0.0, 0.0, math.pi), 'XYZ')
            print(f"[Dome Rebuild] Positioned {lname} at {obj.location} (rotated 180 deg)")

    plinth_obj = bpy.data.objects.get("Suryakund_Central_Plinth")
    if plinth_obj:
        for v in plinth_obj.data.vertices:
            if v.co.x < -0.1:
                v.co.x = -16.5
            elif v.co.x > 0.1:
                v.co.x = 16.5
        plinth_obj.data.update()
        print("[Dome Rebuild] Widened Suryakund_Central_Plinth to X in [-16.5, 16.5]")

    # -------------------------------------------------------------
    # 2. Materials
    # -------------------------------------------------------------
    mat_roof = bpy.data.materials.get("Mat_Suryakund_Roof")
    mat_steel = bpy.data.materials.get("Mat_Suryakund_SteelGirder")
    mat_granite = bpy.data.materials.get("Mat_SarpaVasal_Granite")
    mat_brass = bpy.data.materials.get("Mat_Suryakund_Sun")

    # Sacred 24K Temple Gold Material for the Golden Lingas
    mat_gold = bpy.data.materials.get("Mat_Suryakund_Gold")
    if not mat_gold:
        mat_gold = bpy.data.materials.new(name="Mat_Suryakund_Gold")
    mat_gold.use_nodes = True
    g_nodes = mat_gold.node_tree.nodes
    g_links = mat_gold.node_tree.links
    g_nodes.clear()
    g_out = g_nodes.new(type='ShaderNodeOutputMaterial')
    g_bsdf = g_nodes.new(type='ShaderNodeBsdfPrincipled')
    g_bsdf.inputs['Base Color'].default_value = (0.95, 0.76, 0.22, 1.0) # Radiant 24K Gold
    g_bsdf.inputs['Metallic'].default_value = 0.94
    g_bsdf.inputs['Roughness'].default_value = 0.16
    g_links.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])

    # Consecrated Sacred Copper Basin Material for Underwater Flooring
    mat_copper = bpy.data.materials.get("Mat_Suryakund_CopperBasin")
    if not mat_copper:
        mat_copper = bpy.data.materials.new(name="Mat_Suryakund_CopperBasin")
    mat_copper.use_nodes = True
    c_nodes = mat_copper.node_tree.nodes
    c_links = mat_copper.node_tree.links
    c_nodes.clear()
    c_out = c_nodes.new(type='ShaderNodeOutputMaterial')
    c_bsdf = c_nodes.new(type='ShaderNodeBsdfPrincipled')
    c_bsdf.inputs['Base Color'].default_value = (0.96, 0.58, 0.38, 1.0) # Radiant 100% Sacred Copper
    c_bsdf.inputs['Metallic'].default_value = 0.98
    c_bsdf.inputs['Roughness'].default_value = 0.16
    c_links.new(c_bsdf.outputs['BSDF'], c_out.inputs['Surface'])

    # Consecrated Sacred Copper Material for Lingas & Pool Basin Flooring
    for lname in ["Rasalinga_Center", "Rasalinga_West", "Rasalinga_East", "Suryakund_Basin_Floor"]:
        lo = bpy.data.objects.get(lname)
        if lo:
            lo.data.materials.clear()
            lo.data.materials.append(mat_copper)

    # Linga basement/plinth alone is authentic Ashlar granite stone ("not the basement of the linga")
    plinth_obj = bpy.data.objects.get("Suryakund_Central_Plinth")
    if plinth_obj:
        plinth_obj.data.materials.clear()
        if mat_granite:
            plinth_obj.data.materials.append(mat_granite)

    # Bright Isha Megalithic Granite Material for Big Pool Edge Rocks
    mat_bright_rock = bpy.data.materials.get("Mat_Suryakund_BrightGraniteRock")
    if not mat_bright_rock:
        mat_bright_rock = bpy.data.materials.new(name="Mat_Suryakund_BrightGraniteRock")
    mat_bright_rock.use_nodes = True
    br_nodes = mat_bright_rock.node_tree.nodes
    br_links = mat_bright_rock.node_tree.links
    br_nodes.clear()
    br_out = br_nodes.new(type='ShaderNodeOutputMaterial')
    br_bsdf = br_nodes.new(type='ShaderNodeBsdfPrincipled')
    br_bsdf.inputs['Base Color'].default_value = (0.95, 0.91, 0.83, 1.0)
    br_bsdf.inputs['Metallic'].default_value = 0.0
    br_bsdf.inputs['Roughness'].default_value = 0.58
    br_links.new(br_bsdf.outputs['BSDF'], br_out.inputs['Surface'])

    # -------------------------------------------------------------
    # 3. Clean up old roof, dome, cupola, and kalasha meshes
    # -------------------------------------------------------------
    objs_to_remove = [
        "Mandapam_Multi_Domes_Roof",
        "Mandapam_Arch_Ribs_Y",
        "Mandapam_Purlins_X",
        "Mandapam_Side_Roofs",
        "Mandapam_Side_Roofs_Exterior",
        "Mandapam_Side_Ceilings",
        "Mandapam_Grand_Vault_Roof",
        "Mandapam_6_Vaulted_Domes_Roof",
        "Mandapam_Transverse_Beams",
        "Mandapam_Valley_Girders",
        "Mandapam_Transverse_Clerestory_Walls",
        "Mandapam_Lateral_Arch_Pediments",
        "Mandapam_Central_Dome_Cupola",
        "Mandapam_Ridge_Kalashas",
        "Mandapam_Master_Golden_Linga",
        "Mandapam_Zigzag_Golden_Lingas",
        "Mandapam_Arch_Trusses",
        "Mandapam_Longitudinal_Purlins",
        "Mandapam_Arched_Pediments",
        "Mandapam_Sun_Suspension_Cables",
        "Mandapam_Sun_Cables",
        "Mandapam_Pool_Edge_Rock_Blocks",
        "Mandapam_Exterior_Front_Fascia",
        "Suryakund_Waterfall_Sheet",
        "Suryakund_Waterfall_Foam",
        "Suryakund_Naga_Base_Pedestal",
        "Suryakund_Pillar_Naga_Sculpture"
    ]
    for oname in objs_to_remove:
        obj = bpy.data.objects.get(oname)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
            print(f"[Dome Rebuild] Removed old object {oname}")

    # -------------------------------------------------------------
    # 4. Stepped Horizontal Barrel Vaults Ascending from Front to Back
    # Matching exact Isha reference photo:
    # - Horizontal cylinders running East-West (across X in [-25.5, +25.5m])
    # - Arch curve in Y-Z plane
    # - Stepped heights monotonically ascending from front entrance canopy up to master sanctuary:
    #     Bay 6 (North Arrival Canopy):   Y in [45, 59m], z_base=8.98m, rise=1.30m -> Apex Z=10.28m (LOWEST)
    #     Bay 5 (Upper Mandapam):         Y in [31, 45m], z_base=9.80m, rise=1.60m -> Apex Z=11.40m
    #     Bay 4 (Grand Descent Stairs):   Y in [17, 31m], z_base=10.70m, rise=2.00m -> Apex Z=12.70m
    #     Bay 3 (Steps & Naga Monolith):  Y in [6, 17m],  z_base=11.80m, rise=2.50m -> Apex Z=14.30m
    #     Bay 2 (Master Pool Sanctuary):  Y in [-12, 6m], z_base=13.00m, rise=3.80m -> Apex Z=16.80m (HIGHEST MASTER DOME)
    #     Bay 1 (South Portico):          Y in [-25, -12m], z_base=9.50m, rise=2.50m -> Apex Z=12.00m
    # -------------------------------------------------------------
    domes_def = [
        {"id": 1, "name": "South_Portico",        "y0": -25.0, "y1": -12.0, "z_base":  9.50, "rise": 2.50},
        {"id": 2, "name": "Master_Pool_Sanctuary","y0": -12.0, "y1":   6.0, "z_base": 13.00, "rise": 3.80},
        {"id": 3, "name": "Steps_Naga_Monolith",  "y0":   6.0, "y1":  17.0, "z_base": 11.80, "rise": 2.50},
        {"id": 4, "name": "Grand_Descent_Stairs", "y0":  17.0, "y1":  31.0, "z_base": 10.70, "rise": 2.00},
        {"id": 5, "name": "Upper_Mandapam",       "y0":  31.0, "y1":  45.0, "z_base":  9.80, "rise": 1.60},
        {"id": 6, "name": "North_Arrival_Hall",   "y0":  45.0, "y1":  59.0, "z_base":  8.98, "rise": 1.30},
    ]

    t_shell = 0.35 # Solid 35cm shell thickness
    nx_d = 28
    ny_per_dome = 20

    bm_domes = bmesh.new()
    uv_domes = bm_domes.loops.layers.uv.new("UVMap")

    x_d_pts = np.linspace(-25.5, 25.5, nx_d + 1)

    def calc_bay_z(yj, d):
        """Calculates exact horizontal cylinder arch height along Y."""
        y0, y1 = d["y0"], d["y1"]
        yc = (y0 + y1) / 2.0
        ry = (y1 - y0) / 2.0
        rise = d["rise"]
        zb = d["z_base"]
        uy = min(abs(yj - yc) / ry, 1.0)
        return zb + rise * (1.0 - uy**2)

    tier_grids = []

    for d in domes_def:
        y0, y1 = d["y0"], d["y1"]
        yc = (y0 + y1) / 2.0
        ry = (y1 - y0) / 2.0
        rise = d["rise"]
        zb = d["z_base"]

        y_pts = np.linspace(y0, y1, ny_per_dome + 1)
        top_grid = {}
        bot_grid = {}

        for j in range(ny_per_dome + 1):
            yj = y_pts[j]
            uy = min(abs(yj - yc) / ry, 1.0)
            zi_top = zb + rise * (1.0 - uy**2)

            # Normal vector in Y-Z plane for uniform downward ceiling thickness
            dz_dy = -2.0 * rise * ((yj - yc) / (ry**2))
            n_vec = Vector((0.0, -dz_dy, 1.0)).normalized()

            for i in range(nx_d + 1):
                xi = x_d_pts[i]
                yj_bot = yj - t_shell * n_vec.y
                zi_bot = zi_top - t_shell * n_vec.z

                top_grid[(i, j)] = bm_domes.verts.new((xi, yj, zi_top))
                bot_grid[(i, j)] = bm_domes.verts.new((xi, yj_bot, zi_bot))

        # Top outer roof faces
        for j in range(ny_per_dome):
            for i in range(nx_d):
                f_top = bm_domes.faces.new((
                    top_grid[(i, j)],
                    top_grid[(i + 1, j)],
                    top_grid[(i + 1, j + 1)],
                    top_grid[(i, j + 1)]
                ))
                f_top.loops[0][uv_domes].uv = (i * 0.25, j * 0.25)
                f_top.loops[1][uv_domes].uv = ((i + 1) * 0.25, j * 0.25)
                f_top.loops[2][uv_domes].uv = ((i + 1) * 0.25, (j + 1) * 0.25)
                f_top.loops[3][uv_domes].uv = (i * 0.25, (j + 1) * 0.25)

        # Bottom inner ceiling faces (terracotta tile texture)
        for j in range(ny_per_dome):
            for i in range(nx_d):
                f_bot = bm_domes.faces.new((
                    bot_grid[(i, j)],
                    bot_grid[(i, j + 1)],
                    bot_grid[(i + 1, j + 1)],
                    bot_grid[(i + 1, j)]
                ))
                f_bot.loops[0][uv_domes].uv = (i * 0.25, j * 0.25)
                f_bot.loops[1][uv_domes].uv = (i * 0.25, (j + 1) * 0.25)
                f_bot.loops[2][uv_domes].uv = ((i + 1) * 0.25, (j + 1) * 0.25)
                f_bot.loops[3][uv_domes].uv = ((i + 1) * 0.25, j * 0.25)

        tier_grids.append((top_grid, bot_grid))

    # Stepped vertical riser walls connecting adjacent ascending tiers along Y beam lines
    # Order of tier_grids matches domes_def: id 1 (South), id 2, id 3, id 4, id 5, id 6 (North)
    for k in range(len(domes_def) - 1):
        d_lower = domes_def[k]
        d_upper = domes_def[k + 1]
        grid_lower = tier_grids[k]
        grid_upper = tier_grids[k + 1]

        # The shared beam line is at d_lower['y1'] == d_upper['y0']
        # Connect upper edge of grid_lower (j = ny_per_dome) to lower edge of grid_upper (j = 0)
        for i in range(nx_d):
            # Outer riser wall
            bm_domes.faces.new((
                grid_lower[0][(i, ny_per_dome)],
                grid_upper[0][(i, 0)],
                grid_upper[0][(i + 1, 0)],
                grid_lower[0][(i + 1, ny_per_dome)]
            ))
            # Inner riser ceiling
            bm_domes.faces.new((
                grid_lower[1][(i, ny_per_dome)],
                grid_lower[1][(i + 1, ny_per_dome)],
                grid_upper[1][(i + 1, 0)],
                grid_upper[1][(i, 0)]
            ))

    # Exterior End Rim Caps at South end (y0 of Bay 1) and North end (y1 of Bay 6)
    for i in range(nx_d):
        # South end rim
        bm_domes.faces.new((
            tier_grids[0][0][(i, 0)],
            tier_grids[0][1][(i, 0)],
            tier_grids[0][1][(i + 1, 0)],
            tier_grids[0][0][(i + 1, 0)]
        ))
        # North arrival end rim
        bm_domes.faces.new((
            tier_grids[-1][0][(i, ny_per_dome)],
            tier_grids[-1][0][(i + 1, ny_per_dome)],
            tier_grids[-1][1][(i + 1, ny_per_dome)],
            tier_grids[-1][1][(i, ny_per_dome)]
        ))

    bmesh.ops.recalc_face_normals(bm_domes, faces=bm_domes.faces)
    mesh_domes = bpy.data.meshes.new("Mandapam_6_Vaulted_Domes_Roof")
    bm_domes.to_mesh(mesh_domes)
    bm_domes.free()
    if mat_roof:
        mesh_domes.materials.append(mat_roof)
    obj_domes = bpy.data.objects.new("Mandapam_6_Vaulted_Domes_Roof", mesh_domes)
    col.objects.link(obj_domes)
    print("[Dome Rebuild] Created Mandapam_6_Vaulted_Domes_Roof (Stepped Horizontal Vaults Ascending Front-to-Back)")

    # -------------------------------------------------------------
    # 5. Solid Lateral Clerestory Walls on East & West Sides (X = +/- 25.25m)
    # "when the domes were raised the side it is open on top fix that also"
    # Extends continuously from side roof deck level (Z = 7.40m) up to the curved
    # barrel vault ceiling for ALL 6 bays, with vertical step risers connecting
    # each ascending tier. Completely seals the sides with 0 daylight gaps!
    # -------------------------------------------------------------
    bm_ped = bmesh.new()
    uv_ped = bm_ped.loops.layers.uv.new("UVMap")
    t_ped = 0.80 # 80cm solid megalithic wall thickness bridging roof junction
    z_side_floor = 8.98 # Flat side roof deck level aligned flush with architraves

    for x_center, sign_side in [(-25.25, -1.0), (25.25, 1.0)]:
        x_in = x_center + sign_side * (-t_ped / 2.0)
        x_out = x_center + sign_side * (t_ped / 2.0)

        prev_top_in = None
        prev_top_out = None

        for k, d in enumerate(domes_def):
            y0, y1 = d["y0"], d["y1"]
            yc = (y0 + y1) / 2.0
            ry = (y1 - y0) / 2.0
            rise = d["rise"]
            zb = d["z_base"]

            n_py = 20
            yp_pts = np.linspace(y0, y1, n_py + 1)

            v_in_bot, v_in_top = [], []
            v_out_bot, v_out_top = [], []

            for j in range(n_py + 1):
                yj = yp_pts[j]
                uy = min(abs(yj - yc) / ry, 1.0)
                zj_arch = zb + rise * (1.0 - uy**2)

                # Extends all the way down to z_side_floor = 8.98m!
                v_in_bot.append(bm_ped.verts.new((x_in, yj, z_side_floor)))
                v_in_top.append(bm_ped.verts.new((x_in, yj, zj_arch)))
                v_out_bot.append(bm_ped.verts.new((x_out, yj, z_side_floor)))
                v_out_top.append(bm_ped.verts.new((x_out, yj, zj_arch)))

            # If there is a vertical step riser from previous bay at y0, seal it!
            if prev_top_in is not None and prev_top_out is not None:
                # Vertical step between adjacent bays
                if sign_side > 0:
                    bm_ped.faces.new((prev_top_out, v_out_top[0], v_in_top[0], prev_top_in))
                else:
                    bm_ped.faces.new((prev_top_in, v_in_top[0], v_out_top[0], prev_top_out))

            # Faces for this bay
            for j in range(n_py):
                # Outer face (facing outside towards East/West)
                if sign_side > 0:
                    bm_ped.faces.new((v_out_bot[j], v_out_top[j], v_out_top[j + 1], v_out_bot[j + 1]))
                    bm_ped.faces.new((v_in_bot[j], v_in_bot[j + 1], v_in_top[j + 1], v_in_top[j]))
                else:
                    bm_ped.faces.new((v_out_bot[j], v_out_bot[j + 1], v_out_top[j + 1], v_out_top[j]))
                    bm_ped.faces.new((v_in_bot[j], v_in_top[j], v_in_top[j + 1], v_in_bot[j + 1]))

                # Top coping face connecting inner and outer top vertices
                if sign_side > 0:
                    bm_ped.faces.new((v_in_top[j], v_in_top[j + 1], v_out_top[j + 1], v_out_top[j]))
                else:
                    bm_ped.faces.new((v_out_top[j], v_out_top[j + 1], v_in_top[j + 1], v_in_top[j]))

                # Bottom face sealing against side roof deck
                bm_ped.faces.new((v_in_bot[j], v_out_bot[j], v_out_bot[j + 1], v_in_bot[j + 1]))

            prev_top_in = v_in_top[-1]
            prev_top_out = v_out_top[-1]

    # South Gable End Riser Wall at Y = -25.0m sealing Bay 1 base (Z = 9.50m) down to roof deck (Z = 8.98m)
    # Spans X in [-25.5, +25.5m]
    s_end_v = [
        bm_ped.verts.new((-25.5, -25.0, 8.98)),
        bm_ped.verts.new(( 25.5, -25.0, 8.98)),
        bm_ped.verts.new(( 25.5, -25.0, 9.50)),
        bm_ped.verts.new((-25.5, -25.0, 9.50)),
    ]
    bm_ped.faces.new((s_end_v[0], s_end_v[1], s_end_v[2], s_end_v[3]))

    bmesh.ops.recalc_face_normals(bm_ped, faces=bm_ped.faces)
    mesh_ped = bpy.data.meshes.new("Mandapam_Lateral_Arch_Pediments")
    bm_ped.to_mesh(mesh_ped)
    bm_ped.free()
    if mat_granite:
        mesh_ped.materials.append(mat_granite)
    obj_ped = bpy.data.objects.new("Mandapam_Lateral_Arch_Pediments", mesh_ped)
    col.objects.link(obj_ped)
    print("[Dome Rebuild] Created Mandapam_Lateral_Arch_Pediments")

    # -------------------------------------------------------------
    # 6. Exterior Monumental Dravidian Stone Fascia / Architrave
    # Covers front at Y = 59.0 and back at Y = -25.0 (Zero black beams visible outside)
    # Perfectly aligned with:
    #   - Ceiling underside at Z = 8.38m
    #   - Flat roof deck at Z = 8.98m
    #   - Parapet coping top at Z = 9.78m
    # -------------------------------------------------------------
    bm_ext_fascia = bmesh.new()
    uv_ef = bm_ext_fascia.loops.layers.uv.new("UVMap")
    fascia_configs = [
        {"y": 59.0, "sign": 1.0, "z0": 8.38, "z1": 8.98, "pz": 9.78},
        {"y": -25.0, "sign": -1.0, "z0": 8.38, "z1": 8.98, "pz": 9.78},
    ]
    for fc in fascia_configs:
        ey = fc["y"]
        sign_y = fc["sign"]
        z0, z1, pz = fc["z0"], fc["z1"], fc["pz"]
        fy0 = ey - sign_y * 0.40
        fy1 = ey + sign_y * 0.40
        y_min = min(fy0, fy1)
        y_max = max(fy0, fy1)

        # Architrave Fascia Beam: Z in [8.38, 8.98m]
        fv = [
            bm_ext_fascia.verts.new((-44.2, y_min, z0)),
            bm_ext_fascia.verts.new(( 44.2, y_min, z0)),
            bm_ext_fascia.verts.new(( 44.2, y_max, z0)),
            bm_ext_fascia.verts.new((-44.2, y_max, z0)),
            bm_ext_fascia.verts.new((-44.2, y_min, z1)),
            bm_ext_fascia.verts.new(( 44.2, y_min, z1)),
            bm_ext_fascia.verts.new(( 44.2, y_max, z1)),
            bm_ext_fascia.verts.new((-44.2, y_max, z1)),
        ]
        bm_ext_fascia.faces.new((fv[0], fv[1], fv[2], fv[3]))
        bm_ext_fascia.faces.new((fv[4], fv[7], fv[6], fv[5]))
        bm_ext_fascia.faces.new((fv[0], fv[4], fv[5], fv[1]))
        bm_ext_fascia.faces.new((fv[1], fv[5], fv[6], fv[2]))
        bm_ext_fascia.faces.new((fv[2], fv[6], fv[7], fv[3]))
        bm_ext_fascia.faces.new((fv[3], fv[7], fv[4], fv[0]))

        # Parapet Fascia above Roof Deck: Z in [8.98, 9.78m]
        pv = [
            bm_ext_fascia.verts.new((-44.2, y_min, z1)),
            bm_ext_fascia.verts.new(( 44.2, y_min, z1)),
            bm_ext_fascia.verts.new(( 44.2, y_max, z1)),
            bm_ext_fascia.verts.new((-44.2, y_max, z1)),
            bm_ext_fascia.verts.new((-44.2, y_min, pz)),
            bm_ext_fascia.verts.new(( 44.2, y_min, pz)),
            bm_ext_fascia.verts.new(( 44.2, y_max, pz)),
            bm_ext_fascia.verts.new((-44.2, y_max, pz)),
        ]
        bm_ext_fascia.faces.new((pv[0], pv[1], pv[2], pv[3]))
        bm_ext_fascia.faces.new((pv[4], pv[7], pv[6], pv[5]))
        bm_ext_fascia.faces.new((pv[0], pv[4], pv[5], pv[1]))
        bm_ext_fascia.faces.new((pv[1], pv[5], pv[6], pv[2]))
        bm_ext_fascia.faces.new((pv[2], pv[6], pv[7], pv[3]))
        bm_ext_fascia.faces.new((pv[3], pv[7], pv[4], pv[0]))
    bmesh.ops.recalc_face_normals(bm_ext_fascia, faces=bm_ext_fascia.faces)
    mesh_ef = bpy.data.meshes.new("Mandapam_Exterior_Front_Fascia")
    bm_ext_fascia.to_mesh(mesh_ef)
    bm_ext_fascia.free()
    if mat_granite:
        mesh_ef.materials.append(mat_granite)
    obj_ef = bpy.data.objects.new("Mandapam_Exterior_Front_Fascia", mesh_ef)
    col.objects.link(obj_ef)
    print("[Dome Rebuild] Created Mandapam_Exterior_Front_Fascia (Granite frieze enclosing exterior beams)")

    # -------------------------------------------------------------
    # 7. BIGGEST DOME (Bay 2): ONE MASTER GOLDEN LINGA & NO GOPURAM
    # Position: Exact Apex of Bay 2 at (X = 0.0, Y = -3.0, Z = 16.80m)
    # Lotus Plinth + Sculpted 24K Temple Gold Linga (Height 2.40m, Apex Z = 19.20m)
    # -------------------------------------------------------------
    bm_master_linga = bmesh.new()
    uv_master = bm_master_linga.loops.layers.uv.new("UVMap")
    create_linga_geometry(
        bm_master_linga, uv_master,
        cx=0.0, cy=-3.0, base_z=16.80,
        total_height=2.40, r_body=0.45, n_circ=20
    )
    bmesh.ops.recalc_face_normals(bm_master_linga, faces=bm_master_linga.faces)
    mesh_master_linga = bpy.data.meshes.new("Mandapam_Master_Golden_Linga")
    bm_master_linga.to_mesh(mesh_master_linga)
    bm_master_linga.free()
    if mat_gold:
        mesh_master_linga.materials.append(mat_gold)
    obj_master_linga = bpy.data.objects.new("Mandapam_Master_Golden_Linga", mesh_master_linga)
    col.objects.link(obj_master_linga)
    print("[Dome Rebuild] Created Mandapam_Master_Golden_Linga on Bay 2 apex (Z = 16.80m, NO GOPURAM)")

    # -------------------------------------------------------------
    # 8. LOWER TWO DOMES (Bay 6 & Bay 5): 4 AND 4 GOLDEN LINGAS IN ZIGZAG
    # Matching exact Isha reference photo:
    #   Bay 6 (Front Canopy): Ridge at Yc = 52.0m, Apex Z = 10.28m
    #     4 golden lingas at X = -15.0, -5.0, 5.0, 15.0
    #   Bay 5 (Upper Mandapam): Ridge at Yc = 38.0m, Apex Z = 11.40m
    #     4 golden lingas at X = -20.0, -10.0, 0.0, 10.0 (Staggered / Zigzag with Bay 6)
    # -------------------------------------------------------------
    bm_zigzag = bmesh.new()
    uv_zigzag = bm_zigzag.loops.layers.uv.new("UVMap")

    # Bay 6 (Front Tier): 4 Golden Lingas along horizontal ridge
    bay6_xs = [-15.0, -5.0, 5.0, 15.0]
    for lx in bay6_xs:
        create_linga_geometry(
            bm_zigzag, uv_zigzag,
            cx=lx, cy=52.0, base_z=10.28,
            total_height=1.25, r_body=0.26, n_circ=16
        )

    # Bay 5 (Second Tier): 4 Golden Lingas along horizontal ridge in staggered zigzag
    bay5_xs = [-20.0, -10.0, 0.0, 10.0]
    for lx in bay5_xs:
        create_linga_geometry(
            bm_zigzag, uv_zigzag,
            cx=lx, cy=38.0, base_z=11.40,
            total_height=1.25, r_body=0.26, n_circ=16
        )

    bmesh.ops.recalc_face_normals(bm_zigzag, faces=bm_zigzag.faces)
    mesh_zigzag = bpy.data.meshes.new("Mandapam_Zigzag_Golden_Lingas")
    bm_zigzag.to_mesh(mesh_zigzag)
    bm_zigzag.free()
    if mat_gold:
        mesh_zigzag.materials.append(mat_gold)
    obj_zigzag = bpy.data.objects.new("Mandapam_Zigzag_Golden_Lingas", mesh_zigzag)
    col.objects.link(obj_zigzag)
    print("[Dome Rebuild] Created Mandapam_Zigzag_Golden_Lingas (4 on Bay 6, 4 on Bay 5 in staggered zigzag pattern)")

    # -------------------------------------------------------------
    # 9. Side Mandapam Roofs: Terracotta Ceilings Inside & Granite Roof Deck Outside
    # "the mandapam inner roofing should be in the terracota texure"
    # A. Mandapam_Side_Ceilings: Underside ceiling (Z = 8.38m) in Terracotta Tile texture (Mat_Suryakund_Roof)
    #    Flush with pillar capitals and architrave soffit across the entire mandapam
    # B. Mandapam_Side_Roofs_Exterior: Top flat deck (Z = 8.98m) & Parapets (Z = 9.78m) in Granite
    #    Flush with architrave top and front fascia across outer steps and aisles
    # -------------------------------------------------------------
    bm_ceil = bmesh.new()
    uv_ceil = bm_ceil.loops.layers.uv.new("UVMap")
    for x_min, x_max in [(-44.2, -24.8), (24.8, 44.2)]:
        nx_c = 12
        ny_c = 28
        xs = np.linspace(x_min, x_max, nx_c + 1)
        ys = np.linspace(-25.0, 59.0, ny_c + 1)
        c_verts = {}
        for j in range(ny_c + 1):
            for i in range(nx_c + 1):
                c_verts[(i, j)] = bm_ceil.verts.new((xs[i], ys[j], 8.38))
        for j in range(ny_c):
            for i in range(nx_c):
                f = bm_ceil.faces.new((
                    c_verts[(i, j)],
                    c_verts[(i, j + 1)],
                    c_verts[(i + 1, j + 1)],
                    c_verts[(i + 1, j)]
                ))
                f.loops[0][uv_ceil].uv = (i * 0.35, j * 0.35)
                f.loops[1][uv_ceil].uv = (i * 0.35, (j + 1) * 0.35)
                f.loops[2][uv_ceil].uv = ((i + 1) * 0.35, (j + 1) * 0.35)
                f.loops[3][uv_ceil].uv = ((i + 1) * 0.35, j * 0.35)

    bmesh.ops.recalc_face_normals(bm_ceil, faces=bm_ceil.faces)
    mesh_ceil = bpy.data.meshes.new("Mandapam_Side_Ceilings")
    bm_ceil.to_mesh(mesh_ceil)
    bm_ceil.free()
    if mat_roof:
        mesh_ceil.materials.append(mat_roof)
    obj_ceil = bpy.data.objects.new("Mandapam_Side_Ceilings", mesh_ceil)
    col.objects.link(obj_ceil)
    print("[Dome Rebuild] Created Mandapam_Side_Ceilings (Terracotta tile texture on mandapam inner ceilings at Z = 8.38m)")

    # Exterior Flat Roof Deck & Outer Stone Parapet Walls (Mat_SarpaVasal_Granite)
    bm_side_ext = bmesh.new()
    uv_side_ext = bm_side_ext.loops.layers.uv.new("UVMap")
    for x_min, x_max, sign_parapet in [(-44.2, -24.8, -1.0), (24.8, 44.2, 1.0)]:
        sv = [
            bm_side_ext.verts.new((x_min, -25.0, 8.98)),
            bm_side_ext.verts.new((x_max, -25.0, 8.98)),
            bm_side_ext.verts.new((x_max,  59.0, 8.98)),
            bm_side_ext.verts.new((x_min,  59.0, 8.98)),
        ]
        bm_side_ext.faces.new((sv[0], sv[3], sv[2], sv[1]))

        if sign_parapet < 0:
            pv = [
                bm_side_ext.verts.new((x_min - 0.35, -25.0, 8.38)),
                bm_side_ext.verts.new((x_min,        -25.0, 8.38)),
                bm_side_ext.verts.new((x_min,         59.0, 8.38)),
                bm_side_ext.verts.new((x_min - 0.35,  59.0, 8.38)),
                bm_side_ext.verts.new((x_min - 0.35, -25.0, 9.78)),
                bm_side_ext.verts.new((x_min,        -25.0, 9.78)),
                bm_side_ext.verts.new((x_min,         59.0, 9.78)),
                bm_side_ext.verts.new((x_min - 0.35,  59.0, 9.78)),
            ]
        else:
            pv = [
                bm_side_ext.verts.new((x_max,        -25.0, 8.38)),
                bm_side_ext.verts.new((x_max + 0.35, -25.0, 8.38)),
                bm_side_ext.verts.new((x_max + 0.35,  59.0, 8.38)),
                bm_side_ext.verts.new((x_max,         59.0, 8.38)),
                bm_side_ext.verts.new((x_max,        -25.0, 9.78)),
                bm_side_ext.verts.new((x_max + 0.35, -25.0, 9.78)),
                bm_side_ext.verts.new((x_max + 0.35,  59.0, 9.78)),
                bm_side_ext.verts.new((x_max + 0.35,  59.0, 9.78)),
            ]
        bm_side_ext.faces.new((pv[0], pv[1], pv[2], pv[3]))
        bm_side_ext.faces.new((pv[4], pv[7], pv[6], pv[5]))
        bm_side_ext.faces.new((pv[0], pv[4], pv[5], pv[1]))
        bm_side_ext.faces.new((pv[1], pv[5], pv[6], pv[2]))
        bm_side_ext.faces.new((pv[2], pv[6], pv[7], pv[3]))
        bm_side_ext.faces.new((pv[3], pv[7], pv[4], pv[0]))

    bmesh.ops.recalc_face_normals(bm_side_ext, faces=bm_side_ext.faces)
    mesh_side_ext = bpy.data.meshes.new("Mandapam_Side_Roofs_Exterior")
    bm_side_ext.to_mesh(mesh_side_ext)
    bm_side_ext.free()
    if mat_granite:
        mesh_side_ext.materials.append(mat_granite)
    obj_side_ext = bpy.data.objects.new("Mandapam_Side_Roofs_Exterior", mesh_side_ext)
    col.objects.link(obj_side_ext)
    print("[Dome Rebuild] Created Mandapam_Side_Roofs_Exterior (Flat Stone Decks & Parapets)")

    # -------------------------------------------------------------
    # 10. AUTHENTIC USER 3D SUN MODEL MESH INTEGRATION
    # -------------------------------------------------------------
    old_sun = bpy.data.objects.get("Suryakund_Sun_Sculpture")
    if old_sun:
        bpy.data.objects.remove(old_sun, do_unlink=True)

    sun_obj = None
    if os.path.exists(blend_bak_path):
        print(f"[Dome Rebuild] Appending user's Plane from {blend_bak_path}...")
        try:
            with bpy.data.libraries.load(blend_bak_path) as (data_from, data_to):
                if "Plane" in data_from.objects:
                    data_to.objects = ["Plane"]
            appended_plane = bpy.data.objects.get("Plane")
            if appended_plane:
                appended_plane.hide_viewport = False
                appended_plane.hide_render = False
                appended_plane.hide_set(False)
                col.objects.link(appended_plane)
                bpy.context.view_layer.objects.active = appended_plane
                appended_plane.select_set(True)

                s_scale_x = appended_plane.scale.x
                s_scale_y = appended_plane.scale.y
                s_scale_z = appended_plane.scale.z

                for m in list(appended_plane.modifiers):
                    try:
                        bpy.ops.object.modifier_apply(modifier=m.name)
                    except Exception as me_err:
                        print(f"[Dome Rebuild] Warning applying {m.name}: {me_err}")

                img_sun_path = "/home/mullainathan/Downloads/855973520_1795521495964691.jpg-Photoroom.png"
                img_sun = bpy.data.images.get("855973520_1795521495964691.jpg-Photoroom.png")
                if not img_sun and os.path.exists(img_sun_path):
                    img_sun = bpy.data.images.load(img_sun_path, check_existing=True)

                if img_sun:
                    w_px, h_px = img_sun.size[0], img_sun.size[1]
                    pix = list(img_sun.pixels)

                    bm_sun = bmesh.new()
                    bm_sun.from_mesh(appended_plane.data)
                    uv_sun = bm_sun.loops.layers.uv.active

                    verts_to_delete = []
                    for v in bm_sun.verts:
                        u_vals = [l[uv_sun].uv.x for l in v.link_loops]
                        v_vals = [l[uv_sun].uv.y for l in v.link_loops]
                        if u_vals and v_vals:
                            u_avg = max(0.0, min(1.0, sum(u_vals) / len(u_vals)))
                            v_avg = max(0.0, min(1.0, sum(v_vals) / len(v_vals)))
                            px = int(u_avg * (w_px - 1))
                            py = int(v_avg * (h_px - 1))
                            idx = (py * w_px + px) * 4 + 3
                            if pix[idx] < 0.15:
                                verts_to_delete.append(v)
                        else:
                            verts_to_delete.append(v)

                    print(f"[Dome Rebuild] Cropping alpha: Deleting {len(verts_to_delete)} verts, keeping {len(bm_sun.verts) - len(verts_to_delete)}")
                    bmesh.ops.delete(bm_sun, geom=verts_to_delete, context="VERTS")

                    # Center & Scale to 6.10m diameter (20ft)
                    xs = [v.co.x for v in bm_sun.verts]
                    ys = [v.co.y for v in bm_sun.verts]
                    cx_raw = (min(xs) + max(xs)) / 2.0
                    cy_raw = (min(ys) + max(ys)) / 2.0
                    span_x = (max(xs) - min(xs)) * s_scale_x
                    span_y = (max(ys) - min(ys)) * s_scale_y
                    scale_factor = 6.10 / max(span_x, span_y)

                    # In the original 2D Plane:
                    # v.co.x is horizontal (-X to +X)
                    # v.co.y is image vertical (-Y to +Y)
                    # v.co.z is displacement depth
                    # To make the Sun sculpture stand completely STRAIGHT and VERTICAL facing +Y:
                    # - Horizontal remains X: x_w = (v.co.x - cx_raw) * s_scale_x * scale_factor
                    # - Vertical height becomes Z: z_w = (v.co.y - cy_raw) * s_scale_y * scale_factor
                    # - Relief / depth along Y: y_front = (v.co.z * s_scale_z) * 0.35
                    # Front face is at y_front facing +Y towards grand descent stairs!
                    # Back face is at -t_back facing -Y!
                    t_back = 0.15 # 15cm solid medallion depth
                    for v in bm_sun.verts:
                        x_w = (v.co.x - cx_raw) * s_scale_x * scale_factor
                        z_w = (v.co.y - cy_raw) * s_scale_y * scale_factor
                        y_w = (v.co.z * s_scale_z) * 0.35
                        v.co = Vector((x_w, y_w, z_w))

                    boundary_edges = [e for e in bm_sun.edges if e.is_boundary]
                    front_verts = list(bm_sun.verts)
                    vert_map_back = {}
                    for v in front_verts:
                        vb = bm_sun.verts.new((v.co.x, -t_back, v.co.z))
                        vert_map_back[v] = vb

                    for f in list(bm_sun.faces):
                        back_f_verts = [vert_map_back[v] for v in reversed(f.verts)]
                        fb = bm_sun.faces.new(back_f_verts)
                        if uv_sun:
                            for idx, l in enumerate(fb.loops):
                                l[uv_sun].uv = f.loops[len(f.loops) - 1 - idx][uv_sun].uv

                    for e in boundary_edges:
                        v0, v1 = e.verts[0], e.verts[1]
                        f = e.link_faces[0]
                        f_verts = list(f.verts)
                        idx0 = f_verts.index(v0)
                        idx1 = f_verts.index(v1)
                        is_forward = ((idx0 + 1) % len(f_verts) == idx1)
                        if is_forward:
                            bm_sun.faces.new((v1, v0, vert_map_back[v0], vert_map_back[v1]))
                        else:
                            bm_sun.faces.new((v0, v1, vert_map_back[v1], vert_map_back[v0]))

                    # Assign two materials:
                    # Slot 0: Mat_Suryakund_Sun (radiant 24K temple gold / brass outer rays, r > 1.35m)
                    # Slot 1: Mat_Suryakund_CopperBasin (consecrated sacred copper center medallion, r <= 1.35m)
                    r_medallion = 1.35
                    for f in bm_sun.faces:
                        fc_x = sum(v.co.x for v in f.verts) / len(f.verts)
                        fc_z = sum(v.co.z for v in f.verts) / len(f.verts)
                        r_dist = math.sqrt(fc_x**2 + fc_z**2)
                        if r_dist <= r_medallion:
                            f.material_index = 1
                        else:
                            f.material_index = 0

                    bmesh.ops.recalc_face_normals(bm_sun, faces=bm_sun.faces)
                    bm_sun.to_mesh(appended_plane.data)
                    bm_sun.free()

                    appended_plane.name = "Suryakund_Sun_Sculpture"
                    appended_plane.scale = Vector((1.0, 1.0, 1.0))
                    appended_plane.location = Vector((0.0, -3.0, 7.80))
                    appended_plane.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
                    appended_plane.hide_viewport = False
                    appended_plane.hide_render = False
                    appended_plane.hide_set(False)

                    appended_plane.data.materials.clear()
                    if mat_brass:
                        appended_plane.data.materials.append(mat_brass)
                    if mat_copper:
                        appended_plane.data.materials.append(mat_copper)

                    sun_obj = appended_plane
                    print(f"[Dome Rebuild] Successfully built Watertight 3D Straight Sun Sculpture with Copper Center: {len(sun_obj.data.vertices)} verts, {len(sun_obj.data.polygons)} faces")
        except Exception as sun_err:
            print(f"[Dome Rebuild] Error extracting user sun mesh: {sun_err}")

    if not sun_obj:
        print("[Dome Rebuild] Warning: using procedural sun sculpture fallback")
        bm_fallback = bmesh.new()
        uv_fb = bm_fallback.loops.layers.uv.new("UVMap")
        r_sun = 3.05
        n_fb = 32
        v_c = bm_fallback.verts.new((0.0, 0.0, 0.0))
        rim = [bm_fallback.verts.new((r_sun * math.cos(2*math.pi*s/n_fb), 0.0, r_sun * math.sin(2*math.pi*s/n_fb))) for s in range(n_fb)]
        for s in range(n_fb):
            f = bm_fallback.faces.new((v_c, rim[(s + 1) % n_fb], rim[s]))
            f.material_index = 0
            f.loops[0][uv_fb].uv = (0.5, 0.5)
            f.loops[1][uv_fb].uv = (0.5 + 0.5*math.cos(2*math.pi*(s+1)/n_fb), 0.5 + 0.5*math.sin(2*math.pi*(s+1)/n_fb))
            f.loops[2][uv_fb].uv = (0.5 + 0.5*math.cos(2*math.pi*s/n_fb), 0.5 + 0.5*math.sin(2*math.pi*s/n_fb))
        bmesh.ops.recalc_face_normals(bm_fallback, faces=bm_fallback.faces)
        me_fb = bpy.data.meshes.new("Suryakund_Sun_Sculpture")
        bm_fallback.to_mesh(me_fb)
        bm_fallback.free()
        if mat_brass:
            me_fb.materials.append(mat_brass)
        if mat_copper:
            me_fb.materials.append(mat_copper)
        sun_obj = bpy.data.objects.new("Suryakund_Sun_Sculpture", me_fb)
        sun_obj.location = Vector((0.0, -3.0, 7.80))
        sun_obj.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
        col.objects.link(sun_obj)

    sun_obj.hide_viewport = False
    sun_obj.hide_render = False
    sun_obj.hide_set(False)

    # -------------------------------------------------------------
    # 11. Sculpted 3D King Cobra (Naga) Mounted on Central Pillar
    # User feedback: "and the naga piller everything id correct except the naga is missing"
    # Central pillar is at X = 0.0, Y = 14.40, with base at Z = 2.650m resting
    # squarely on Suryakund_Naga_Monolith.
    # We import the high-poly 3D sculpted Naga (assets/naga_pillar.glb, 117,937 verts),
    # scale it 2.4x (3.24m tall x 1.58m wide), and seat its base squarely at Z = 2.650m
    # touching the monolith top surface, mounted on the front face of the central pillar
    # facing +Y towards descending visitors!
    # -------------------------------------------------------------
    naga_obj = bpy.data.objects.get("Suryakund_Naga_Monolith")
    if naga_obj:
        for v in naga_obj.data.vertices:
            # North face lower vertices
            if v.co.y >= 15.3 and v.co.z <= -0.90:
                v.co.z = -3.20
            # South face lower vertices
            elif v.co.y <= 13.3 and v.co.z <= -2.50:
                v.co.z = -3.20
            # East & West side lower vertices
            elif abs(v.co.x) >= 1.25 and v.co.z <= -0.90:
                v.co.z = -3.20

        # Move bottom capping faces down to -3.20m
        for p in naga_obj.data.polygons:
            if p.normal.z < -0.5:
                for vi in p.vertices:
                    naga_obj.data.vertices[vi].co.z = -3.20

        naga_obj.data.update()
        print(f"[Dome Rebuild] Naga Monolith seated firmly into steps: Z in [-3.20, 2.65m] (zero daylight gap on all 4 sides)")

    # Clean up redundant old pedestal
    old_ped = bpy.data.objects.get("Suryakund_Naga_Base_Pedestal")
    if old_ped:
        bpy.data.objects.remove(old_ped, do_unlink=True)

    pillar_obj = bpy.data.objects.get("Suryakund_Central_Pillar")
    if pillar_obj:
        pillar_obj.location.z = 2.650
        if mat_granite:
            pillar_obj.data.materials.clear()
            pillar_obj.data.materials.append(mat_granite)
        print(f"[Dome Rebuild] Central Pillar base at Z = {pillar_obj.location.z:.3f}m touching Naga rock top")

    # Import and mount the 3D sculpted King Cobra (Naga)
    naga_glb_path = "/home/mullainathan/Games/IshaGodot/assets/naga_pillar.glb"
    if os.path.exists(naga_glb_path):
        bpy.ops.import_scene.gltf(filepath=naga_glb_path)
        imported_naga = bpy.data.objects.get("naga")
        if imported_naga:
            imported_naga.name = "Suryakund_Pillar_Naga_Sculpture"
            col.objects.link(imported_naga)
            if imported_naga.name in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.unlink(imported_naga)

            s_naga = 2.4
            imported_naga.scale = Vector((s_naga, s_naga, s_naga))
            imported_naga.location = Vector((0.0, 14.85, 2.650))
            imported_naga.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')

            if mat_granite:
                imported_naga.data.materials.clear()
                imported_naga.data.materials.append(mat_granite)

            imported_naga.hide_viewport = False
            imported_naga.hide_render = False
            imported_naga.hide_set(False)
            print(f"[Dome Rebuild] Mounted 3D Sculpted Naga Sculpture: {len(imported_naga.data.vertices)} verts on central pillar at Z = {imported_naga.location.z:.3f}m")

    # -------------------------------------------------------------
    # 12. Proper Rectangular Blocks & Stepped 3-2-1 Cascade Stair Retaining Walls
    # User feedback: "and the block rockes in the line with the steps should end with 321 so that it looks finished and clean"
    # Covering full inner pool walls AND full inner stair side walls
    # with authentic 3 -> 2 -> 1 stepped blocks ending at the top of the grand stairs!
    # -------------------------------------------------------------
    bm_rocks = bmesh.new()
    uv_rocks = bm_rocks.loops.layers.uv.new("UVMap")

    def add_proper_rectangular_block(bm, uv, cx, cy, cz_bot, sx, sy, sz):
        dx = sx / 2.0
        dy = sy / 2.0
        x0, x1 = cx - dx, cx + dx
        y0, y1 = cy - dy, cy + dy
        z0, z1 = cz_bot, cz_bot + sz
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
        bm.faces.new((v[0], v[1], v[2], v[3]))
        bm.faces.new((v[4], v[7], v[6], v[5]))
        bm.faces.new((v[0], v[4], v[5], v[1]))
        bm.faces.new((v[1], v[5], v[6], v[2]))
        bm.faces.new((v[2], v[6], v[7], v[3]))
        bm.faces.new((v[3], v[7], v[4], v[0]))

    # A. Subterranean Pool Walls (Y in [-9.0, 6.0m], Z in [-6.10, 3.50m])
    n_courses = 8
    course_h = 9.60 / n_courses
    block_sz = 1.18

    for c_idx in range(n_courses):
        cz_bot = -6.10 + c_idx * course_h
        stagger = 1.40 if (c_idx % 2 == 1) else 0.0

        n_w_blocks = 6
        for b_idx in range(n_w_blocks):
            by = -9.0 + b_idx * 3.0 + (stagger * 0.40)
            by = max(-9.0, min(6.0, by))
            add_proper_rectangular_block(bm_rocks, uv_rocks, -23.60, by, cz_bot, 0.80, 2.96, block_sz)

        for b_idx in range(n_w_blocks):
            by = -9.0 + b_idx * 3.0 + (stagger * 0.40)
            by = max(-9.0, min(6.0, by))
            add_proper_rectangular_block(bm_rocks, uv_rocks, 23.60, by, cz_bot, 0.80, 2.96, block_sz)

        n_s_blocks = 16
        for b_idx in range(n_s_blocks):
            bx = -22.5 + b_idx * 3.0 + (stagger * 0.40)
            bx = max(-22.5, min(22.5, bx))
            add_proper_rectangular_block(bm_rocks, uv_rocks, bx, -10.10, cz_bot, 2.96, 0.80, block_sz)

    # B. Inner Stair Side Retaining Walls (Y in [6.0, 28.6m])
    # Main wall along West (X = -23.60m) and East (X = +23.60m)
    # Stacking megalithic rectangular rock blocks
    # From Y = 6.0m to Y = 22.0m: Full 7 courses from Z = -4.90m up to Z = 3.50m
    n_main_courses = 7
    main_course_h = 8.40 / n_main_courses
    n_main_blocks = 6

    for c_idx in range(n_main_courses):
        cz_bot = -4.90 + c_idx * main_course_h
        stagger = 1.33 if (c_idx % 2 == 1) else 0.0

        for b_idx in range(n_main_blocks):
            by = 6.0 + b_idx * 2.67 + 1.335 + (stagger * 0.35)
            by = max(6.0, min(22.0, by))
            add_proper_rectangular_block(bm_rocks, uv_rocks, -23.60, by, cz_bot, 0.80, 2.60, 1.18)
            add_proper_rectangular_block(bm_rocks, uv_rocks,  23.60, by, cz_bot, 0.80, 2.60, 1.18)

    # Clean Stepped 3 - 2 - 1 Cascade Termination where retaining wall meets upper stair landing (Y in [22.0, 28.6m]):
    # User feedback: "and the block rockes in the line with the steps should end with 321 so that it looks finished and clean"
    # Ground stair landing is at Z = 0.00m; upper mandapam platform is at Z = 3.50m.
    # Tier 3 (Y in [22.0, 24.2m], center Y = 23.1m): 3 blocks high (Z = 0.00 to 3.50m, 3 x 1.167m)
    # Tier 2 (Y in [24.2, 26.4m], center Y = 25.3m): 2 blocks high (Z = 0.00 to 2.34m, 2 x 1.167m)
    # Tier 1 (Y in [26.4, 28.6m], center Y = 27.5m): 1 block high  (Z = 0.00 to 1.17m, 1 x 1.167m)
    block_len = 2.15
    for x_side in [-23.60, 23.60]:
        # Sub-surface foundation blocks anchoring flush into the slope
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_side, 23.10, -1.18, 0.80, block_len, 1.18)
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_side, 25.30, -1.18, 0.80, block_len, 1.18)
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_side, 27.50, -1.18, 0.80, block_len, 1.18)

        # Tier 3: 3 blocks high
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_side, 23.10, 0.00, 0.80, block_len, 1.15)
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_side, 23.10, 1.17, 0.80, block_len, 1.15)
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_side, 23.10, 2.34, 0.80, block_len, 1.15)

        # Tier 2: 2 blocks high
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_side, 25.30, 0.00, 0.80, block_len, 1.15)
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_side, 25.30, 1.17, 0.80, block_len, 1.15)

        # Tier 1: 1 block high
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_side, 27.50, 0.00, 0.80, block_len, 1.15)

    # Top Coping Blocks along Pool Rim & Top Back Mandapam Edge (Z = 3.50m)
    for bx in np.linspace(-22.5, 22.5, 16):
        add_proper_rectangular_block(bm_rocks, uv_rocks, bx, -11.30, 3.50, 2.96, 1.45, 1.15)

    for by in np.linspace(-9.0, 1.8, 4):
        add_proper_rectangular_block(bm_rocks, uv_rocks, -24.50, by, 3.50, 1.45, 3.10, 1.15)
        add_proper_rectangular_block(bm_rocks, uv_rocks,  24.50, by, 3.50, 1.45, 3.10, 1.15)

    # Top Coping Blocks along Stair Retaining Wall Edges up to Y = 22.0m (Z = 3.50m)
    for by in np.linspace(6.0, 22.0, 6):
        add_proper_rectangular_block(bm_rocks, uv_rocks, -24.50, by, 3.50, 1.45, 2.60, 1.15)
        add_proper_rectangular_block(bm_rocks, uv_rocks,  24.50, by, 3.50, 1.45, 2.60, 1.15)

    # Stepped Coping Blocks over the 3 - 2 - 1 Cascade:
    for x_cop in [-24.50, 24.50]:
        # Coping over Tier 3 at Z = 3.50m
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_cop, 23.10, 3.50, 1.45, block_len, 0.50)
        # Coping over Tier 2 at Z = 2.34m
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_cop, 25.30, 2.34, 1.45, block_len, 0.50)
        # Coping over Tier 1 at Z = 1.17m
        add_proper_rectangular_block(bm_rocks, uv_rocks, x_cop, 27.50, 1.17, 1.45, block_len, 0.50)

    bmesh.ops.recalc_face_normals(bm_rocks, faces=bm_rocks.faces)
    mesh_rocks = bpy.data.meshes.new("Mandapam_Pool_Edge_Rock_Blocks")
    bm_rocks.to_mesh(mesh_rocks)
    bm_rocks.free()
    if mat_bright_rock:
        mesh_rocks.materials.append(mat_bright_rock)
    obj_rocks = bpy.data.objects.new("Mandapam_Pool_Edge_Rock_Blocks", mesh_rocks)
    col.objects.link(obj_rocks)
    print("[Dome Rebuild] Created full inner pool walls and rims of proper rectangular rock blocks with 3-2-1 stepped cascade")

    # -------------------------------------------------------------
    # 13. Volumetric 3D Cascading Waterfall with Ballistic Drop Physics
    # - Width: 14.0m wide (X in [-7.0, 7.0m])
    # - Thickness: 0.45m volumetric fluid body (Front Sheet, Back Sheet, Side Enclosures)
    # - Height: 8.81m drop from Z = 3.50m down to pool Z = -5.31m
    # - Trajectory: Pours over weir at Y = -9.55m (clearing South wall front at Y = -9.70m),
    #   arching forward into pool plunge at Y = -8.92m (100% unclipped, open air cascading torrent).
    # -------------------------------------------------------------
    bm_wf = bmesh.new()
    uv_wf = bm_wf.loops.layers.uv.new("UVMap")
    n_wfx = 28
    n_wfz = 36
    wf_xs = np.linspace(-7.0, 7.0, n_wfx + 1)
    wf_zs = np.linspace(3.50, -5.31, n_wfz + 1)
    t_cascade = 0.45

    def calc_wf_y(z, is_front=True):
        uz = (3.50 - z) / 8.81
        # Clear front face of south wall (-9.70m) by placing weir at -9.55m, arching forward to -8.92m
        y_front = -9.55 + 0.65 * (1.0 - math.exp(-3.5 * uz))
        return y_front if is_front else (y_front - t_cascade)

    front_grid = {}
    back_grid = {}

    for j in range(n_wfz + 1):
        z = wf_zs[j]
        uz = (3.50 - z) / 8.81
        yf = calc_wf_y(z, is_front=True)
        yb = calc_wf_y(z, is_front=False)

        for i in range(n_wfx + 1):
            x = wf_xs[i]
            ripple_f = 0.04 * math.sin(x * 1.8 + uz * 7.0)
            ripple_b = 0.03 * math.cos(x * 2.2 - uz * 6.0)

            front_grid[(i, j)] = bm_wf.verts.new((x, yf + ripple_f, z))
            back_grid[(i, j)] = bm_wf.verts.new((x, yb + ripple_b, z))

    # Front Cascading Torrent Faces
    for j in range(n_wfz):
        for i in range(n_wfx):
            f = bm_wf.faces.new((
                front_grid[(i, j)],
                front_grid[(i + 1, j)],
                front_grid[(i + 1, j + 1)],
                front_grid[(i, j + 1)]
            ))
            u0 = i / float(n_wfx)
            u1 = (i + 1) / float(n_wfx)
            v0 = j / float(n_wfz)
            v1 = (j + 1) / float(n_wfz)
            f.loops[0][uv_wf].uv = (u0, v0)
            f.loops[1][uv_wf].uv = (u1, v0)
            f.loops[2][uv_wf].uv = (u1, v1)
            f.loops[3][uv_wf].uv = (u0, v1)

    # Back Cascade Sheet
    for j in range(n_wfz):
        for i in range(n_wfx):
            f = bm_wf.faces.new((
                back_grid[(i, j)],
                back_grid[(i, j + 1)],
                back_grid[(i + 1, j + 1)],
                back_grid[(i + 1, j)]
            ))
            u0 = i / float(n_wfx)
            u1 = (i + 1) / float(n_wfx)
            v0 = j / float(n_wfz)
            v1 = (j + 1) / float(n_wfz)
            f.loops[0][uv_wf].uv = (u0, v0)
            f.loops[1][uv_wf].uv = (u0, v1)
            f.loops[2][uv_wf].uv = (u1, v1)
            f.loops[3][uv_wf].uv = (u1, v0)

    # Left & Right Enclosures
    for j in range(n_wfz):
        f_l = bm_wf.faces.new((
            back_grid[(0, j)],
            front_grid[(0, j)],
            front_grid[(0, j + 1)],
            back_grid[(0, j + 1)]
        ))
        v0 = j / float(n_wfz)
        v1 = (j + 1) / float(n_wfz)
        f_l.loops[0][uv_wf].uv = (0.0, v0)
        f_l.loops[1][uv_wf].uv = (0.3, v0)
        f_l.loops[2][uv_wf].uv = (0.3, v1)
        f_l.loops[3][uv_wf].uv = (0.0, v1)

        f_r = bm_wf.faces.new((
            front_grid[(n_wfx, j)],
            back_grid[(n_wfx, j)],
            back_grid[(n_wfx, j + 1)],
            front_grid[(n_wfx, j + 1)]
        ))
        f_r.loops[0][uv_wf].uv = (0.7, v0)
        f_r.loops[1][uv_wf].uv = (1.0, v0)
        f_r.loops[2][uv_wf].uv = (1.0, v1)
        f_r.loops[3][uv_wf].uv = (0.7, v1)

    # Top Weir Crest Cap (Z = 3.50m)
    for i in range(n_wfx):
        f_top = bm_wf.faces.new((
            back_grid[(i, 0)],
            back_grid[(i + 1, 0)],
            front_grid[(i + 1, 0)],
            front_grid[(i, 0)]
        ))
        f_top.loops[0][uv_wf].uv = (i / float(n_wfx), 0.0)
        f_top.loops[1][uv_wf].uv = ((i + 1) / float(n_wfx), 0.0)
        f_top.loops[2][uv_wf].uv = ((i + 1) / float(n_wfx), 0.1)
        f_top.loops[3][uv_wf].uv = (i / float(n_wfx), 0.1)

    bmesh.ops.recalc_face_normals(bm_wf, faces=bm_wf.faces)
    mesh_wf = bpy.data.meshes.new("Suryakund_Waterfall_Sheet")
    bm_wf.to_mesh(mesh_wf)
    bm_wf.free()
    mat_wf = bpy.data.materials.get("Mat_Suryakund_Waterfall")
    if not mat_wf:
        mat_wf = bpy.data.materials.new(name="Mat_Suryakund_Waterfall")
    mesh_wf.materials.append(mat_wf)
    obj_wf = bpy.data.objects.new("Suryakund_Waterfall_Sheet", mesh_wf)
    col.objects.link(obj_wf)
    print(f"[Dome Rebuild] Created thick 3D volumetric Suryakund_Waterfall_Sheet (14m wide x {t_cascade*100:.0f}cm thick)")

    # Foam splash base impact zone
    bm_f = bmesh.new()
    uv_f = bm_f.loops.layers.uv.new("UVMap")
    n_fseg = 32
    rx_f, ry_f = 8.50, 3.00
    c_f = bm_f.verts.new((0.0, -8.92, -5.26))
    f_rim = [bm_f.verts.new((rx_f * math.cos(2*math.pi*s/n_fseg), -8.92 + ry_f * math.sin(2*math.pi*s/n_fseg), -5.26)) for s in range(n_fseg)]
    for s in range(n_fseg):
        f = bm_f.faces.new((c_f, f_rim[s], f_rim[(s + 1) % n_fseg]))
        f.loops[0][uv_f].uv = (0.5, 0.5)
        f.loops[1][uv_f].uv = (0.5 + 0.5*math.cos(2*math.pi*s/n_fseg), 0.5 + 0.5*math.sin(2*math.pi*s/n_fseg))
        f.loops[2][uv_f].uv = (0.5 + 0.5*math.cos(2*math.pi*(s+1)/n_fseg), 0.5 + 0.5*math.sin(2*math.pi*(s+1)/n_fseg))

    bmesh.ops.recalc_face_normals(bm_f, faces=bm_f.faces)
    mesh_f = bpy.data.meshes.new("Suryakund_Waterfall_Foam")
    bm_f.to_mesh(mesh_f)
    bm_f.free()
    mat_f = bpy.data.materials.get("Mat_Suryakund_WaterfallFoam")
    if not mat_f:
        mat_f = bpy.data.materials.new(name="Mat_Suryakund_WaterfallFoam")
    mesh_f.materials.append(mat_f)
    obj_f = bpy.data.objects.new("Suryakund_Waterfall_Foam", mesh_f)
    col.objects.link(obj_f)
    print("[Dome Rebuild] Created wide elliptical Suryakund_Waterfall_Foam impact splash zone")

    # -------------------------------------------------------------
    # 14. Save Untitled.blend & Export GLB
    # -------------------------------------------------------------
    print(f"[Dome Rebuild] Saving updated scene to {blend_path}...")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(f"[Dome Rebuild] Exporting GLB to {glb_export_path}...")
    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.objects:
        obj.hide_viewport = False
        obj.hide_render = False
        obj.hide_set(False)
        obj.select_set(True)

    bpy.ops.export_scene.gltf(
        filepath=glb_export_path,
        use_selection=True,
        export_format='GLB',
        export_materials='EXPORT',
        export_apply=True
    )
    print(f"[Dome Rebuild] Successfully exported {glb_export_path}!")

if __name__ == "__main__":
    rebuild_suryakund_6domes_and_lingas()
