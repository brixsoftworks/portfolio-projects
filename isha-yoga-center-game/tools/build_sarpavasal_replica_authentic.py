"""Build Pristine Authentic 3D Architectural Replica of Sarpa Vasal Gateway

Exact Specifications per User Request:
1. Extract sculpted Center Naga panel from /home/mullainathan/Downloads/mahan.blend:
   - High-resolution 3D cobra relief with positive bas-relief protrusion (snake body and hood proud of the column).
   - Crop out transparent alpha background margins around the carved stone column.
   - Crop out the bottom rectangular stone slab base (y >= 789 in pixel space), keeping only the clean vertical carved stone shaft and cobra sculpture.
   - Attach this clean sculpted Naga panel to the front face of the center monolithic column of Sarpa Vasal.
2. Authentic Dravidian Gateway Architecture:
   - Left and right outer pilasters with classical Dravidian stepped plinths, facets, and capitals.
   - Dual open doorway portals (100% hollow, open, passable from front to back at ground level).
   - Molded stepped stone architraves (jambs and lintels) framing both portals.
   - Warm terracotta brick masonry infill recessed behind the stone framework.
   - Continuous carved lotus-petal (Kapota/Padma) stone cornice beam running across the top.
   - Flat roof terrace with decorative stepped parapets.
3. End-to-End Vaulted Terracotta Temple Dome:
   - Spans full width of gateway (8.30m length end to end, 1.70m depth, 1.30m height).
   - Textured with authentic 2K PBR terracotta tiles.
   - Dressed stone gable copings at East and West ends.
4. Half-Cut Sacred Golden Linga:
   - Stepped golden lotus plinth, semicircular cylindrical shaft, and ellipsoidal dome top.
   - 24K temple gold (Metallic=0.96, Roughness=0.15) aligned directly above the Center Naga column.
5. BlendKit Rock Granite & PBR Materials:
   - BlendKit rock albedo, normal, and roughness maps on all pilasters, jambs, lintels, and rear walls.
   - Sits flush on flat ground at Z = 0.0m (zero basement rocks, zero debris).
"""
import bpy
import bmesh
import math
import os
import numpy as np
from PIL import Image

def build_sarpavasal_replica():
    source_blend = "/home/mullainathan/Downloads/mahan.blend"
    out_blend = "/home/mullainathan/Downloads/sarpavasal.blend"
    out_glb = "/home/mullainathan/Games/IshaGodot/assets/models/sarpavasal.glb"
    tex_dir = "/home/mullainathan/Games/IshaGodot/assets/textures"

    naga_img_path = os.path.join(tex_dir, "sarpavasal_naga_photoroom.png")
    if not os.path.exists(naga_img_path):
        naga_img_path = "/home/mullainathan/Downloads/639603094_1795521495069900.jpg-Photoroom.png"

    print(f"[SarpaVasal Replica] Loading Naga texture for alpha analysis: {naga_img_path}")
    im = Image.open(naga_img_path)
    im_arr = np.array(im)
    alpha = im_arr[:, :, 3]
    H, W = alpha.shape # 896, 1200

    print(f"[SarpaVasal Replica] Extracting Center Naga Panel from {source_blend}...")
    bpy.ops.wm.open_mainfile(filepath=source_blend)

    source_obj = bpy.data.objects.get("Plane")
    if not source_obj:
        raise ValueError("Could not find object 'Plane' in source blend!")

    # Set subdivision level for pristine high-density detail
    sub = source_obj.modifiers.get("Subdivision")
    if sub:
        sub.levels = 3
        sub.render_levels = 3

    # Apply transform so modifiers evaluate in true metric units
    bpy.context.view_layer.objects.active = source_obj
    source_obj.select_set(True)

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = source_obj.evaluated_get(depsgraph)
    eval_mesh = eval_obj.to_mesh()

    bm_source = bmesh.new()
    bm_source.from_mesh(eval_mesh)
    source_uv_layer = bm_source.loops.layers.uv.active

    # Filter faces:
    # 1. py < 789: Crops out the bottom rectangular stone slab base!
    # 2. py >= 73: Crops out empty top margin above the column shaft.
    # 3. alpha > 20: Crops out all transparent background margins on sides!
    selected_faces = []
    selected_verts = set()
    for f in bm_source.faces:
        uvs = [l[source_uv_layer].uv for l in f.loops]
        cu = sum(uv[0] for uv in uvs) / len(uvs)
        cv = sum(uv[1] for uv in uvs) / len(uvs)
        px = int(np.clip(cu * W, 0, W - 1))
        py = int(np.clip((1.0 - cv) * H, 0, H - 1))
        if 73 <= py < 789 and alpha[py, px] > 20:
            selected_faces.append(f)
            for v in f.verts:
                selected_verts.add(v)

    print(f"[SarpaVasal Replica] Filtered clean Naga shaft: {len(selected_verts)} vertices, {len(selected_faces)} faces")

    xs = [v.co.x for v in selected_verts]
    ys = [v.co.y for v in selected_verts]
    zs = [v.co.z for v in selected_verts]

    x_min, x_max = min(xs), max(xs)
    x_center = (x_min + x_max) / 2.0
    x_span = x_max - x_min

    y_min, y_max = min(ys), max(ys)
    y_span = y_max - y_min

    z_min, z_max = min(zs), max(zs)
    z_span = z_max - z_min

    print(f"[SarpaVasal Replica] Source BBox: X:[{x_min:.4f}, {x_max:.4f}], Y:[{y_min:.4f}, {y_max:.4f}], Z:[{z_min:.4f}, {z_max:.4f}]")

    bm_final = bmesh.new()
    uv_layer = bm_final.loops.layers.uv.new("UVMap")

    # Front main face of the gateway is at Y = -0.85m (facing South in Godot)
    # Rear main face is at Y = +0.85m (facing North towards Suryakund)
    FRONT_Y = -0.85
    REAR_Y = 0.85

    # Center monolithic pier width: X in [-0.55, 0.55] (1.10m wide)
    # Naga shaft width on pier: 1.04m wide (leaves crisp 3cm granite border on sides)
    target_width = 1.04
    scale_x = target_width / x_span
    target_height = 4.00 # Height Z from 0.0m to 4.00m (cornice bottom)

    # 1. Insert sculpted Naga panel on the front face of the center column
    vert_map = {}
    for f in selected_faces:
        face_verts_new = []
        for v in f.verts:
            if v not in vert_map:
                x_new = (v.co.x - x_center) * scale_x
                z_new = ((v.co.y - y_min) / y_span) * target_height
                # Positive bas-relief: snake sculpture protrudes forward into negative Y by up to 7.5cm
                protrusion = (v.co.z - z_min) * 0.12
                y_new = FRONT_Y - protrusion - 0.005
                v_new = bm_final.verts.new((x_new, y_new, z_new))
                vert_map[v] = v_new
            face_verts_new.append(vert_map[v])

        # Counter-clockwise winding: normals face outward toward -Y (Front / South)
        new_f = bm_final.faces.new(face_verts_new)
        new_f.material_index = 0 # Slot 0: Material.001 (Photo texture)
        for idx, loop in enumerate(new_f.loops):
            loop[uv_layer].uv = f.loops[idx][source_uv_layer].uv

    # 1B. Build side return skirt quads along the outer boundary of the Naga panel back to FRONT_Y
    # Find boundary edges of selected_faces
    selected_faces_set = set(selected_faces)
    boundary_edges = []
    for f in selected_faces:
        for e in f.edges:
            shared = sum(1 for ef in e.link_faces if ef in selected_faces_set)
            if shared == 1:
                boundary_edges.append((e, f))

    back_vert_map = {}
    for e, f in boundary_edges:
        # Determine loop direction along edge in face f
        v0, v1 = None, None
        for l in f.loops:
            if l.edge == e:
                v0 = l.vert
                v1 = l.link_loop_next.vert
                break
        if not v0 or not v1:
            v0, v1 = e.verts[0], e.verts[1]

        nv0 = vert_map[v0]
        nv1 = vert_map[v1]

        if nv0 not in back_vert_map:
            back_vert_map[nv0] = bm_final.verts.new((nv0.co.x, FRONT_Y, nv0.co.z))
        if nv1 not in back_vert_map:
            back_vert_map[nv1] = bm_final.verts.new((nv1.co.x, FRONT_Y, nv1.co.z))

        nv0_b = back_vert_map[nv0]
        nv1_b = back_vert_map[nv1]

        # Skirt quad facing outward
        try:
            skirt_f = bm_final.faces.new([nv0, nv0_b, nv1_b, nv1])
            skirt_f.material_index = 1 # Slot 1: Material_SarpaVasal_Granite (Solid rock side)
            if uv_layer:
                skirt_f.loops[0][uv_layer].uv = (nv0.co.x * 0.5, nv0.co.z * 0.5)
                skirt_f.loops[1][uv_layer].uv = (nv0.co.x * 0.5, FRONT_Y * 0.5)
                skirt_f.loops[2][uv_layer].uv = (nv1.co.x * 0.5, FRONT_Y * 0.5)
                skirt_f.loops[3][uv_layer].uv = (nv1.co.x * 0.5, nv1.co.z * 0.5)
        except ValueError:
            pass

    bm_source.free()
    eval_obj.to_mesh_clear()
    bm_final.verts.ensure_lookup_table()
    bm_final.faces.ensure_lookup_table()
    print(f"[SarpaVasal Replica] Sculpted Naga panel attached with {len(bm_final.verts)} verts, {len(bm_final.faces)} faces")

    # 2. ROBUST SOLID BOX GENERATOR WITH TRUE 2D UV MAPPING PER FACE
    MAT_PHOTO = 0       # Slot 0: Material.001 (Photo texture, only used for Center Naga panel)
    MAT_GRANITE = 1     # Slot 1: Material_SarpaVasal_Granite (BlendKit Rock)
    MAT_BRICK = 2       # Slot 2: Material_SarpaVasal_Brick (Stacked Terracotta Brick)
    MAT_TERRACOTTA = 3  # Slot 3: Material_SarpaVasal_Terracotta (Terracotta Roof Dome)
    MAT_GOLD = 4        # Slot 4: Material_Gold_Linga (Sacred 24K Temple Gold Linga)

    def add_box(min_pt, max_pt, mat_default=MAT_GRANITE, front_mat=None, rear_mat=None,
                uv_scale=0.50, skip_front=False, skip_rear=False, skip_bottom=False):
        """Builds a solid 6-sided rectangular prism with proper normals and explicit UV coordinates.
        min_pt = (x0, y0, z0), max_pt = (x1, y1, z1).
        """
        x0, y0, z0 = min_pt
        x1, y1, z1 = max_pt
        v0 = bm_final.verts.new((x0, y0, z0)) # Front bottom left
        v1 = bm_final.verts.new((x1, y0, z0)) # Front bottom right
        v2 = bm_final.verts.new((x1, y0, z1)) # Front top right
        v3 = bm_final.verts.new((x0, y0, z1)) # Front top left
        v4 = bm_final.verts.new((x0, y1, z0)) # Rear bottom left
        v5 = bm_final.verts.new((x1, y1, z0)) # Rear bottom right
        v6 = bm_final.verts.new((x1, y1, z1)) # Rear top right
        v7 = bm_final.verts.new((x0, y1, z1)) # Rear top left

        # 1. Front face (-Y normal, pointing South)
        if not skip_front:
            f_front = bm_final.faces.new([v0, v3, v2, v1])
            f_front.material_index = front_mat if front_mat is not None else mat_default
            if uv_layer:
                f_front.loops[0][uv_layer].uv = (x0 * uv_scale, z0 * uv_scale)
                f_front.loops[1][uv_layer].uv = (x0 * uv_scale, z1 * uv_scale)
                f_front.loops[2][uv_layer].uv = (x1 * uv_scale, z1 * uv_scale)
                f_front.loops[3][uv_layer].uv = (x1 * uv_scale, z0 * uv_scale)

        # 2. Rear face (+Y normal, pointing North)
        if not skip_rear:
            f_rear = bm_final.faces.new([v4, v5, v6, v7])
            f_rear.material_index = rear_mat if rear_mat is not None else mat_default
            if uv_layer:
                f_rear.loops[0][uv_layer].uv = (x0 * uv_scale, z0 * uv_scale)
                f_rear.loops[1][uv_layer].uv = (x1 * uv_scale, z0 * uv_scale)
                f_rear.loops[2][uv_layer].uv = (x1 * uv_scale, z1 * uv_scale)
                f_rear.loops[3][uv_layer].uv = (x0 * uv_scale, z1 * uv_scale)

        # 3. Bottom face (-Z normal, ground)
        if not skip_bottom:
            f_bottom = bm_final.faces.new([v0, v1, v5, v4])
            f_bottom.material_index = mat_default
            if uv_layer:
                f_bottom.loops[0][uv_layer].uv = (x0 * uv_scale, y0 * uv_scale)
                f_bottom.loops[1][uv_layer].uv = (x1 * uv_scale, y0 * uv_scale)
                f_bottom.loops[2][uv_layer].uv = (x1 * uv_scale, y1 * uv_scale)
                f_bottom.loops[3][uv_layer].uv = (x0 * uv_scale, y1 * uv_scale)

        # 4. Top face (+Z normal)
        f_top = bm_final.faces.new([v3, v7, v6, v2])
        f_top.material_index = mat_default
        if uv_layer:
            f_top.loops[0][uv_layer].uv = (x0 * uv_scale, y0 * uv_scale)
            f_top.loops[1][uv_layer].uv = (x0 * uv_scale, y1 * uv_scale)
            f_top.loops[2][uv_layer].uv = (x1 * uv_scale, y1 * uv_scale)
            f_top.loops[3][uv_layer].uv = (x1 * uv_scale, y0 * uv_scale)

        # 5. West face (-X normal)
        f_west = bm_final.faces.new([v0, v4, v7, v3])
        f_west.material_index = mat_default
        if uv_layer:
            f_west.loops[0][uv_layer].uv = (y0 * uv_scale, z0 * uv_scale)
            f_west.loops[1][uv_layer].uv = (y1 * uv_scale, z0 * uv_scale)
            f_west.loops[2][uv_layer].uv = (y1 * uv_scale, z1 * uv_scale)
            f_west.loops[3][uv_layer].uv = (y0 * uv_scale, z1 * uv_scale)

        # 6. East face (+X normal)
        f_east = bm_final.faces.new([v1, v2, v6, v5])
        f_east.material_index = mat_default
        if uv_layer:
            f_east.loops[0][uv_layer].uv = (y0 * uv_scale, z0 * uv_scale)
            f_east.loops[1][uv_layer].uv = (y0 * uv_scale, z1 * uv_scale)
            f_east.loops[2][uv_layer].uv = (y1 * uv_scale, z1 * uv_scale)
            f_east.loops[3][uv_layer].uv = (y1 * uv_scale, z0 * uv_scale)

    # 3. BUILD AUTHENTIC REPLICA GATEWAY ARCHITECTURE

    # A. Center Monolithic Pier (Behind and supporting the Naga Panel)
    # Width X in [-0.55, 0.55], Depth Y in [FRONT_Y, REAR_Y], Height Z in [0.0, 4.00m]
    # Solid granite front face at FRONT_Y gives solid backing to the sculpted Naga panel
    add_box((-0.55, FRONT_Y, 0.0), (0.55, REAR_Y, 4.00), mat_default=MAT_GRANITE, skip_front=False)

    # B. Left (West) Outer Pilaster
    # Width X in [-4.05, -3.05], Depth Y in [FRONT_Y, REAR_Y], Height Z in [0.0, 4.00m]
    # Base plinth
    add_box((-4.10, FRONT_Y - 0.04, 0.0), (-3.00, REAR_Y + 0.04, 0.40), mat_default=MAT_GRANITE)
    # Main pilaster shaft
    add_box((-4.05, FRONT_Y, 0.40), (-3.05, REAR_Y, 3.75), mat_default=MAT_GRANITE)
    # Pilaster capital
    add_box((-4.10, FRONT_Y - 0.03, 3.75), (-3.00, REAR_Y + 0.03, 4.00), mat_default=MAT_GRANITE)

    # C. Right (East) Outer Pilaster
    # Width X in [3.05, 4.05], Depth Y in [FRONT_Y, REAR_Y], Height Z in [0.0, 4.00m]
    # Base plinth
    add_box((3.00, FRONT_Y - 0.04, 0.0), (4.10, REAR_Y + 0.04, 0.40), mat_default=MAT_GRANITE)
    # Main shaft
    add_box((3.05, FRONT_Y, 0.40), (4.05, REAR_Y, 3.75), mat_default=MAT_GRANITE)
    # Capital
    add_box((3.00, FRONT_Y - 0.03, 3.75), (4.10, REAR_Y + 0.03, 4.00), mat_default=MAT_GRANITE)

    # D. Open Doorway Portals (Clear Passageways)
    # West Doorway opening: X in [-2.75, -0.65], Z in [0.0, 3.05m] (2.10m wide x 3.05m clear headroom)
    # East Doorway opening: X in [0.65, 2.75], Z in [0.0, 3.05m] (2.10m wide x 3.05m clear headroom)

    # E. Stepped Architectural Stone Doorframe (Architrave / Sakha Moldings)
    def add_stepped_doorframe(x_open_min, x_open_max, z_open_top=3.05):
        # Tier 1 (Inner step: 10cm wide frame, 3cm projection)
        w1 = 0.10
        p1 = 0.03
        add_box((x_open_min - w1, FRONT_Y - p1, 0.0), (x_open_min, FRONT_Y, z_open_top + w1), mat_default=MAT_GRANITE)
        add_box((x_open_min - w1, REAR_Y, 0.0), (x_open_min, REAR_Y + p1, z_open_top + w1), mat_default=MAT_GRANITE)
        add_box((x_open_max, FRONT_Y - p1, 0.0), (x_open_max + w1, FRONT_Y, z_open_top + w1), mat_default=MAT_GRANITE)
        add_box((x_open_max, REAR_Y, 0.0), (x_open_max + w1, REAR_Y + p1, z_open_top + w1), mat_default=MAT_GRANITE)
        add_box((x_open_min - w1, FRONT_Y - p1, z_open_top), (x_open_max + w1, FRONT_Y, z_open_top + w1), mat_default=MAT_GRANITE)
        add_box((x_open_min - w1, REAR_Y, z_open_top), (x_open_max + w1, REAR_Y + p1, z_open_top + w1), mat_default=MAT_GRANITE)

        # Tier 2 (Outer step: another 10cm wide frame, 5cm projection)
        w2 = 0.20
        p2 = 0.05
        add_box((x_open_min - w2, FRONT_Y - p2, 0.0), (x_open_min - w1, FRONT_Y, z_open_top + w2), mat_default=MAT_GRANITE)
        add_box((x_open_min - w2, REAR_Y, 0.0), (x_open_min - w1, REAR_Y + p2, z_open_top + w2), mat_default=MAT_GRANITE)
        add_box((x_open_max + w1, FRONT_Y - p2, 0.0), (x_open_max + w2, FRONT_Y, z_open_top + w2), mat_default=MAT_GRANITE)
        add_box((x_open_max + w1, REAR_Y, 0.0), (x_open_max + w2, REAR_Y + p2, z_open_top + w2), mat_default=MAT_GRANITE)
        add_box((x_open_min - w2, FRONT_Y - p2, z_open_top + w1), (x_open_max + w2, FRONT_Y, z_open_top + w2), mat_default=MAT_GRANITE)
        add_box((x_open_min - w2, REAR_Y, z_open_top + w1), (x_open_max + w2, REAR_Y + p2, z_open_top + w2), mat_default=MAT_GRANITE)

        # Portal Passage Side Walls & Ceiling (100% passable through the gateway)
        add_box((x_open_min - w2, FRONT_Y, 0.0), (x_open_min, REAR_Y, z_open_top), mat_default=MAT_GRANITE)
        add_box((x_open_max, FRONT_Y, 0.0), (x_open_max + w2, REAR_Y, z_open_top), mat_default=MAT_GRANITE)
        add_box((x_open_min, FRONT_Y, z_open_top), (x_open_max, REAR_Y, z_open_top + w2), mat_default=MAT_GRANITE)

    add_stepped_doorframe(-2.75, -0.65, z_open_top=3.05)
    add_stepped_doorframe(0.65, 2.75, z_open_top=3.05)

    # F. Terracotta Brick Masonry Panels (Recessed Behind Stone Framework)
    add_box((-3.05, FRONT_Y + 0.06, 3.25), (-0.55, REAR_Y - 0.06, 4.00),
            mat_default=MAT_GRANITE, front_mat=MAT_BRICK, rear_mat=MAT_BRICK, uv_scale=2.2)
    add_box((0.55, FRONT_Y + 0.06, 3.25), (3.05, REAR_Y - 0.06, 4.00),
            mat_default=MAT_GRANITE, front_mat=MAT_BRICK, rear_mat=MAT_BRICK, uv_scale=2.2)

    add_box((-3.05, FRONT_Y + 0.06, 0.0), (-2.95, REAR_Y - 0.06, 3.25),
            mat_default=MAT_GRANITE, front_mat=MAT_BRICK, rear_mat=MAT_BRICK, uv_scale=2.2)
    add_box((2.95, FRONT_Y + 0.06, 0.0), (3.05, REAR_Y - 0.06, 3.25),
            mat_default=MAT_GRANITE, front_mat=MAT_BRICK, rear_mat=MAT_BRICK, uv_scale=2.2)

    # G. Continuous Carved Dravidian Cornice (Kapota / Padma Beam)
    # Across entire monument width: X in [-4.20, 4.20]
    add_box((-4.14, FRONT_Y - 0.05, 4.00), (4.14, REAR_Y + 0.05, 4.12), mat_default=MAT_GRANITE)
    add_box((-4.20, FRONT_Y - 0.10, 4.12), (4.20, REAR_Y + 0.10, 4.24), mat_default=MAT_GRANITE)
    add_box((-4.14, FRONT_Y - 0.05, 4.24), (4.14, REAR_Y + 0.05, 4.32), mat_default=MAT_GRANITE)

    # H. Roof Terrace Plinth (End to End)
    add_box((-4.18, FRONT_Y - 0.04, 4.32), (4.18, REAR_Y + 0.04, 4.45), mat_default=MAT_GRANITE)

    # I. End-to-End Vaulted Terracotta Temple Dome
    # Spans full width: X in [-4.15m, +4.15m] (total length 8.30m)
    # Depth Y in [FRONT_Y, REAR_Y] = [-0.85m, +0.85m] (total depth 1.70m)
    # Height: base at Z = 4.45m, apex at Z = 5.75m (height 1.30m)
    z_base = 4.45
    dome_len = 4.15
    dome_ry = 0.85
    dome_h = 1.30

    nx_body = 32
    ny_body = 24

    vault_grid = []
    for ix in range(nx_body + 1):
        x_val = -dome_len + 2.0 * dome_len * (float(ix) / float(nx_body))
        row = []
        for iy in range(ny_body + 1):
            theta = float(iy) / float(ny_body) * math.pi
            y_val = -dome_ry * math.cos(theta)
            arch_factor = math.sin(theta)
            z_val = z_base + dome_h * arch_factor
            v = bm_final.verts.new((x_val, y_val, z_val))
            row.append(v)
        vault_grid.append(row)

    for ix in range(nx_body):
        for iy in range(ny_body):
            v00 = vault_grid[ix][iy]
            v10 = vault_grid[ix + 1][iy]
            v11 = vault_grid[ix + 1][iy + 1]
            v01 = vault_grid[ix][iy + 1]
            f = bm_final.faces.new([v00, v10, v11, v01])
            f.material_index = MAT_TERRACOTTA
            if uv_layer:
                u0 = (v00.co.x + dome_len) * 0.75
                u1 = (v10.co.x + dome_len) * 0.75
                w0 = (float(iy) / float(ny_body)) * 3.0
                w1 = (float(iy + 1) / float(ny_body)) * 3.0
                f.loops[0][uv_layer].uv = (u0, w0)
                f.loops[1][uv_layer].uv = (u1, w0)
                f.loops[2][uv_layer].uv = (u1, w1)
                f.loops[3][uv_layer].uv = (u0, w1)

    # Gable End Walls at West and East
    v_w_center = bm_final.verts.new((-dome_len, 0.0, z_base + dome_h * 0.45))
    for iy in range(ny_body):
        f = bm_final.faces.new([v_w_center, vault_grid[0][iy], vault_grid[0][iy + 1]])
        f.material_index = MAT_GRANITE
        if uv_layer:
            for l in f.loops:
                l[uv_layer].uv = (l.vert.co.y * 0.50, (l.vert.co.z - z_base) * 0.50)

    v_e_center = bm_final.verts.new((dome_len, 0.0, z_base + dome_h * 0.45))
    for iy in range(ny_body):
        f = bm_final.faces.new([v_e_center, vault_grid[nx_body][iy + 1], vault_grid[nx_body][iy]])
        f.material_index = MAT_GRANITE
        if uv_layer:
            for l in f.loops:
                l[uv_layer].uv = (l.vert.co.y * 0.50, (l.vert.co.z - z_base) * 0.50)

    # Ridge Beam capping dome crest
    add_box((-4.18, -0.08, z_base + dome_h - 0.04), (4.18, 0.08, z_base + dome_h + 0.05),
            mat_default=MAT_TERRACOTTA)

    # J. A Half-Cut Sacred Golden Linga
    # Centered at X = 0.0, directly above the Center Naga column!
    linga_r = 0.38
    linga_z_base = 4.45
    linga_z_shaft_top = 5.75
    linga_z_apex = 6.45
    n_linga_segs = 16
    n_dome_rings = 10

    # 1. Stepped Golden Lotus Pedestal (Padma base)
    pedestal_tiers = [
        (linga_r + 0.12, linga_z_base, linga_z_base + 0.08),
        (linga_r + 0.06, linga_z_base + 0.08, linga_z_base + 0.16),
        (linga_r + 0.02, linga_z_base + 0.16, linga_z_base + 0.20),
    ]
    for r_tier, z0_t, z1_t in pedestal_tiers:
        ring_bot = []
        ring_top = []
        for i in range(n_linga_segs + 1):
            theta = float(i) / float(n_linga_segs) * math.pi
            kx = r_tier * math.cos(theta)
            ky = -r_tier * math.sin(theta)
            ring_bot.append(bm_final.verts.new((kx, ky, z0_t)))
            ring_top.append(bm_final.verts.new((kx, ky, z1_t)))
        for i in range(n_linga_segs):
            f = bm_final.faces.new([ring_bot[i], ring_bot[i + 1], ring_top[i + 1], ring_top[i]])
            f.material_index = MAT_GOLD
            if uv_layer:
                f.loops[0][uv_layer].uv = (float(i)/n_linga_segs, 0.0)
                f.loops[1][uv_layer].uv = (float(i+1)/n_linga_segs, 0.0)
                f.loops[2][uv_layer].uv = (float(i+1)/n_linga_segs, 1.0)
                f.loops[3][uv_layer].uv = (float(i)/n_linga_segs, 1.0)
        v_c_top = bm_final.verts.new((0.0, 0.0, z1_t))
        for i in range(n_linga_segs):
            f = bm_final.faces.new([v_c_top, ring_top[i + 1], ring_top[i]])
            f.material_index = MAT_GOLD
        f_back = bm_final.faces.new([ring_bot[0], ring_top[0], ring_top[-1], ring_bot[-1]])
        f_back.material_index = MAT_GOLD

    # 2. Semicircular Golden Cylindrical Shaft
    z_shaft_base = linga_z_base + 0.20
    n_shaft_rings = 12
    shaft_grid = []
    for iz in range(n_shaft_rings + 1):
        cur_z = z_shaft_base + (linga_z_shaft_top - z_shaft_base) * (float(iz) / float(n_shaft_rings))
        row = []
        for i in range(n_linga_segs + 1):
            theta = float(i) / float(n_linga_segs) * math.pi
            kx = linga_r * math.cos(theta)
            ky = -linga_r * math.sin(theta)
            row.append(bm_final.verts.new((kx, ky, cur_z)))
        shaft_grid.append(row)

    for iz in range(n_shaft_rings):
        for i in range(n_linga_segs):
            v00 = shaft_grid[iz][i]
            v01 = shaft_grid[iz][i + 1]
            v11 = shaft_grid[iz + 1][i + 1]
            v10 = shaft_grid[iz + 1][i]
            f = bm_final.faces.new([v00, v01, v11, v10])
            f.material_index = MAT_GOLD
            if uv_layer:
                f.loops[0][uv_layer].uv = (float(i)/n_linga_segs, float(iz)/n_shaft_rings)
                f.loops[1][uv_layer].uv = (float(i+1)/n_linga_segs, float(iz)/n_shaft_rings)
                f.loops[2][uv_layer].uv = (float(i+1)/n_linga_segs, float(iz+1)/n_shaft_rings)
                f.loops[3][uv_layer].uv = (float(i)/n_linga_segs, float(iz+1)/n_shaft_rings)
        f_back = bm_final.faces.new([shaft_grid[iz][0], shaft_grid[iz + 1][0],
                                     shaft_grid[iz + 1][-1], shaft_grid[iz][-1]])
        f_back.material_index = MAT_GOLD

    # 3. Semicircular Golden Linga Rounded Dome Head (Ellipsoidal Cap)
    dome_head_h = linga_z_apex - linga_z_shaft_top
    head_rings = [shaft_grid[-1]]
    for ir in range(1, n_dome_rings):
        phi = (float(ir) / float(n_dome_rings)) * (math.pi * 0.5)
        cur_z = linga_z_shaft_top + dome_head_h * math.sin(phi)
        scale_r = math.cos(phi)
        row = []
        for i in range(n_linga_segs + 1):
            theta = float(i) / float(n_linga_segs) * math.pi
            kx = linga_r * scale_r * math.cos(theta)
            ky = -linga_r * scale_r * math.sin(theta)
            row.append(bm_final.verts.new((kx, ky, cur_z)))
        head_rings.append(row)

    v_linga_apex = bm_final.verts.new((0.0, 0.0, linga_z_apex))

    for ir in range(n_dome_rings - 1):
        for i in range(n_linga_segs):
            v00 = head_rings[ir][i]
            v01 = head_rings[ir][i + 1]
            v11 = head_rings[ir + 1][i + 1]
            v10 = head_rings[ir + 1][i]
            f = bm_final.faces.new([v00, v01, v11, v10])
            f.material_index = MAT_GOLD
            if uv_layer:
                f.loops[0][uv_layer].uv = (float(i)/n_linga_segs, float(ir)/n_dome_rings)
                f.loops[1][uv_layer].uv = (float(i+1)/n_linga_segs, float(ir)/n_dome_rings)
                f.loops[2][uv_layer].uv = (float(i+1)/n_linga_segs, float(ir+1)/n_dome_rings)
                f.loops[3][uv_layer].uv = (float(i)/n_linga_segs, float(ir+1)/n_dome_rings)
        f_back = bm_final.faces.new([head_rings[ir][0], head_rings[ir + 1][0],
                                     head_rings[ir + 1][-1], head_rings[ir][-1]])
        f_back.material_index = MAT_GOLD

    for i in range(n_linga_segs):
        v0 = head_rings[-1][i]
        v1 = head_rings[-1][i + 1]
        tf = bm_final.faces.new([v0, v1, v_linga_apex])
        tf.material_index = MAT_GOLD

    f_back_top = bm_final.faces.new([head_rings[-1][0], v_linga_apex, head_rings[-1][-1]])
    f_back_top.material_index = MAT_GOLD

    # Rear Facade: Symmetrical Half-Cut Golden Linga on the North Face (Facing Suryakund)
    rear_shaft_grid = []
    for iz in range(n_shaft_rings + 1):
        cur_z = z_shaft_base + (linga_z_shaft_top - z_shaft_base) * (float(iz) / float(n_shaft_rings))
        row = []
        for i in range(n_linga_segs + 1):
            theta = float(i) / float(n_linga_segs) * math.pi
            kx = linga_r * math.cos(theta)
            ky = linga_r * math.sin(theta)
            row.append(bm_final.verts.new((kx, ky, cur_z)))
        rear_shaft_grid.append(row)

    for iz in range(n_shaft_rings):
        for i in range(n_linga_segs):
            v00 = rear_shaft_grid[iz][i]
            v01 = rear_shaft_grid[iz][i + 1]
            v11 = rear_shaft_grid[iz + 1][i + 1]
            v10 = rear_shaft_grid[iz + 1][i]
            f = bm_final.faces.new([v00, v10, v11, v01])
            f.material_index = MAT_GOLD
            if uv_layer:
                f.loops[0][uv_layer].uv = (float(i)/n_linga_segs, float(iz)/n_shaft_rings)
                f.loops[1][uv_layer].uv = (float(i)/n_linga_segs, float(iz+1)/n_shaft_rings)
                f.loops[2][uv_layer].uv = (float(i+1)/n_linga_segs, float(iz+1)/n_shaft_rings)
                f.loops[3][uv_layer].uv = (float(i+1)/n_linga_segs, float(iz)/n_shaft_rings)

    rear_head_rings = [rear_shaft_grid[-1]]
    for ir in range(1, n_dome_rings):
        phi = (float(ir) / float(n_dome_rings)) * (math.pi * 0.5)
        cur_z = linga_z_shaft_top + dome_head_h * math.sin(phi)
        scale_r = math.cos(phi)
        row = []
        for i in range(n_linga_segs + 1):
            theta = float(i) / float(n_linga_segs) * math.pi
            kx = linga_r * scale_r * math.cos(theta)
            ky = linga_r * scale_r * math.sin(theta)
            row.append(bm_final.verts.new((kx, ky, cur_z)))
        rear_head_rings.append(row)

    for ir in range(n_dome_rings - 1):
        for i in range(n_linga_segs):
            v00 = rear_head_rings[ir][i]
            v01 = rear_head_rings[ir][i + 1]
            v11 = rear_head_rings[ir + 1][i + 1]
            v10 = rear_head_rings[ir + 1][i]
            f = bm_final.faces.new([v00, v10, v11, v01])
            f.material_index = MAT_GOLD

    for i in range(n_linga_segs):
        v0 = rear_head_rings[-1][i]
        v1 = rear_head_rings[-1][i + 1]
        tf = bm_final.faces.new([v0, v_linga_apex, v1])
        tf.material_index = MAT_GOLD

    bm_final.verts.ensure_lookup_table()
    bm_final.faces.ensure_lookup_table()
    print(f"[SarpaVasal Replica] Total model geometry: {len(bm_final.verts)} vertices, {len(bm_final.faces)} faces")

    # 4. PBR MATERIALS SETUP
    mat_naga = bpy.data.materials.get("Material.001")
    if not mat_naga:
        mat_naga = bpy.data.materials.new(name="Material.001")
    mat_naga.use_nodes = True
    nnodes = mat_naga.node_tree.nodes
    nlinks = mat_naga.node_tree.links
    nnodes.clear()

    nout = nnodes.new(type='ShaderNodeOutputMaterial')
    nbsdf = nnodes.new(type='ShaderNodeBsdfPrincipled')
    nbsdf.inputs['Roughness'].default_value = 0.65
    nbsdf.inputs['Metallic'].default_value = 0.0
    nlinks.new(nbsdf.outputs['BSDF'], nout.inputs['Surface'])

    if os.path.exists(naga_img_path):
        inaga = bpy.data.images.load(naga_img_path)
        tnaga = nnodes.new(type='ShaderNodeTexImage')
        tnaga.image = inaga
        nlinks.new(tnaga.outputs['Color'], nbsdf.inputs['Base Color'])
        nlinks.new(tnaga.outputs['Alpha'], nbsdf.inputs['Alpha'])

    # Material_SarpaVasal_Granite (Authentic BlendKit Temple Rock)
    mat_granite = bpy.data.materials.get("Material_SarpaVasal_Granite")
    if not mat_granite:
        mat_granite = bpy.data.materials.new(name="Material_SarpaVasal_Granite")
    mat_granite.use_nodes = True
    gnodes = mat_granite.node_tree.nodes
    glinks = mat_granite.node_tree.links
    gnodes.clear()

    gout = gnodes.new(type='ShaderNodeOutputMaterial')
    gbsdf = gnodes.new(type='ShaderNodeBsdfPrincipled')
    gbsdf.inputs['Roughness'].default_value = 0.75
    gbsdf.inputs['Metallic'].default_value = 0.0
    glinks.new(gbsdf.outputs['BSDF'], gout.inputs['Surface'])

    diff_p = os.path.join(tex_dir, "blendkit_rock_albedo.png")
    nor_p = os.path.join(tex_dir, "blendkit_rock_normal.png")
    rough_p = os.path.join(tex_dir, "blendkit_rock_roughness.png")

    if os.path.exists(diff_p):
        idiff = bpy.data.images.load(diff_p)
        tdiff = gnodes.new(type='ShaderNodeTexImage')
        tdiff.image = idiff
        glinks.new(tdiff.outputs['Color'], gbsdf.inputs['Base Color'])
    else:
        gbsdf.inputs['Base Color'].default_value = (0.52, 0.50, 0.48, 1.0)

    if os.path.exists(nor_p):
        inor = bpy.data.images.load(nor_p)
        inor.colorspace_settings.name = 'Non-Color'
        tnor = gnodes.new(type='ShaderNodeTexImage')
        tnor.image = inor
        nmap = gnodes.new(type='ShaderNodeNormalMap')
        nmap.inputs['Strength'].default_value = 0.90
        glinks.new(tnor.outputs['Color'], nmap.inputs['Color'])
        glinks.new(nmap.outputs['Normal'], gbsdf.inputs['Normal'])

    if os.path.exists(rough_p):
        irough = bpy.data.images.load(rough_p)
        irough.colorspace_settings.name = 'Non-Color'
        trough = gnodes.new(type='ShaderNodeTexImage')
        trough.image = irough
        glinks.new(trough.outputs['Color'], gbsdf.inputs['Roughness'])

    # Material_SarpaVasal_Brick (BlenderKit Terracotta Brick)
    mat_brick = bpy.data.materials.get("Material_SarpaVasal_Brick")
    if not mat_brick:
        mat_brick = bpy.data.materials.new(name="Material_SarpaVasal_Brick")
    mat_brick.use_nodes = True
    bnodes = mat_brick.node_tree.nodes
    blinks = mat_brick.node_tree.links
    bnodes.clear()

    bout = bnodes.new(type='ShaderNodeOutputMaterial')
    bbsdf = bnodes.new(type='ShaderNodeBsdfPrincipled')
    bbsdf.inputs['Roughness'].default_value = 0.82
    blinks.new(bbsdf.outputs['BSDF'], bout.inputs['Surface'])

    brick_diff = os.path.join(tex_dir, "stacked_brick_color.jpg")
    brick_nor = os.path.join(tex_dir, "stacked_brick_normal.jpg")
    brick_rough = os.path.join(tex_dir, "stacked_brick_roughness.jpg")

    if os.path.exists(brick_diff):
        ibdiff = bpy.data.images.load(brick_diff)
        tbdiff = bnodes.new(type='ShaderNodeTexImage')
        tbdiff.image = ibdiff
        blinks.new(tbdiff.outputs['Color'], bbsdf.inputs['Base Color'])
    else:
        bbsdf.inputs['Base Color'].default_value = (0.55, 0.25, 0.16, 1.0)

    if os.path.exists(brick_nor):
        ibnor = bpy.data.images.load(brick_nor)
        ibnor.colorspace_settings.name = 'Non-Color'
        tbnor = bnodes.new(type='ShaderNodeTexImage')
        tbnor.image = ibnor
        bnmap = bnodes.new(type='ShaderNodeNormalMap')
        bnmap.inputs['Strength'].default_value = 0.90
        blinks.new(tbnor.outputs['Color'], bnmap.inputs['Color'])
        blinks.new(bnmap.outputs['Normal'], bbsdf.inputs['Normal'])

    if os.path.exists(brick_rough):
        ibrough = bpy.data.images.load(brick_rough)
        ibrough.colorspace_settings.name = 'Non-Color'
        tbrough = bnodes.new(type='ShaderNodeTexImage')
        tbrough.image = ibrough
        blinks.new(tbrough.outputs['Color'], bbsdf.inputs['Roughness'])

    # Material_SarpaVasal_Terracotta (Authentic Terracotta Tiles for End-to-End Dome)
    mat_terracotta = bpy.data.materials.get("Material_SarpaVasal_Terracotta")
    if not mat_terracotta:
        mat_terracotta = bpy.data.materials.new(name="Material_SarpaVasal_Terracotta")
    mat_terracotta.use_nodes = True
    tnodes = mat_terracotta.node_tree.nodes
    tlinks = mat_terracotta.node_tree.links
    tnodes.clear()

    tout = tnodes.new(type='ShaderNodeOutputMaterial')
    tbsdf = tnodes.new(type='ShaderNodeBsdfPrincipled')
    tbsdf.inputs['Roughness'].default_value = 0.80
    tbsdf.inputs['Metallic'].default_value = 0.0
    tlinks.new(tbsdf.outputs['BSDF'], tout.inputs['Surface'])

    terra_diff = os.path.join(tex_dir, "terracotta_tiles_color.png")
    terra_nor = os.path.join(tex_dir, "terracotta_tiles_normal.png")
    terra_rough = os.path.join(tex_dir, "terracotta_tiles_roughness.png")

    if os.path.exists(terra_diff):
        itdiff = bpy.data.images.load(terra_diff)
        ttdiff = tnodes.new(type='ShaderNodeTexImage')
        ttdiff.image = itdiff
        tlinks.new(ttdiff.outputs['Color'], tbsdf.inputs['Base Color'])
    else:
        tbsdf.inputs['Base Color'].default_value = (0.54, 0.27, 0.20, 1.0)

    if os.path.exists(terra_nor):
        itnor = bpy.data.images.load(terra_nor)
        itnor.colorspace_settings.name = 'Non-Color'
        ttnor = tnodes.new(type='ShaderNodeTexImage')
        ttnor.image = itnor
        tnmap = tnodes.new(type='ShaderNodeNormalMap')
        tnmap.inputs['Strength'].default_value = 0.90
        tlinks.new(ttnor.outputs['Color'], tnmap.inputs['Color'])
        tlinks.new(tnmap.outputs['Normal'], tbsdf.inputs['Normal'])

    if os.path.exists(terra_rough):
        itrough = bpy.data.images.load(terra_rough)
        itrough.colorspace_settings.name = 'Non-Color'
        ttrough = tnodes.new(type='ShaderNodeTexImage')
        ttrough.image = itrough
        tlinks.new(ttrough.outputs['Color'], tbsdf.inputs['Roughness'])

    # Material_Gold_Linga (Sacred 24K Temple Gold Linga)
    mat_gold = bpy.data.materials.get("Material_Gold_Linga")
    if not mat_gold:
        mat_gold = bpy.data.materials.new(name="Material_Gold_Linga")
    mat_gold.use_nodes = True
    knodes = mat_gold.node_tree.nodes
    klinks = mat_gold.node_tree.links
    knodes.clear()

    kout = knodes.new(type='ShaderNodeOutputMaterial')
    kbsdf = knodes.new(type='ShaderNodeBsdfPrincipled')
    kbsdf.inputs['Base Color'].default_value = (0.98, 0.82, 0.28, 1.0)
    kbsdf.inputs['Metallic'].default_value = 0.96
    kbsdf.inputs['Roughness'].default_value = 0.15
    klinks.new(kbsdf.outputs['BSDF'], kout.inputs['Surface'])

    # 5. Create Mesh and Object
    new_mesh = bpy.data.meshes.new("SarpaVasal_Authentic_Replica_Mesh")
    bm_final.to_mesh(new_mesh)
    bm_final.free()

    new_mesh.materials.append(mat_naga)        # slot 0: Naga panel
    new_mesh.materials.append(mat_granite)     # slot 1: BlendKit Rock
    new_mesh.materials.append(mat_brick)       # slot 2: Terracotta Brick
    new_mesh.materials.append(mat_terracotta)  # slot 3: Terracotta Dome Roof
    new_mesh.materials.append(mat_gold)        # slot 4: Sacred Gold Linga

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    final_obj = bpy.data.objects.new("SarpaVasal_Gateway", new_mesh)
    bpy.context.collection.objects.link(final_obj)
    bpy.context.view_layer.objects.active = final_obj
    final_obj.select_set(True)

    xs = [v.co.x for v in final_obj.data.vertices]
    ys = [v.co.y for v in final_obj.data.vertices]
    zs = [v.co.z for v in final_obj.data.vertices]
    print(f"[SarpaVasal Replica] Final Dimensions (Blender Coordinates):")
    print(f"  Width  (X): {min(xs):.4f}m to {max(xs):.4f}m (Total: {max(xs)-min(xs):.4f}m)")
    print(f"  Depth  (Y): {min(ys):.4f}m to {max(ys):.4f}m (Total: {max(ys)-min(ys):.4f}m)")
    print(f"  Height (Z): {min(zs):.4f}m to {max(zs):.4f}m (Total: {max(zs)-min(zs):.4f}m)")

    # Save Blend
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"[SarpaVasal Replica] Saved updated {out_blend}")

    # Export to GLB with export_yup=True
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    print(f"[SarpaVasal Replica] Exported GLB to {out_glb} (Size: {os.path.getsize(out_glb)/1024/1024:.2f} MB)")

if __name__ == "__main__":
    build_sarpavasal_replica()
