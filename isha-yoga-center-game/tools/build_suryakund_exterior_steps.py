"""
Suryakund Exterior Grand Steps, Plinths & Ground Plaza (v12 - 3 Pillars Side Mandapams, World Floor Z = 0.0m)
- Widened side mandapams: Outer boundary at X = +-43.0m to house 3 columns wide (X = +-25.0m, +-33.5m, +-42.0m)
- Front side (North) is at World Floor Level Z = 0.0m
- Outer steps side (South) is elevated at Z = +3.50m (12 feet above ground):
  * 48m Exterior Grand Steps (Suryakund_Exterior_Grand_Steps):
    Starts at South Mandapam end (Y = -25.0m, Z = +3.50m) and descends OUTWARD to outside arrival plaza (Y = -45.0m, Z = 0.0m)
  * Outside arrival plaza at Z = 0.0m (Y in [-45.0m, -68.0m], X in [-72.0m, +72.0m])
- Subterranean Pool Pit (Under the Base Line Z = 0.0m):
  * Top of pool stairs connects flush to North Mandapam at Z = 0.0m (Y = 28.0m)
  * Pool promenade at Z = -4.50m (14.8 ft below ground)
  * Pool water at Z = -4.75m
  * 3 Mercury Rasalingas at Z = -4.95m on central plinth
  * Basin floor at Z = -6.10m (20 ft below ground)
  * Solid megalithic South retaining wall behind 3 Rasalingas: Y = -10.50m, Z from -4.50m to +3.50m (8m tall solid ashlar wall)
  * West and East inner pool retaining walls: X = +-24.0m, Z from -4.50m up to floor coping
- Solid Foundation Plinth Walls ("fill the side empties to the ground"):
  * West Exterior Plinth (X in [-43.0, -42.2m]): solid 0.8m thick ashlar masonry wall with Dravidian Adhisthana moldings from ground Z = 0.0m up to elevated floor (Z in [0.0m, 3.50m])
  * East Exterior Plinth (X in [42.2, 43.0m]): solid 0.8m thick ashlar masonry wall with moldings from ground Z = 0.0m up to elevated floor (Z in [0.0m, 3.50m])
  * South Exterior Plinth Wings (Y in [-25.0, -24.2m]): solid walls from Z = 0.0m up to +3.50m flanking the 48m exterior steps (X in [-43.0, -24.0] and [24.0, 43.0])
"""

import bpy
import bmesh
import math
import os
import numpy as np
from mathutils import Vector

def build_exterior_steps():
    print("=== Building Suryakund Exterior Steps & Plinths (v12 - 3-Pillar Gallery, X = +-43.0m) ===")

    col_name = "Suryakund_Complex"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

    mat_granite = bpy.data.materials.get("Mat_SarpaVasal_Granite")
    mat_water = bpy.data.materials.get("Mat_Suryakund_Water")
    mat_copper = bpy.data.materials.get("Mat_Suryakund_Copper")

    # Ensure specialized Waterfall and Foam PBR materials exist
    tex_dir = "/home/mullainathan/Games/IshaGodot/assets/textures"
    albedo_path = os.path.join(tex_dir, "waterfall_albedo.png")
    normal_path = os.path.join(tex_dir, "waterfall_normal.png")
    rough_path = os.path.join(tex_dir, "waterfall_roughness.png")
    foam_path = os.path.join(tex_dir, "waterfall_foam.png")

    mat_waterfall = bpy.data.materials.get("Mat_Suryakund_Waterfall")
    if not mat_waterfall:
        mat_waterfall = bpy.data.materials.new(name="Mat_Suryakund_Waterfall")
    mat_waterfall.use_nodes = True
    try:
        mat_waterfall.surface_render_method = 'BLENDED'
    except Exception:
        pass
    try:
        mat_waterfall.blend_method = 'BLEND'
    except Exception:
        pass
    mat_waterfall.use_backface_culling = False

    wf_nodes = mat_waterfall.node_tree.nodes
    wf_links = mat_waterfall.node_tree.links
    wf_nodes.clear()
    wf_out = wf_nodes.new(type='ShaderNodeOutputMaterial')
    wf_bsdf = wf_nodes.new(type='ShaderNodeBsdfPrincipled')
    try:
        wf_bsdf.inputs['Transmission Weight'].default_value = 0.55
    except Exception:
        try:
            wf_bsdf.inputs['Transmission'].default_value = 0.55
        except Exception:
            pass
    wf_bsdf.inputs['IOR'].default_value = 1.333

    # Load Real PBR Textures (ensures realistic appearance in Blender AND when exported to Godot 4!)
    if os.path.exists(albedo_path):
        img_albedo = bpy.data.images.load(albedo_path, check_existing=True)
        tex_albedo = wf_nodes.new(type='ShaderNodeTexImage')
        tex_albedo.image = img_albedo
        wf_links.new(tex_albedo.outputs['Color'], wf_bsdf.inputs['Base Color'])
        wf_links.new(tex_albedo.outputs['Alpha'], wf_bsdf.inputs['Alpha'])
    else:
        wf_bsdf.inputs['Base Color'].default_value = (0.75, 0.90, 0.96, 1.0)
        wf_bsdf.inputs['Alpha'].default_value = 0.55

    if os.path.exists(normal_path):
        img_norm = bpy.data.images.load(normal_path, check_existing=True)
        img_norm.colorspace_settings.name = 'Non-Color'
        tex_norm = wf_nodes.new(type='ShaderNodeTexImage')
        tex_norm.image = img_norm
        node_norm = wf_nodes.new(type='ShaderNodeNormalMap')
        node_norm.inputs['Strength'].default_value = 1.4
        wf_links.new(tex_norm.outputs['Color'], node_norm.inputs['Color'])
        wf_links.new(node_norm.outputs['Normal'], wf_bsdf.inputs['Normal'])

    if os.path.exists(rough_path):
        img_rough = bpy.data.images.load(rough_path, check_existing=True)
        img_rough.colorspace_settings.name = 'Non-Color'
        tex_rough = wf_nodes.new(type='ShaderNodeTexImage')
        tex_rough.image = img_rough
        wf_links.new(tex_rough.outputs['Color'], wf_bsdf.inputs['Roughness'])
    else:
        wf_bsdf.inputs['Roughness'].default_value = 0.05

    wf_links.new(wf_bsdf.outputs['BSDF'], wf_out.inputs['Surface'])

    mat_foam = bpy.data.materials.get("Mat_Suryakund_Foam")
    if not mat_foam:
        mat_foam = bpy.data.materials.new(name="Mat_Suryakund_Foam")
    mat_foam.use_nodes = True
    try:
        mat_foam.surface_render_method = 'BLENDED'
        mat_foam.blend_method = 'BLEND'
    except Exception:
        pass
    mat_foam.use_backface_culling = False
    fm_nodes = mat_foam.node_tree.nodes
    fm_links = mat_foam.node_tree.links
    fm_nodes.clear()
    fm_out = fm_nodes.new(type='ShaderNodeOutputMaterial')
    fm_bsdf = fm_nodes.new(type='ShaderNodeBsdfPrincipled')
    fm_bsdf.inputs['Roughness'].default_value = 0.22

    if os.path.exists(foam_path):
        img_foam = bpy.data.images.load(foam_path, check_existing=True)
        tex_foam = fm_nodes.new(type='ShaderNodeTexImage')
        tex_foam.image = img_foam
        fm_links.new(tex_foam.outputs['Color'], fm_bsdf.inputs['Base Color'])
        fm_links.new(tex_foam.outputs['Alpha'], fm_bsdf.inputs['Alpha'])
    else:
        fm_bsdf.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
        fm_bsdf.inputs['Alpha'].default_value = 0.70

    fm_links.new(fm_bsdf.outputs['BSDF'], fm_out.inputs['Surface'])

    # 1. Clean up any old South stairs, exterior steps, plinths, balustrades, pool or waterfall objects
    for obj_name in [
        "Suryakund_South_Stairs", 
        "Suryakund_Exterior_Grand_Steps", 
        "Suryakund_Outside_Plaza", 
        "Suryakund_Ground_Plaza", 
        "Suryakund_Retaining_Walls", 
        "Suryakund_Plinth_Foundation", 
        "Mandapam_Plinth_Foundation",
        "Mandapam_Parapet_Balustrade",
        "Suryakund_Water",
        "Suryakund_Central_Plinth",
        "Suryakund_Promenade",
        "Suryakund_Pool_Ghats",
        "Suryakund_Basin_Floor",
        "Suryakund_Pool_Steps",
        "Suryakund_Waterfall_Spout",
        "Suryakund_Waterfall_Sheet",
        "Suryakund_Waterfall_Foam"
    ]:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Shift Grand Stairs under the base line (Z < 0.0m)
    # The pool staircase top at Y = 28.0m connects flush at Z = 0.0m (World Floor)
    shift_pool_z = -6.10
    grand_stairs_obj = bpy.data.objects.get("Suryakund_Grand_Stairs")
    if grand_stairs_obj:
        grand_stairs_obj.location = (0.0, 0.0, shift_pool_z)

    # 2b. Build Wall-to-Wall Copper Basin Floor (X in [-24.0, 24.0m], Y in [-10.50, 7.50m], Z = -6.10m)
    # The water and pool now reach completely to the side and back walls with zero leftover space!
    bm_floor = bmesh.new()
    uv_floor = bm_floor.loops.layers.uv.new("UVMap")
    n_fx, n_fy = 24, 12
    fx_pts = np.linspace(-24.0, 24.0, n_fx + 1)
    fy_pts = np.linspace(-10.50, 7.50, n_fy + 1)
    f_grid = {}
    for j in range(n_fy + 1):
        for i in range(n_fx + 1):
            f_grid[(i, j)] = bm_floor.verts.new((fx_pts[i], fy_pts[j], -6.10))
    for j in range(n_fy):
        for i in range(n_fx):
            ff = bm_floor.faces.new((f_grid[(i, j)], f_grid[(i+1, j)], f_grid[(i+1, j+1)], f_grid[(i, j+1)]))
            ff.loops[0][uv_floor].uv = (i * 0.4, j * 0.4)
            ff.loops[1][uv_floor].uv = ((i+1) * 0.4, j * 0.4)
            ff.loops[2][uv_floor].uv = ((i+1) * 0.4, (j+1) * 0.4)
            ff.loops[3][uv_floor].uv = (i * 0.4, (j+1) * 0.4)
    mesh_bfloor = bpy.data.meshes.new("Suryakund_Basin_Floor")
    bm_floor.to_mesh(mesh_bfloor)
    bm_floor.free()
    if mat_copper:
        mesh_bfloor.materials.append(mat_copper)
    obj_bfloor = bpy.data.objects.new("Suryakund_Basin_Floor", mesh_bfloor)
    col.objects.link(obj_bfloor)

    # 2c. Submerged Central Granite Plinth for the 3 Rasalingas (Z in [-6.10, -6.05m])
    bm_plinth_pool = bmesh.new()
    uv_pp = bm_plinth_pool.loops.layers.uv.new("UVMap")
    px1, py1 = 9.0, 1.8
    pz0, pz1 = -6.10, -6.05
    vp = [
        bm_plinth_pool.verts.new((-px1, -py1, pz0)),
        bm_plinth_pool.verts.new((px1, -py1, pz0)),
        bm_plinth_pool.verts.new((px1, py1, pz0)),
        bm_plinth_pool.verts.new((-px1, py1, pz0)),
        bm_plinth_pool.verts.new((-px1, -py1, pz1)),
        bm_plinth_pool.verts.new((px1, -py1, pz1)),
        bm_plinth_pool.verts.new((px1, py1, pz1)),
        bm_plinth_pool.verts.new((-px1, py1, pz1)),
    ]
    bm_plinth_pool.faces.new((vp[0], vp[1], vp[5], vp[4]))
    bm_plinth_pool.faces.new((vp[1], vp[2], vp[6], vp[5]))
    bm_plinth_pool.faces.new((vp[2], vp[3], vp[7], vp[6]))
    bm_plinth_pool.faces.new((vp[3], vp[0], vp[4], vp[7]))
    bm_plinth_pool.faces.new((vp[4], vp[5], vp[6], vp[7]))
    mesh_cplinth = bpy.data.meshes.new("Suryakund_Central_Plinth")
    bm_plinth_pool.to_mesh(mesh_cplinth)
    bm_plinth_pool.free()
    if mat_granite:
        mesh_cplinth.materials.append(mat_granite)
    obj_cplinth = bpy.data.objects.new("Suryakund_Central_Plinth", mesh_cplinth)
    col.objects.link(obj_cplinth)

    # 2d. 3 Mercury Rasalingas positioned so exactly 3/4 (75%) of the Linga is soaked in water!
    # Centered at Y = 0.0m, X = [-5.5, 0.0, +5.5m], in direct line with South center wall waterfall!
    linga_z_pos = -7.263
    for linga_name in ["Rasalinga_Center", "Rasalinga_East", "Rasalinga_West"]:
        l_obj = bpy.data.objects.get(linga_name)
        if l_obj:
            l_obj.location.z = linga_z_pos

    # 2e. Full 48m Wide North Pool Steps (X in [-24.0, 24.0m]) descending from Z = -4.50m to -6.10m
    # Connecting flush with the base of Suryakund_Grand_Stairs at Y = 7.50m:
    # Step 1: Y in [7.50, 6.70m], Z = -4.77m (dry)
    # Step 2: Y in [6.70, 5.90m], Z = -5.04m (dry)
    # Step 3: Y in [5.90, 5.10m], Z = -5.31m (WATER LEVEL! Meets the water plane!)
    # Step 4: Y in [5.10, 4.30m], Z = -5.58m (submerged)
    # Step 5: Y in [4.30, 3.50m], Z = -5.85m (submerged)
    bm_psteps = bmesh.new()
    uv_psteps = bm_psteps.loops.layers.uv.new("UVMap")
    n_psteps = 5
    y_pstep_bounds = [7.50, 6.70, 5.90, 5.10, 4.30, 3.50]
    z_pstep_levels = [-4.50, -4.77, -5.04, -5.31, -5.58, -5.85]
    n_bx = 20
    px_bounds = np.linspace(-24.0, 24.0, n_bx + 1)
    for ps in range(n_psteps):
        y_top = y_pstep_bounds[ps]
        y_bot = y_pstep_bounds[ps + 1]
        z_high = z_pstep_levels[ps]
        z_tread = z_pstep_levels[ps + 1]
        for b in range(n_bx):
            xb0, xb1 = px_bounds[b], px_bounds[b + 1]
            # Vertical Riser
            vr0 = bm_psteps.verts.new((xb0, y_top, z_tread))
            vr1 = bm_psteps.verts.new((xb1, y_top, z_tread))
            vr2 = bm_psteps.verts.new((xb1, y_top, z_high))
            vr3 = bm_psteps.verts.new((xb0, y_top, z_high))
            bm_psteps.faces.new((vr0, vr1, vr2, vr3))
            # Horizontal Tread
            vt0 = bm_psteps.verts.new((xb0, y_top, z_tread))
            vt1 = bm_psteps.verts.new((xb1, y_top, z_tread))
            vt2 = bm_psteps.verts.new((xb1, y_bot, z_tread))
            vt3 = bm_psteps.verts.new((xb0, y_bot, z_tread))
            bm_psteps.faces.new((vt0, vt3, vt2, vt1))
    # Bottom riser to basin floor at Y = 3.50m, Z from -5.85 to -6.10m
    for b in range(n_bx):
        xb0, xb1 = px_bounds[b], px_bounds[b + 1]
        vbf0 = bm_psteps.verts.new((xb0, 3.50, -6.10))
        vbf1 = bm_psteps.verts.new((xb1, 3.50, -6.10))
        vbf2 = bm_psteps.verts.new((xb1, 3.50, -5.85))
        vbf3 = bm_psteps.verts.new((xb0, 3.50, -5.85))
        bm_psteps.faces.new((vbf0, vbf1, vbf2, vbf3))
    bmesh.ops.recalc_face_normals(bm_psteps, faces=bm_psteps.faces)
    for f in bm_psteps.faces:
        for loop in f.loops:
            loop[uv_psteps].uv = (loop.vert.co.x * 0.25, loop.vert.co.y * 0.25 + loop.vert.co.z * 0.35)
    mesh_psteps = bpy.data.meshes.new("Suryakund_Pool_Steps")
    bm_psteps.to_mesh(mesh_psteps)
    bm_psteps.free()
    if mat_granite:
        mesh_psteps.materials.append(mat_granite)
    obj_psteps = bpy.data.objects.new("Suryakund_Pool_Steps", mesh_psteps)
    col.objects.link(obj_psteps)

    # 2f. Build Energized Water Volume Wall-to-Wall ("no left space, water till the walls!")
    # - West: X = -24.0m (till the West wall)
    # - East: X = +24.0m (till the East wall)
    # - Back: Y = -10.50m (till the South wall)
    # - Front: Y = 5.90m (meets Step 3 riser!)
    # - Elevation: Z = -5.310m (Step 3)
    bm_water = bmesh.new()
    uv_water = bm_water.loops.layers.uv.new("UVMap")
    wx_pts = np.linspace(-24.0, 24.0, 48)
    wy_pts = np.linspace(-10.50, 5.90, 24)
    water_v = {}
    z_water_step3 = -5.310
    for j in range(len(wy_pts)):
        for i in range(len(wx_pts)):
            v = bm_water.verts.new((wx_pts[i], wy_pts[j], z_water_step3))
            water_v[(i, j)] = v
    for j in range(len(wy_pts) - 1):
        for i in range(len(wx_pts) - 1):
            f = bm_water.faces.new((
                water_v[(i, j)], 
                water_v[(i + 1, j)], 
                water_v[(i + 1, j + 1)], 
                water_v[(i, j + 1)]
            ))
            f.loops[0][uv_water].uv = (i * 0.15, j * 0.15)
            f.loops[1][uv_water].uv = ((i + 1) * 0.15, j * 0.15)
            f.loops[2][uv_water].uv = ((i + 1) * 0.15, (j + 1) * 0.15)
            f.loops[3][uv_water].uv = (i * 0.15, (j + 1) * 0.15)
    mesh_water = bpy.data.meshes.new("Suryakund_Water")
    bm_water.to_mesh(mesh_water)
    bm_water.free()
    if mat_water:
        mesh_water.materials.append(mat_water)
    obj_water = bpy.data.objects.new("Suryakund_Water", mesh_water)
    col.objects.link(obj_water)

    # 2g. Build Authentic Dravidian Waterfall ("only water should fall, from the top where the wall starts")
    # Centered at X = 0.0m on the South wall (Y = -10.50m):
    # - NO STONE SPOUT MESH! Only pure rushing cascading water!
    # - Starts at the top where the wall starts: Z = +3.50m (top of South wall at Y = -10.50m)
    # - Cascades down 8.81m to plunge directly into the pool at Z = -5.310m
    
    # 1. Cascading 3D Water Volume from Top of Wall (Z = 3.50m down to Z = -5.310m)
    bm_sheet = bmesh.new()
    uv_sheet = bm_sheet.loops.layers.uv.new("UVMap")
    n_sy = 48
    n_sx = 24
    z_fall_pts = np.linspace(3.50, -5.310, n_sy + 1)
    sx_pts = np.linspace(-1.80, 1.80, n_sx + 1)

    front_grid = {}
    back_grid = {}

    for j in range(n_sy + 1):
        zf = z_fall_pts[j]
        # Natural outward parabolic trajectory as water gushes over the top edge of the wall
        t = (3.50 - zf) / (3.50 - (-5.310))
        # At top (Z = 3.50m), water comes from upper floor Y = -10.50m, arcs forward to -10.38m,
        # and plunges straight into the pool at Y = -10.42m
        yf_center = -10.50 + 0.12 * math.sin(t * math.pi * 0.70)
        thickness = 0.06 # 6cm physical volume thickness

        yf_front = yf_center + thickness * 0.5
        yf_back = yf_center - thickness * 0.5

        for i in range(n_sx + 1):
            x_raw = sx_pts[i]
            # Subtle organic undulating ripple displacement
            pert_x = 0.03 * math.sin(j * 0.6 + i * 1.0)
            pert_y = 0.02 * math.cos(j * 1.1 + i * 0.8)
            front_grid[(i, j)] = bm_sheet.verts.new((x_raw + pert_x, yf_front + pert_y, zf))
            back_grid[(i, j)] = bm_sheet.verts.new((x_raw + pert_x, yf_back + pert_y, zf))

    for j in range(n_sy):
        for i in range(n_sx):
            # Front face (facing North toward the 3 Rasalingas and pool steps)
            ff = bm_sheet.faces.new((
                front_grid[(i, j)], 
                front_grid[(i+1, j)], 
                front_grid[(i+1, j+1)], 
                front_grid[(i, j+1)]
            ))
            # Seamless vertical UV tiling for realistic flow in Blender and Godot 4
            ff.loops[0][uv_sheet].uv = (i / n_sx, (j / n_sy) * 4.0)
            ff.loops[1][uv_sheet].uv = ((i+1) / n_sx, (j / n_sy) * 4.0)
            ff.loops[2][uv_sheet].uv = ((i+1) / n_sx, ((j+1) / n_sy) * 4.0)
            ff.loops[3][uv_sheet].uv = (i / n_sx, ((j+1) / n_sy) * 4.0)

            # Back face (facing South toward wall)
            bf = bm_sheet.faces.new((
                back_grid[(i+1, j)], 
                back_grid[(i, j)], 
                back_grid[(i, j+1)], 
                back_grid[(i+1, j+1)]
            ))
            bf.loops[0][uv_sheet].uv = ((i+1) / n_sx, (j / n_sy) * 4.0)
            bf.loops[1][uv_sheet].uv = (i / n_sx, (j / n_sy) * 4.0)
            bf.loops[2][uv_sheet].uv = (i / n_sx, ((j+1) / n_sy) * 4.0)
            bf.loops[3][uv_sheet].uv = ((i+1) / n_sx, ((j+1) / n_sy) * 4.0)

    # Watertight side edge caps (West & East)
    for j in range(n_sy):
        bm_sheet.faces.new((
            back_grid[(0, j)],
            front_grid[(0, j)],
            front_grid[(0, j+1)],
            back_grid[(0, j+1)]
        ))
        bm_sheet.faces.new((
            front_grid[(n_sx, j)],
            back_grid[(n_sx, j)],
            back_grid[(n_sx, j+1)],
            front_grid[(n_sx, j+1)]
        ))

    # Top water intake cap at Z = 3.50m (connecting smoothly to elevated floor)
    v_top0 = bm_sheet.verts.new((-1.80, -10.65, 3.50))
    v_top1 = bm_sheet.verts.new((1.80, -10.65, 3.50))
    bm_sheet.faces.new((v_top0, v_top1, front_grid[(n_sx, 0)], front_grid[(0, 0)]))

    mesh_sheet = bpy.data.meshes.new("Suryakund_Waterfall_Sheet")
    bm_sheet.to_mesh(mesh_sheet)
    bm_sheet.free()
    if mat_waterfall:
        mesh_sheet.materials.append(mat_waterfall)
    obj_sheet = bpy.data.objects.new("Suryakund_Waterfall_Sheet", mesh_sheet)
    col.objects.link(obj_sheet)

    # 2. Concentric Aerated Frothy Foam Impact Zone at Plunge Pool (Z = -5.30m)
    bm_foam = bmesh.new()
    uv_foam = bm_foam.loops.layers.uv.new("UVMap")
    n_seg = 32
    r_x1, r_y1 = 2.60, 0.85
    r_x2, r_y2 = 3.80, 1.35

    c_foam = bm_foam.verts.new((0.0, -10.38, -5.30))
    inner_ring = []
    outer_ring = []

    for k in range(n_seg):
        ang = 2.0 * math.pi * k / n_seg
        ix = r_x1 * math.cos(ang) + 0.05 * math.sin(3 * ang)
        iy = -10.38 + r_y1 * math.sin(ang)
        inner_ring.append(bm_foam.verts.new((ix, iy, -5.30)))
        ox = r_x2 * math.cos(ang)
        oy = -10.38 + r_y2 * math.sin(ang)
        outer_ring.append(bm_foam.verts.new((ox, oy, -5.30)))

    for k in range(n_seg):
        kn = (k + 1) % n_seg
        # Inner circle
        f_in = bm_foam.faces.new((c_foam, inner_ring[k], inner_ring[kn]))
        f_in.loops[0][uv_foam].uv = (0.5, 0.5)
        f_in.loops[1][uv_foam].uv = (0.5 + 0.35 * math.cos(ang), 0.5 + 0.35 * math.sin(ang))
        f_in.loops[2][uv_foam].uv = (0.5 + 0.35 * math.cos(2*math.pi*kn/n_seg), 0.5 + 0.35 * math.sin(2*math.pi*kn/n_seg))

        # Outer annular ring
        f_out = bm_foam.faces.new((inner_ring[k], outer_ring[k], outer_ring[kn], inner_ring[kn]))
        f_out.loops[0][uv_foam].uv = (0.5 + 0.35 * math.cos(ang), 0.5 + 0.35 * math.sin(ang))
        f_out.loops[1][uv_foam].uv = (0.5 + 0.50 * math.cos(ang), 0.5 + 0.50 * math.sin(ang))
        f_out.loops[2][uv_foam].uv = (0.5 + 0.50 * math.cos(2*math.pi*kn/n_seg), 0.5 + 0.50 * math.sin(2*math.pi*kn/n_seg))
        f_out.loops[3][uv_foam].uv = (0.5 + 0.35 * math.cos(2*math.pi*kn/n_seg), 0.5 + 0.35 * math.sin(2*math.pi*kn/n_seg))

    mesh_foam = bpy.data.meshes.new("Suryakund_Waterfall_Foam")
    bm_foam.to_mesh(mesh_foam)
    bm_foam.free()
    if mat_foam:
        mesh_foam.materials.append(mat_foam)
    obj_foam = bpy.data.objects.new("Suryakund_Waterfall_Foam", mesh_foam)
    col.objects.link(obj_foam)

    # 3. Dedicated Waterfall Shimmer Light (soft wash illuminating the 8.81m water torrent)
    wf_light = bpy.data.objects.get("Suryakund_Waterfall_Light")
    if not wf_light:
        wf_light_data = bpy.data.lights.new(name="Suryakund_Waterfall_Light", type='POINT')
        wf_light = bpy.data.objects.new(name="Suryakund_Waterfall_Light", object_data=wf_light_data)
        col.objects.link(wf_light)
    wf_light.data.energy = 450.0
    wf_light.data.color = (0.94, 0.97, 1.0)
    wf_light.location = (0.0, -8.80, 0.50) # midway up the 8.81m waterfall
    try:
        wf_light.data.shadow_soft_size = 5.0
        wf_light.data.specular_factor = 0.15
    except Exception:
        pass

    # Shift Fill Light
    fill_light = bpy.data.objects.get("Suryakund_Fill_Light")
    if fill_light:
        fill_light.location.z = 8.0 + shift_pool_z # 1.90m

    print("Built wall-to-wall pool (no left space!), water at Step 3 (Z = -5.31m), 3/4 Linga soaked & center wall waterfall!")

    # -------------------------------------------------------------
    # 3. Subterranean Pool Retaining Walls (From Basin Floor Z = -6.10m to +3.50m!)
    # Dropping straight into the water on South, West, and East!
    # -------------------------------------------------------------
    bm_walls = bmesh.new()
    uv_walls = bm_walls.loops.layers.uv.new("UVMap")

    n_courses = 12
    z_course_heights = np.linspace(-6.10, 3.50, n_courses + 1)

    # South Megalithic Retaining Wall (Y = -10.50m, X: -24.0 to +24.0m, solid wall behind waterfall and Rasalingas)
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

    # West and East Pool Retaining Walls (X = +-24.0m, Y: -10.5 to 28.0m)
    n_blks_y = 18
    y_blks = np.linspace(-10.5, 28.0, n_blks_y + 1)

    for b in range(n_blks_y):
        yb0, yb1 = y_blks[b], y_blks[b + 1]
        def get_wall_top(y):
            if y <= 21.0:
                return 3.50
            elif y >= 28.0:
                return 0.00
            else:
                return 3.50 - 3.50 * ((y - 21.0) / (28.0 - 21.0))
        zt0 = get_wall_top(yb0)
        zt1 = get_wall_top(yb1)
        # In the pool basin (Y <= 7.5m), walls go down to floor Z = -6.10m!
        z_base0 = -6.10 if yb0 <= 7.5 else -4.50
        z_base1 = -6.10 if yb1 <= 7.5 else -4.50

        # West wall (facing East into pool)
        v0 = bm_walls.verts.new((-24.0, yb0, z_base0))
        v1 = bm_walls.verts.new((-24.0, yb1, z_base1))
        v2 = bm_walls.verts.new((-24.0, yb1, zt1))
        v3 = bm_walls.verts.new((-24.0, yb0, zt0))
        f = bm_walls.faces.new((v0, v1, v2, v3))
        u_off = (b * 0.38) % 3.0
        f.loops[0][uv_walls].uv = (u_off, 0.0)
        f.loops[1][uv_walls].uv = (u_off + 0.6, 0.0)
        f.loops[2][uv_walls].uv = (u_off + 0.6, 0.5)
        f.loops[3][uv_walls].uv = (u_off, 0.5)

        # East wall (facing West into pool)
        v0 = bm_walls.verts.new((24.0, yb1, z_base1))
        v1 = bm_walls.verts.new((24.0, yb0, z_base0))
        v2 = bm_walls.verts.new((24.0, yb0, zt0))
        v3 = bm_walls.verts.new((24.0, yb1, zt1))
        f = bm_walls.faces.new((v0, v1, v2, v3))
        u_off = (b * 0.33) % 3.0
        f.loops[0][uv_walls].uv = (u_off, 0.0)
        f.loops[1][uv_walls].uv = (u_off + 0.6, 0.0)
        f.loops[2][uv_walls].uv = (u_off + 0.6, 0.5)
        f.loops[3][uv_walls].uv = (u_off, 0.5)

    # South Wall Coping Parapet at Z = 3.50m (Y in [-10.5, -11.3])
    v_sc0 = bm_walls.verts.new((-24.8, -11.3, 3.50))
    v_sc1 = bm_walls.verts.new((24.8, -11.3, 3.50))
    v_sc2 = bm_walls.verts.new((24.0, -10.5, 3.50))
    v_sc3 = bm_walls.verts.new((-24.0, -10.5, 3.50))
    bm_walls.faces.new((v_sc0, v_sc1, v_sc2, v_sc3))

    mesh_walls = bpy.data.meshes.new("Suryakund_Retaining_Walls")
    bm_walls.to_mesh(mesh_walls)
    bm_walls.free()
    if mat_granite:
        mesh_walls.materials.append(mat_granite)
    obj_walls = bpy.data.objects.new("Suryakund_Retaining_Walls", mesh_walls)
    col.objects.link(obj_walls)
    print("Built solid pool retaining walls from floor Z = -6.10m!")

    # -------------------------------------------------------------
    # 4. Solid Foundation Plinth Walls ("fill the side empties to the ground")
    # Complete 3D solid masonry foundation structure with Adhisthana base moldings:
    # - West Exterior Plinth (X in [-43.0, -42.2m], Y in [-25.0, 28.0m])
    # - East Exterior Plinth (X in [42.2, 43.0m], Y in [-25.0, 28.0m])
    # - South Exterior Plinth Wings (Y in [-25.0, -24.2m], X in [-43.0, -24.0] & [24.0, 43.0])
    # All rise solidly from World Ground Z = 0.0m up to the elevated floor plane!
    # -------------------------------------------------------------
    bm_plinth = bmesh.new()
    uv_plinth = bm_plinth.loops.layers.uv.new("UVMap")

    n_p_blks = 24
    y_p_pts = np.linspace(-25.0, 28.0, n_p_blks + 1)
    
    def get_plinth_top(y):
        if y <= 21.0:
            return 3.50
        elif y >= 28.0:
            return 0.00
        else:
            return 3.50 - 3.50 * ((y - 21.0) / (28.0 - 21.0))

    for b in range(n_p_blks):
        yb0, yb1 = y_p_pts[b], y_p_pts[b + 1]
        zt0 = get_plinth_top(yb0)
        zt1 = get_plinth_top(yb1)

        # --- West Plinth (Solid Wall, X_out = -43.0m, X_in = -42.2m) ---
        # 1. Outer Face (facing West)
        v_wo0 = bm_plinth.verts.new((-43.0, yb0, 0.0))
        v_wo1 = bm_plinth.verts.new((-43.0, yb1, 0.0))
        v_wo2 = bm_plinth.verts.new((-43.0, yb1, zt1))
        v_wo3 = bm_plinth.verts.new((-43.0, yb0, zt0))
        f_wo = bm_plinth.faces.new((v_wo0, v_wo1, v_wo2, v_wo3))
        u_off = (b * 0.41) % 3.0
        f_wo.loops[0][uv_plinth].uv = (u_off, 0.0)
        f_wo.loops[1][uv_plinth].uv = (u_off + 0.6, 0.0)
        f_wo.loops[2][uv_plinth].uv = (u_off + 0.6, 0.5)
        f_wo.loops[3][uv_plinth].uv = (u_off, 0.5)

        # 2. Inner Face (facing East toward interior)
        v_wi0 = bm_plinth.verts.new((-42.2, yb1, 0.0))
        v_wi1 = bm_plinth.verts.new((-42.2, yb0, 0.0))
        v_wi2 = bm_plinth.verts.new((-42.2, yb0, zt0))
        v_wi3 = bm_plinth.verts.new((-42.2, yb1, zt1))
        bm_plinth.faces.new((v_wi0, v_wi1, v_wi2, v_wi3))

        # --- East Plinth (Solid Wall, X_out = +43.0m, X_in = +42.2m) ---
        # 1. Outer Face (facing East)
        v_eo0 = bm_plinth.verts.new((43.0, yb1, 0.0))
        v_eo1 = bm_plinth.verts.new((43.0, yb0, 0.0))
        v_eo2 = bm_plinth.verts.new((43.0, yb0, zt0))
        v_eo3 = bm_plinth.verts.new((43.0, yb1, zt1))
        f_eo = bm_plinth.faces.new((v_eo0, v_eo1, v_eo2, v_eo3))
        u_off = (b * 0.37) % 3.0
        f_eo.loops[0][uv_plinth].uv = (u_off, 0.0)
        f_eo.loops[1][uv_plinth].uv = (u_off + 0.6, 0.0)
        f_eo.loops[2][uv_plinth].uv = (u_off + 0.6, 0.5)
        f_eo.loops[3][uv_plinth].uv = (u_off, 0.5)

        # 2. Inner Face (facing West toward interior)
        v_ei0 = bm_plinth.verts.new((42.2, yb0, 0.0))
        v_ei1 = bm_plinth.verts.new((42.2, yb1, 0.0))
        v_ei2 = bm_plinth.verts.new((42.2, yb1, zt1))
        v_ei3 = bm_plinth.verts.new((42.2, yb0, zt0))
        bm_plinth.faces.new((v_ei0, v_ei1, v_ei2, v_ei3))

    # --- South Exterior Wings Plinth (Y = -25.0m, Z: 0.0m to 3.50m) ---
    # West wing (X in [-43.0, -24.0m], thickness Y in [-25.0, -24.2m])
    vsw0 = bm_plinth.verts.new((-43.0, -25.0, 0.0))
    vsw1 = bm_plinth.verts.new((-24.0, -25.0, 0.0))
    vsw2 = bm_plinth.verts.new((-24.0, -25.0, 3.50))
    vsw3 = bm_plinth.verts.new((-43.0, -25.0, 3.50))
    bm_plinth.faces.new((vsw0, vsw1, vsw2, vsw3))

    vsw_i0 = bm_plinth.verts.new((-24.0, -24.2, 0.0))
    vsw_i1 = bm_plinth.verts.new((-43.0, -24.2, 0.0))
    vsw_i2 = bm_plinth.verts.new((-43.0, -24.2, 3.50))
    vsw_i3 = bm_plinth.verts.new((-24.0, -24.2, 3.50))
    bm_plinth.faces.new((vsw_i0, vsw_i1, vsw_i2, vsw_i3))

    # East wing (X in [24.0, 43.0m], thickness Y in [-25.0, -24.2m])
    vse0 = bm_plinth.verts.new((24.0, -25.0, 0.0))
    vse1 = bm_plinth.verts.new((43.0, -25.0, 0.0))
    vse2 = bm_plinth.verts.new((43.0, -25.0, 3.50))
    vse3 = bm_plinth.verts.new((24.0, -25.0, 3.50))
    bm_plinth.faces.new((vse0, vse1, vse2, vse3))

    vse_i0 = bm_plinth.verts.new((43.0, -24.2, 0.0))
    vse_i1 = bm_plinth.verts.new((24.0, -24.2, 0.0))
    vse_i2 = bm_plinth.verts.new((24.0, -24.2, 3.50))
    vse_i3 = bm_plinth.verts.new((43.0, -24.2, 3.50))
    bm_plinth.faces.new((vse_i0, vse_i1, vse_i2, vse_i3))

    mesh_plinth = bpy.data.meshes.new("Suryakund_Plinth_Foundation")
    bm_plinth.to_mesh(mesh_plinth)
    bm_plinth.free()
    if mat_granite:
        mesh_plinth.materials.append(mat_granite)
    obj_plinth = bpy.data.objects.new("Suryakund_Plinth_Foundation", mesh_plinth)
    col.objects.link(obj_plinth)
    print("Filled side empties with solid foundation plinth walls to ground Z = 0.0m (X = +-43.0m)!")

    # -------------------------------------------------------------
    # 5. Build Exterior Grand Steps (48m Full Width, Y: -25.0m down to -45.0m, Z: 3.50m down to 0.0m)
    # Going OUT from the South Mandapam end (Z = 3.50m) down to outside ground level (Z = 0.0m)
    # -------------------------------------------------------------
    bm_ext = bmesh.new()
    uv_ext = bm_ext.loops.layers.uv.new("UVMap")

    n_ext_steps = 16
    y_ext_pts = np.linspace(-25.0, -45.0, n_ext_steps + 1)
    z_ext_pts = np.linspace(3.50, 0.00, n_ext_steps + 1)

    n_blocks_wide = 16
    x_bounds = np.linspace(-24.0, 24.0, n_blocks_wide + 1)

    for s in range(n_ext_steps):
        y_top = y_ext_pts[s]
        y_bot = y_ext_pts[s + 1]
        z_high = z_ext_pts[s]
        z_low = z_ext_pts[s + 1]

        for b in range(n_blocks_wide):
            xb0 = x_bounds[b]
            xb1 = x_bounds[b + 1]

            # Horizontal Tread Face (counter-clockwise winding so normal points UP +Z)
            vt0 = bm_ext.verts.new((xb0, y_top, z_high))
            vt1 = bm_ext.verts.new((xb1, y_top, z_high))
            vt2 = bm_ext.verts.new((xb1, y_bot, z_high))
            vt3 = bm_ext.verts.new((xb0, y_bot, z_high))
            ft = bm_ext.faces.new((vt0, vt3, vt2, vt1))
            
            u_off = (b * 0.31 + s * 0.27) % 3.0
            v_off = (s * 0.43) % 3.0
            ft.loops[0][uv_ext].uv = (u_off, v_off)
            ft.loops[1][uv_ext].uv = (u_off, v_off + 0.3)
            ft.loops[2][uv_ext].uv = (u_off + 0.6, v_off + 0.3)
            ft.loops[3][uv_ext].uv = (u_off + 0.6, v_off)

            # Vertical Riser Face (facing South, outward away from the mandapam)
            vr0 = bm_ext.verts.new((xb0, y_bot, z_low))
            vr1 = bm_ext.verts.new((xb1, y_bot, z_low))
            vr2 = bm_ext.verts.new((xb1, y_bot, z_high))
            vr3 = bm_ext.verts.new((xb0, y_bot, z_high))
            fr = bm_ext.faces.new((vr0, vr1, vr2, vr3))
            
            fr.loops[0][uv_ext].uv = (u_off, v_off + 0.3)
            fr.loops[1][uv_ext].uv = (u_off + 0.6, v_off + 0.3)
            fr.loops[2][uv_ext].uv = (u_off + 0.6, v_off + 0.5)
            fr.loops[3][uv_ext].uv = (u_off, v_off + 0.5)

    # Flanking Side Stringer Walls on West & East (Flush with step treads, NO raised edge blocks!)
    # West Stringer Wall
    for s in range(n_ext_steps):
        y_top = y_ext_pts[s]
        y_bot = y_ext_pts[s + 1]
        z_high = z_ext_pts[s]
        z_low = 0.00

        vsw0 = bm_ext.verts.new((-24.0, y_top, z_low))
        vsw1 = bm_ext.verts.new((-24.0, y_bot, z_low))
        vsw2 = bm_ext.verts.new((-24.0, y_bot, z_high))
        vsw3 = bm_ext.verts.new((-24.0, y_top, z_high))
        f_sw = bm_ext.faces.new((vsw0, vsw1, vsw2, vsw3))
        f_sw.loops[0][uv_ext].uv = (0.0, 0.0)
        f_sw.loops[1][uv_ext].uv = (0.5, 0.0)
        f_sw.loops[2][uv_ext].uv = (0.5, 0.5)
        f_sw.loops[3][uv_ext].uv = (0.0, 0.5)

        # Flush outer boundary
        vc0 = bm_ext.verts.new((-24.8, y_top, z_high))
        vc1 = bm_ext.verts.new((-24.0, y_top, z_high))
        vc2 = bm_ext.verts.new((-24.0, y_bot, z_high))
        vc3 = bm_ext.verts.new((-24.8, y_bot, z_high))
        bm_ext.faces.new((vc0, vc1, vc2, vc3))

    # East Stringer Wall
    for s in range(n_ext_steps):
        y_top = y_ext_pts[s]
        y_bot = y_ext_pts[s + 1]
        z_high = z_ext_pts[s]
        z_low = 0.00

        vse0 = bm_ext.verts.new((24.0, y_bot, z_low))
        vse1 = bm_ext.verts.new((24.0, y_top, z_low))
        vse2 = bm_ext.verts.new((24.0, y_top, z_high))
        vse3 = bm_ext.verts.new((24.0, y_bot, z_high))
        f_se = bm_ext.faces.new((vse0, vse1, vse2, vse3))
        f_se.loops[0][uv_ext].uv = (0.0, 0.0)
        f_se.loops[1][uv_ext].uv = (0.5, 0.0)
        f_se.loops[2][uv_ext].uv = (0.5, 0.5)
        f_se.loops[3][uv_ext].uv = (0.0, 0.5)

        # Flush outer boundary
        vc0 = bm_ext.verts.new((24.0, y_top, z_high))
        vc1 = bm_ext.verts.new((24.8, y_top, z_high))
        vc2 = bm_ext.verts.new((24.8, y_bot, z_high))
        vc3 = bm_ext.verts.new((24.0, y_bot, z_high))
        bm_ext.faces.new((vc0, vc1, vc2, vc3))

    bmesh.ops.recalc_face_normals(bm_ext, faces=bm_ext.faces)
    mesh_ext = bpy.data.meshes.new("Suryakund_Exterior_Grand_Steps")
    bm_ext.to_mesh(mesh_ext)
    bm_ext.free()
    if mat_granite:
        mesh_ext.materials.append(mat_granite)
    obj_ext = bpy.data.objects.new("Suryakund_Exterior_Grand_Steps", mesh_ext)
    col.objects.link(obj_ext)
    print("Constructed 48m Full-Width Exterior Grand Steps descending from +3.50m OUTWARD to ground Z = 0.0m!")

    # -------------------------------------------------------------
    # 6. Outside Arrival / Exit Plaza at Ground Level Z = 0.0m
    # (Y in [-45.0m, -68.0m], X in [-72.0m, +72.0m])
    # -------------------------------------------------------------
    bm_plaza = bmesh.new()
    uv_plaza = bm_plaza.loops.layers.uv.new("UVMap")

    n_p_x = 24
    n_p_y = 12
    px_pts = np.linspace(-72.0, 72.0, n_p_x + 1)
    py_pts = np.linspace(-45.0, -68.0, n_p_y + 1)

    for iy in range(n_p_y):
        y0, y1 = py_pts[iy], py_pts[iy + 1]
        for ix in range(n_p_x):
            x0, x1 = px_pts[ix], px_pts[ix + 1]
            vp0 = bm_plaza.verts.new((x0, y0, 0.00))
            vp1 = bm_plaza.verts.new((x1, y0, 0.00))
            vp2 = bm_plaza.verts.new((x1, y1, 0.00))
            vp3 = bm_plaza.verts.new((x0, y1, 0.00))
            fp = bm_plaza.faces.new((vp0, vp1, vp2, vp3))
            u_off = (ix * 0.23 + iy * 0.31) % 3.0
            fp.loops[0][uv_plaza].uv = (u_off, 0.0)
            fp.loops[1][uv_plaza].uv = (u_off + 0.6, 0.0)
            fp.loops[2][uv_plaza].uv = (u_off + 0.6, 0.5)
            fp.loops[3][uv_plaza].uv = (u_off, 0.5)

    mesh_plaza = bpy.data.meshes.new("Suryakund_Outside_Plaza")
    bm_plaza.to_mesh(mesh_plaza)
    bm_plaza.free()
    if mat_granite:
        mesh_plaza.materials.append(mat_granite)
    obj_plaza = bpy.data.objects.new("Suryakund_Outside_Plaza", mesh_plaza)
    col.objects.link(obj_plaza)
    print("Built outside arrival/exit plaza at World Floor Z = 0.0m (X = +-72.0m)!")

if __name__ == "__main__":
    build_exterior_steps()
