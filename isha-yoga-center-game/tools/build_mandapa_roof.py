import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Clear all existing data
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create a collection for Mandapa Roof
col = bpy.data.collections.new("Mandapa_Roof")
bpy.context.scene.collection.children.link(col)

# Dimensions
slab_thick = 0.30       # 0.3m thick as requested
half_x = 5.80           # 11.6m width (X)
half_z = 5.30           # 10.6m depth (Z)
slider_w = 0.80         # Edge slider width
inner_hx = half_x - slider_w  # 5.0m
inner_hz = half_z - slider_w  # 4.5m
slider_drop = 0.14      # Slope drop for the slider
fascia_y = slab_thick - slider_drop # 0.16m
dome_r = 0.92           # Radius of the hole under
dome_h = 0.70           # Dome height

# 1. Create Roof Slab Object with Edge Slider and Fascia
# We construct the geometry using BMesh
me_roof = bpy.data.meshes.new("Mesh_Roof_Slab")
bm = bmesh.new()

# Bottom vertices (at y = 0.0, world bottom of the slab resting on pillars/beams)
# Inner soffit and outer boundary
b_sw = bm.verts.new((-half_x, 0.0,  half_z))
b_se = bm.verts.new(( half_x, 0.0,  half_z))
b_ne = bm.verts.new(( half_x, 0.0, -half_z))
b_nw = bm.verts.new((-half_x, 0.0, -half_z))

# Soffit face (pointing down)
f_soffit = bm.faces.new((b_sw, b_se, b_ne, b_nw))

# Outer rim vertices at fascia top (y = fascia_y)
f_sw = bm.verts.new((-half_x, fascia_y,  half_z))
f_se = bm.verts.new(( half_x, fascia_y,  half_z))
f_ne = bm.verts.new(( half_x, fascia_y, -half_z))
f_nw = bm.verts.new((-half_x, fascia_y, -half_z))

# Vertical Fascia faces (4 sides)
# South (+Z)
bm.faces.new((b_sw, b_se, f_se, f_sw))
# East (+X)
bm.faces.new((b_se, b_ne, f_ne, f_se))
# North (-Z)
bm.faces.new((b_ne, b_nw, f_nw, f_ne))
# West (-X)
bm.faces.new((b_nw, b_sw, f_sw, f_nw))

# Inner deck vertices (top of slider, start of flat deck at y = slab_thick = 0.30)
t_sw = bm.verts.new((-inner_hx, slab_thick,  inner_hz))
t_se = bm.verts.new(( inner_hx, slab_thick,  inner_hz))
t_ne = bm.verts.new(( inner_hx, slab_thick, -inner_hz))
t_nw = bm.verts.new((-inner_hx, slab_thick, -inner_hz))

# Slider faces (sloped down from inner deck to outer fascia)
# South slider (+Z)
bm.faces.new((f_sw, f_se, t_se, t_sw))
# East slider (+X)
bm.faces.new((f_se, f_ne, t_ne, t_se))
# North slider (-Z)
bm.faces.new((f_ne, f_nw, t_nw, t_ne))
# West slider (-X)
bm.faces.new((f_nw, f_sw, t_sw, t_nw))

# Center hole cutout on top deck for the dome base (circle of radius dome_r at y = slab_thick)
# This connects the flat terracotta deck cleanly to the dome collar!
dome_plinth_r = dome_r + 0.12 # 1.04m plinth ring radius
segments = 48
c_verts = []
for i in range(segments):
    angle = 2.0 * math.pi * i / segments
    cx = dome_plinth_r * math.cos(angle)
    cz = dome_plinth_r * math.sin(angle)
    c_verts.append(bm.verts.new((cx, slab_thick, cz)))

# Connect inner deck rectangle to the circular dome plinth base
# Helper: connect rectangle (t_sw, t_se, t_ne, t_nw) to circle c_verts
# Quadrants:
# Q0 (East): angles -pi/4 to +pi/4 -> connects to t_ne -> t_se
# Q1 (South): angles +pi/4 to +3pi/4 -> connects to t_se -> t_sw
# Q2 (West): angles +3pi/4 to +5pi/4 -> connects to t_sw -> t_nw
# Q3 (North): angles +5pi/4 to +7pi/4 -> connects to t_nw -> t_ne
q_seg = segments // 4
for i in range(segments):
    v0 = c_verts[i]
    v1 = c_verts[(i + 1) % segments]
    if i < q_seg: # 0 to 11: South-East quadrant
        # Split between East and South
        if i < q_seg // 2:
            bm.faces.new((v0, v1, t_ne))
        else:
            bm.faces.new((v0, v1, t_se))
    elif i < 2 * q_seg:
        if i < 3 * q_seg // 2:
            bm.faces.new((v0, v1, t_se))
        else:
            bm.faces.new((v0, v1, t_sw))
    elif i < 3 * q_seg:
        if i < 5 * q_seg // 2:
            bm.faces.new((v0, v1, t_sw))
        else:
            bm.faces.new((v0, v1, t_nw))
    else:
        if i < 7 * q_seg // 2:
            bm.faces.new((v0, v1, t_nw))
        else:
            bm.faces.new((v0, v1, t_ne))

# Corner bridge triangles
bm.faces.new((t_ne, c_verts[q_seg // 2], t_se))
bm.faces.new((t_se, c_verts[3 * q_seg // 2], t_sw))
bm.faces.new((t_sw, c_verts[5 * q_seg // 2], t_nw))
bm.faces.new((t_nw, c_verts[7 * q_seg // 2], t_ne))

# Recalculate normals
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me_roof)
bm.free()

obj_roof = bpy.data.objects.new("Roof_Slab", me_roof)
col.objects.link(obj_roof)
print("Created Roof Slab with Edge Slider and Flat Deck!")
