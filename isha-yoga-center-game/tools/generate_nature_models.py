import bpy
import bmesh
import math
import mathutils

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

# ------------------------------------------------------------------------------
# 1. BUILD ARECA PALM (Betel Nut Palm)
# ------------------------------------------------------------------------------
def build_areca_palm():
    clear_scene()
    bm = bmesh.new()

    # Materials
    mat_trunk = bpy.data.materials.new(name="Areca_Trunk")
    mat_trunk.use_nodes = True
    bsdf_trunk = mat_trunk.node_tree.nodes.get("Principled BSDF")
    bsdf_trunk.inputs["Base Color"].default_value = (0.55, 0.58, 0.50, 1.0) # Grey-green ringed trunk
    bsdf_trunk.inputs["Roughness"].default_value = 0.75

    mat_shaft = bpy.data.materials.new(name="Areca_Crownshaft")
    mat_shaft.use_nodes = True
    bsdf_shaft = mat_shaft.node_tree.nodes.get("Principled BSDF")
    bsdf_shaft.inputs["Base Color"].default_value = (0.22, 0.45, 0.15, 1.0) # Bright lime-green crownshaft
    bsdf_shaft.inputs["Roughness"].default_value = 0.40

    mat_frond = bpy.data.materials.new(name="Areca_Frond")
    mat_frond.use_nodes = True
    bsdf_frond = mat_frond.node_tree.nodes.get("Principled BSDF")
    bsdf_frond.inputs["Base Color"].default_value = (0.18, 0.42, 0.12, 1.0) # Rich emerald palm green
    bsdf_frond.inputs["Roughness"].default_value = 0.55

    # Trunk: height 10.5m, radius 0.14m tapering to 0.12m with rings
    rings = 32
    trunk_h = 10.5
    dz = trunk_h / rings
    verts_prev = []
    
    # Base flare
    for i in range(12):
        ang = i * 2.0 * math.pi / 12
        x = math.cos(ang) * 0.22
        y = math.sin(ang) * 0.22
        verts_prev.append(bm.verts.new((x, y, 0.0)))
    
    for r in range(1, rings + 1):
        z = r * dz
        rad = 0.14 - (r / rings) * 0.02
        # Ring node bulging
        if r % 2 == 0:
            rad += 0.012
        verts_curr = []
        for i in range(12):
            ang = i * 2.0 * math.pi / 12
            x = math.cos(ang) * rad
            y = math.sin(ang) * rad
            verts_curr.append(bm.verts.new((x, y, z)))
        for i in range(12):
            i_next = (i + 1) % 12
            bm.faces.new([verts_prev[i], verts_prev[i_next], verts_curr[i_next], verts_curr[i]])
        verts_prev = verts_curr

    # Crownshaft: height 1.5m above trunk
    shaft_h = 1.5
    for s in range(1, 6):
        z = trunk_h + s * (shaft_h / 5.0)
        rad = 0.13 - s * 0.005
        verts_curr = []
        for i in range(12):
            ang = i * 2.0 * math.pi / 12
            x = math.cos(ang) * rad
            y = math.sin(ang) * rad
            verts_curr.append(bm.verts.new((x, y, z)))
        for i in range(12):
            i_next = (i + 1) % 12
            f = bm.faces.new([verts_prev[i], verts_prev[i_next], verts_curr[i_next], verts_curr[i]])
            f.material_index = 1 # Crownshaft material
        verts_prev = verts_curr

    # Fronds at top of crownshaft (Z = 12.0m)
    crown_z = trunk_h + shaft_h
    num_fronds = 14
    for fi in range(num_fronds):
        f_ang = fi * 2.0 * math.pi / num_fronds + (fi % 2) * 0.15
        elev = math.radians(35.0 + (fi % 3) * 12.0)
        length = 2.8 + (fi % 2) * 0.4
        f_segs = 8
        f_prev_left = None
        f_prev_right = None
        for si in range(f_segs + 1):
            t = si / float(f_segs)
            # Arching curve: rises then droops
            dist_horiz = t * length * math.cos(elev)
            droop = math.sin(t * math.pi * 0.5) * 0.6 - (t * t * 1.2)
            fz = crown_z + math.sin(elev) * length * t + droop
            fx = math.cos(f_ang) * dist_horiz
            fy = math.sin(f_ang) * dist_horiz
            
            # Frond width
            fw = math.sin(t * math.pi) * 0.38 + 0.05
            perp_x = -math.sin(f_ang) * fw * 0.5
            perp_y =  math.cos(f_ang) * fw * 0.5
            
            vl = bm.verts.new((fx + perp_x, fy + perp_y, fz))
            vr = bm.verts.new((fx - perp_x, fy - perp_y, fz))
            
            if f_prev_left and f_prev_right:
                face = bm.faces.new([f_prev_left, f_prev_right, vr, vl])
                face.material_index = 2 # Frond material
            f_prev_left = vl
            f_prev_right = vr

    mesh = bpy.data.meshes.new("Areca_Palm_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_trunk)
    mesh.materials.append(mat_shaft)
    mesh.materials.append(mat_frond)

    obj = bpy.data.objects.new("Areca_Palm", mesh)
    bpy.context.collection.objects.link(obj)

    out_path = "/home/mullainathan/Games/IshaGodot/assets/models/areca_palm.glb"
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', use_selection=False)
    print("Exported:", out_path)

# ------------------------------------------------------------------------------
# 2. BUILD INDIAN BROADLEAF SHADE TREE (Neem / Tamarind)
# ------------------------------------------------------------------------------
def build_indian_shade_tree():
    clear_scene()
    bm = bmesh.new()

    mat_bark = bpy.data.materials.new(name="Neem_Bark")
    mat_bark.use_nodes = True
    bsdf_bark = mat_bark.node_tree.nodes.get("Principled BSDF")
    bsdf_bark.inputs["Base Color"].default_value = (0.28, 0.22, 0.17, 1.0) # Deep rugged brown bark
    bsdf_bark.inputs["Roughness"].default_value = 0.88

    mat_leaf = bpy.data.materials.new(name="Neem_Leaves")
    mat_leaf.use_nodes = True
    bsdf_leaf = mat_leaf.node_tree.nodes.get("Principled BSDF")
    bsdf_leaf.inputs["Base Color"].default_value = (0.16, 0.36, 0.12, 1.0) # Lush Indian neem foliage green
    bsdf_leaf.inputs["Roughness"].default_value = 0.65

    # Trunk: height 3.2m, radius 0.5m tapering to 0.38m
    segs = 8
    rings = 10
    dz = 3.2 / rings
    verts_prev = []
    for i in range(segs):
        ang = i * 2.0 * math.pi / segs
        r = 0.55 + 0.08 * math.sin(ang * 3) # organic fluting
        verts_prev.append(bm.verts.new((math.cos(ang) * r, math.sin(ang) * r, 0.0)))
    
    for ring in range(1, rings + 1):
        z = ring * dz
        rad = 0.55 - (ring / rings) * 0.18
        verts_curr = []
        for i in range(segs):
            ang = i * 2.0 * math.pi / segs
            r = rad + 0.03 * math.sin(ang * 2 + ring)
            verts_curr.append(bm.verts.new((math.cos(ang) * r, math.sin(ang) * r, z)))
        for i in range(segs):
            i_next = (i + 1) % segs
            bm.faces.new([verts_prev[i], verts_prev[i_next], verts_curr[i_next], verts_curr[i]])
        verts_prev = verts_curr

    # 4 Main Spreading Branches
    branches = [
        (math.radians(30),  math.radians(45), 3.2, 4.2),
        (math.radians(120), math.radians(50), 3.0, 4.0),
        (math.radians(210), math.radians(40), 3.2, 4.4),
        (math.radians(300), math.radians(52), 3.1, 4.1),
        (0.0, math.radians(80), 3.2, 3.5), # Central upward branch
    ]

    foliage_centers = []

    for b_az, b_el, b_start_z, b_len in branches:
        b_steps = 6
        b_prev = []
        start_x = 0.2 * math.cos(b_az)
        start_y = 0.2 * math.sin(b_az)
        for i in range(6):
            ang = i * 2.0 * math.pi / 6
            b_prev.append(bm.verts.new((start_x + math.cos(ang)*0.22, start_y + math.sin(ang)*0.22, b_start_z)))
        
        for step in range(1, b_steps + 1):
            t = step / float(b_steps)
            dist_h = t * b_len * math.cos(b_el)
            bz = b_start_z + t * b_len * math.sin(b_el) + math.sin(t * math.pi) * 0.3
            bx = math.cos(b_az) * dist_h
            by = math.sin(b_az) * dist_h
            b_rad = 0.22 * (1.0 - t * 0.6)
            b_curr = []
            for i in range(6):
                ang = i * 2.0 * math.pi / 6
                b_curr.append(bm.verts.new((bx + math.cos(ang)*b_rad, by + math.sin(ang)*b_rad, bz)))
            for i in range(6):
                i_next = (i + 1) % 6
                bm.faces.new([b_prev[i], b_prev[i_next], b_curr[i_next], b_curr[i]])
            b_prev = b_curr
        
        foliage_centers.append((bx, by, bz))

    # Add lush foliage canopy masses around branch tips and crown center
    foliage_nodes = [
        (0.0, 0.0, 7.5, 3.2, 2.2), # central top dome
    ]
    for fx, fy, fz in foliage_centers:
        foliage_nodes.append((fx, fy, fz + 0.5, 2.8, 1.9))
        foliage_nodes.append((fx * 0.65, fy * 0.65, fz - 0.4, 2.2, 1.6))

    for cx, cy, cz, rxz, ry in foliage_nodes:
        # Create an icosphere-like rounded organic leaf blob
        sub_bm = bmesh.new()
        bmesh.ops.create_icosphere(sub_bm, subdivisions=2, radius=1.0)
        for v in sub_bm.verts:
            # Add organic lumpiness
            noise = math.sin(v.co.x * 4.0) * math.cos(v.co.y * 4.0) * 0.18
            v.co.x = cx + v.co.x * rxz * (1.0 + noise)
            v.co.y = cy + v.co.y * rxz * (1.0 + noise)
            v.co.z = cz + v.co.z * ry * (1.0 + noise)
        for f in sub_bm.faces:
            verts_new = [bm.verts.new(v.co) for v in f.verts]
            face = bm.faces.new(verts_new)
            face.material_index = 1 # Neem Leaves material
        sub_bm.free()

    mesh = bpy.data.meshes.new("Indian_Shade_Tree_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_bark)
    mesh.materials.append(mat_leaf)

    obj = bpy.data.objects.new("Indian_Shade_Tree", mesh)
    bpy.context.collection.objects.link(obj)

    out_path = "/home/mullainathan/Games/IshaGodot/assets/models/indian_shade_tree.glb"
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', use_selection=False)
    print("Exported:", out_path)

# ------------------------------------------------------------------------------
# 3. BUILD TROPICAL FLOWERING SHRUB (Bougainvillea / Tropical Bush)
# ------------------------------------------------------------------------------
def build_tropical_shrub():
    clear_scene()
    bm = bmesh.new()

    mat_shrub_leaf = bpy.data.materials.new(name="Shrub_Leaves")
    mat_shrub_leaf.use_nodes = True
    bsdf_leaf = mat_shrub_leaf.node_tree.nodes.get("Principled BSDF")
    bsdf_leaf.inputs["Base Color"].default_value = (0.22, 0.48, 0.16, 1.0) # Lush bush green
    bsdf_leaf.inputs["Roughness"].default_value = 0.55

    mat_flower = bpy.data.materials.new(name="Bougainvillea_Blossoms")
    mat_flower.use_nodes = True
    bsdf_flower = mat_flower.node_tree.nodes.get("Principled BSDF")
    bsdf_flower.inputs["Base Color"].default_value = (0.86, 0.15, 0.42, 1.0) # Rich magenta bougainvillea blossom
    bsdf_flower.inputs["Roughness"].default_value = 0.60

    # Shrub clusters
    clusters = [
        ( 0.0,   0.0,  0.8, 1.25, 0.8),
        (-0.55,  0.3,  0.65, 0.95, 0.65),
        ( 0.60, -0.2,  0.70, 1.05, 0.70),
        ( 0.20,  0.65, 0.60, 0.90, 0.60),
        (-0.40, -0.55, 0.62, 0.92, 0.62),
    ]

    for cx, cy, cz, rxz, ry in clusters:
        sub_bm = bmesh.new()
        bmesh.ops.create_icosphere(sub_bm, subdivisions=2, radius=1.0)
        for v in sub_bm.verts:
            noise = math.sin(v.co.x * 5.0) * math.cos(v.co.y * 5.0) * 0.15
            v.co.x = cx + v.co.x * rxz * (1.0 + noise)
            v.co.y = cy + v.co.y * rxz * (1.0 + noise)
            v.co.z = cz + v.co.z * ry * (1.0 + noise)
        for f in sub_bm.faces:
            verts_new = [bm.verts.new(v.co) for v in f.verts]
            face = bm.faces.new(verts_new)
            # 25% of faces on top are bougainvillea flowers
            if face.normal.z > 0.4 and (abs(face.calc_center_median().x * 7.0) % 1.0 < 0.35):
                face.material_index = 1 # Flower material
            else:
                face.material_index = 0 # Shrub leaf material
        sub_bm.free()

    mesh = bpy.data.meshes.new("Tropical_Shrub_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_shrub_leaf)
    mesh.materials.append(mat_flower)

    obj = bpy.data.objects.new("Tropical_Shrub", mesh)
    bpy.context.collection.objects.link(obj)

    out_path = "/home/mullainathan/Games/IshaGodot/assets/models/tropical_shrub.glb"
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', use_selection=False)
    print("Exported:", out_path)

if __name__ == "__main__":
    build_areca_palm()
    build_indian_shade_tree()
    build_tropical_shrub()
