"""
Suryakund Base 3D Procedural Architectural Builder for Blender (Full-Width Steps v5)
Authentic Subterranean Temple Architecture matching Isha Foundation Suryakund:
- Full-width (48-meter wall-to-wall) grand stepped ghats spanning X = [-24.0, +24.0]
- Individual ashlar granite blocks with natural UV jitter across the 48m span
- Intermediate full-width resting landing (48m x 2m) and upper arrival terrace (48m x 5.5m)
- Subterranean megalithic ashlar granite retaining walls (up to Z = 9.6m) enclosing the space
- Sunken energized pool basin (40m x 12.5m) with copper floor & 5-tier immersion ghats
- Central ceremonial stone plinth with the 3 Rasalingas emerging from the water
- Translucent energized water volume with subtle wave ripple normal
- 20-foot brass & copper Sun sculpture suspended overhead at Z = 12.5m
- Dravidian monolithic granite pillars along terraces and perimeter corners
"""

import bpy
import bmesh
import math
import os
import numpy as np

def build_suryakund_base():
    print("=== Building Full-Width Suryakund Base (48m Wall-to-Wall Steps v5) ===")

    # Clean up stale/temporary objects
    stale_names = [
        "Inspect_Cam", "Inspect_Sun", "Plane",
        "Pillar_Entry_L", "Pillar_Entry_R",
        "Pillar_NW", "Pillar_NE", "Pillar_SW", "Pillar_SE",
        "Pillar_Mid_W", "Pillar_Mid_E"
    ]
    for name in stale_names:
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    # Create / get collection
    col_name = "Suryakund_Complex"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

    # Fetch materials
    mat_granite = bpy.data.materials.get("Mat_SarpaVasal_Granite")
    mat_copper = bpy.data.materials.get("Mat_Suryakund_Copper")

    # -------------------------------------------------------------
    # 1. Reflective Energized Water Material
    # -------------------------------------------------------------
    mat_water = bpy.data.materials.get("Mat_Suryakund_Water")
    if not mat_water:
        mat_water = bpy.data.materials.new(name="Mat_Suryakund_Water")
    mat_water.use_nodes = True
    nodes = mat_water.node_tree.nodes
    links = mat_water.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.012, 0.082, 0.092, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.020
    bsdf.inputs['Metallic'].default_value = 0.25
    bsdf.inputs['IOR'].default_value = 1.333
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.45
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.45

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 3.0
    noise.inputs['Detail'].default_value = 4.0
    noise.inputs['Roughness'].default_value = 0.40
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.020
    bump.inputs['Distance'].default_value = 0.04

    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # -------------------------------------------------------------
    # 2. 20-Foot Brass Sun Sculpture Material
    # -------------------------------------------------------------
    mat_sun = bpy.data.materials.get("Mat_Suryakund_Sun")
    if not mat_sun:
        mat_sun = bpy.data.materials.new(name="Mat_Suryakund_Sun")
    mat_sun.use_nodes = True
    s_nodes = mat_sun.node_tree.nodes
    s_links = mat_sun.node_tree.links
    s_nodes.clear()

    s_out = s_nodes.new(type='ShaderNodeOutputMaterial')
    s_bsdf = s_nodes.new(type='ShaderNodeBsdfPrincipled')
    s_tex = s_nodes.new(type='ShaderNodeTexImage')
    sun_img_path = "/home/mullainathan/Downloads/855973520_1795521495964691.jpg-Photoroom.png"
    if os.path.exists(sun_img_path):
        s_img = bpy.data.images.load(sun_img_path, check_existing=True)
        s_tex.image = s_img

    s_bsdf.inputs['Metallic'].default_value = 0.88
    s_bsdf.inputs['Roughness'].default_value = 0.20
    s_links.new(s_tex.outputs['Color'], s_bsdf.inputs['Base Color'])
    s_links.new(s_tex.outputs['Alpha'], s_bsdf.inputs['Alpha'])
    s_links.new(s_bsdf.outputs['BSDF'], s_out.inputs['Surface'])

    # -------------------------------------------------------------
    # 3. Pool Basin Floor (Copper-lined chamber: 40m x 12.5m, Z=0.0)
    # -------------------------------------------------------------
    old_floor = bpy.data.objects.get("Suryakund_Basin_Floor")
    if old_floor:
        bpy.data.objects.remove(old_floor, do_unlink=True)

    bm_floor = bmesh.new()
    uv_floor = bm_floor.loops.layers.uv.new("UVMap")
    
    nx, ny = 20, 8
    xs = np.linspace(-20.0, 20.0, nx + 1)
    ys = np.linspace(-6.25, 6.25, ny + 1)

    verts_floor = {}
    for j in range(ny + 1):
        for i in range(nx + 1):
            v = bm_floor.verts.new((xs[i], ys[j], 0.0))
            verts_floor[(i, j)] = v

    for j in range(ny):
        for i in range(nx):
            v00 = verts_floor[(i, j)]
            v10 = verts_floor[(i + 1, j)]
            v11 = verts_floor[(i + 1, j + 1)]
            v01 = verts_floor[(i, j + 1)]
            f = bm_floor.faces.new((v00, v10, v11, v01))
            f.loops[0][uv_floor].uv = (i * 0.5, j * 0.5)
            f.loops[1][uv_floor].uv = ((i + 1) * 0.5, j * 0.5)
            f.loops[2][uv_floor].uv = ((i + 1) * 0.5, (j + 1) * 0.5)
            f.loops[3][uv_floor].uv = (i * 0.5, (j + 1) * 0.5)

    mesh_floor = bpy.data.meshes.new("Suryakund_Basin_Floor")
    bm_floor.to_mesh(mesh_floor)
    bm_floor.free()
    if mat_copper:
        mesh_floor.materials.append(mat_copper)
    obj_floor = bpy.data.objects.new("Suryakund_Basin_Floor", mesh_floor)
    col.objects.link(obj_floor)

    # -------------------------------------------------------------
    # 4. Central Pedestal Plinth for 3 Rasalingas (18m x 3.6m, Z=0 to 1.15m)
    # -------------------------------------------------------------
    old_ped = bpy.data.objects.get("Suryakund_Central_Plinth")
    if old_ped:
        bpy.data.objects.remove(old_ped, do_unlink=True)

    bm_ped = bmesh.new()
    uv_ped = bm_ped.loops.layers.uv.new("UVMap")

    hx1, hy1, z1 = 9.0, 1.8, 0.60
    hx2, hy2, z2 = 8.6, 1.4, 1.15

    v_b = [
        bm_ped.verts.new((-hx1, -hy1, 0.0)),
        bm_ped.verts.new((hx1, -hy1, 0.0)),
        bm_ped.verts.new((hx1, hy1, 0.0)),
        bm_ped.verts.new((-hx1, hy1, 0.0)),
        bm_ped.verts.new((-hx1, -hy1, z1)),
        bm_ped.verts.new((hx1, -hy1, z1)),
        bm_ped.verts.new((hx1, hy1, z1)),
        bm_ped.verts.new((-hx1, hy1, z1)),
    ]
    bm_ped.faces.new((v_b[0], v_b[1], v_b[5], v_b[4]))
    bm_ped.faces.new((v_b[1], v_b[2], v_b[6], v_b[5]))
    bm_ped.faces.new((v_b[2], v_b[3], v_b[7], v_b[6]))
    bm_ped.faces.new((v_b[3], v_b[0], v_b[4], v_b[7]))

    v_t = [
        bm_ped.verts.new((-hx2, -hy2, z1)),
        bm_ped.verts.new((hx2, -hy2, z1)),
        bm_ped.verts.new((hx2, hy2, z1)),
        bm_ped.verts.new((-hx2, hy2, z1)),
        bm_ped.verts.new((-hx2, -hy2, z2)),
        bm_ped.verts.new((hx2, -hy2, z2)),
        bm_ped.verts.new((hx2, hy2, z2)),
        bm_ped.verts.new((-hx2, hy2, z2)),
    ]
    bm_ped.faces.new((v_b[4], v_b[5], v_t[1], v_t[0]))
    bm_ped.faces.new((v_b[5], v_b[6], v_t[2], v_t[1]))
    bm_ped.faces.new((v_b[6], v_b[7], v_t[3], v_t[2]))
    bm_ped.faces.new((v_b[7], v_b[4], v_t[0], v_t[3]))
    bm_ped.faces.new((v_t[0], v_t[1], v_t[5], v_t[4]))
    bm_ped.faces.new((v_t[1], v_t[2], v_t[6], v_t[5]))
    bm_ped.faces.new((v_t[2], v_t[3], v_t[7], v_t[6]))
    bm_ped.faces.new((v_t[3], v_t[0], v_t[4], v_t[7]))
    bm_ped.faces.new((v_t[4], v_t[5], v_t[6], v_t[7]))

    for f in bm_ped.faces:
        for loop in f.loops:
            loop[uv_ped].uv = (loop.vert.co.x * 0.20, loop.vert.co.y * 0.20 + loop.vert.co.z * 0.40)

    mesh_ped = bpy.data.meshes.new("Suryakund_Central_Plinth")
    bm_ped.to_mesh(mesh_ped)
    bm_ped.free()
    if mat_granite:
        mesh_ped.materials.append(mat_granite)
    obj_ped = bpy.data.objects.new("Suryakund_Central_Plinth", mesh_ped)
    col.objects.link(obj_ped)

    # -------------------------------------------------------------
    # 5. Stepped Ghats inside Pool (Full length & width immersion steps)
    # -------------------------------------------------------------
    old_ghats = bpy.data.objects.get("Suryakund_Pool_Ghats")
    if old_ghats:
        bpy.data.objects.remove(old_ghats, do_unlink=True)

    bm_ghats = bmesh.new()
    uv_ghats = bm_ghats.loops.layers.uv.new("UVMap")

    n_steps = 5
    tread_w = 0.65
    riser_h = 0.27
    z_coping = 1.60

    rings = []
    for s in range(n_steps + 1):
        z_s = z_coping - s * riser_h
        rx = 20.0 - s * tread_w
        ry = 6.25 - s * tread_w
        r_verts = [
            bm_ghats.verts.new((-rx, -ry, z_s)),
            bm_ghats.verts.new((rx, -ry, z_s)),
            bm_ghats.verts.new((rx, ry, z_s)),
            bm_ghats.verts.new((-rx, ry, z_s)),
        ]
        rings.append(r_verts)

    for s in range(n_steps):
        v_curr = rings[s]
        v_next = rings[s + 1]
        v_riser_top = [
            bm_ghats.verts.new((v_next[0].co.x, v_next[0].co.y, v_curr[0].co.z)),
            bm_ghats.verts.new((v_next[1].co.x, v_next[1].co.y, v_curr[1].co.z)),
            bm_ghats.verts.new((v_next[2].co.x, v_next[2].co.y, v_curr[2].co.z)),
            bm_ghats.verts.new((v_next[3].co.x, v_next[3].co.y, v_curr[3].co.z)),
        ]
        for k in range(4):
            k_next = (k + 1) % 4
            bm_ghats.faces.new((v_curr[k], v_curr[k_next], v_riser_top[k_next], v_riser_top[k]))
        for k in range(4):
            k_next = (k + 1) % 4
            bm_ghats.faces.new((v_riser_top[k], v_riser_top[k_next], v_next[k_next], v_next[k]))

    for f in bm_ghats.faces:
        for loop in f.loops:
            loop[uv_ghats].uv = (loop.vert.co.x * 0.20, loop.vert.co.y * 0.20 + loop.vert.co.z * 0.40)

    mesh_ghats = bpy.data.meshes.new("Suryakund_Pool_Ghats")
    bm_ghats.to_mesh(mesh_ghats)
    bm_ghats.free()
    if mat_granite:
        mesh_ghats.materials.append(mat_granite)
    obj_ghats = bpy.data.objects.new("Suryakund_Pool_Ghats", mesh_ghats)
    col.objects.link(obj_ghats)

    # -------------------------------------------------------------
    # 6. Translucent Energized Water Volume (Z = 1.35m)
    # -------------------------------------------------------------
    old_water = bpy.data.objects.get("Suryakund_Water")
    if old_water:
        bpy.data.objects.remove(old_water, do_unlink=True)

    bm_water = bmesh.new()
    uv_water = bm_water.loops.layers.uv.new("UVMap")
    
    wx_pts = np.linspace(-19.5, 19.5, 40)
    wy_pts = np.linspace(-5.8, 5.8, 16)
    water_v = {}
    for j in range(len(wy_pts)):
        for i in range(len(wx_pts)):
            v = bm_water.verts.new((wx_pts[i], wy_pts[j], 1.35))
            water_v[(i, j)] = v

    for j in range(len(wy_pts) - 1):
        for i in range(len(wx_pts) - 1):
            f = bm_water.faces.new((water_v[(i, j)], water_v[(i+1, j)], water_v[(i+1, j+1)], water_v[(i, j+1)]))
            f.loops[0][uv_water].uv = (i * 0.15, j * 0.15)
            f.loops[1][uv_water].uv = ((i+1) * 0.15, j * 0.15)
            f.loops[2][uv_water].uv = ((i+1) * 0.15, (j+1) * 0.15)
            f.loops[3][uv_water].uv = (i * 0.15, (j+1) * 0.15)

    mesh_water = bpy.data.meshes.new("Suryakund_Water")
    bm_water.to_mesh(mesh_water)
    bm_water.free()
    if mat_water:
        mesh_water.materials.append(mat_water)
    obj_water = bpy.data.objects.new("Suryakund_Water", mesh_water)
    col.objects.link(obj_water)

    # -------------------------------------------------------------
    # 7. Subterranean Promenade (Lower Terrace: Z = 1.60m)
    # -------------------------------------------------------------
    old_prom = bpy.data.objects.get("Suryakund_Promenade")
    if old_prom:
        bpy.data.objects.remove(old_prom, do_unlink=True)

    bm_prom = bmesh.new()
    uv_prom = bm_prom.loops.layers.uv.new("UVMap")

    # South slab
    v_s0 = bm_prom.verts.new((-24.0, -10.5, 1.60))
    v_s1 = bm_prom.verts.new((24.0, -10.5, 1.60))
    v_s2 = bm_prom.verts.new((20.0, -6.25, 1.60))
    v_s3 = bm_prom.verts.new((-20.0, -6.25, 1.60))
    bm_prom.faces.new((v_s0, v_s1, v_s2, v_s3))

    # West slab
    v_w0 = bm_prom.verts.new((-24.0, -10.5, 1.60))
    v_w1 = bm_prom.verts.new((-20.0, -6.25, 1.60))
    v_w2 = bm_prom.verts.new((-20.0, 6.25, 1.60))
    v_w3 = bm_prom.verts.new((-24.0, 6.25, 1.60))
    bm_prom.faces.new((v_w0, v_w1, v_w2, v_w3))

    # East slab
    v_e0 = bm_prom.verts.new((20.0, -6.25, 1.60))
    v_e1 = bm_prom.verts.new((24.0, -10.5, 1.60))
    v_e2 = bm_prom.verts.new((24.0, 6.25, 1.60))
    v_e3 = bm_prom.verts.new((20.0, 6.25, 1.60))
    bm_prom.faces.new((v_e0, v_e1, v_e2, v_e3))

    # North promenade strip in front of the full-width grand steps:
    # From Y = 6.25 (pool edge) to Y = 7.50 (base of grand steps)
    v_np0 = bm_prom.verts.new((-24.0, 6.25, 1.60))
    v_np1 = bm_prom.verts.new((24.0, 6.25, 1.60))
    v_np2 = bm_prom.verts.new((24.0, 7.50, 1.60))
    v_np3 = bm_prom.verts.new((-24.0, 7.50, 1.60))
    bm_prom.faces.new((v_np0, v_np1, v_np2, v_np3))

    for f in bm_prom.faces:
        for loop in f.loops:
            loop[uv_prom].uv = (loop.vert.co.x * 0.20, loop.vert.co.y * 0.20)

    mesh_prom = bpy.data.meshes.new("Suryakund_Promenade")
    bm_prom.to_mesh(mesh_prom)
    bm_prom.free()
    if mat_granite:
        mesh_prom.materials.append(mat_granite)
    obj_prom = bpy.data.objects.new("Suryakund_Promenade", mesh_prom)
    col.objects.link(obj_prom)

    # -------------------------------------------------------------
    # 8. FULL-WIDTH (48-METER WALL-TO-WALL) GRAND DESCENT STEPS
    # Spans from X = -24.0m to X = +24.0m continuously!
    # 2 Flights with wide intermediate landing:
    # Flight 1: 10 steps (Z: 6.10m -> 3.85m, Y: 22.5m -> 16.5m)
    # Intermediate Landing: Z = 3.85m, Y: 16.5m -> 14.5m (48m wide!)
    # Flight 2: 10 steps (Z: 3.85m -> 1.60m, Y: 14.5m -> 7.5m)
    # Constructed with individual dressed ashlar blocks across the 48m width!
    # -------------------------------------------------------------
    old_stairs = bpy.data.objects.get("Suryakund_Grand_Stairs")
    if old_stairs:
        bpy.data.objects.remove(old_stairs, do_unlink=True)

    bm_stairs = bmesh.new()
    uv_stairs = bm_stairs.loops.layers.uv.new("UVMap")

    n_blocks_wide = 20 # 20 granite blocks across the 48m width (2.4m per block)
    x_bounds = np.linspace(-24.0, 24.0, n_blocks_wide + 1)

    # --- Flight 1 (Z: 6.10 -> 3.85, Y: 22.5 -> 16.5) ---
    n_f1 = 10
    riser_f1 = (6.10 - 3.85) / n_f1
    tread_f1 = (22.5 - 16.5) / n_f1

    for s in range(n_f1):
        z_top = 6.10 - s * riser_f1
        z_bot = z_top - riser_f1
        y_front = 22.5 - s * tread_f1
        y_back = y_front - tread_f1

        for b in range(n_blocks_wide):
            xb0, xb1 = x_bounds[b], x_bounds[b + 1]

            # Horizontal Tread Block (counter-clockwise so normal points UP +Z)
            vt0 = bm_stairs.verts.new((xb0, y_front, z_top))
            vt1 = bm_stairs.verts.new((xb1, y_front, z_top))
            vt2 = bm_stairs.verts.new((xb1, y_back, z_top))
            vt3 = bm_stairs.verts.new((xb0, y_back, z_top))
            ft = bm_stairs.faces.new((vt0, vt3, vt2, vt1))
            # Unique UV per block to eliminate repetitive tile look
            u_off = (b * 0.37) % 3.0
            v_off = (s * 0.43) % 3.0
            ft.loops[0][uv_stairs].uv = (u_off, v_off)
            ft.loops[1][uv_stairs].uv = (u_off, v_off + 0.3)
            ft.loops[2][uv_stairs].uv = (u_off + 0.6, v_off + 0.3)
            ft.loops[3][uv_stairs].uv = (u_off + 0.6, v_off)

            # Vertical Riser Block
            vr0 = bm_stairs.verts.new((xb0, y_back, z_top))
            vr1 = bm_stairs.verts.new((xb1, y_back, z_top))
            vr2 = bm_stairs.verts.new((xb1, y_back, z_bot))
            vr3 = bm_stairs.verts.new((xb0, y_back, z_bot))
            fr = bm_stairs.faces.new((vr0, vr1, vr2, vr3))
            fr.loops[0][uv_stairs].uv = (u_off, v_off + 0.3)
            fr.loops[1][uv_stairs].uv = (u_off + 0.6, v_off + 0.3)
            fr.loops[2][uv_stairs].uv = (u_off + 0.6, v_off + 0.5)
            fr.loops[3][uv_stairs].uv = (u_off, v_off + 0.5)

    # --- Intermediate Landing (48m wide x 2.0m deep at Z = 3.85m) ---
    n_land_y = 2
    y_land_pts = np.linspace(16.5, 14.5, n_land_y + 1)
    for ly in range(n_land_y):
        y0, y1 = y_land_pts[ly], y_land_pts[ly + 1]
        for b in range(n_blocks_wide):
            xb0, xb1 = x_bounds[b], x_bounds[b + 1]
            vl0 = bm_stairs.verts.new((xb0, y0, 3.85))
            vl1 = bm_stairs.verts.new((xb1, y0, 3.85))
            vl2 = bm_stairs.verts.new((xb1, y1, 3.85))
            vl3 = bm_stairs.verts.new((xb0, y1, 3.85))
            fl = bm_stairs.faces.new((vl0, vl3, vl2, vl1))
            u_off = (b * 0.41 + ly * 0.25) % 3.0
            fl.loops[0][uv_stairs].uv = (u_off, 0.0)
            fl.loops[1][uv_stairs].uv = (u_off, 0.5)
            fl.loops[2][uv_stairs].uv = (u_off + 0.6, 0.5)
            fl.loops[3][uv_stairs].uv = (u_off + 0.6, 0.0)

    # --- Flight 2 (Z: 3.85 -> 1.60, Y: 14.5 -> 7.5) ---
    n_f2 = 10
    riser_f2 = (3.85 - 1.60) / n_f2
    tread_f2 = (14.5 - 7.50) / n_f2

    for s in range(n_f2):
        z_top = 3.85 - s * riser_f2
        z_bot = z_top - riser_f2
        y_front = 14.5 - s * tread_f2
        y_back = y_front - tread_f2

        for b in range(n_blocks_wide):
            xb0, xb1 = x_bounds[b], x_bounds[b + 1]

            # Horizontal Tread Block
            vt0 = bm_stairs.verts.new((xb0, y_front, z_top))
            vt1 = bm_stairs.verts.new((xb1, y_front, z_top))
            vt2 = bm_stairs.verts.new((xb1, y_back, z_top))
            vt3 = bm_stairs.verts.new((xb0, y_back, z_top))
            ft = bm_stairs.faces.new((vt0, vt3, vt2, vt1))
            u_off = (b * 0.33) % 3.0
            v_off = (s * 0.47) % 3.0
            ft.loops[0][uv_stairs].uv = (u_off, v_off)
            ft.loops[1][uv_stairs].uv = (u_off, v_off + 0.3)
            ft.loops[2][uv_stairs].uv = (u_off + 0.6, v_off + 0.3)
            ft.loops[3][uv_stairs].uv = (u_off + 0.6, v_off)

            # Vertical Riser Block
            vr0 = bm_stairs.verts.new((xb0, y_back, z_top))
            vr1 = bm_stairs.verts.new((xb1, y_back, z_top))
            vr2 = bm_stairs.verts.new((xb1, y_back, z_bot))
            vr3 = bm_stairs.verts.new((xb0, y_back, z_bot))
            fr = bm_stairs.faces.new((vr0, vr1, vr2, vr3))
            fr.loops[0][uv_stairs].uv = (u_off, v_off + 0.3)
            fr.loops[1][uv_stairs].uv = (u_off + 0.6, v_off + 0.3)
            fr.loops[2][uv_stairs].uv = (u_off + 0.6, v_off + 0.5)
            fr.loops[3][uv_stairs].uv = (u_off, v_off + 0.5)

    # --- Upper Arrival Platform (48m wide x 5.5m deep at Z = 6.10m, Y in [22.5, 28.0]) ---
    n_arr_y = 4
    y_arr_pts = np.linspace(22.5, 28.0, n_arr_y + 1)
    for ay in range(n_arr_y):
        y0, y1 = y_arr_pts[ay], y_arr_pts[ay + 1]
        for b in range(n_blocks_wide):
            xb0, xb1 = x_bounds[b], x_bounds[b + 1]
            vp0 = bm_stairs.verts.new((xb0, y0, 6.10))
            vp1 = bm_stairs.verts.new((xb1, y0, 6.10))
            vp2 = bm_stairs.verts.new((xb1, y1, 6.10))
            vp3 = bm_stairs.verts.new((xb0, y1, 6.10))
            fp = bm_stairs.faces.new((vp0, vp1, vp2, vp3))
            u_off = (b * 0.29 + ay * 0.33) % 3.0
            fp.loops[0][uv_stairs].uv = (u_off, 0.0)
            fp.loops[1][uv_stairs].uv = (u_off + 0.6, 0.0)
            fp.loops[2][uv_stairs].uv = (u_off + 0.6, 0.5)
            fp.loops[3][uv_stairs].uv = (u_off, 0.5)

    bmesh.ops.recalc_face_normals(bm_stairs, faces=bm_stairs.faces)
    mesh_stairs = bpy.data.meshes.new("Suryakund_Grand_Stairs")
    bm_stairs.to_mesh(mesh_stairs)
    bm_stairs.free()
    if mat_granite:
        mesh_stairs.materials.append(mat_granite)
    obj_stairs = bpy.data.objects.new("Suryakund_Grand_Stairs", mesh_stairs)
    col.objects.link(obj_stairs)
    print("Built full-width (48m wall-to-wall) Grand Descent Steps with dressed ashlar blocks!")

    # -------------------------------------------------------------
    # 9. Towering Megalithic Retaining Walls (Z: 1.60m to 9.60m, 8m tall!)
    # Flanking the pool and 48m steps on West, East, South, and North
    # -------------------------------------------------------------
    old_walls = bpy.data.objects.get("Suryakund_Retaining_Walls")
    if old_walls:
        bpy.data.objects.remove(old_walls, do_unlink=True)

    bm_walls = bmesh.new()
    uv_walls = bm_walls.loops.layers.uv.new("UVMap")

    n_courses = 8
    z_course_heights = np.linspace(1.60, 9.60, n_courses + 1)

    # South Wall (Y = -10.5, X: -24.0 to +24.0, 48m span, 20 blocks per course)
    for c in range(n_courses):
        z0, z1 = z_course_heights[c], z_course_heights[c + 1]
        n_blks = 20
        x_blks = np.linspace(-24.0, 24.0, n_blks + 1)
        for b in range(n_blks):
            xb0, xb1 = x_blks[b], x_blks[b + 1]
            y_wall = -10.50
            v0 = bm_walls.verts.new((xb0, y_wall, z0))
            v1 = bm_walls.verts.new((xb1, y_wall, z0))
            v2 = bm_walls.verts.new((xb1, y_wall, z1))
            v3 = bm_walls.verts.new((xb0, y_wall, z1))
            f = bm_walls.faces.new((v0, v1, v2, v3))
            u_off = (b * 0.35 + c * 0.17) % 3.0
            f.loops[0][uv_walls].uv = (u_off, 0.0)
            f.loops[1][uv_walls].uv = (u_off + 0.6, 0.0)
            f.loops[2][uv_walls].uv = (u_off + 0.6, 0.5)
            f.loops[3][uv_walls].uv = (u_off, 0.5)

    # West Retaining Wall (X = -24.0, Y: -10.5 to 28.0, 38.5m span, 16 blocks per course)
    # Flanks the entire pool and the 48m grand steps on the West side
    for c in range(n_courses):
        z0, z1 = z_course_heights[c], z_course_heights[c + 1]
        n_blks = 16
        y_blks = np.linspace(-10.5, 28.0, n_blks + 1)
        for b in range(n_blks):
            yb0, yb1 = y_blks[b], y_blks[b + 1]
            x_wall = -24.0
            v0 = bm_walls.verts.new((x_wall, yb0, z0))
            v1 = bm_walls.verts.new((x_wall, yb1, z0))
            v2 = bm_walls.verts.new((x_wall, yb1, z1))
            v3 = bm_walls.verts.new((x_wall, yb0, z1))
            f = bm_walls.faces.new((v0, v1, v2, v3))
            u_off = (b * 0.38 + c * 0.21) % 3.0
            f.loops[0][uv_walls].uv = (u_off, 0.0)
            f.loops[1][uv_walls].uv = (u_off + 0.6, 0.0)
            f.loops[2][uv_walls].uv = (u_off + 0.6, 0.5)
            f.loops[3][uv_walls].uv = (u_off, 0.5)

    # East Retaining Wall (X = +24.0, Y: -10.5 to 28.0, 38.5m span, 16 blocks per course)
    # Flanks the entire pool and the 48m grand steps on the East side
    for c in range(n_courses):
        z0, z1 = z_course_heights[c], z_course_heights[c + 1]
        n_blks = 16
        y_blks = np.linspace(-10.5, 28.0, n_blks + 1)
        for b in range(n_blks):
            yb0, yb1 = y_blks[b], y_blks[b + 1]
            x_wall = 24.0
            v0 = bm_walls.verts.new((x_wall, yb1, z0))
            v1 = bm_walls.verts.new((x_wall, yb0, z0))
            v2 = bm_walls.verts.new((x_wall, yb0, z1))
            v3 = bm_walls.verts.new((x_wall, yb1, z1))
            f = bm_walls.faces.new((v0, v1, v2, v3))
            u_off = (b * 0.33 + c * 0.19) % 3.0
            f.loops[0][uv_walls].uv = (u_off, 0.0)
            f.loops[1][uv_walls].uv = (u_off + 0.6, 0.0)
            f.loops[2][uv_walls].uv = (u_off + 0.6, 0.5)
            f.loops[3][uv_walls].uv = (u_off, 0.5)

    # North Retaining Wall (Y = 28.0, X: -24.0 to +24.0, back of arrival platform, Z: 6.10 to 9.60)
    n_north_c = 4
    z_north_heights = np.linspace(6.10, 9.60, n_north_c + 1)
    for c in range(n_north_c):
        z0, z1 = z_north_heights[c], z_north_heights[c + 1]
        n_blks = 20
        x_blks = np.linspace(-24.0, 24.0, n_blks + 1)
        for b in range(n_blks):
            xb0, xb1 = x_blks[b], x_blks[b + 1]
            y_wall = 28.0
            v0 = bm_walls.verts.new((xb1, y_wall, z0))
            v1 = bm_walls.verts.new((xb0, y_wall, z0))
            v2 = bm_walls.verts.new((xb0, y_wall, z1))
            v3 = bm_walls.verts.new((xb1, y_wall, z1))
            f = bm_walls.faces.new((v0, v1, v2, v3))
            u_off = (b * 0.31 + c * 0.23) % 3.0
            f.loops[0][uv_walls].uv = (u_off, 0.0)
            f.loops[1][uv_walls].uv = (u_off + 0.6, 0.0)
            f.loops[2][uv_walls].uv = (u_off + 0.6, 0.5)
            f.loops[3][uv_walls].uv = (u_off, 0.5)

    # Monolithic Coping Parapet at Z = 9.60m running around top of all walls
    # South Coping
    v_sc0 = bm_walls.verts.new((-24.8, -11.3, 9.60))
    v_sc1 = bm_walls.verts.new((24.8, -11.3, 9.60))
    v_sc2 = bm_walls.verts.new((24.0, -10.5, 9.60))
    v_sc3 = bm_walls.verts.new((-24.0, -10.5, 9.60))
    bm_walls.faces.new((v_sc0, v_sc1, v_sc2, v_sc3))

    # West Coping
    v_wc0 = bm_walls.verts.new((-24.8, -11.3, 9.60))
    v_wc1 = bm_walls.verts.new((-24.0, -10.5, 9.60))
    v_wc2 = bm_walls.verts.new((-24.0, 28.0, 9.60))
    v_wc3 = bm_walls.verts.new((-24.8, 28.8, 9.60))
    bm_walls.faces.new((v_wc0, v_wc1, v_wc2, v_wc3))

    # East Coping
    v_ec0 = bm_walls.verts.new((24.0, -10.5, 9.60))
    v_ec1 = bm_walls.verts.new((24.8, -11.3, 9.60))
    v_ec2 = bm_walls.verts.new((24.8, 28.8, 9.60))
    v_ec3 = bm_walls.verts.new((24.0, 28.0, 9.60))
    bm_walls.faces.new((v_ec0, v_ec1, v_ec2, v_ec3))

    # North Coping
    v_nc0 = bm_walls.verts.new((-24.8, 28.8, 9.60))
    v_nc1 = bm_walls.verts.new((-24.0, 28.0, 9.60))
    v_nc2 = bm_walls.verts.new((24.0, 28.0, 9.60))
    v_nc3 = bm_walls.verts.new((24.8, 28.8, 9.60))
    bm_walls.faces.new((v_nc0, v_nc1, v_nc2, v_nc3))

    mesh_walls = bpy.data.meshes.new("Suryakund_Retaining_Walls")
    bm_walls.to_mesh(mesh_walls)
    bm_walls.free()
    if mat_granite:
        mesh_walls.materials.append(mat_granite)
    obj_walls = bpy.data.objects.new("Suryakund_Retaining_Walls", mesh_walls)
    col.objects.link(obj_walls)

    # -------------------------------------------------------------
    # 10. Three Rasalingas on Central Plinth (Top of Plinth Z = 1.15m)
    # Pedestal partially submerged in energized water (water Z = 1.35m)
    # -------------------------------------------------------------
    linga_orig = bpy.data.objects.get("linga")
    if linga_orig:
        linga_mesh = linga_orig.data
        positions = [
            ("Rasalinga_West", -5.5, 0.0),
            ("Rasalinga_Center", 0.0, 0.0),
            ("Rasalinga_East", 5.5, 0.0),
        ]
        scale_val = 0.50
        for name, rx, ry in positions:
            obj_r = bpy.data.objects.get(name)
            if not obj_r:
                obj_r = bpy.data.objects.new(name, linga_mesh)
                col.objects.link(obj_r)
            obj_r.location = (rx, ry, 1.15)
            obj_r.scale = (scale_val, scale_val, scale_val)
            obj_r.rotation_euler = (0, 0, 0)
        
        linga_orig.hide_render = True
        linga_orig.hide_viewport = True

    # -------------------------------------------------------------
    # 11. Dravidian Monolithic Columns along Retaining Wall Terraces
    # (Along the perimeter coping at Z = 9.60m)
    # -------------------------------------------------------------
    piller_orig = bpy.data.objects.get("piller")
    if piller_orig:
        piller_mesh = piller_orig.data
        pillar_positions = [
            # Corners of the upper coping at Z=9.60m
            ("Pillar_SW", -24.4, -10.9),
            ("Pillar_SE", 24.4, -10.9),
            ("Pillar_NW", -24.4, 28.4),
            ("Pillar_NE", 24.4, 28.4),
            # Flanking mid-terrace along West and East walls
            ("Pillar_Mid_W", -24.4, 8.5),
            ("Pillar_Mid_E", 24.4, 8.5),
        ]
        for name, px, py in pillar_positions:
            obj_p = bpy.data.objects.get(name)
            if not obj_p:
                obj_p = bpy.data.objects.new(name, piller_mesh)
                col.objects.link(obj_p)
            obj_p.location = (px, py, 9.60)
            obj_p.scale = (1.0, 1.0, 1.0)
            obj_p.rotation_euler = (0, 0, 0)

        piller_orig.hide_render = True
        piller_orig.hide_viewport = True

    # -------------------------------------------------------------
    # 12. 20-Foot Brass Sun Sculpture (Overhead at Z = 12.5m)
    # Suspended horizontally facing down towards the pool, with double-sided visibility
    # -------------------------------------------------------------
    old_sun_sculp = bpy.data.objects.get("Suryakund_Sun_Sculpture")
    if old_sun_sculp:
        bpy.data.objects.remove(old_sun_sculp, do_unlink=True)

    bm_sun = bmesh.new()
    uv_sun = bm_sun.loops.layers.uv.new("UVMap")
    
    radius = 3.05 # 6.1m diameter (20ft)
    n_seg = 32
    z_sun = 12.5
    v_center_bot = bm_sun.verts.new((0.0, 0.0, z_sun))
    v_center_top = bm_sun.verts.new((0.0, 0.0, z_sun + 0.10))
    rim_bot = []
    rim_top = []

    for s in range(n_seg):
        ang = 2.0 * math.pi * s / n_seg
        vx = radius * math.cos(ang)
        vy = radius * math.sin(ang)
        rim_bot.append(bm_sun.verts.new((vx, vy, z_sun)))
        rim_top.append(bm_sun.verts.new((vx, vy, z_sun + 0.10)))

    # Bottom face (facing down towards pool)
    for s in range(n_seg):
        v1 = rim_bot[s]
        v2 = rim_bot[(s + 1) % n_seg]
        f = bm_sun.faces.new((v_center_bot, v2, v1))
        f.loops[0][uv_sun].uv = (0.5, 0.5)
        f.loops[1][uv_sun].uv = (0.5 + 0.5 * math.cos(2.0 * math.pi * (s+1) / n_seg), 0.5 + 0.5 * math.sin(2.0 * math.pi * (s+1) / n_seg))
        f.loops[2][uv_sun].uv = (0.5 + 0.5 * math.cos(2.0 * math.pi * s / n_seg), 0.5 + 0.5 * math.sin(2.0 * math.pi * s / n_seg))

    # Top face (facing up)
    for s in range(n_seg):
        v1 = rim_top[s]
        v2 = rim_top[(s + 1) % n_seg]
        f = bm_sun.faces.new((v_center_top, v1, v2))
        f.loops[0][uv_sun].uv = (0.5, 0.5)
        f.loops[1][uv_sun].uv = (0.5 + 0.5 * math.cos(2.0 * math.pi * s / n_seg), 0.5 + 0.5 * math.sin(2.0 * math.pi * s / n_seg))
        f.loops[2][uv_sun].uv = (0.5 + 0.5 * math.cos(2.0 * math.pi * (s+1) / n_seg), 0.5 + 0.5 * math.sin(2.0 * math.pi * (s+1) / n_seg))

    # Rim side faces
    for s in range(n_seg):
        s_next = (s + 1) % n_seg
        bm_sun.faces.new((rim_bot[s], rim_bot[s_next], rim_top[s_next], rim_top[s]))

    mesh_sun = bpy.data.meshes.new("Suryakund_Sun_Sculpture")
    bm_sun.to_mesh(mesh_sun)
    bm_sun.free()
    if mat_sun:
        mesh_sun.materials.append(mat_sun)
    obj_sun_sculp = bpy.data.objects.new("Suryakund_Sun_Sculpture", mesh_sun)
    col.objects.link(obj_sun_sculp)

    # Save mainfile
    blend_path = "/home/mullainathan/Downloads/Untitled.blend"
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print("Full-Width Suryakund Base built and saved successfully!")

if __name__ == "__main__":
    build_suryakund_base()
