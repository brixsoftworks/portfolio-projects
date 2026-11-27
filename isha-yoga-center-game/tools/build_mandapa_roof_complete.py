import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.wm.read_factory_settings(use_empty=True)

col = bpy.data.collections.new("Mandapa_Roof_Collection")
bpy.context.scene.collection.children.link(col)

# Dimensions in meters
slab_thick = 0.30       # Exact user requirement: 0.3m thick
half_x = 5.80           # 11.6m width (X)
half_y = 5.30           # 10.6m depth (Y in Blender, maps to Z in Godot)
slider_w = 0.80         # Edge slider width
inner_hx = half_x - slider_w  # 5.0m
inner_hy = half_y - slider_w  # 4.5m
slider_drop = 0.14      # Slope drop for the slider
fascia_z = slab_thick - slider_drop # 0.16m
dome_r = 0.92           # Radius of the hole under (0.92m)
dome_h = 0.68           # Dome height

# Create Materials
mat_deck = bpy.data.materials.new(name="Roof_Deck_Darker_Copper")
mat_deck.use_nodes = True
bsdf_deck = mat_deck.node_tree.nodes["Principled BSDF"]
bsdf_deck.inputs["Base Color"].default_value = (0.36, 0.17, 0.11, 1.0)
bsdf_deck.inputs["Roughness"].default_value = 0.32
bsdf_deck.inputs["Metallic"].default_value = 0.94

mat_slider = bpy.data.materials.new(name="Roof_Edge_Slider_Dark_Copper")
mat_slider.use_nodes = True
bsdf_slider = mat_slider.node_tree.nodes["Principled BSDF"]
bsdf_slider.inputs["Base Color"].default_value = (0.50, 0.24, 0.16, 1.0)
bsdf_slider.inputs["Roughness"].default_value = 0.26
bsdf_slider.inputs["Metallic"].default_value = 0.94

mat_dome = bpy.data.materials.new(name="Roof_Dome_Dark_Copper")
mat_dome.use_nodes = True
bsdf_dome = mat_dome.node_tree.nodes["Principled BSDF"]
bsdf_dome.inputs["Base Color"].default_value = (0.46, 0.22, 0.15, 1.0)
bsdf_dome.inputs["Roughness"].default_value = 0.20
bsdf_dome.inputs["Metallic"].default_value = 0.96

mat_finial = bpy.data.materials.new(name="Roof_Finial_Brass")
mat_finial.use_nodes = True
bsdf_finial = mat_finial.node_tree.nodes["Principled BSDF"]
bsdf_finial.inputs["Base Color"].default_value = (0.92, 0.76, 0.45, 1.0)
bsdf_finial.inputs["Roughness"].default_value = 0.18
bsdf_finial.inputs["Metallic"].default_value = 0.95

mat_ceiling = bpy.data.materials.new(name="Roof_Ceiling_Wood")
mat_ceiling.use_nodes = True
bsdf_ceiling = mat_ceiling.node_tree.nodes["Principled BSDF"]
bsdf_ceiling.inputs["Base Color"].default_value = (0.28, 0.16, 0.11, 1.0)
bsdf_ceiling.inputs["Roughness"].default_value = 0.55

mat_beams = bpy.data.materials.new(name="Roof_Beams_Wood")
mat_beams.use_nodes = True
bsdf_beams = mat_beams.node_tree.nodes["Principled BSDF"]
bsdf_beams.inputs["Base Color"].default_value = (0.24, 0.14, 0.09, 1.0)
bsdf_beams.inputs["Roughness"].default_value = 0.55

# -------------------------------------------------------------
# 1. ROOF SLAB OBJECT (Deck + Edge Slider + Fascia + Soffit)
# In Blender: Z is UP, X is Width, Y is Depth
# -------------------------------------------------------------
me_roof = bpy.data.meshes.new("Roof_Slab")
bm = bmesh.new()

# Bottom Soffit vertices at z = 0.0
b_sw = bm.verts.new((-half_x, -half_y, 0.0))
b_se = bm.verts.new(( half_x, -half_y, 0.0))
b_ne = bm.verts.new(( half_x,  half_y, 0.0))
b_nw = bm.verts.new((-half_x,  half_y, 0.0))

f_soffit = bm.faces.new((b_sw, b_se, b_ne, b_nw))
f_soffit.material_index = 4 # Ceiling wood material

# Outer rim vertices at fascia top (z = fascia_z = 0.16m)
f_sw = bm.verts.new((-half_x, -half_y, fascia_z))
f_se = bm.verts.new(( half_x, -half_y, fascia_z))
f_ne = bm.verts.new(( half_x,  half_y, fascia_z))
f_nw = bm.verts.new((-half_x,  half_y, fascia_z))

# 4 Fascia faces (vertical outer drip edge)
f_fascia_s = bm.faces.new((b_sw, b_se, f_se, f_sw))
f_fascia_e = bm.faces.new((b_se, b_ne, f_ne, f_se))
f_fascia_n = bm.faces.new((b_ne, b_nw, f_nw, f_ne))
f_fascia_w = bm.faces.new((b_nw, b_sw, f_sw, f_nw))
for f in [f_fascia_s, f_fascia_e, f_fascia_n, f_fascia_w]:
    f.material_index = 1 # Slider/granite trim

# Inner deck vertices at top of slider (z = slab_thick = 0.30m)
t_sw = bm.verts.new((-inner_hx, -inner_hy, slab_thick))
t_se = bm.verts.new(( inner_hx, -inner_hy, slab_thick))
t_ne = bm.verts.new(( inner_hx,  inner_hy, slab_thick))
t_nw = bm.verts.new((-inner_hx,  inner_hy, slab_thick))

# 4 Edge Slider faces (sloped down from inner deck to outer fascia)
f_slide_s = bm.faces.new((f_sw, f_se, t_se, t_sw))
f_slide_e = bm.faces.new((f_se, f_ne, t_ne, t_se))
f_slide_n = bm.faces.new((f_ne, f_nw, t_nw, t_ne))
f_slide_w = bm.faces.new((f_nw, f_sw, t_sw, t_nw))
for f in [f_slide_s, f_slide_e, f_slide_n, f_slide_w]:
    f.material_index = 1 # Slider/granite trim

# Circular hole on top deck for the dome plinth
plinth_r = dome_r + 0.12 # 1.04m radius
segs = 48
c_verts = []
for i in range(segs):
    ang = 2.0 * math.pi * i / segs
    cx = plinth_r * math.cos(ang)
    cy = plinth_r * math.sin(ang)
    c_verts.append(bm.verts.new((cx, cy, slab_thick)))

# Triangulate / quad-bridge between inner deck rectangle and plinth circle
q = segs // 4
for i in range(segs):
    v0 = c_verts[i]
    v1 = c_verts[(i + 1) % segs]
    face = None
    if i < q:
        if i < q // 2:
            face = bm.faces.new((v0, v1, t_ne))
        else:
            face = bm.faces.new((v0, v1, t_se))
    elif i < 2 * q:
        if i < 3 * q // 2:
            face = bm.faces.new((v0, v1, t_se))
        else:
            face = bm.faces.new((v0, v1, t_sw))
    elif i < 3 * q:
        if i < 5 * q // 2:
            face = bm.faces.new((v0, v1, t_sw))
        else:
            face = bm.faces.new((v0, v1, t_nw))
    else:
        if i < 7 * q // 2:
            face = bm.faces.new((v0, v1, t_nw))
        else:
            face = bm.faces.new((v0, v1, t_ne))
    if face:
        face.material_index = 0 # Roof Deck Terracotta

# Corner infills
f_c1 = bm.faces.new((t_ne, c_verts[q // 2], t_se))
f_c2 = bm.faces.new((t_se, c_verts[3 * q // 2], t_sw))
f_c3 = bm.faces.new((t_sw, c_verts[5 * q // 2], t_nw))
f_c4 = bm.faces.new((t_nw, c_verts[7 * q // 2], t_ne))
for f in [f_c1, f_c2, f_c3, f_c4]:
    f.material_index = 0

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me_roof)
bm.free()

obj_roof = bpy.data.objects.new("Roof_Slab", me_roof)
col.objects.link(obj_roof)
for mat in [mat_deck, mat_slider, mat_dome, mat_finial, mat_ceiling, mat_beams]:
    obj_roof.data.materials.append(mat)

# -------------------------------------------------------------
# 2. CENTRAL DOME (Plinth + Parabolic Dome + Kalasam Finial)
# -------------------------------------------------------------
me_dome = bpy.data.meshes.new("Roof_Dome")
bm_d = bmesh.new()

# A. Plinth cylinder (from z = slab_thick to z = slab_thick + 0.06m)
plinth_h = 0.06
p_base_z = slab_thick
p_top_z = slab_thick + plinth_h
p_bot_verts = []
p_top_verts = []
for i in range(segs):
    ang = 2.0 * math.pi * i / segs
    cx = plinth_r * math.cos(ang)
    cy = plinth_r * math.sin(ang)
    p_bot_verts.append(bm_d.verts.new((cx, cy, p_base_z)))
    p_top_verts.append(bm_d.verts.new((cx, cy, p_top_z)))

for i in range(segs):
    v0 = p_bot_verts[i]
    v1 = p_bot_verts[(i + 1) % segs]
    v2 = p_top_verts[(i + 1) % segs]
    v3 = p_top_verts[i]
    f = bm_d.faces.new((v0, v1, v2, v3))
    f.material_index = 2 # Dome Charcoal

# Plinth step inset from plinth_r to dome_r at z = p_top_z
dome_base_verts = []
for i in range(segs):
    ang = 2.0 * math.pi * i / segs
    cx = dome_r * math.cos(ang)
    cy = dome_r * math.sin(ang)
    dome_base_verts.append(bm_d.verts.new((cx, cy, p_top_z)))

for i in range(segs):
    v0 = p_top_verts[i]
    v1 = p_top_verts[(i + 1) % segs]
    v2 = dome_base_verts[(i + 1) % segs]
    v3 = dome_base_verts[i]
    f = bm_d.faces.new((v0, v1, v2, v3))
    f.material_index = 2

# B. Parabolic Dome Shell (rings of vertices)
dome_rings = 32
ring_verts = [dome_base_verts]
for r in range(1, dome_rings):
    frac = float(r) / float(dome_rings)
    theta = frac * (math.pi / 2.0)
    z_curr = p_top_z + dome_h * math.sin(theta)
    r_curr = dome_r * math.cos(theta)
    curr_ring = []
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        cx = r_curr * math.cos(ang)
        cy = r_curr * math.sin(ang)
        curr_ring.append(bm_d.verts.new((cx, cy, z_curr)))
    ring_verts.append(curr_ring)

# Connect dome rings
for r in range(dome_rings - 1):
    r0 = ring_verts[r]
    r1 = ring_verts[r + 1]
    for i in range(segs):
        v0 = r0[i]
        v1 = r0[(i + 1) % segs]
        v2 = r1[(i + 1) % segs]
        v3 = r1[i]
        f = bm_d.faces.new((v0, v1, v2, v3))
        f.material_index = 2 # Dome Charcoal

top_ring = ring_verts[-1]

# C. Kalasam Finial (Sacred Golden/Brass Temple Pinnacle)
finial_base_z = p_top_z + dome_h
finial_neck_r = 0.08
finial_pot_r = 0.12
finial_neck_z = finial_base_z + 0.05
finial_pot_z = finial_neck_z + 0.10
finial_spire_z = finial_pot_z + 0.12

# Neck ring
neck_verts = []
for i in range(segs):
    ang = 2.0 * math.pi * i / segs
    cx = finial_neck_r * math.cos(ang)
    cy = finial_neck_r * math.sin(ang)
    neck_verts.append(bm_d.verts.new((cx, cy, finial_neck_z)))

for i in range(segs):
    v0 = top_ring[i]
    v1 = top_ring[(i + 1) % segs]
    v2 = neck_verts[(i + 1) % segs]
    v3 = neck_verts[i]
    f = bm_d.faces.new((v0, v1, v2, v3))
    f.material_index = 2

# Pot bulge ring
pot_verts = []
for i in range(segs):
    ang = 2.0 * math.pi * i / segs
    cx = finial_pot_r * math.cos(ang)
    cy = finial_pot_r * math.sin(ang)
    pot_verts.append(bm_d.verts.new((cx, cy, finial_pot_z)))

for i in range(segs):
    v0 = neck_verts[i]
    v1 = neck_verts[(i + 1) % segs]
    v2 = pot_verts[(i + 1) % segs]
    v3 = pot_verts[i]
    f = bm_d.faces.new((v0, v1, v2, v3))
    f.material_index = 3 # Finial Brass

# Apex tip vertex
apex_vert = bm_d.verts.new((0.0, 0.0, finial_spire_z))
for i in range(segs):
    v0 = pot_verts[i]
    v1 = pot_verts[(i + 1) % segs]
    f = bm_d.faces.new((v0, v1, apex_vert))
    f.material_index = 3 # Finial Brass

bmesh.ops.recalc_face_normals(bm_d, faces=bm_d.faces)
bm_d.to_mesh(me_dome)
bm_d.free()

obj_dome = bpy.data.objects.new("Roof_Dome", me_dome)
col.objects.link(obj_dome)
for mat in [mat_deck, mat_slider, mat_dome, mat_finial, mat_ceiling, mat_beams]:
    obj_dome.data.materials.append(mat)

# -------------------------------------------------------------
# 3. UNDER-ROOF SUPPORT BEAMS (Lintels spanning the 4 pillars)
# -------------------------------------------------------------
# Pillar coordinates relative to center:
# X = +/- 5.0m, Y = +/- 4.4m
# Beam width = 0.52m, depth = 0.24m (z = -0.24 to 0.0)
me_beams = bpy.data.meshes.new("Roof_Support_Beams")
bm_b = bmesh.new()

def add_beam_box(bm_target, min_v, max_v):
    x0, y0, z0 = min_v
    x1, y1, z1 = max_v
    v_000 = bm_target.verts.new((x0, y0, z0))
    v_100 = bm_target.verts.new((x1, y0, z0))
    v_110 = bm_target.verts.new((x1, y1, z0))
    v_010 = bm_target.verts.new((x0, y1, z0))
    v_001 = bm_target.verts.new((x0, y0, z1))
    v_101 = bm_target.verts.new((x1, y0, z1))
    v_111 = bm_target.verts.new((x1, y1, z1))
    v_011 = bm_target.verts.new((x0, y1, z1))
    faces = [
        bm_target.faces.new((v_000, v_100, v_110, v_010)), # -Z (bottom)
        bm_target.faces.new((v_101, v_001, v_011, v_111)), # +Z (top)
        bm_target.faces.new((v_000, v_010, v_011, v_001)), # -X
        bm_target.faces.new((v_100, v_101, v_111, v_110)), # +X
        bm_target.faces.new((v_000, v_001, v_101, v_100)), # -Y
        bm_target.faces.new((v_010, v_110, v_111, v_011)), # +Y
    ]
    for f in faces:
        f.material_index = 5 # Beams Wood Material

bw = 0.26 # half width = 0.26 (0.52m total)
# Beam 1: Front beam along X (Y = -4.4m, X from -5.6 to +5.6)
add_beam_box(bm_b, (-5.6, -4.4 - bw, -0.24), (5.6, -4.4 + bw, 0.0))
# Beam 2: Back beam along X (Y = +4.4m, X from -5.6 to +5.6)
add_beam_box(bm_b, (-5.6,  4.4 - bw, -0.24), (5.6,  4.4 + bw, 0.0))
# Beam 3: Left beam along Y (X = -5.0m, Y from -4.4 to +4.4)
add_beam_box(bm_b, (-5.0 - bw, -4.4, -0.24), (-5.0 + bw,  4.4, 0.0))
# Beam 4: Right beam along Y (X = +5.0m, Y from -4.4 to +4.4)
add_beam_box(bm_b, ( 5.0 - bw, -4.4, -0.24), ( 5.0 + bw,  4.4, 0.0))

bmesh.ops.recalc_face_normals(bm_b, faces=bm_b.faces)
bm_b.to_mesh(me_beams)
bm_b.free()

obj_beams = bpy.data.objects.new("Roof_Support_Beams", me_beams)
col.objects.link(obj_beams)
for mat in [mat_deck, mat_slider, mat_dome, mat_finial, mat_ceiling, mat_beams]:
    obj_beams.data.materials.append(mat)

# -------------------------------------------------------------
# Join meshes into a single cohesive Mandapa_Roof object
# -------------------------------------------------------------
bpy.context.view_layer.objects.active = obj_roof
obj_roof.select_set(True)
obj_dome.select_set(True)
obj_beams.select_set(True)
bpy.ops.object.join()
obj_roof.name = "Mandapa_Roof"

# Ensure smooth shading on dome faces, flat shading on slab/beams
for poly in obj_roof.data.polygons:
    if poly.material_index in [2, 3]:
        poly.use_smooth = True
    else:
        poly.use_smooth = False

# Auto generate clean UVs
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

# Export to GLB
out_path = "/home/mullainathan/Games/IshaGodot/assets/mandapa_roof.glb"
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',
    use_selection=True,
    export_apply=True
)
print("Successfully generated and exported: ", out_path)
