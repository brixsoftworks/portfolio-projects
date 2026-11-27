"""
Linga Bhairavi Temple - Complete Exterior & Authentic Grand Stepped Interior Construction
Isha Yoga Center, Coimbatore

Faithfully replicates both the authentic exterior and sacred interior architecture of Linga Bhairavi Temple
based on ground-truth visitor photography, architectural records, and sacred geometry:

EXTERIOR:
- Adhishthana: Low polished dark granite platform with 2 wide shallow steps.
- Colonnade: 4 massive rock-hewn dark granite monolithic columns with sculpted crouching gana beast
  pedestals and Padma-pitha lotus cushion toruses.
- Prahara Vilakku Diya Wall: Light warm sandstone ashlar wall with hundreds of 3D triangular
  lamp niches, each holding a clay diya saucer and glowing golden flame tip.
- Entrance Portal: Dark stone doorframe, open dark teak double doors with brass boss rivets,
  and sacred Bhairavi Yantra plaque above the lintel.
- Cantilevered Flat Canopy: Modern horizontal roof with sleek dark metallic fascia and a rich
  geometric coffered teak wood ceiling with recessed downlights.
- Sacred Polygonal / Triangular Sanctum: Expansive 30-meter deep inverted trapezoidal-to-triangular envelope.
- Forecourt & Amenities: Paved courtyard apron, reflecting water pool, and diamond lattice screens.

GRAND INTERIOR (SANCTUM SANCTORUM & MEDITATION MANDAPAM):
- Expansive Temple Hall: 30 meters deep, 25 meters wide, clear height of 5.60 meters.
- Grand Entrance Descent Steps: 3 wide shallow dressed granite steps (Z: 0.40m -> 0.04m) transitioning
  devotees from the entrance threshold down into the sunken meditation hall.
- Sunken Meditation Hall Floor: Mirror-polished black granite flagstones with high specular reflection.
- Tiered Devotee Seating Steps: 3 broad stone seating terraces along both left and right flanks
  (Z: 0.24m, 0.44m, 0.64m) with dressed bullnose granite curbs and traditional woven meditation asanas.
- Sanctum Ascending Steps: 3 grand ascending granite steps (Y: -20.0m to -22.4m, Z: 0.04m -> 0.64m)
  leading devotees up to the sacred Garbhagriha dais, flanked by antique brass balustrades.
- Flanking Ceremonial Urulis: Large turned brass offering bowls at the base of the sanctum steps,
  filled with water, floating fresh pink lotus blossoms, and burning ghee wicks.
- Monumental Inner Colonnade: 8 massive rock-hewn granite columns (4 pairs flanking the central aisle)
  with crouching gana beast bases, padma-pitha lotus cushion toruses, fluted shafts, and carved corbel brackets.
- Inner Sanctum Portal (Torana): Carved black granite gateway framing the sacred Garbhagriha.
- Ceremonial Crimson Runner Carpet: Leading continuously down the sunken hall and up onto the sanctum dais.
- Exposed Teak Timber Ceiling: Heavy dark timber cross-beams and purlins with suspended bronze temple bells (Ghanta).
- Authentic Devi Shrine: Curved 3D Linga Bhairavi shrine on elevated Peedam with authentic PBR albedo, normal,
  roughness, metallic, and emission maps capturing the 8-foot Devi Linga, Trinetra, golden nose ring,
  jasmine garland, sacred silk vastram, Ashtabhuja 8-armed Prabhavali backdrop, and top Bhairavi Yantra.
- Peedam (Altar Base): Molded dark granite pedestal with fresh flower offerings, standing brass oil lamp
  (Kuthuvilakku), bronze offering chests (Hundi), and curved guard railings (Kattalai).
- Inner Diya Matrix: Wall-mounted brass oil lamps on the interior dark granite side walls extending 28 meters deep.
- Balanced Architectural Lighting: Dual-side soft spotlights, warm candle bounce, and hall aisle downlights.
"""

import bpy
import bmesh
import math
import os
import shutil
import numpy as np
from mathutils import Vector, Matrix, Euler, Quaternion

# Paths
TEXTURES_DIR = "/home/mullainathan/Games/IshaGodot/assets/textures"
OUTPUT_MODEL_PATH = "/home/mullainathan/Games/IshaGodot/assets/models/lingabhairavi_temple.glb"
OUTPUT_BLEND_PATH = "/home/mullainathan/Games/IshaGodot/assets/models/lingabhairavi_temple.blend"
CAPTURES_DIR = "/home/mullainathan/Games/IshaGodot/captures/lingabhairavi"
ARTIFACTS_DIR = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures"

os.makedirs(CAPTURES_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


# ==============================================================================
# UTILITIES
# ==============================================================================
def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    main_col = bpy.data.collections.new("LingaBhairavi_Master")
    bpy.context.scene.collection.children.link(main_col)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[0]


def apply_smart_uv(obj):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)


def apply_floor_planar_uv(obj, uv_scale=1.0):
    me = obj.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv_layer = me.uv_layers.active.data
    for poly in me.polygons:
        for loop_idx in poly.loop_indices:
            vert_idx = me.loops[loop_idx].vertex_index
            co = me.vertices[vert_idx].co
            # Seamless continuous world-aligned planar projection without cuts or glitch lines
            uv_layer[loop_idx].uv = (co.x * uv_scale, co.y * uv_scale)


def apply_box_uv(obj, uv_scale=1.0):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    cube_size = 1.0 / uv_scale if uv_scale > 0 else 1.0
    bpy.ops.uv.cube_project(cube_size=cube_size, correct_aspect=True, clip_to_bounds=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)


def point_at(obj, target):
    direction = target - obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj.rotation_euler = rot_quat.to_euler()


def setup_pbr_material(mat, albedo_path=None, norm_path=None, rough_path=None, metal_path=None):
    if not mat:
        return
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        for n in nodes:
            if n.type == 'BSDF_PRINCIPLED':
                bsdf = n
                break
    if not bsdf:
        return

    # Base Color
    if albedo_path and os.path.exists(albedo_path):
        img_alb = bpy.data.images.load(albedo_path)
        img_alb.pack()
        tex_alb = None
        for n in nodes:
            if n.type == 'TEX_IMAGE' and n.name == 'Image Texture':
                tex_alb = n
                break
        if not tex_alb:
            tex_alb = nodes.new("ShaderNodeTexImage")
        tex_alb.image = img_alb
        links.new(tex_alb.outputs["Color"], bsdf.inputs["Base Color"])
        if "Alpha" in tex_alb.outputs and "Alpha" in bsdf.inputs:
            links.new(tex_alb.outputs["Alpha"], bsdf.inputs["Alpha"])

    # Normal Map
    if norm_path and os.path.exists(norm_path):
        img_norm = bpy.data.images.load(norm_path)
        img_norm.colorspace_settings.name = 'Non-Color'
        img_norm.pack()
        tex_norm = nodes.new("ShaderNodeTexImage")
        tex_norm.image = img_norm
        norm_node = nodes.new("ShaderNodeNormalMap")
        norm_node.inputs["Strength"].default_value = 1.0
        links.new(tex_norm.outputs["Color"], norm_node.inputs["Color"])
        links.new(norm_node.outputs["Normal"], bsdf.inputs["Normal"])

    # Roughness
    if rough_path and os.path.exists(rough_path):
        img_rough = bpy.data.images.load(rough_path)
        img_rough.colorspace_settings.name = 'Non-Color'
        img_rough.pack()
        tex_rough = nodes.new("ShaderNodeTexImage")
        tex_rough.image = img_rough
        links.new(tex_rough.outputs["Color"], bsdf.inputs["Roughness"])

    # Metallic
    if metal_path and os.path.exists(metal_path):
        img_metal = bpy.data.images.load(metal_path)
        img_metal.colorspace_settings.name = 'Non-Color'
        img_metal.pack()
        tex_metal = nodes.new("ShaderNodeTexImage")
        tex_metal.image = img_metal
        links.new(tex_metal.outputs["Color"], bsdf.inputs["Metallic"])


# ==============================================================================
# PBR MATERIAL FACTORY
# ==============================================================================
def create_materials():
    materials = {}

    # 1. Chiseled Granite Wall (Official BlenderKit Chiseled Granite 2K PBR)
    mat_granite_wall = bpy.data.materials.new("Mat_Granite_Wall")
    mat_granite_wall.use_nodes = True
    nodes = mat_granite_wall.node_tree.nodes
    links = mat_granite_wall.node_tree.links
    nodes.clear()

    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_out.location = (600, 0)
    bsdf.location = (200, 0)
    links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    wall_diff = os.path.join(TEXTURES_DIR, "bk_chiseled_granite_diff_2k.png")
    wall_nor = os.path.join(TEXTURES_DIR, "bk_chiseled_granite_nor_2k.png")
    wall_rough = os.path.join(TEXTURES_DIR, "bk_chiseled_granite_rough_2k.png")

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1.0, 1.0, 1.0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    if os.path.exists(wall_diff):
        img_col = bpy.data.images.load(wall_diff)
        node_col = nodes.new('ShaderNodeTexImage')
        node_col.image = img_col
        links.new(mapping.outputs['Vector'], node_col.inputs['Vector'])
        links.new(node_col.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.75, 0.74, 0.72, 1.0)

    if os.path.exists(wall_nor):
        img_nor = bpy.data.images.load(wall_nor)
        img_nor.colorspace_settings.name = 'Non-Color'
        node_nor_tex = nodes.new('ShaderNodeTexImage')
        node_nor_tex.image = img_nor
        norm_map = nodes.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 0.50
        links.new(mapping.outputs['Vector'], node_nor_tex.inputs['Vector'])
        links.new(node_nor_tex.outputs['Color'], norm_map.inputs['Color'])
        links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])

    if os.path.exists(wall_rough):
        img_rou = bpy.data.images.load(wall_rough)
        img_rou.colorspace_settings.name = 'Non-Color'
        node_rou_tex = nodes.new('ShaderNodeTexImage')
        node_rou_tex.image = img_rou
        rou_map = nodes.new('ShaderNodeMapRange')
        rou_map.inputs['From Min'].default_value = 0.0
        rou_map.inputs['From Max'].default_value = 1.0
        rou_map.inputs['To Min'].default_value = 0.55
        rou_map.inputs['To Max'].default_value = 0.85
        links.new(mapping.outputs['Vector'], node_rou_tex.inputs['Vector'])
        links.new(node_rou_tex.outputs['Color'], rou_map.inputs['Value'])
        links.new(rou_map.outputs['Result'], bsdf.inputs['Roughness'])
    else:
        bsdf.inputs['Roughness'].default_value = 0.68

    materials['granite_wall'] = mat_granite_wall
    materials['sandstone'] = mat_granite_wall

    # 2. Pattern-Free Dark Gray Honed Granite (Door Frame Slab, Monolithic Columns)
    mat_granite = bpy.data.materials.new("Mat_Rock_Granite")
    mat_granite.use_nodes = True
    nodes = mat_granite.node_tree.nodes
    links = mat_granite.node_tree.links
    nodes.clear()

    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_out.location = (600, 0)
    bsdf.location = (200, 0)
    links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    granite_diff = os.path.join(TEXTURES_DIR, "dark_gray_granite_diff_2k.png")
    granite_nor = os.path.join(TEXTURES_DIR, "dark_gray_granite_nor_2k.png")
    granite_rough = os.path.join(TEXTURES_DIR, "dark_gray_granite_rough_2k.png")

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1.0, 1.0, 1.0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    if os.path.exists(granite_diff):
        img_col = bpy.data.images.load(granite_diff)
        node_col = nodes.new('ShaderNodeTexImage')
        node_col.image = img_col
        links.new(mapping.outputs['Vector'], node_col.inputs['Vector'])
        links.new(node_col.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.20, 0.20, 0.21, 1.0)

    if os.path.exists(granite_nor):
        img_nor = bpy.data.images.load(granite_nor)
        img_nor.colorspace_settings.name = 'Non-Color'
        node_nor_tex = nodes.new('ShaderNodeTexImage')
        node_nor_tex.image = img_nor
        norm_map = nodes.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 0.25
        links.new(mapping.outputs['Vector'], node_nor_tex.inputs['Vector'])
        links.new(node_nor_tex.outputs['Color'], norm_map.inputs['Color'])
        links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])

    if os.path.exists(granite_rough):
        img_rou = bpy.data.images.load(granite_rough)
        img_rou.colorspace_settings.name = 'Non-Color'
        node_rou_tex = nodes.new('ShaderNodeTexImage')
        node_rou_tex.image = img_rou
        links.new(mapping.outputs['Vector'], node_rou_tex.inputs['Vector'])
        links.new(node_rou_tex.outputs['Color'], bsdf.inputs['Roughness'])
    else:
        bsdf.inputs['Roughness'].default_value = 0.62

    materials['granite'] = mat_granite
    materials['dark_gray_stone'] = mat_granite

    # 2b. Pure Black Ceiling Beams & Architrave Trim (Corridor Roof)
    mat_black_beams = bpy.data.materials.new("Mat_Corridor_Black_Beams")
    mat_black_beams.use_nodes = True
    nodes_bb = mat_black_beams.node_tree.nodes
    links_bb = mat_black_beams.node_tree.links
    nodes_bb.clear()

    node_out_bb = nodes_bb.new('ShaderNodeOutputMaterial')
    bsdf_bb = nodes_bb.new('ShaderNodeBsdfPrincipled')
    node_out_bb.location = (600, 0)
    bsdf_bb.location = (200, 0)
    links_bb.new(bsdf_bb.outputs['BSDF'], node_out_bb.inputs['Surface'])

    bsdf_bb.inputs['Base Color'].default_value = (0.025, 0.025, 0.028, 1.0)
    bsdf_bb.inputs['Roughness'].default_value = 0.55
    bsdf_bb.inputs['Specular IOR Level'].default_value = 0.30

    if os.path.exists(granite_nor):
        tex_coord_bb = nodes_bb.new('ShaderNodeTexCoord')
        mapping_bb = nodes_bb.new('ShaderNodeMapping')
        mapping_bb.inputs['Scale'].default_value = (2.0, 2.0, 2.0)
        links_bb.new(tex_coord_bb.outputs['UV'], mapping_bb.inputs['Vector'])
        img_nor_bb = bpy.data.images.load(granite_nor)
        img_nor_bb.colorspace_settings.name = 'Non-Color'
        node_nor_bb = nodes_bb.new('ShaderNodeTexImage')
        node_nor_bb.image = img_nor_bb
        norm_map_bb = nodes_bb.new('ShaderNodeNormalMap')
        norm_map_bb.inputs['Strength'].default_value = 0.15
        links_bb.new(mapping_bb.outputs['Vector'], node_nor_bb.inputs['Vector'])
        links_bb.new(node_nor_bb.outputs['Color'], norm_map_bb.inputs['Color'])
        links_bb.new(norm_map_bb.outputs['Normal'], bsdf_bb.inputs['Normal'])

    materials['black_beams'] = mat_black_beams
    materials['fascia'] = mat_black_beams

    # 3. Interior Dark Ashlar Granite Wall (Warm dark stone blocks for sanctum walls)
    mat_in_granite = bpy.data.materials.new("Mat_Interior_Granite_Wall")
    mat_in_granite.use_nodes = True
    nodes = mat_in_granite.node_tree.nodes
    links = mat_in_granite.node_tree.links
    nodes.clear()

    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_out.location = (600, 0)
    bsdf.location = (200, 0)
    links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1.0, 1.0, 1.0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    if os.path.exists(granite_diff):
        img_col = bpy.data.images.load(granite_diff)
        node_col = nodes.new('ShaderNodeTexImage')
        node_col.image = img_col
        color_mix = nodes.new('ShaderNodeMix')
        color_mix.data_type = 'RGBA'
        color_mix.blend_type = 'MULTIPLY'
        color_mix.inputs['Factor'].default_value = 0.60
        color_mix.inputs[7].default_value = (0.35, 0.28, 0.22, 1.0)
        links.new(mapping.outputs['Vector'], node_col.inputs['Vector'])
        links.new(node_col.outputs['Color'], color_mix.inputs[6])
        links.new(color_mix.outputs[2], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.12, 0.10, 0.09, 1.0)

    if os.path.exists(granite_nor):
        img_nor = bpy.data.images.load(granite_nor)
        img_nor.colorspace_settings.name = 'Non-Color'
        node_nor_tex = nodes.new('ShaderNodeTexImage')
        node_nor_tex.image = img_nor
        norm_map = nodes.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 1.6
        links.new(mapping.outputs['Vector'], node_nor_tex.inputs['Vector'])
        links.new(node_nor_tex.outputs['Color'], norm_map.inputs['Color'])
        links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])

    bsdf.inputs['Roughness'].default_value = 0.72
    materials['interior_granite'] = mat_in_granite

    # 4. Chiseled Granite Floor (Official BlenderKit Chiseled Granite 2K PBR)
    mat_floor = bpy.data.materials.new("Mat_Polished_Granite_Floor")
    mat_floor.use_nodes = True
    nodes = mat_floor.node_tree.nodes
    links = mat_floor.node_tree.links
    nodes.clear()

    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_out.location = (600, 0)
    bsdf.location = (200, 0)
    links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    floor_diff = os.path.join(TEXTURES_DIR, "bk_chiseled_granite_diff_2k.png")
    floor_nor = os.path.join(TEXTURES_DIR, "bk_chiseled_granite_nor_2k.png")
    floor_rough = os.path.join(TEXTURES_DIR, "bk_chiseled_granite_rough_2k.png")

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1.0, 1.0, 1.0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    if os.path.exists(floor_diff):
        img_col = bpy.data.images.load(floor_diff)
        node_col = nodes.new('ShaderNodeTexImage')
        node_col.image = img_col
        links.new(mapping.outputs['Vector'], node_col.inputs['Vector'])
        links.new(node_col.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.75, 0.74, 0.72, 1.0)

    if os.path.exists(floor_nor):
        img_nor = bpy.data.images.load(floor_nor)
        img_nor.colorspace_settings.name = 'Non-Color'
        node_nor_tex = nodes.new('ShaderNodeTexImage')
        node_nor_tex.image = img_nor
        norm_map = nodes.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 0.35
        links.new(mapping.outputs['Vector'], node_nor_tex.inputs['Vector'])
        links.new(node_nor_tex.outputs['Color'], norm_map.inputs['Color'])
        links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])

    if os.path.exists(floor_rough):
        img_rou = bpy.data.images.load(floor_rough)
        img_rou.colorspace_settings.name = 'Non-Color'
        node_rou_tex = nodes.new('ShaderNodeTexImage')
        node_rou_tex.image = img_rou
        rou_map = nodes.new('ShaderNodeMapRange')
        rou_map.inputs['From Min'].default_value = 0.0
        rou_map.inputs['From Max'].default_value = 1.0
        rou_map.inputs['To Min'].default_value = 0.40
        rou_map.inputs['To Max'].default_value = 0.65
        links.new(mapping.outputs['Vector'], node_rou_tex.inputs['Vector'])
        links.new(node_rou_tex.outputs['Color'], rou_map.inputs['Value'])
        links.new(rou_map.outputs['Result'], bsdf.inputs['Roughness'])
    else:
        bsdf.inputs['Roughness'].default_value = 0.50

    bsdf.inputs['Specular IOR Level'].default_value = 0.45
    materials['polished_floor'] = mat_floor
    materials['granite_floor'] = mat_floor
    materials['paving'] = mat_floor

    # 5. Teak Wood (Ceilings, Doors & Beams)
    mat_wood = bpy.data.materials.new("Mat_Teak_Wood")
    mat_wood.use_nodes = True
    nodes = mat_wood.node_tree.nodes
    links = mat_wood.node_tree.links
    nodes.clear()

    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_out.location = (600, 0)
    bsdf.location = (200, 0)
    links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    wood_diff = os.path.join(TEXTURES_DIR, "preview_teak_veneer.png")
    if not os.path.exists(wood_diff):
        wood_diff = os.path.join(TEXTURES_DIR, "dark_paneled_wood_diff_2k.jpg")

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (3.5, 3.5, 3.5)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    if os.path.exists(wood_diff):
        img_col = bpy.data.images.load(wood_diff)
        node_col = nodes.new('ShaderNodeTexImage')
        node_col.image = img_col
        links.new(mapping.outputs['Vector'], node_col.inputs['Vector'])
        links.new(node_col.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.35, 0.20, 0.10, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
    materials['teak'] = mat_wood

    # 5b. Authentic BlenderKit Old Copper 2K PBR Material (Door & Niche Backplates)
    # Non-shining aged matte copper with natural patina and surface aging
    mat_copper = bpy.data.materials.new("Mat_Burnished_Copper")
    mat_copper.use_nodes = True
    nodes_cp = mat_copper.node_tree.nodes
    links_cp = mat_copper.node_tree.links
    nodes_cp.clear()

    node_out_cp = nodes_cp.new('ShaderNodeOutputMaterial')
    bsdf_cp = nodes_cp.new('ShaderNodeBsdfPrincipled')
    node_out_cp.location = (800, 0)
    bsdf_cp.location = (400, 0)
    links_cp.new(bsdf_cp.outputs['BSDF'], node_out_cp.inputs['Surface'])

    cp_diff = os.path.join(TEXTURES_DIR, "bk_old_copper_diff_2k.png")
    cp_nor = os.path.join(TEXTURES_DIR, "bk_old_copper_nor_2k.png")
    cp_rough = os.path.join(TEXTURES_DIR, "bk_old_copper_rough_2k.png")
    cp_metal = os.path.join(TEXTURES_DIR, "bk_old_copper_metal_2k.png")

    tex_coord_cp = nodes_cp.new('ShaderNodeTexCoord')
    mapping_cp = nodes_cp.new('ShaderNodeMapping')
    mapping_cp.inputs['Scale'].default_value = (1.0, 1.0, 1.0)
    links_cp.new(tex_coord_cp.outputs['UV'], mapping_cp.inputs['Vector'])

    if os.path.exists(cp_diff):
        img_col = bpy.data.images.load(cp_diff)
        node_col = nodes_cp.new('ShaderNodeTexImage')
        node_col.image = img_col
        links_cp.new(mapping_cp.outputs['Vector'], node_col.inputs['Vector'])
        links_cp.new(node_col.outputs['Color'], bsdf_cp.inputs['Base Color'])
    else:
        bsdf_cp.inputs['Base Color'].default_value = (0.68, 0.48, 0.38, 1.0)

    if os.path.exists(cp_nor):
        img_nor = bpy.data.images.load(cp_nor)
        img_nor.colorspace_settings.name = 'Non-Color'
        node_nor_tex = nodes_cp.new('ShaderNodeTexImage')
        node_nor_tex.image = img_nor
        norm_map = nodes_cp.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 0.50
        links_cp.new(mapping_cp.outputs['Vector'], node_nor_tex.inputs['Vector'])
        links_cp.new(node_nor_tex.outputs['Color'], norm_map.inputs['Color'])
        links_cp.new(norm_map.outputs['Normal'], bsdf_cp.inputs['Normal'])

    if os.path.exists(cp_rough):
        img_rou = bpy.data.images.load(cp_rough)
        img_rou.colorspace_settings.name = 'Non-Color'
        node_rou_tex = nodes_cp.new('ShaderNodeTexImage')
        node_rou_tex.image = img_rou
        rou_map = nodes_cp.new('ShaderNodeMapRange')
        rou_map.inputs['From Min'].default_value = 0.0
        rou_map.inputs['From Max'].default_value = 1.0
        # Non-shining aged matte copper (roughness 0.55 to 0.85)
        rou_map.inputs['To Min'].default_value = 0.55
        rou_map.inputs['To Max'].default_value = 0.85
        links_cp.new(mapping_cp.outputs['Vector'], node_rou_tex.inputs['Vector'])
        links_cp.new(node_rou_tex.outputs['Color'], rou_map.inputs['Value'])
        links_cp.new(rou_map.outputs['Result'], bsdf_cp.inputs['Roughness'])
    else:
        bsdf_cp.inputs['Roughness'].default_value = 0.65

    if os.path.exists(cp_metal):
        img_met = bpy.data.images.load(cp_metal)
        img_met.colorspace_settings.name = 'Non-Color'
        node_met_tex = nodes_cp.new('ShaderNodeTexImage')
        node_met_tex.image = img_met
        links_cp.new(mapping_cp.outputs['Vector'], node_met_tex.inputs['Vector'])
        links_cp.new(node_met_tex.outputs['Color'], bsdf_cp.inputs['Metallic'])
    else:
        bsdf_cp.inputs['Metallic'].default_value = 0.95

    bsdf_cp.inputs['Specular IOR Level'].default_value = 0.35
    materials['copper'] = mat_copper

    # 5c. Authentic Temple Baked Terracotta Roof PBR Material
    mat_terracotta = bpy.data.materials.new("Mat_Terracotta_Roof")
    mat_terracotta.use_nodes = True
    nodes_tc = mat_terracotta.node_tree.nodes
    links_tc = mat_terracotta.node_tree.links
    nodes_tc.clear()
    node_out_tc = nodes_tc.new('ShaderNodeOutputMaterial')
    bsdf_tc = nodes_tc.new('ShaderNodeBsdfPrincipled')
    node_out_tc.location = (600, 0)
    bsdf_tc.location = (200, 0)
    links_tc.new(bsdf_tc.outputs['BSDF'], node_out_tc.inputs['Surface'])
    bsdf_tc.inputs['Base Color'].default_value = (0.70, 0.28, 0.16, 1.0)
    bsdf_tc.inputs['Metallic'].default_value = 0.0
    bsdf_tc.inputs['Roughness'].default_value = 0.78
    bsdf_tc.inputs['Specular IOR Level'].default_value = 0.25
    materials['terracotta'] = mat_terracotta

    # 6. Complete Devi Shrine PBR Material (Authentic capture from bing_ref_10.jpg)
    mat_shrine = bpy.data.materials.new("Mat_Devi_Shrine_PBR")
    mat_shrine.use_nodes = True
    nodes = mat_shrine.node_tree.nodes
    links = mat_shrine.node_tree.links
    nodes.clear()

    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_out.location = (800, 0)
    bsdf.location = (400, 0)
    links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')

    s_diff = os.path.join(TEXTURES_DIR, "shrine_pbr_albedo.png")
    s_nor = os.path.join(TEXTURES_DIR, "shrine_pbr_normal.png")
    s_rou = os.path.join(TEXTURES_DIR, "shrine_pbr_roughness.png")
    s_met = os.path.join(TEXTURES_DIR, "shrine_pbr_metallic.png")
    s_emit = os.path.join(TEXTURES_DIR, "shrine_pbr_emission.png")

    if os.path.exists(s_diff):
        img_diff = bpy.data.images.load(s_diff)
        node_diff = nodes.new('ShaderNodeTexImage')
        node_diff.image = img_diff
        links.new(tex_coord.outputs['UV'], node_diff.inputs['Vector'])
        links.new(node_diff.outputs['Color'], bsdf.inputs['Base Color'])

    if os.path.exists(s_nor):
        img_nor = bpy.data.images.load(s_nor)
        img_nor.colorspace_settings.name = 'Non-Color'
        node_nor = nodes.new('ShaderNodeTexImage')
        node_nor.image = img_nor
        norm_map = nodes.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 0.40
        links.new(tex_coord.outputs['UV'], node_nor.inputs['Vector'])
        links.new(node_nor.outputs['Color'], norm_map.inputs['Color'])
        links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])

    if os.path.exists(s_rou):
        img_rou = bpy.data.images.load(s_rou)
        img_rou.colorspace_settings.name = 'Non-Color'
        node_rou = nodes.new('ShaderNodeTexImage')
        node_rou.image = img_rou
        links.new(tex_coord.outputs['UV'], node_rou.inputs['Vector'])
        links.new(node_rou.outputs['Color'], bsdf.inputs['Roughness'])
    else:
        bsdf.inputs['Roughness'].default_value = 0.28

    if os.path.exists(s_met):
        img_met = bpy.data.images.load(s_met)
        img_met.colorspace_settings.name = 'Non-Color'
        node_met = nodes.new('ShaderNodeTexImage')
        node_met.image = img_met
        links.new(tex_coord.outputs['UV'], node_met.inputs['Vector'])
        links.new(node_met.outputs['Color'], bsdf.inputs['Metallic'])

    if os.path.exists(s_emit):
        img_emit = bpy.data.images.load(s_emit)
        node_emit = nodes.new('ShaderNodeTexImage')
        node_emit.image = img_emit
        links.new(tex_coord.outputs['UV'], node_emit.inputs['Vector'])
        links.new(node_emit.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 4.0

    bsdf.inputs['Specular IOR Level'].default_value = 0.65
    materials['devi_shrine'] = mat_shrine

    # 7. Jet-Black Polished Granite for Devi Linga Body Sides/Rear
    mat_devi_stone = bpy.data.materials.new("Mat_Devi_Linga_Stone")
    mat_devi_stone.use_nodes = True
    nodes = mat_devi_stone.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_devi_stone.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.025, 0.025, 0.028, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.16
    bsdf.inputs['Specular IOR Level'].default_value = 0.65
    materials['devi_stone'] = mat_devi_stone

    # 8. Consecrated Crimson Silk Drape (Right flank)
    mat_drape = bpy.data.materials.new("Mat_Devi_Silk_Drape")
    mat_drape.use_nodes = True
    nodes = mat_drape.node_tree.nodes
    links = mat_drape.node_tree.links
    nodes.clear()

    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_out.location = (600, 0)
    bsdf.location = (200, 0)
    links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    drape_diff = os.path.join(TEXTURES_DIR, "devi_silk_drape_albedo.png")
    if os.path.exists(drape_diff):
        img_ddiff = bpy.data.images.load(drape_diff)
        node_ddiff = nodes.new('ShaderNodeTexImage')
        node_ddiff.image = img_ddiff
        tex_coord = nodes.new('ShaderNodeTexCoord')
        links.new(tex_coord.outputs['UV'], node_ddiff.inputs['Vector'])
        links.new(node_ddiff.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.75, 0.06, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Sheen Weight'].default_value = 1.0
    materials['devi_silk_drape'] = mat_drape

    # 9. Antique Bronze Temple Bells, Railings, & Donation Chests
    mat_bell_bronze = bpy.data.materials.new("Mat_Temple_Bronze")
    mat_bell_bronze.use_nodes = True
    nodes = mat_bell_bronze.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_bell_bronze.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.72, 0.52, 0.25, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.92
    bsdf.inputs['Roughness'].default_value = 0.28
    materials['bronze'] = mat_bell_bronze

    # 10. Ceremonial Red Runner Carpet
    mat_carpet = bpy.data.materials.new("Mat_Ceremonial_Carpet")
    mat_carpet.use_nodes = True
    nodes = mat_carpet.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_carpet.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.58, 0.05, 0.07, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.90
    materials['carpet'] = mat_carpet

    # 11. Diya Clay & Burning Flame
    mat_clay = bpy.data.materials.new("Mat_Diya_Clay")
    mat_clay.use_nodes = True
    nodes = mat_clay.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_clay.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.75, 0.38, 0.18, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    materials['diya_clay'] = mat_clay

    mat_flame = bpy.data.materials.new("Mat_Diya_Flame")
    mat_flame.use_nodes = True
    nodes = mat_flame.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_emit = nodes.new('ShaderNodeEmission')
    node_emit.inputs['Color'].default_value = (1.0, 0.75, 0.22, 1.0)
    node_emit.inputs['Strength'].default_value = 45.0
    mat_flame.node_tree.links.new(node_emit.outputs['Emission'], node_out.inputs['Surface'])
    materials['flame'] = mat_flame

    # 12. Modern Fascia & Paving & Water & Lawn & Yantra
    mat_fascia = bpy.data.materials.new("Mat_Canopy_Fascia")
    mat_fascia.use_nodes = True
    nodes = mat_fascia.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_fascia.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.16, 0.17, 0.18, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.88
    bsdf.inputs['Roughness'].default_value = 0.22
    materials['fascia'] = mat_fascia

    mat_paving = bpy.data.materials.new("Mat_Courtyard_Paving")
    mat_paving.use_nodes = True
    nodes = mat_paving.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_paving.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.26, 0.25, 0.24, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.50
    materials['paving'] = mat_paving

    mat_water = bpy.data.materials.new("Mat_Reflecting_Water")
    mat_water.use_nodes = True
    nodes = mat_water.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_water.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.02, 0.03, 0.05, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['Metallic'].default_value = 0.15
    bsdf.inputs['IOR'].default_value = 1.333
    materials['water'] = mat_water

    mat_lawn = bpy.data.materials.new("Mat_Foreground_Lawn")
    mat_lawn.use_nodes = True
    nodes = mat_lawn.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_lawn.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.16, 0.32, 0.10, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    materials['lawn'] = mat_lawn

    mat_yantra = bpy.data.materials.new("Mat_Bhairavi_Yantra")
    mat_yantra.use_nodes = True
    nodes = mat_yantra.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_yantra.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.76, 0.08, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.30
    materials['yantra'] = mat_yantra

    mat_jasmine = bpy.data.materials.new("Mat_Jasmine_Flowers")
    mat_jasmine.use_nodes = True
    nodes = mat_jasmine.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_jasmine.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.92, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    materials['jasmine'] = mat_jasmine

    mat_rose = bpy.data.materials.new("Mat_Rose_Petals")
    mat_rose.use_nodes = True
    nodes = mat_rose.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_rose.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.82, 0.05, 0.12, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.75
    materials['rose'] = mat_rose

    # 13. Devotee Meditation Asana Cushion (Woven fabric on seating steps)
    mat_asana = bpy.data.materials.new("Mat_Meditation_Asana")
    mat_asana.use_nodes = True
    nodes = mat_asana.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_asana.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.72, 0.22, 0.08, 1.0)  # Saffron / deep rust ochre
    bsdf.inputs['Roughness'].default_value = 0.88
    bsdf.inputs['Sheen Weight'].default_value = 0.75
    materials['asana'] = mat_asana

    # 14. Ceremonial Offering Uruli (Turned reflective brass)
    mat_uruli = bpy.data.materials.new("Mat_Ceremonial_Uruli")
    mat_uruli.use_nodes = True
    nodes = mat_uruli.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_uruli.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.88, 0.68, 0.26, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.18
    materials['uruli'] = mat_uruli

    # 15. Sacred Lotus Petals (Floating in Uruli water)
    mat_lotus = bpy.data.materials.new("Mat_Lotus_Petals")
    mat_lotus.use_nodes = True
    nodes = mat_lotus.node_tree.nodes
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    mat_lotus.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.92, 0.28, 0.48, 1.0)  # Vivid sacred pink lotus
    bsdf.inputs['Roughness'].default_value = 0.45
    materials['lotus'] = mat_lotus

    # 17. Light Warm Carved Granite (for the 2 diamond-cut pillars & architrave in devi.jpg)
    mat_pillar_stone = bpy.data.materials.new("Mat_Carved_Pillar_Stone")
    mat_pillar_stone.use_nodes = True
    m_nodes = mat_pillar_stone.node_tree.nodes
    m_nodes.clear()
    m_out = m_nodes.new('ShaderNodeOutputMaterial')
    m_bsdf = m_nodes.new('ShaderNodeBsdfPrincipled')
    mat_pillar_stone.node_tree.links.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])
    m_bsdf.inputs['Base Color'].default_value = (0.76, 0.74, 0.70, 1.0) # Light warm grey stone
    m_bsdf.inputs['Roughness'].default_value = 0.72
    materials['pillar_stone'] = mat_pillar_stone

    # 17b. Authentic Suryakund Dravidian Pillar Material (naga_stone textures matching Suryakund 1:1)
    mat_sk_pillar = bpy.data.materials.new("Mat_Suryakund_Dravidian_Pillars_PBR")
    mat_sk_pillar.use_nodes = True
    sk_nodes = mat_sk_pillar.node_tree.nodes
    sk_links = mat_sk_pillar.node_tree.links
    sk_nodes.clear()

    sk_out = sk_nodes.new('ShaderNodeOutputMaterial')
    sk_bsdf = sk_nodes.new('ShaderNodeBsdfPrincipled')
    sk_out.location = (600, 0)
    sk_bsdf.location = (200, 0)
    sk_links.new(sk_bsdf.outputs['BSDF'], sk_out.inputs['Surface'])

    p_col = os.path.join(TEXTURES_DIR, "naga_stone_color.png")
    p_nor = os.path.join(TEXTURES_DIR, "naga_stone_normal.png")
    p_rough = os.path.join(TEXTURES_DIR, "naga_stone_roughness.png")

    sk_tc = sk_nodes.new('ShaderNodeTexCoord')
    sk_map = sk_nodes.new('ShaderNodeMapping')
    sk_map.inputs['Scale'].default_value = (1.0, 1.0, 1.0)
    sk_links.new(sk_tc.outputs['UV'], sk_map.inputs['Vector'])

    if os.path.exists(p_col):
        img_col = bpy.data.images.load(p_col)
        node_col = sk_nodes.new('ShaderNodeTexImage')
        node_col.image = img_col
        sk_links.new(sk_map.outputs['Vector'], node_col.inputs['Vector'])
        color_mix = sk_nodes.new('ShaderNodeMix')
        color_mix.data_type = 'RGBA'
        color_mix.blend_type = 'MULTIPLY'
        color_mix.inputs['Factor'].default_value = 0.50
        color_mix.inputs[7].default_value = (1.15, 1.10, 1.02, 1.0)
        sk_links.new(node_col.outputs['Color'], color_mix.inputs[6])
        sk_links.new(color_mix.outputs[2], sk_bsdf.inputs['Base Color'])
    else:
        sk_bsdf.inputs['Base Color'].default_value = (0.78, 0.74, 0.68, 1.0)

    if os.path.exists(p_nor):
        img_nor = bpy.data.images.load(p_nor)
        img_nor.colorspace_settings.name = 'Non-Color'
        node_nor_tex = sk_nodes.new('ShaderNodeTexImage')
        node_nor_tex.image = img_nor
        norm_map = sk_nodes.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 1.25
        sk_links.new(sk_map.outputs['Vector'], node_nor_tex.inputs['Vector'])
        sk_links.new(node_nor_tex.outputs['Color'], norm_map.inputs['Color'])
        sk_links.new(norm_map.outputs['Normal'], sk_bsdf.inputs['Normal'])

    if os.path.exists(p_rough):
        img_rou = bpy.data.images.load(p_rough)
        img_rou.colorspace_settings.name = 'Non-Color'
        node_rou_tex = sk_nodes.new('ShaderNodeTexImage')
        node_rou_tex.image = img_rou
        sk_links.new(sk_map.outputs['Vector'], node_rou_tex.inputs['Vector'])
        sk_links.new(node_rou_tex.outputs['Color'], sk_bsdf.inputs['Roughness'])
    else:
        sk_bsdf.inputs['Roughness'].default_value = 0.65

    sk_bsdf.inputs['Specular IOR Level'].default_value = 0.30
    materials['suryakund_pillar'] = mat_sk_pillar

    # 18. Sacred Gold (for Sarpa Bandha knot, Devi eyes, Trinetra, Nose Ring)
    mat_gold = bpy.data.materials.new("Mat_Sacred_Gold")
    mat_gold.use_nodes = True
    m_nodes = mat_gold.node_tree.nodes
    m_nodes.clear()
    m_out = m_nodes.new('ShaderNodeOutputMaterial')
    m_bsdf = m_nodes.new('ShaderNodeBsdfPrincipled')
    mat_gold.node_tree.links.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])
    m_bsdf.inputs['Base Color'].default_value = (1.0, 0.78, 0.20, 1.0)
    m_bsdf.inputs['Metallic'].default_value = 0.95
    m_bsdf.inputs['Roughness'].default_value = 0.22
    materials['gold'] = mat_gold

    # 19. Crimson Velvet (for temple curtains framing the 2 pillars)
    mat_crimson = bpy.data.materials.new("Mat_Crimson_Velvet")
    mat_crimson.use_nodes = True
    m_nodes = mat_crimson.node_tree.nodes
    m_nodes.clear()
    m_out = m_nodes.new('ShaderNodeOutputMaterial')
    m_bsdf = m_nodes.new('ShaderNodeBsdfPrincipled')
    mat_crimson.node_tree.links.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])
    m_bsdf.inputs['Base Color'].default_value = (0.62, 0.04, 0.08, 1.0)
    m_bsdf.inputs['Roughness'].default_value = 0.80
    m_bsdf.inputs['Sheen Weight'].default_value = 0.90
    materials['crimson_velvet'] = mat_crimson

    # 20. Green Temple Valance (for side wall fabric hangings)
    mat_green = bpy.data.materials.new("Mat_Green_Valance")
    mat_green.use_nodes = True
    m_nodes = mat_green.node_tree.nodes
    m_nodes.clear()
    m_out = m_nodes.new('ShaderNodeOutputMaterial')
    m_bsdf = m_nodes.new('ShaderNodeBsdfPrincipled')
    mat_green.node_tree.links.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])
    m_bsdf.inputs['Base Color'].default_value = (0.12, 0.45, 0.18, 1.0)
    m_bsdf.inputs['Roughness'].default_value = 0.75
    materials['green_valance'] = mat_green

    # 21. Yellow Sand Mandala (for ceremonial floor rangoli)
    mat_mandala = bpy.data.materials.new("Mat_Mandala_Yellow")
    mat_mandala.use_nodes = True
    m_nodes = mat_mandala.node_tree.nodes
    m_nodes.clear()
    m_out = m_nodes.new('ShaderNodeOutputMaterial')
    m_bsdf = m_nodes.new('ShaderNodeBsdfPrincipled')
    mat_mandala.node_tree.links.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])
    m_bsdf.inputs['Base Color'].default_value = (0.96, 0.78, 0.10, 1.0)
    m_bsdf.inputs['Roughness'].default_value = 0.88
    materials['mandala_yellow'] = mat_mandala

    # 22. Upper Mezzanine Sandstone Bricks
    mat_upper_bricks = bpy.data.materials.new("Mat_Upper_Mezzanine_Bricks")
    mat_upper_bricks.use_nodes = True
    m_nodes = mat_upper_bricks.node_tree.nodes
    m_nodes.clear()
    m_out = m_nodes.new('ShaderNodeOutputMaterial')
    m_bsdf = m_nodes.new('ShaderNodeBsdfPrincipled')
    mat_upper_bricks.node_tree.links.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])
    m_bsdf.inputs['Base Color'].default_value = (0.84, 0.72, 0.52, 1.0)
    m_bsdf.inputs['Roughness'].default_value = 0.85
    materials['upper_bricks'] = mat_upper_bricks

    # 23. Green Floral Rosette Diamond Tiles (Mezzanine wall ornament)
    mat_rosette = bpy.data.materials.new("Mat_Floral_Rosette")
    mat_rosette.use_nodes = True
    m_nodes = mat_rosette.node_tree.nodes
    m_nodes.clear()
    m_out = m_nodes.new('ShaderNodeOutputMaterial')
    m_bsdf = m_nodes.new('ShaderNodeBsdfPrincipled')
    mat_rosette.node_tree.links.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])
    m_bsdf.inputs['Base Color'].default_value = (0.15, 0.32, 0.22, 1.0)
    m_bsdf.inputs['Roughness'].default_value = 0.50
    materials['rosette'] = mat_rosette

    # 24. Authentic Sacred Metal Chain Material (Matte Wrought-Iron Pure Black)
    mat_metal_chain = bpy.data.materials.new("Mat_Sacred_Metal_Chain")
    mat_metal_chain.use_nodes = True
    m_nodes_mc = mat_metal_chain.node_tree.nodes
    m_nodes_mc.clear()
    m_out_mc = m_nodes_mc.new('ShaderNodeOutputMaterial')
    m_bsdf_mc = m_nodes_mc.new('ShaderNodeBsdfPrincipled')
    mat_metal_chain.node_tree.links.new(m_bsdf_mc.outputs['BSDF'], m_out_mc.inputs['Surface'])
    m_bsdf_mc.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0) # Matte wrought-iron pure black
    m_bsdf_mc.inputs['Metallic'].default_value = 0.88
    m_bsdf_mc.inputs['Roughness'].default_value = 0.45
    m_bsdf_mc.inputs['Specular IOR Level'].default_value = 0.40
    materials['metal_chain'] = mat_metal_chain

    # 25. Sacred Sanctum Dividing Brick Wall Material (Stacked Burnt Terracotta Bricks)
    mat_brick_wall = bpy.data.materials.new("Mat_Sanctum_Brick_Wall")
    setup_pbr_material(
        mat_brick_wall,
        albedo_path=os.path.join(TEXTURES_DIR, "stacked_brick_color.jpg"),
        norm_path=os.path.join(TEXTURES_DIR, "stacked_brick_normal.png"),
        rough_path=os.path.join(TEXTURES_DIR, "stacked_brick_roughness.jpg")
    )
    materials['brick_wall'] = mat_brick_wall

    return materials


# ==============================================================================
# 1. EXTERIOR ARCHITECTURE
# ==============================================================================
def build_plinth_and_courtyard(materials):
    # Expanded Grand Mandapam Corridor Plinth (Floor space expanded from 5.8m to 14.0m deep)
    deck_w = 30.0
    deck_d = 14.6
    deck_h = 0.40

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= deck_w
        v.co.y *= deck_d
        v.co.y += (deck_d / 2.0 - 0.6)  # Y from -0.6 to +14.0
        v.co.z = (v.co.z + 0.5) * deck_h

    me = bpy.data.meshes.new("Mesh_Mandapam_Plinth")
    bm.to_mesh(me)
    bm.free()

    obj_deck = bpy.data.objects.new("Mandapam_Plinth", me)
    bpy.context.collection.objects.link(obj_deck)
    obj_deck.data.materials.append(materials['granite_floor'])
    apply_box_uv(obj_deck, uv_scale=1.0)

    # Perimeter Descending Steps at outer edge of corridor (Y = 14.0m)
    # Step 1
    step1_bm = bmesh.new()
    bmesh.ops.create_cube(step1_bm, size=1.0)
    for v in step1_bm.verts:
        v.co.x *= 28.0
        v.co.y *= 0.45
        v.co.y += 14.0 + 0.225
        v.co.z = (v.co.z + 0.5) * 0.20
    me_s1 = bpy.data.meshes.new("Mesh_Plinth_Step1")
    step1_bm.to_mesh(me_s1)
    step1_bm.free()
    obj_s1 = bpy.data.objects.new("Plinth_Step1", me_s1)
    bpy.context.collection.objects.link(obj_s1)
    obj_s1.data.materials.append(materials['granite_floor'])
    apply_box_uv(obj_s1, uv_scale=1.0)

    # Step 2
    step2_bm = bmesh.new()
    bmesh.ops.create_cube(step2_bm, size=1.0)
    for v in step2_bm.verts:
        v.co.x *= 29.0
        v.co.y *= 0.45
        v.co.y += 14.45 + 0.225
        v.co.z = (v.co.z + 0.5) * 0.10
    me_s2 = bpy.data.meshes.new("Mesh_Plinth_Step2")
    step2_bm.to_mesh(me_s2)
    step2_bm.free()
    obj_s2 = bpy.data.objects.new("Plinth_Step2", me_s2)
    bpy.context.collection.objects.link(obj_s2)
    obj_s2.data.materials.append(materials['granite_floor'])
    apply_box_uv(obj_s2, uv_scale=1.0)

    # Outside floor planes (Courtyard_Paving, Reflecting_Pool, Foreground_Lawn)
    # removed per user request: "remove the planes which are in the floor in front if the temple outside not inside"


# ==============================================================================
# MONOLITHIC GRANITE COLUMNS (EXTERIOR & INTERIOR)
# ==============================================================================
def create_crouching_gana_beast_mesh():
    bm = bmesh.new()
    pw = 0.92
    pd = 0.92
    ph = 0.28
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation((0, 0, ph/2)) @ Matrix.Scale(pw, 4, Vector((1, 0, 0))) @ Matrix.Scale(pd, 4, Vector((0, 1, 0))) @ Matrix.Scale(ph, 4, Vector((0, 0, 1)))
    )
    bmesh.ops.create_uvsphere(
        bm, u_segments=12, v_segments=8, radius=0.34,
        matrix=Matrix.Translation((0, 0.12, ph + 0.22)) @ Matrix.Scale(1.15, 4, Vector((1, 0, 0))) @ Matrix.Scale(1.35, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.85, 4, Vector((0, 0, 1)))
    )
    bmesh.ops.create_uvsphere(
        bm, u_segments=10, v_segments=8, radius=0.22,
        matrix=Matrix.Translation((0, 0.46, ph + 0.32)) @ Matrix.Scale(1.0, 4, Vector((1, 0, 0))) @ Matrix.Scale(1.2, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.9, 4, Vector((0, 0, 1)))
    )
    bmesh.ops.create_cone(
        bm, cap_ends=True, segments=8, radius1=0.08, radius2=0.02, depth=0.18,
        matrix=Matrix.Translation((0, 0.65, ph + 0.28)) @ Matrix.Rotation(math.radians(-85.0), 4, 'X')
    )
    for sx in [-0.36, 0.36]:
        bmesh.ops.create_cone(
            bm, cap_ends=True, segments=8, radius1=0.12, radius2=0.12, depth=0.34,
            matrix=Matrix.Translation((sx, 0.28, ph + 0.17)) @ Matrix.Rotation(math.radians(25.0), 4, 'X')
        )
    for sx in [-0.38, 0.38]:
        bmesh.ops.create_cone(
            bm, cap_ends=True, segments=8, radius1=0.13, radius2=0.13, depth=0.32,
            matrix=Matrix.Translation((sx, -0.22, ph + 0.16)) @ Matrix.Rotation(math.radians(-30.0), 4, 'X')
        )

    me = bpy.data.meshes.new("Mesh_Gana_Beast_Base")
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = True
    return me


def create_padma_torus_mesh():
    bm = bmesh.new()
    segs = 24
    r_major = 0.44
    r_minor = 0.11
    verts_ring = []
    for i in range(segs):
        phi = 2.0 * math.pi * i / segs
        cos_phi = math.cos(phi)
        sin_phi = math.sin(phi)
        for j in range(12):
            theta = 2.0 * math.pi * j / 12
            x = (r_major + r_minor * math.cos(theta)) * cos_phi
            y = (r_major + r_minor * math.cos(theta)) * sin_phi
            z = r_minor * math.sin(theta) + r_minor
            verts_ring.append(bm.verts.new(Vector((x, y, z))))

    bm.verts.ensure_lookup_table()
    for i in range(segs):
        i_next = (i + 1) % segs
        for j in range(12):
            j_next = (j + 1) % 12
            v0 = verts_ring[i * 12 + j]
            v1 = verts_ring[i_next * 12 + j]
            v2 = verts_ring[i_next * 12 + j_next]
            v3 = verts_ring[i * 12 + j_next]
            bm.faces.new([v0, v1, v2, v3])

    me = bpy.data.meshes.new("Mesh_Padma_Torus")
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = True
    return me


def create_rock_hewn_shaft_mesh(height=3.85):
    bm = bmesh.new()
    shaft_r = 0.36
    bmesh.ops.create_cone(
        bm, cap_ends=True, segments=8,
        radius1=shaft_r, radius2=shaft_r * 0.94, depth=height,
        matrix=Matrix.Translation((0, 0, height/2.0))
    )
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation((0, 0, height - 0.12)) @ Matrix.Scale(0.92, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.92, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.24, 4, Vector((0, 0, 1)))
    )
    # Double-bracket corbel capital (Potika)
    for bx in [-0.55, 0.55]:
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((bx * 0.45, 0, height + 0.12)) @ Matrix.Scale(0.55, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.75, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.24, 4, Vector((0, 0, 1)))
        )
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation((0, 0, height + 0.28)) @ Matrix.Scale(1.18, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.92, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 0, 1)))
    )
    me = bpy.data.meshes.new("Mesh_Shaft_Capital")
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = True
    return me


def build_front_colonnade(materials):
    base_z = 0.40
    # Single monumental front row per user request: "remove one row and have only the front row"
    col_rows_y = [13.0]
    col_x_positions = [-11.0, -6.6, -2.4, 2.4, 6.6, 11.0]

    # Load authentic Suryakund Dravidian monolithic pillar per user request:
    # "replace the piller with the piller which is in the suryakund scale it to this level and add them here"
    blend_path = "/home/mullainathan/Downloads/Untitled.blend"
    mesh_pillar = None
    if os.path.exists(blend_path):
        with bpy.data.libraries.load(blend_path) as (data_from, data_to):
            if "piller" in data_from.objects:
                data_to.objects = ["piller"]
        if data_to.objects and data_to.objects[0]:
            p_loaded = data_to.objects[0]
            mesh_pillar = p_loaded.data

    if not mesh_pillar:
        mesh_pillar = create_rock_hewn_shaft_mesh(height=4.425)

    if mesh_pillar:
        mesh_pillar.materials.clear()
        mesh_pillar.materials.append(materials['suryakund_pillar'])

    # Scale pillar from native height 9.597m to 4.425m reaching underside of architrave beam
    sz = 4.425 / 9.5970
    scale_xy = sz

    col_idx = 0
    for cx in col_x_positions:
        col_idx += 1
        obj_pillar = bpy.data.objects.new(f"Col_Suryakund_Pillar_Front_{col_idx}", mesh_pillar)
        obj_pillar.location = Vector((cx, 13.0, base_z))
        obj_pillar.scale = Vector((scale_xy, scale_xy, sz))
        bpy.context.collection.objects.link(obj_pillar)
        # Apply authentic Suryakund Dravidian Pillar material matching Suryakund complex 1:1
        obj_pillar.data.materials.clear()
        obj_pillar.data.materials.append(materials['suryakund_pillar'])

    # Transverse & Longitudinal Black Architrave Beams connecting all columns to the Diya wall
    bm_beams = bmesh.new()
    arch_z = base_z + 4.60 # Z = 5.00m
    arch_th = 0.35
    arch_w = 0.70

    # 1. Transverse architrave along the single front row at Y = 13.0m
    bmesh.ops.create_cube(
        bm_beams, size=1.0,
        matrix=Matrix.Translation((0.0, 13.0, arch_z)) @
               Matrix.Scale(25.0, 4, Vector((1, 0, 0))) @
               Matrix.Scale(arch_w, 4, Vector((0, 1, 0))) @
               Matrix.Scale(arch_th, 4, Vector((0, 0, 1)))
    )

    # 2. Longitudinal architraves along each column line connecting from Diya wall (Y = 0) to outer row (Y = 13.0)
    for cx in col_x_positions:
        bmesh.ops.create_cube(
            bm_beams, size=1.0,
            matrix=Matrix.Translation((cx, 13.0 / 2.0, arch_z)) @
                   Matrix.Scale(arch_w, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(13.5, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(arch_th, 4, Vector((0, 0, 1)))
        )

    me_beam = bpy.data.meshes.new("Mesh_Colonnade_Architraves")
    bm_beams.to_mesh(me_beam)
    bm_beams.free()
    obj_beam = bpy.data.objects.new("Colonnade_Architraves", me_beam)
    bpy.context.collection.objects.link(obj_beam)
    obj_beam.data.materials.append(materials['black_beams'])
    apply_smart_uv(obj_beam)


# ==============================================================================
# DIYA WALL & ENTRANCE PORTAL
# ==============================================================================
def build_diya_wall_and_portal(materials):
    base_z = 0.40
    wall_w = 30.0
    wall_h = 4.80
    wall_th = 0.40
    door_w = 2.8
    door_h = 3.2

    # Sandstone Wall with entrance portal opening
    bm_wall = bmesh.new()
    bmesh.ops.create_cube(
        bm_wall, size=1.0,
        matrix=Matrix.Translation((-1.4 - (wall_w/2 - 1.4)/2, 0, base_z + wall_h/2)) @
               Matrix.Scale(wall_w/2 - 1.4, 4, Vector((1, 0, 0))) @
               Matrix.Scale(wall_th, 4, Vector((0, 1, 0))) @
               Matrix.Scale(wall_h, 4, Vector((0, 0, 1)))
    )
    bmesh.ops.create_cube(
        bm_wall, size=1.0,
        matrix=Matrix.Translation((1.4 + (wall_w/2 - 1.4)/2, 0, base_z + wall_h/2)) @
               Matrix.Scale(wall_w/2 - 1.4, 4, Vector((1, 0, 0))) @
               Matrix.Scale(wall_th, 4, Vector((0, 1, 0))) @
               Matrix.Scale(wall_h, 4, Vector((0, 0, 1)))
    )
    lintel_h = wall_h - door_h
    bmesh.ops.create_cube(
        bm_wall, size=1.0,
        matrix=Matrix.Translation((0, 0, base_z + door_h + lintel_h/2)) @
               Matrix.Scale(door_w, 4, Vector((1, 0, 0))) @
               Matrix.Scale(wall_th, 4, Vector((0, 1, 0))) @
               Matrix.Scale(lintel_h, 4, Vector((0, 0, 1)))
    )

    me_wall = bpy.data.meshes.new("Mesh_Diya_Wall_Structure")
    bm_wall.to_mesh(me_wall)
    bm_wall.free()
    obj_wall = bpy.data.objects.new("Diya_Wall_Structure", me_wall)
    bpy.context.collection.objects.link(obj_wall)
    obj_wall.data.materials.append(materials['granite_wall'])
    apply_box_uv(obj_wall, uv_scale=1.0)

    # 400+ 3D Triangular Lamp Niches & Lit Clay Diyas
    bm_niches = bmesh.new()
    bm_copper_triangles = bmesh.new()
    bm_diyas = bmesh.new()
    bm_flames = bmesh.new()

    niche_w = 0.17
    niche_h = 0.20
    wall_front_y = wall_th / 2.0

    rows_z = [0.65 + i * 0.44 for i in range(8)]
    wings_x_ranges = [(-14.2, -1.8), (1.8, 14.2)]

    for row_idx, rz in enumerate(rows_z):
        stagger = 0.18 if (row_idx % 2 == 1) else 0.0
        for x_min, x_max in wings_x_ranges:
            curr_x = x_min + stagger
            while curr_x <= x_max:
                z_bot = base_z + rz
                z_top = z_bot + niche_h

                # Stone bracket / shelf
                bmesh.ops.create_cube(
                    bm_niches, size=1.0,
                    matrix=Matrix.Translation((curr_x, wall_front_y + 0.025, z_bot + 0.015)) @
                           Matrix.Scale(niche_w * 1.15, 4, Vector((1, 0, 0))) @
                           Matrix.Scale(0.05, 4, Vector((0, 1, 0))) @
                           Matrix.Scale(0.03, 4, Vector((0, 0, 1)))
                )

                # Outer triangular stone frame/border on wall
                v_bl = bm_niches.verts.new(Vector((curr_x - niche_w/2, wall_front_y + 0.03, z_bot + 0.03)))
                v_br = bm_niches.verts.new(Vector((curr_x + niche_w/2, wall_front_y + 0.03, z_bot + 0.03)))
                v_ap = bm_niches.verts.new(Vector((curr_x, wall_front_y + 0.03, z_top)))

                v_bl_w = bm_niches.verts.new(Vector((curr_x - niche_w/2 - 0.02, wall_front_y, z_bot + 0.03)))
                v_br_w = bm_niches.verts.new(Vector((curr_x + niche_w/2 + 0.02, wall_front_y, z_bot + 0.03)))
                v_ap_w = bm_niches.verts.new(Vector((curr_x, wall_front_y, z_top + 0.025)))

                bm_niches.faces.new([v_bl_w, v_ap_w, v_ap, v_bl])
                bm_niches.faces.new([v_ap_w, v_br_w, v_br, v_ap])

                # Inner recessed triangular backplate & lining - IN COPPER ONLY INSIDE THE TRIANGLES
                v_in_l = bm_copper_triangles.verts.new(Vector((curr_x - niche_w * 0.44, wall_front_y + 0.005, z_bot + 0.035)))
                v_in_r = bm_copper_triangles.verts.new(Vector((curr_x + niche_w * 0.44, wall_front_y + 0.005, z_bot + 0.035)))
                v_in_t = bm_copper_triangles.verts.new(Vector((curr_x, wall_front_y + 0.005, z_top - 0.015)))
                bm_copper_triangles.faces.new([v_in_l, v_in_r, v_in_t])

                bmesh.ops.create_cone(
                    bm_diyas, cap_ends=True, segments=8,
                    radius1=0.048, radius2=0.022, depth=0.025,
                    matrix=Matrix.Translation((curr_x, wall_front_y + 0.032, z_bot + 0.038))
                )

                bmesh.ops.create_cone(
                    bm_flames, cap_ends=True, segments=6,
                    radius1=0.022, radius2=0.002, depth=0.045,
                    matrix=Matrix.Translation((curr_x, wall_front_y + 0.034, z_bot + 0.065))
                )

                curr_x += 0.36

    me_niches = bpy.data.meshes.new("Mesh_Diya_Niches")
    bm_niches.to_mesh(me_niches)
    bm_niches.free()
    obj_niches = bpy.data.objects.new("Diya_Wall_Niches", me_niches)
    bpy.context.collection.objects.link(obj_niches)
    obj_niches.data.materials.append(materials['granite_wall'])
    apply_box_uv(obj_niches, uv_scale=1.0)

    me_cp_triangles = bpy.data.meshes.new("Mesh_Diya_Niches_Inner_Copper")
    bm_copper_triangles.to_mesh(me_cp_triangles)
    bm_copper_triangles.free()
    obj_cp_triangles = bpy.data.objects.new("Diya_Niches_Inner_Copper", me_cp_triangles)
    bpy.context.collection.objects.link(obj_cp_triangles)
    obj_cp_triangles.data.materials.append(materials['copper'])
    apply_box_uv(obj_cp_triangles, uv_scale=1.0)

    me_diyas = bpy.data.meshes.new("Mesh_Diya_Clay_Saucers")
    bm_diyas.to_mesh(me_diyas)
    bm_diyas.free()
    obj_diyas = bpy.data.objects.new("Diya_Clay_Saucers", me_diyas)
    bpy.context.collection.objects.link(obj_diyas)
    obj_diyas.data.materials.append(materials['diya_clay'])

    me_flames = bpy.data.meshes.new("Mesh_Diya_Flames")
    bm_flames.to_mesh(me_flames)
    bm_flames.free()
    obj_flames = bpy.data.objects.new("Diya_Flames_Emissive", me_flames)
    bpy.context.collection.objects.link(obj_flames)
    obj_flames.data.materials.append(materials['flame'])

    # Door Frame
    bm_portal = bmesh.new()
    jamb_w = 0.28
    jamb_th = 0.50

    bmesh.ops.create_cube(
        bm_portal, size=1.0,
        matrix=Matrix.Translation((-door_w/2 - jamb_w/2, 0, base_z + door_h/2)) @
               Matrix.Scale(jamb_w, 4, Vector((1, 0, 0))) @
               Matrix.Scale(jamb_th, 4, Vector((0, 1, 0))) @
               Matrix.Scale(door_h, 4, Vector((0, 0, 1)))
    )
    bmesh.ops.create_cube(
        bm_portal, size=1.0,
        matrix=Matrix.Translation((door_w/2 + jamb_w/2, 0, base_z + door_h/2)) @
               Matrix.Scale(jamb_w, 4, Vector((1, 0, 0))) @
               Matrix.Scale(jamb_th, 4, Vector((0, 1, 0))) @
               Matrix.Scale(door_h, 4, Vector((0, 0, 1)))
    )
    bmesh.ops.create_cube(
        bm_portal, size=1.0,
        matrix=Matrix.Translation((0, 0, base_z + door_h + 0.15)) @
               Matrix.Scale(door_w + jamb_w * 2, 4, Vector((1, 0, 0))) @
               Matrix.Scale(jamb_th * 1.08, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.30, 4, Vector((0, 0, 1)))
    )
    bmesh.ops.create_cube(
        bm_portal, size=1.0,
        matrix=Matrix.Translation((0, 0, base_z + 0.08)) @
               Matrix.Scale(door_w + jamb_w * 2, 4, Vector((1, 0, 0))) @
               Matrix.Scale(jamb_th * 1.15, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.16, 4, Vector((0, 0, 1)))
    )

    me_portal = bpy.data.meshes.new("Mesh_Portal_Frame")
    bm_portal.to_mesh(me_portal)
    bm_portal.free()
    obj_portal = bpy.data.objects.new("Entrance_Portal_Frame", me_portal)
    bpy.context.collection.objects.link(obj_portal)
    obj_portal.data.materials.append(materials['granite'])
    apply_box_uv(obj_portal, uv_scale=1.0)

    # REMADE AUTHENTIC LINGA BHAIRAVI COPPER DOUBLE DOORS
    # Embossed sacred geometry yantra panels, raised studs, ornamental rosettes & copper bosses
    leaf_w = (door_w - 0.08) / 2.0  # ~1.36m
    leaf_h = door_h - 0.08          # ~3.12m
    leaf_th = 0.09                  # 9cm heavy copper clad door

    def create_copper_door_leaf_mesh(is_left=True):
        bm = bmesh.new()
        # Main core slab
        x_center = leaf_w / 2.0 if is_left else -leaf_w / 2.0
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((x_center, leaf_th/2, leaf_h/2)) @
                   Matrix.Scale(leaf_w, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(leaf_th, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(leaf_h, 4, Vector((0, 0, 1)))
        )

        # 2 cols x 4 rows of embossed copper yantra panels
        cols_x = [leaf_w * 0.30, leaf_w * 0.70] if is_left else [-leaf_w * 0.30, -leaf_w * 0.70]
        rows_z = [0.45 + i * 0.68 for i in range(4)]
        p_w = leaf_w * 0.34
        p_h = 0.54

        for px in cols_x:
            for pz in rows_z:
                # Outer raised panel bevel frame
                bmesh.ops.create_cube(
                    bm, size=1.0,
                    matrix=Matrix.Translation((px, leaf_th + 0.012, pz)) @
                           Matrix.Scale(p_w, 4, Vector((1, 0, 0))) @
                           Matrix.Scale(0.024, 4, Vector((0, 1, 0))) @
                           Matrix.Scale(p_h, 4, Vector((0, 0, 1)))
                )
                # Recessed inner field
                bmesh.ops.create_cube(
                    bm, size=1.0,
                    matrix=Matrix.Translation((px, leaf_th + 0.018, pz)) @
                           Matrix.Scale(p_w * 0.82, 4, Vector((1, 0, 0))) @
                           Matrix.Scale(0.015, 4, Vector((0, 1, 0))) @
                           Matrix.Scale(p_h * 0.82, 4, Vector((0, 0, 1)))
                )
                # Embossed Diamond / Lozenge Yantra Relief
                bmesh.ops.create_cone(
                    bm, cap_ends=True, segments=4,
                    radius1=0.12, radius2=0.01, depth=0.035,
                    matrix=Matrix.Translation((px, leaf_th + 0.035, pz)) @
                           Matrix.Rotation(math.radians(90), 4, Vector((1, 0, 0))) @
                           Matrix.Rotation(math.radians(45), 4, Vector((0, 1, 0)))
                )
                # Central raised copper boss stud
                bmesh.ops.create_uvsphere(
                    bm, u_segments=8, v_segments=6, radius=0.026,
                    matrix=Matrix.Translation((px, leaf_th + 0.046, pz))
                )

        # Ornamental copper rivet studs along rails & stiles
        stud_cols = [0.06, leaf_w * 0.50, leaf_w - 0.06] if is_left else [-0.06, -leaf_w * 0.50, -(leaf_w - 0.06)]
        for sx in stud_cols:
            for sz in [0.12, 0.78, 1.48, 2.18, 2.92]:
                bmesh.ops.create_uvsphere(
                    bm, u_segments=8, v_segments=6, radius=0.020,
                    matrix=Matrix.Translation((sx, leaf_th + 0.014, sz))
                )

        # Heavy ornate cast copper door pull boss with circular rosette backplate
        handle_x = leaf_w - 0.16 if is_left else -(leaf_w - 0.16)
        bmesh.ops.create_cone(
            bm, cap_ends=True, segments=12,
            radius1=0.08, radius2=0.05, depth=0.02,
            matrix=Matrix.Translation((handle_x, leaf_th + 0.02, 1.45)) @
                   Matrix.Rotation(math.radians(90), 4, Vector((1, 0, 0)))
        )
        bmesh.ops.create_uvsphere(
            bm, u_segments=12, v_segments=8, radius=0.045,
            matrix=Matrix.Translation((handle_x, leaf_th + 0.05, 1.45))
        )

        me = bpy.data.meshes.new("Mesh_Copper_Door_Leaf_Left" if is_left else "Mesh_Copper_Door_Leaf_Right")
        bm.to_mesh(me)
        bm.free()
        for poly in me.polygons:
            poly.use_smooth = True
        return me

    # Left Door Leaf
    me_door_l = create_copper_door_leaf_mesh(is_left=True)
    obj_door_l = bpy.data.objects.new("Door_Leaf_Left", me_door_l)
    obj_door_l.location = Vector((-door_w/2, -0.10, base_z + 0.04))
    obj_door_l.rotation_euler = Euler((0, 0, math.radians(-75.0)), 'XYZ')
    bpy.context.collection.objects.link(obj_door_l)
    obj_door_l.data.materials.append(materials['copper'])
    apply_box_uv(obj_door_l, uv_scale=1.0)

    # Right Door Leaf
    me_door_r = create_copper_door_leaf_mesh(is_left=False)
    obj_door_r = bpy.data.objects.new("Door_Leaf_Right", me_door_r)
    obj_door_r.location = Vector((door_w/2, -0.10, base_z + 0.04))
    obj_door_r.rotation_euler = Euler((0, 0, math.radians(75.0)), 'XYZ')
    bpy.context.collection.objects.link(obj_door_r)
    obj_door_r.data.materials.append(materials['copper'])
    apply_box_uv(obj_door_r, uv_scale=1.0)


# ==============================================================================
# CANTILEVERED CANOPY & SCREENS
# ==============================================================================
def build_cantilever_canopy(materials):
    base_z = 0.40
    ceiling_z = base_z + 4.80 # 5.20m
    canopy_w = 30.0
    canopy_d = 14.6
    canopy_th = 0.36
    center_y = (-0.6 + 14.0) / 2.0 # 6.70m

    # Canopy Roof Slab
    bm_roof = bmesh.new()
    bmesh.ops.create_cube(
        bm_roof, size=1.0,
        matrix=Matrix.Translation((0, center_y, ceiling_z + canopy_th/2)) @
               Matrix.Scale(canopy_w, 4, Vector((1, 0, 0))) @
               Matrix.Scale(canopy_d, 4, Vector((0, 1, 0))) @
               Matrix.Scale(canopy_th, 4, Vector((0, 0, 1)))
    )
    me_roof = bpy.data.meshes.new("Mesh_Canopy_Roof_Slab")
    bm_roof.to_mesh(me_roof)
    bm_roof.free()
    obj_roof = bpy.data.objects.new("Canopy_Roof_Slab", me_roof)
    bpy.context.collection.objects.link(obj_roof)
    obj_roof.data.materials.append(materials['terracotta'])
    apply_smart_uv(obj_roof)

    # Architectural Black Fascia Trim around front and flanks
    bm_fascia = bmesh.new()
    fascia_h = canopy_th + 0.10
    fascia_th = 0.10

    # Front fascia at Y = 14.0
    bmesh.ops.create_cube(
        bm_fascia, size=1.0,
        matrix=Matrix.Translation((0, 14.0 + fascia_th/2, ceiling_z + canopy_th/2)) @
               Matrix.Scale(canopy_w + fascia_th * 2, 4, Vector((1, 0, 0))) @
               Matrix.Scale(fascia_th, 4, Vector((0, 1, 0))) @
               Matrix.Scale(fascia_h, 4, Vector((0, 0, 1)))
    )
    # Left flank fascia
    bmesh.ops.create_cube(
        bm_fascia, size=1.0,
        matrix=Matrix.Translation((-canopy_w/2 - fascia_th/2, center_y, ceiling_z + canopy_th/2)) @
               Matrix.Scale(fascia_th, 4, Vector((1, 0, 0))) @
               Matrix.Scale(canopy_d, 4, Vector((0, 1, 0))) @
               Matrix.Scale(fascia_h, 4, Vector((0, 0, 1)))
    )
    # Right flank fascia
    bmesh.ops.create_cube(
        bm_fascia, size=1.0,
        matrix=Matrix.Translation((canopy_w/2 + fascia_th/2, center_y, ceiling_z + canopy_th/2)) @
               Matrix.Scale(fascia_th, 4, Vector((1, 0, 0))) @
               Matrix.Scale(canopy_d, 4, Vector((0, 1, 0))) @
               Matrix.Scale(fascia_h, 4, Vector((0, 0, 1)))
    )

    me_fascia = bpy.data.meshes.new("Mesh_Canopy_Fascia")
    bm_fascia.to_mesh(me_fascia)
    bm_fascia.free()
    obj_fascia = bpy.data.objects.new("Canopy_Edge_Fascia", me_fascia)
    bpy.context.collection.objects.link(obj_fascia)
    obj_fascia.data.materials.append(materials['black_beams'])
    apply_smart_uv(obj_fascia)

    # Coffered Black Grid Beams across the entire expanded corridor ceiling
    bm_ceiling = bmesh.new()
    beam_w = 0.16
    beam_d = 0.18

    # Longitudinal black beams running along Y
    for x_c in np.linspace(-canopy_w/2 + 0.8, canopy_w/2 - 0.8, 17):
        bmesh.ops.create_cube(
            bm_ceiling, size=1.0,
            matrix=Matrix.Translation((x_c, center_y, ceiling_z - beam_d/2)) @
                   Matrix.Scale(beam_w, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(canopy_d - 0.2, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(beam_d, 4, Vector((0, 0, 1)))
        )
    # Transverse black beams running along X
    for y_c in np.linspace(0.8, 13.2, 9):
        bmesh.ops.create_cube(
            bm_ceiling, size=1.0,
            matrix=Matrix.Translation((0, y_c, ceiling_z - beam_d/2)) @
                   Matrix.Scale(canopy_w - 0.2, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(beam_w, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(beam_d, 4, Vector((0, 0, 1)))
        )

    me_ceiling = bpy.data.meshes.new("Mesh_Canopy_Black_Beams")
    bm_ceiling.to_mesh(me_ceiling)
    bm_ceiling.free()
    obj_ceiling = bpy.data.objects.new("Canopy_Black_Beams", me_ceiling)
    bpy.context.collection.objects.link(obj_ceiling)
    obj_ceiling.data.materials.append(materials['black_beams'])
    apply_smart_uv(obj_ceiling)


def build_screens_and_amenities(materials):
    # Free and open corridor circulation (screens removed per user request)
    pass


# ==============================================================================
# ==============================================================================
# EXPANDED SACRED ENVELOPE (PURE TRIANGULAR MANDAPAM & RAISED SANCTUM ROOF)
# ==============================================================================
def add_wall_prism(bm, p1_in, p1_out, p2_in, p2_out, z_bot, z_top1, z_top2):
    v1 = bm.verts.new((p1_in.x, p1_in.y, z_bot))
    v2 = bm.verts.new((p1_out.x, p1_out.y, z_bot))
    v3 = bm.verts.new((p2_out.x, p2_out.y, z_bot))
    v4 = bm.verts.new((p2_in.x, p2_in.y, z_bot))
    v5 = bm.verts.new((p1_in.x, p1_in.y, z_top1))
    v6 = bm.verts.new((p1_out.x, p1_out.y, z_top1))
    v7 = bm.verts.new((p2_out.x, p2_out.y, z_top2))
    v8 = bm.verts.new((p2_in.x, p2_in.y, z_top2))

    bm.faces.new([v1, v2, v3, v4])
    bm.faces.new([v8, v7, v6, v5])
    bm.faces.new([v1, v5, v6, v2])
    bm.faces.new([v2, v6, v7, v3])
    bm.faces.new([v3, v7, v8, v4])
    bm.faces.new([v4, v8, v5, v1])


def build_triangular_sanctum_envelope(materials):
    """
    Constructs the Authentic Pure Triangular Linga Bhairavi Temple Structure:
    1. Continuous Symmetrical Triangular Perimeter Walls:
       - Baseline at front corners: (-15.0, 0.0) and (+15.0, 0.0) (30m wide).
       - Converges directly to the sacred rear apex behind Devi at (0.0, -38.0).
       - Left Wall: (-15.0, 0.0) -> (0.0, -38.0)
       - Right Wall: (+15.0, 0.0) -> (0.0, -38.0)
       - Wall thickness: 0.65m thick dressed ashlar granite and golden sandstone.
    2. Open-Sky Ceremonial Forecourt with 1m Edge Triangular Roof Beams & Suspended Metal Chains:
       - Wall height: Z = 6.20m with carved coping parapet band at Z in [6.20m, 6.55m].
       - Framed by monumental 1-meter edge triangular roof beams (1m cross-section).
       - Filled with suspended 3D metal chains forming a permeable temple trellis.
       - Looking up from the floor, the open sky and clouds remain completely visible through the chains!
    3. Flat Raised Triangular Roof over Sanctum (Y: -20.0m -> -38.0m):
       - Per user request: flat roof above Devi idol with a little raised height.
       - Sanctum walls rise to uniform raised horizontal height Z = 7.60m.
       - Flat triangular architectural roof slab rests at Z in [7.60m, 8.10m] (0.50m thick) with eaves overhang.
       - 3 Sacred Golden Kalashas stand proudly on the flat raised roof slab.
    """
    base_z = 0.40
    apex_y = -38.0
    front_y = 0.0
    mid_y = -20.0
    front_w = 15.0
    fc_h = 6.20
    sc_flat_z = 7.60    # Flat raised roof bottom (elevated above forecourt parapet)
    sc_flat_top = 8.10  # Flat raised roof top (0.50m solid architectural slab)

    w_mid = front_w * (apex_y - mid_y) / (apex_y - front_y)  # 7.105m

    # 1. TRIANGULAR PERIMETER WALLS
    bm_walls = bmesh.new()

    p_li_f = Vector((-front_w, front_y))
    p_lo_f = Vector((-front_w - 0.65, front_y))
    p_li_m = Vector((-w_mid, mid_y))
    p_lo_m = Vector((-w_mid - 0.65, mid_y))
    p_i_ap = Vector((0.0, apex_y))
    p_o_ap = Vector((0.0, apex_y - 1.65))

    p_ri_f = Vector((front_w, front_y))
    p_ro_f = Vector((front_w + 0.65, front_y))
    p_ri_m = Vector((w_mid, mid_y))
    p_ro_m = Vector((w_mid + 0.65, mid_y))

    # Left Wall Forecourt (Y: 0.0 to -20.0, Open Sky overhead, rooted into plinth)
    add_wall_prism(bm_walls, p_li_f, p_lo_f, p_li_m, p_lo_m, 0.0, fc_h, fc_h)
    # Left Wall Sanctum (Y: -20.0 to -38.0, plunging below sunken floor to Z = -0.85m, rising to flat roof Z = 7.60m)
    add_wall_prism(bm_walls, p_li_m, p_lo_m, p_i_ap, p_o_ap, -0.85, sc_flat_z, sc_flat_z)

    # Right Wall Forecourt (Y: 0.0 to -20.0, Open Sky overhead, rooted into plinth)
    add_wall_prism(bm_walls, p_ri_f, p_ro_f, p_ri_m, p_ro_m, 0.0, fc_h, fc_h)
    # Right Wall Sanctum (Y: -20.0 to -38.0, plunging below sunken floor to Z = -0.85m, rising to flat roof Z = 7.60m)
    add_wall_prism(bm_walls, p_ri_m, p_ro_m, p_i_ap, p_o_ap, -0.85, sc_flat_z, sc_flat_z)

    # Forecourt Parapet Coping Moulding (Z: 6.20m -> 6.55m)
    add_wall_prism(bm_walls, p_li_f + Vector((-0.05, 0)), p_lo_f + Vector((-0.10, 0)), p_li_m + Vector((-0.05, 0)), p_lo_m + Vector((-0.10, 0)), fc_h, fc_h + 0.35, fc_h + 0.35)
    add_wall_prism(bm_walls, p_ri_f + Vector((0.05, 0)), p_ro_f + Vector((0.10, 0)), p_ri_m + Vector((0.05, 0)), p_ro_m + Vector((0.10, 0)), fc_h, fc_h + 0.35, fc_h + 0.35)

    bmesh.ops.recalc_face_normals(bm_walls, faces=bm_walls.faces)
    me_walls = bpy.data.meshes.new("Mesh_Sanctum_Triangular_Walls")
    bm_walls.to_mesh(me_walls)
    bm_walls.free()

    obj_walls = bpy.data.objects.new("Sanctum_Triangular_Walls", me_walls)
    bpy.context.collection.objects.link(obj_walls)
    obj_walls.data.materials.append(materials['granite_wall'])
    apply_box_uv(obj_walls, uv_scale=1.0)

    # 1B. SACRED SANCTUM DIVIDING BRICK WALL (FILLING GAP FROM BIG PILLARS & NAGA PANEL TO HIGHER ROOF)
    # Per user: "fill the gap of the higher roffing to the naga panel which is on top of the big pillers with brick walls"
    bm_brick = bmesh.new()
    wall_y = mid_y - 0.05 # Y = -20.05m
    wall_thick = 0.50     # Y in [-20.30, -19.80]
    top_z = sc_flat_top   # Z = 8.10m (seals into higher flat roof)

    # Left Flank Brick Wall (X in [-w_mid, -3.20], Z in [4.25, top_z])
    x_l = (-w_mid + -3.20) / 2.0
    w_l = -3.20 - (-w_mid)
    h_l = top_z - 4.25
    z_l = 4.25 + h_l / 2.0
    bmesh.ops.create_cube(
        bm_brick, size=1.0,
        matrix=Matrix.Translation((x_l, wall_y, z_l)) @
               Matrix.Scale(w_l, 4, Vector((1, 0, 0))) @
               Matrix.Scale(wall_thick, 4, Vector((0, 1, 0))) @
               Matrix.Scale(h_l, 4, Vector((0, 0, 1)))
    )

    # Right Flank Brick Wall (X in [3.20, w_mid], Z in [4.25, top_z])
    x_r = (3.20 + w_mid) / 2.0
    w_r = w_mid - 3.20
    h_r = top_z - 4.25
    z_r = 4.25 + h_r / 2.0
    bmesh.ops.create_cube(
        bm_brick, size=1.0,
        matrix=Matrix.Translation((x_r, wall_y, z_r)) @
               Matrix.Scale(w_r, 4, Vector((1, 0, 0))) @
               Matrix.Scale(wall_thick, 4, Vector((0, 1, 0))) @
               Matrix.Scale(h_r, 4, Vector((0, 0, 1)))
    )

    # Central Section Above Naga Panel (X in [-3.50, 3.50], Z in [5.40, top_z])
    w_c = 7.00
    h_c = top_z - 5.40
    z_c = 5.40 + h_c / 2.0
    bmesh.ops.create_cube(
        bm_brick, size=1.0,
        matrix=Matrix.Translation((0.0, wall_y, z_c)) @
               Matrix.Scale(w_c, 4, Vector((1, 0, 0))) @
               Matrix.Scale(wall_thick, 4, Vector((0, 1, 0))) @
               Matrix.Scale(h_c, 4, Vector((0, 0, 1)))
    )

    # Central Backing Wall Behind Naga Panel (X in [-3.50, 3.50], Z in [4.25, 5.45])
    # Positioned slightly back at Y = wall_y - 0.10 so Naga relief stands proud in front
    h_b = 5.45 - 4.25
    z_b = 4.25 + h_b / 2.0
    bmesh.ops.create_cube(
        bm_brick, size=1.0,
        matrix=Matrix.Translation((0.0, wall_y - 0.10, z_b)) @
               Matrix.Scale(w_c, 4, Vector((1, 0, 0))) @
               Matrix.Scale(wall_thick, 4, Vector((0, 1, 0))) @
               Matrix.Scale(h_b, 4, Vector((0, 0, 1)))
    )

    bmesh.ops.recalc_face_normals(bm_brick, faces=bm_brick.faces)
    me_brick = bpy.data.meshes.new("Mesh_Sanctum_Dividing_Brick_Wall")
    bm_brick.to_mesh(me_brick)
    bm_brick.free()

    obj_brick = bpy.data.objects.new("Sanctum_Dividing_Brick_Wall", me_brick)
    bpy.context.collection.objects.link(obj_brick)
    obj_brick.data.materials.append(materials['brick_wall'])
    apply_box_uv(obj_brick, uv_scale=1.5)

    # 2. RAISED FLAT TRIANGULAR ROOF OVER SANCTUM (Y: -20.0m -> -38.0m)
    # Per user: "make the roof of the small traingle roof which is in above the devi idol flat and a little raised hight"
    bm_roof = bmesh.new()

    # Flat Triangular Slab (Bottom at Z = 7.60m, Top at Z = 8.10m, with 0.45m perimeter eaves overhang)
    v_fl_b = bm_roof.verts.new((-w_mid - 1.10, mid_y + 0.35, sc_flat_z))
    v_fr_b = bm_roof.verts.new(( w_mid + 1.10, mid_y + 0.35, sc_flat_z))
    v_ap_b = bm_roof.verts.new(( 0.00, apex_y - 2.10, sc_flat_z))

    v_fl_t = bm_roof.verts.new((-w_mid - 1.10, mid_y + 0.35, sc_flat_top))
    v_fr_t = bm_roof.verts.new(( w_mid + 1.10, mid_y + 0.35, sc_flat_top))
    v_ap_t = bm_roof.verts.new(( 0.00, apex_y - 2.10, sc_flat_top))

    # Bottom ceiling face
    bm_roof.faces.new([v_fl_b, v_fr_b, v_ap_b])
    # Top roof face
    bm_roof.faces.new([v_fl_t, v_ap_t, v_fr_t])
    # Front fascia face
    bm_roof.faces.new([v_fl_b, v_fl_t, v_fr_t, v_fr_b])
    # Right eaves fascia face
    bm_roof.faces.new([v_fr_b, v_fr_t, v_ap_t, v_ap_b])
    # Left eaves fascia face
    bm_roof.faces.new([v_ap_b, v_ap_t, v_fl_t, v_fl_b])

    bmesh.ops.recalc_face_normals(bm_roof, faces=bm_roof.faces)
    me_roof = bpy.data.meshes.new("Mesh_Sanctum_Raised_Flat_Roof")
    bm_roof.to_mesh(me_roof)
    bm_roof.free()

    obj_roof = bpy.data.objects.new("Sanctum_Raised_Flat_Roof", me_roof)
    bpy.context.collection.objects.link(obj_roof)
    obj_roof.data.materials.append(materials['fascia'])
    apply_box_uv(obj_roof, uv_scale=1.0)

    # 3. SACRED GOLDEN KALASHAS ON THE FLAT RAISED ROOF
    bm_kalashas = bmesh.new()
    for ky in [-23.5, -28.5, -33.5]:
        kz = sc_flat_top
        # Urn base plinth
        bmesh.ops.create_cube(
            bm_kalashas, size=1.0,
            matrix=Matrix.Translation((0.0, ky, kz + 0.08)) @
                   Matrix.Scale(0.60, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(0.60, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(0.16, 4, Vector((0, 0, 1)))
        )
        # Urn body
        bmesh.ops.create_uvsphere(
            bm_kalashas, u_segments=16, v_segments=10, radius=0.28,
            matrix=Matrix.Translation((0.0, ky, kz + 0.44)) @ Matrix.Scale(0.85, 4, Vector((0, 0, 1)))
        )
        # Pointed spire finial
        bmesh.ops.create_cone(
            bm_kalashas, cap_ends=True, segments=12, radius1=0.18, radius2=0.01, depth=0.55,
            matrix=Matrix.Translation((0.0, ky, kz + 0.84))
        )
    bmesh.ops.recalc_face_normals(bm_kalashas, faces=bm_kalashas.faces)
    me_kalashas = bpy.data.meshes.new("Mesh_Sanctum_Golden_Kalashas")
    bm_kalashas.to_mesh(me_kalashas)
    bm_kalashas.free()
    obj_kalashas = bpy.data.objects.new("Sanctum_Golden_Kalashas", me_kalashas)
    bpy.context.collection.objects.link(obj_kalashas)
    obj_kalashas.data.materials.append(materials['gold'])
    apply_smart_uv(obj_kalashas)

    # 4. MONUMENTAL 1-METER EDGE ROOF BEAMS OVER OPEN FORECOURT (Y: 0.0m -> -20.0m)
    # Per user: "in the open area where there is nothing covering make a triangle 1 mtr edge roof beam"
    bm_beams = bmesh.new()
    beam_w = 1.00 # Exact 1-meter edge thickness
    beam_h = 0.80 # 0.80m tall structural cross-section (Z: 6.20m to 7.00m)
    beam_z = fc_h # 6.20m

    def add_1m_beam(bm, p1, p2, z_bot, height, width):
        p1_vec = Vector((p1[0], p1[1]))
        p2_vec = Vector((p2[0], p2[1]))
        dir_vec = (p2_vec - p1_vec).normalized()
        perp = Vector((-dir_vec.y, dir_vec.x)) * (width / 2.0)

        v1_b = bm.verts.new((p1_vec.x - perp.x, p1_vec.y - perp.y, z_bot))
        v2_b = bm.verts.new((p1_vec.x + perp.x, p1_vec.y + perp.y, z_bot))
        v3_b = bm.verts.new((p2_vec.x + perp.x, p2_vec.y + perp.y, z_bot))
        v4_b = bm.verts.new((p2_vec.x - perp.x, p2_vec.y - perp.y, z_bot))

        v1_t = bm.verts.new((p1_vec.x - perp.x, p1_vec.y - perp.y, z_bot + height))
        v2_t = bm.verts.new((p1_vec.x + perp.x, p1_vec.y + perp.y, z_bot + height))
        v3_t = bm.verts.new((p2_vec.x + perp.x, p2_vec.y + perp.y, z_bot + height))
        v4_t = bm.verts.new((p2_vec.x - perp.x, p2_vec.y - perp.y, z_bot + height))

        bm.faces.new([v1_b, v2_b, v3_b, v4_b])
        bm.faces.new([v4_t, v3_t, v2_t, v1_t])
        bm.faces.new([v1_b, v1_t, v2_t, v2_b])
        bm.faces.new([v2_b, v2_t, v3_t, v3_b])
        bm.faces.new([v3_b, v3_t, v4_t, v4_b])
        bm.faces.new([v4_b, v4_t, v1_t, v1_b])

    # A. 1-Meter Front Perimeter Beam (along Y = 0.0m)
    add_1m_beam(bm_beams, (-front_w - 0.3, front_y), (front_w + 0.3, front_y), beam_z, beam_h, beam_w)

    # B. 1-Meter Left Sloping Perimeter Beam (along Left Wall)
    add_1m_beam(bm_beams, (-front_w, front_y), (-w_mid, mid_y), beam_z, beam_h, beam_w)

    # C. 1-Meter Right Sloping Perimeter Beam (along Right Wall)
    add_1m_beam(bm_beams, (front_w, front_y), (w_mid, mid_y), beam_z, beam_h, beam_w)

    # D. 1-Meter Rear Architrave Beam (across Y = -20.0m)
    add_1m_beam(bm_beams, (-w_mid - 0.3, mid_y), (w_mid + 0.3, mid_y), beam_z, beam_h, beam_w)

    # E. Sacred Triangular Internal Framing Beams (1-meter edge)
    # Converging triangular rafters framing an inner triangular sky opening
    add_1m_beam(bm_beams, (-11.0, -1.0), (0.0, -14.0), beam_z, beam_h, beam_w)
    add_1m_beam(bm_beams, ( 11.0, -1.0), (0.0, -14.0), beam_z, beam_h, beam_w)
    # Intermediate cross tie beam across Y = -9.0m (above Trishul monument)
    add_1m_beam(bm_beams, (-10.5, -9.0), (10.5, -9.0), beam_z, beam_h, beam_w)

    bmesh.ops.recalc_face_normals(bm_beams, faces=bm_beams.faces)
    me_beams = bpy.data.meshes.new("Mesh_Forecourt_Triangular_Roof_Beams")
    bm_beams.to_mesh(me_beams)
    bm_beams.free()

    obj_beams = bpy.data.objects.new("Forecourt_Triangular_Roof_Beams", me_beams)
    bpy.context.collection.objects.link(obj_beams)
    obj_beams.data.materials.append(materials['black_beams'])
    apply_box_uv(obj_beams, uv_scale=1.0)

    # 5. SUSPENDED 3D METAL CHAINS FILLING THE OPEN ROOF AREA (UP VISIBLE SKY)
    # Per user: "ok but download a chain asset from the internet and make traingles and fill the whole sealing with it more smaller triangles and no chains should be hanging down"
    chain_z = beam_z + 0.35 # Suspended at Z = 6.55m
    chain_obj_path = "/home/mullainathan/Games/IshaGodot/assets/models/chain_link.obj"

    # Load authentic downloaded 3D chain link model
    src_verts = []
    src_faces = []
    if os.path.exists(chain_obj_path):
        bpy.ops.wm.obj_import(filepath=chain_obj_path)
        temp_chain_obj = bpy.context.selected_objects[0]
        # Decimate cleanly to optimize vertex performance while preserving smooth curvature
        mod_dec = temp_chain_obj.modifiers.new('Decimate', 'DECIMATE')
        mod_dec.ratio = 0.35
        bpy.context.view_layer.objects.active = temp_chain_obj
        bpy.ops.object.modifier_apply(modifier='Decimate')
        for v in temp_chain_obj.data.vertices:
            src_verts.append(v.co.copy())
        for poly in temp_chain_obj.data.polygons:
            src_faces.append([vi for vi in poly.vertices])
        bpy.data.objects.remove(temp_chain_obj, do_unlink=True)
    else:
        # Fallback procedural torus link if file unavailable
        bm_tmp = bmesh.new()
        bmesh.ops.create_torus(bm_tmp, major_radius=0.07, minor_radius=0.022, major_segments=12, minor_segments=8)
        me_tmp = bpy.data.meshes.new("TempFallback")
        bm_tmp.to_mesh(me_tmp)
        bm_tmp.free()
        for v in me_tmp.vertices:
            src_verts.append(v.co.copy())
        for poly in me_tmp.polygons:
            src_faces.append([vi for vi in poly.vertices])
        bpy.data.meshes.remove(me_tmp)

    n_src_v = len(src_verts)

    # Generate dense triangular lattice tessellation (hundreds of smaller triangles covering ceiling aperture)
    y_start = -1.0
    y_end = -19.2
    n_rows = 14
    dx = 1.60

    rows = []
    for k in range(n_rows):
        y = y_start + k * (y_end - y_start) / (n_rows - 1)
        w = front_w + (y / -20.0) * (w_mid - front_w)
        offset = (dx * 0.5) if (k % 2 == 1) else 0.0
        xs = []
        m_min = math.ceil((-w - offset) / dx)
        m_max = math.floor((w - offset) / dx)
        for m in range(m_min, m_max + 1):
            x = m * dx + offset
            if abs(x) <= w:
                xs.append(x)
        if xs and xs[0] > -w + 0.35:
            xs.insert(0, -w)
        elif not xs:
            xs = [-w, w]
        if xs and xs[-1] < w - 0.35:
            xs.append(w)
        rows.append((y, xs))

    edges = set()
    def add_edge(p1, p2):
        k1 = (round(p1.x, 3), round(p1.y, 3))
        k2 = (round(p2.x, 3), round(p2.y, 3))
        if k1 != k2:
            if k1 > k2:
                k1, k2 = k2, k1
            edges.add((k1, k2))

    for k in range(n_rows):
        y, xs = rows[k]
        # Horizontal edges
        for i in range(len(xs) - 1):
            add_edge(Vector((xs[i], y, chain_z)), Vector((xs[i+1], y, chain_z)))
        # Diagonal edges connecting to adjacent row to create smaller triangles
        if k < n_rows - 1:
            y_next, xs_next = rows[k+1]
            for x in xs:
                p_curr = Vector((x, y, chain_z))
                sorted_next = sorted(xs_next, key=lambda xn: abs(xn - x))
                for xn in sorted_next[:2]:
                    if abs(xn - x) <= dx * 1.35:
                        add_edge(p_curr, Vector((xn, y_next, chain_z)))
            for xn in xs_next:
                p_next = Vector((xn, y_next, chain_z))
                sorted_curr = sorted(xs, key=lambda xc: abs(xc - xn))
                for xc in sorted_curr[:2]:
                    if abs(xc - xn) <= dx * 1.35:
                        add_edge(Vector((xc, y, chain_z)), p_next)

    # Strictly NO hanging vertical chains: all chains remain elevated at the ceiling (Z ~ 6.55m)
    # Instantiate authentic chain link units along all triangle edges
    scale = 0.052
    pitch = 4.0 * scale
    z_axis = Vector((0, 0, 1))

    all_verts = []
    all_faces = []
    vert_offset = 0

    for (x1, y1), (x2, y2) in sorted(list(edges)):
        p1 = Vector((x1, y1, chain_z))
        p2 = Vector((x2, y2, chain_z))
        delta = p2 - p1
        dist = delta.length
        if dist < 0.15:
            continue
        direction = delta.normalized()
        rot = z_axis.rotation_difference(direction)
        n_units = max(1, int(round(dist / pitch)))
        for i in range(n_units):
            t = (i + 0.5) / n_units
            pos = p1.lerp(p2, t)
            pos.z -= 4.0 * 0.035 * t * (1.0 - t) # Gentle realistic 3.5cm catenary sag
            mat = Matrix.Translation(pos) @ (rot.to_matrix().to_4x4() @ Matrix.Diagonal(Vector((scale, scale, scale, 1.0))))
            for v in src_verts:
                all_verts.append(mat @ v)
            for f in src_faces:
                all_faces.append([vi + vert_offset for vi in f])
            vert_offset += n_src_v

    me_chains = bpy.data.meshes.new("Mesh_Forecourt_Roof_Metal_Chains")
    me_chains.from_pydata(all_verts, [], all_faces)
    me_chains.update()

    obj_chains = bpy.data.objects.new("Forecourt_Roof_Metal_Chains", me_chains)
    bpy.context.collection.objects.link(obj_chains)
    obj_chains.data.materials.append(materials['metal_chain'])


# ==============================================================================
# 2. GRAND STEPPED INTERIOR ARCHITECTURE (MANDAPAM & GARBHAGRIHA)
# ==============================================================================
# ==============================================================================
# DIAMOND-CUT JALI PILLAR & SARPA BANDHA KNOT HELPERS (devi.jpg REPLICA)
# ==============================================================================
# ==============================================================================
# DIAMOND-CUT JALI PILLAR & SARPA BANDHA KNOT HELPERS (devi.jpg REPLICA)
# ==============================================================================
def clip_line_to_box(m, c, x_min, x_max, z_min, z_max):
    pts = []
    z = m * x_min + c
    if z_min - 1e-5 <= z <= z_max + 1e-5:
        pts.append((x_min, z))
    z = m * x_max + c
    if z_min - 1e-5 <= z <= z_max + 1e-5:
        pts.append((x_max, z))
    if abs(m) > 1e-5:
        x = (z_min - c) / m
        if x_min - 1e-5 <= x <= x_max + 1e-5:
            pts.append((x, z_min))
        x = (z_max - c) / m
        if x_min - 1e-5 <= x <= x_max + 1e-5:
            pts.append((x, z_max))
    unique = []
    for p in pts:
        if not any(math.hypot(p[0]-u[0], p[1]-u[1]) < 1e-4 for u in unique):
            unique.append(p)
    if len(unique) == 2:
        return unique[0], unique[1]
    return None

def create_lattice_segment(bm, p1, p2, width, depth, normal_axis='Y'):
    v = p2 - p1
    length = v.length
    if length < 0.05:
        return
    mid = (p1 + p2) * 0.5
    angle = math.atan2(v.z, v.x)
    mat = Matrix.Translation(mid) @ Matrix.Rotation(math.pi/2 - angle, 4, normal_axis) @ Matrix.Scale(length, 4, Vector((0, 0, 1))) @ Matrix.Scale(width, 4, Vector((1, 0, 0))) @ Matrix.Scale(depth, 4, Vector((0, 1, 0)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat)

def build_diamond_jali_pillar_mesh(name_prefix):
    """
    Constructs an authentic monumental square pillar as shown in devi.jpg:
    - Base Plinth: Fluted light stone base with vertical carved ribs (Z: 0.40m -> 1.05m)
    - Padma Peetham: Flaring carved lotus petal tier with 4 projecting corner makara/lotus brackets (Z: 1.05m -> 1.55m)
    - Diamond-Cut Lattice Shaft: Openwork stone shaft with 3 diamonds wide x 4 diamonds high (Z: 1.55m -> 3.75m)
    - Stepped Capital Cornice: Tiered expanding molded brackets (Z: 3.75m -> 4.25m)
    """
    bm = bmesh.new()
    
    # 1. Base Plinth (Adhisthana)
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation((0.0, 0.0, 0.40 + 0.125)) @
               Matrix.Scale(1.75, 4, Vector((1, 0, 0))) @
               Matrix.Scale(1.75, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.25, 4, Vector((0, 0, 1)))
    )
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation((0.0, 0.0, 0.65 + 0.15)) @
               Matrix.Scale(1.60, 4, Vector((1, 0, 0))) @
               Matrix.Scale(1.60, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.30, 4, Vector((0, 0, 1)))
    )
    # Vertical carved fluting ribs on all 4 faces
    for face_rot in [0, 90, 180, 270]:
        rad = math.radians(face_rot)
        for fx in [-0.50, -0.30, -0.10, 0.10, 0.30, 0.50]:
            mat_flute = Matrix.Rotation(rad, 4, 'Z') @ Matrix.Translation((fx, 0.80 + 0.02, 0.65 + 0.15)) @ Matrix.Scale(0.08, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.28, 4, Vector((0, 0, 1)))
            bmesh.ops.create_cube(bm, size=1.0, matrix=mat_flute)
    # Upper plinth molding step
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation((0.0, 0.0, 0.95 + 0.05)) @
               Matrix.Scale(1.68, 4, Vector((1, 0, 0))) @
               Matrix.Scale(1.68, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.10, 4, Vector((0, 0, 1)))
    )
    
    # 2. Padma Peetham (Carved Flaring Lotus Tier, Z in [1.05, 1.55])
    # Flaring lotus cushion
    bmesh.ops.create_cone(
        bm, cap_ends=True, segments=32,
        radius1=0.88, radius2=0.74, depth=0.50,
        matrix=Matrix.Translation((0.0, 0.0, 1.05 + 0.25))
    )
    # 4 Corner projecting brackets (Makaras / Lotus buds)
    for dx, dy in [(-0.80, -0.80), (0.80, -0.80), (-0.80, 0.80), (0.80, 0.80)]:
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((dx, dy, 1.05 + 0.25)) @
                   Matrix.Scale(0.26, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(0.26, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(0.48, 4, Vector((0, 0, 1)))
        )

    # 3. Openwork Diamond Jali Lattice Shaft (Z in [1.55, 3.75], height 2.20m)
    w = 1.38
    h = 2.20
    sw = 0.13
    z_base = 1.55
    
    # 4 Corner square stone posts
    for cx in [-w/2 + sw/2, w/2 - sw/2]:
        for cy in [-w/2 + sw/2, w/2 - sw/2]:
            bmesh.ops.create_cube(
                bm, size=1.0,
                matrix=Matrix.Translation((cx, cy, z_base + h/2)) @
                       Matrix.Scale(sw, 4, Vector((1, 0, 0))) @
                       Matrix.Scale(sw, 4, Vector((0, 1, 0))) @
                       Matrix.Scale(h, 4, Vector((0, 0, 1)))
            )
            
    # Bottom and top horizontal stone framing rails
    for zr in [z_base + sw/2, z_base + h - sw/2]:
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((0.0, 0.0, zr)) @
                   Matrix.Scale(w, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(w, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(sw, 4, Vector((0, 0, 1)))
        )
        
    # Diagonal Diamond Lattice (3 diamonds wide x 4 diamonds high)
    x_min, x_max = -w/2 + sw, w/2 - sw
    z_min, z_max = z_base + sw, z_base + h - sw
    pitch = 0.36
    strut_w = 0.075
    strut_d = 0.12
    
    # Front (+Y) and Back (-Y) faces
    for y_sign in [1.0, -1.0]:
        y_pos = y_sign * (w/2 - strut_d/2)
        c_min = int((z_min - x_max) / pitch) - 1
        c_max = int((z_max - x_min) / pitch) + 1
        for i in range(c_min, c_max + 1):
            c = i * pitch
            res = clip_line_to_box(1.0, c, x_min, x_max, z_min, z_max)
            if res:
                create_lattice_segment(bm, Vector((res[0][0], y_pos, res[0][1])), Vector((res[1][0], y_pos, res[1][1])), strut_w, strut_d, 'Y')
        c_min = int((z_min + x_min) / pitch) - 1
        c_max = int((z_max + x_max) / pitch) + 1
        for i in range(c_min, c_max + 1):
            c = i * pitch
            res = clip_line_to_box(-1.0, c, x_min, x_max, z_min, z_max)
            if res:
                create_lattice_segment(bm, Vector((res[0][0], y_pos, res[0][1])), Vector((res[1][0], y_pos, res[1][1])), strut_w, strut_d, 'Y')

    # Left (-X) and Right (+X) faces
    y_min, y_max = -w/2 + sw, w/2 - sw
    for x_sign in [1.0, -1.0]:
        x_pos = x_sign * (w/2 - strut_d/2)
        c_min = int((z_min - y_max) / pitch) - 1
        c_max = int((z_max - y_min) / pitch) + 1
        for i in range(c_min, c_max + 1):
            c = i * pitch
            res = clip_line_to_box(1.0, c, y_min, y_max, z_min, z_max)
            if res:
                v = Vector((0.0, res[1][0] - res[0][0], res[1][1] - res[0][1]))
                length = v.length
                if length >= 0.05:
                    mid = Vector((x_pos, (res[0][0] + res[1][0]) * 0.5, (res[0][1] + res[1][1]) * 0.5))
                    angle = math.atan2(v.z, v.y)
                    mat = Matrix.Translation(mid) @ Matrix.Rotation(-(math.pi/2 - angle), 4, 'X') @ Matrix.Scale(strut_d, 4, Vector((1, 0, 0))) @ Matrix.Scale(strut_w, 4, Vector((0, 1, 0))) @ Matrix.Scale(length, 4, Vector((0, 0, 1)))
                    bmesh.ops.create_cube(bm, size=1.0, matrix=mat)
        c_min = int((z_min + y_min) / pitch) - 1
        c_max = int((z_max + y_max) / pitch) + 1
        for i in range(c_min, c_max + 1):
            c = i * pitch
            res = clip_line_to_box(-1.0, c, y_min, y_max, z_min, z_max)
            if res:
                v = Vector((0.0, res[1][0] - res[0][0], res[1][1] - res[0][1]))
                length = v.length
                if length >= 0.05:
                    mid = Vector((x_pos, (res[0][0] + res[1][0]) * 0.5, (res[0][1] + res[1][1]) * 0.5))
                    angle = math.atan2(v.z, v.y)
                    mat = Matrix.Translation(mid) @ Matrix.Rotation(-(math.pi/2 - angle), 4, 'X') @ Matrix.Scale(strut_d, 4, Vector((1, 0, 0))) @ Matrix.Scale(strut_w, 4, Vector((0, 1, 0))) @ Matrix.Scale(length, 4, Vector((0, 0, 1)))
                    bmesh.ops.create_cube(bm, size=1.0, matrix=mat)

    # 4. Stepped Capital Cornice (Z in [3.75, 4.25], height 0.50m)
    cornices = [
        (3.75 + 0.06, 1.48, 0.12),
        (3.87 + 0.08, 1.62, 0.16),
        (4.03 + 0.11, 1.78, 0.22)
    ]
    for cz, cw, ch in cornices:
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation((0.0, 0.0, cz)) @
                   Matrix.Scale(cw, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(cw, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(ch, 4, Vector((0, 0, 1)))
        )

    me = bpy.data.meshes.new(f"Mesh_Diamond_Jali_Pillar_{name_prefix}")
    bm.to_mesh(me)
    bm.free()
    return me

def build_sarpa_bandha_knot_mesh():
    """
    Constructs the authentic 3D relief Golden Sarpa Bandha (intertwined serpent infinity knot):
    - Central vertical serpent knot with hood loop (top), figure-8 crossing (middle), and flared twin tails (bottom).
    - Flanking 8 intertwined horizontal figure-8 loops on left and right with open circular centers.
    - Connecting horizontal golden ribbons forming the sacred infinity braid.
    - All relief geometry faces +Y (towards camera looking along -Y).
    """
    bm = bmesh.new()
    depth = 0.040 # Relief depth projecting forward from architrave face
    
    # Helper to add a 3D annular ring in the X-Z plane (normal facing +Y towards camera)
    def add_ring(cx, cz, ro, ri, d):
        segs = 16
        for s in range(segs):
            a1 = 2 * math.pi * s / segs
            a2 = 2 * math.pi * (s + 1) / segs
            cos1, sin1 = math.cos(a1), math.sin(a1)
            cos2, sin2 = math.cos(a2), math.sin(a2)
            # Front face (+Y)
            v1 = bm.verts.new((cx + ro * cos1, d/2, cz + ro * sin1))
            v2 = bm.verts.new((cx + ro * cos2, d/2, cz + ro * sin2))
            v3 = bm.verts.new((cx + ri * cos2, d/2, cz + ri * sin2))
            v4 = bm.verts.new((cx + ri * cos1, d/2, cz + ri * sin1))
            # Back face (-Y)
            v5 = bm.verts.new((cx + ro * cos1, -d/2, cz + ro * sin1))
            v6 = bm.verts.new((cx + ro * cos2, -d/2, cz + ro * sin2))
            v7 = bm.verts.new((cx + ri * cos2, -d/2, cz + ri * sin2))
            v8 = bm.verts.new((cx + ri * cos1, -d/2, cz + ri * sin1))
            bm.faces.new((v1, v2, v3, v4))
            bm.faces.new((v8, v7, v6, v5))
            bm.faces.new((v1, v5, v6, v2))
            bm.faces.new((v2, v6, v7, v3))
            bm.faces.new((v3, v7, v8, v4))
            bm.faces.new((v4, v8, v5, v1))

    # Helper to add a relief ribbon in X-Z plane
    def add_ribbon(x1, z1, x2, z2, width, d):
        dx = x2 - x1
        dz = z2 - z1
        l = math.hypot(dx, dz)
        if l < 1e-4:
            return
        nx = -dz / l * (width / 2)
        nz = dx / l * (width / 2)
        v1 = bm.verts.new((x1 + nx, d/2, z1 + nz))
        v2 = bm.verts.new((x2 + nx, d/2, z2 + nz))
        v3 = bm.verts.new((x2 - nx, d/2, z2 - nz))
        v4 = bm.verts.new((x1 - nx, d/2, z1 - nz))
        v5 = bm.verts.new((x1 + nx, -d/2, z1 + nz))
        v6 = bm.verts.new((x2 + nx, -d/2, z2 + nz))
        v7 = bm.verts.new((x2 - nx, -d/2, z2 - nz))
        v8 = bm.verts.new((x1 - nx, -d/2, z1 - nz))
        bm.faces.new((v1, v2, v3, v4))
        bm.faces.new((v8, v7, v6, v5))
        bm.faces.new((v1, v5, v6, v2))
        bm.faces.new((v2, v6, v7, v3))
        bm.faces.new((v3, v7, v8, v4))
        bm.faces.new((v4, v8, v5, v1))

    # 1. Flanking Intertwined Infinity Loops (8 on left, 8 on right)
    loop_spacing = 0.22
    for side in [-1, 1]:
        for i in range(1, 9):
            cx = side * (0.28 + (i - 1) * loop_spacing)
            # Top row loops
            add_ring(cx, 0.08, 0.075, 0.045, depth)
            # Bottom row loops
            add_ring(cx, -0.08, 0.075, 0.045, depth)
            # Intertwining diagonal ribbons between top and bottom loops
            add_ribbon(cx - 0.04 * side, 0.08, cx + 0.04 * side, -0.08, 0.028, depth * 0.9)
            add_ribbon(cx + 0.04 * side, 0.08, cx - 0.04 * side, -0.08, 0.028, depth * 0.9)
            # Horizontal connecting ribbons
            if i < 8:
                next_cx = side * (0.28 + i * loop_spacing)
                add_ribbon(cx, 0.08, next_cx, 0.08, 0.024, depth * 0.85)
                add_ribbon(cx, -0.08, next_cx, -0.08, 0.024, depth * 0.85)

    # 2. Central Vertical Serpent Knot & Hood Loop
    # Top hood loop (oval)
    add_ring(0.0, 0.25, 0.12, 0.075, depth * 1.25)
    # Middle crossing figure-8
    add_ring(0.0, 0.04, 0.09, 0.055, depth * 1.15)
    # Lower knot
    add_ring(0.0, -0.14, 0.08, 0.050, depth * 1.1)
    # Vertical connecting serpent ribbons
    add_ribbon(0.0, 0.25, 0.0, -0.14, 0.038, depth * 1.1)
    # Flaring serpent tails at bottom
    add_ribbon(0.0, -0.14, -0.15, -0.28, 0.032, depth)
    add_ribbon(0.0, -0.14, 0.15, -0.28, 0.032, depth)

    me = bpy.data.meshes.new("Mesh_Sarpa_Bandha_Knot")
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = True
    return me
# ==============================================================================
# AUTHENTIC INTERIOR ARCHITECTURE (1:1 REPLICA OF devi.jpg)
# ==============================================================================
def build_interior_architecture(materials):
    """
    Vast, expansive subterranean temple hall:
    - Door Naga Panel: Authentic relief cobra tile attached directly on top of the entrance door lintel.
    - 20-Meter Gap: Upper Entrance Forecourt Floor at Z = 0.40m spanning from Y = 0.0m to Y = -20.00m (width 20m).
    - Center Trishul Monument: Double-sided 3D metal trident with straightened shaft on stone pedestal at Y = -10.00m.
    - The 2 Big Pillars: Monumental diamond-cut lattice stone pillars standing at Y = -20.00m (X = +/- 3.00m).
    - Pillar Naga Architrave: Arched intertwined serpent panel on top of the big pillars bridging the span.
    - 5 Descending Steps: Exactly 5 steps starting right from the pillars (Y = -20.00m to -22.25m, drop from Z = 0.40m to -0.50m).
    - 3-Meter Gap: Sunken subterranean floor at Z = -0.50m (Y = -22.25m to -25.25m, width 18m).
    - Devi Sanctum Panel & Dais: Positioned at Y = -25.25m facing +Y towards devotees in the hall.
    - Monumental enclosing stone walls (Y = 0.0 to -26.50m) and beamed roof with zero light leaks.
    """
    base_z = 0.40
    sunken_z = -0.50
    parts_blend_path = "/home/mullainathan/Games/IshaGodot/assets/models/parts of devi temple.blend"

    # --------------------------------------------------------------------------
    # 0. ENTRANCE PORTAL NAGA PANEL (ON TOP OF MAIN ENTRANCE DOOR LINTEL)
    # --------------------------------------------------------------------------
    if os.path.exists(parts_blend_path):
        with bpy.data.libraries.load(parts_blend_path) as (data_from, data_to):
            if "front top of the door" in data_from.objects:
                data_to.objects = ["front top of the door"]

        if data_to.objects and data_to.objects[0]:
            obj_door_naga = data_to.objects[0]
            bpy.context.collection.objects.link(obj_door_naga)
            obj_door_naga.name = "Door_Naga_Panel"

            cs = obj_door_naga.modifiers.get("CorrectiveSmooth")
            if cs:
                obj_door_naga.modifiers.remove(cs)
            sub = obj_door_naga.modifiers.get("Subdivision")
            if sub:
                sub.levels = 2
                sub.render_levels = 2
            disp = obj_door_naga.modifiers.get("Displace")
            dn_disp_path = "/home/mullainathan/Games/IshaGodot/assets/textures/devi_parts/door_naga_disp.png"
            if disp and disp.texture and os.path.exists(dn_disp_path):
                img_disp_dn = bpy.data.images.load(dn_disp_path)
                img_disp_dn.pack()
                disp.texture.image = img_disp_dn
                disp.mid_level = 0.0
                disp.strength = 0.12

            mat_dn = obj_door_naga.data.materials[0] if obj_door_naga.data.materials else None
            if not mat_dn:
                mat_dn = bpy.data.materials.new("Mat_Door_Naga")
                obj_door_naga.data.materials.append(mat_dn)
            setup_pbr_material(
                mat_dn,
                albedo_path="/home/mullainathan/Games/IshaGodot/assets/textures/devi_parts/door_naga_albedo.png",
                norm_path="/home/mullainathan/Games/IshaGodot/assets/textures/devi_parts/door_naga_normal.png",
                rough_path="/home/mullainathan/Games/IshaGodot/assets/textures/devi_parts/door_naga_roughness.png",
                metal_path="/home/mullainathan/Games/IshaGodot/assets/textures/devi_parts/door_naga_metallic.png"
            )

            # Orientation: upright facing +Y (proud of wall and lintel, in authentic uncompressed aspect ratio)
            obj_door_naga.rotation_euler = Euler((math.radians(90), 0, math.radians(180)), "XYZ")
            s_dn = 0.115
            obj_door_naga.scale = Vector((3.01 * s_dn, 5.40 * s_dn, 1.0 * s_dn))
            obj_door_naga.location = Vector((0.0, 0.29, 4.52))
            obj_door_naga.select_set(False)
            print(f"[PARTS] Door Naga Panel successfully installed in true uncompressed aspect ratio at {obj_door_naga.location}")

    # --------------------------------------------------------------------------
    # 1. UPPER ENTRANCE FORECOURT FLOOR (Z = 0.40m, 20-METER GAP, OPEN SKY)
    # --------------------------------------------------------------------------
    bm_fg = bmesh.new()
    v1 = bm_fg.verts.new((-15.5,  0.5, 0.0))
    v2 = bm_fg.verts.new(( 15.5,  0.5, 0.0))
    v3 = bm_fg.verts.new((  7.6, -20.0, 0.0))
    v4 = bm_fg.verts.new(( -7.6, -20.0, 0.0))
    v5 = bm_fg.verts.new((-15.5,  0.5, base_z))
    v6 = bm_fg.verts.new(( 15.5,  0.5, base_z))
    v7 = bm_fg.verts.new((  7.6, -20.0, base_z))
    v8 = bm_fg.verts.new(( -7.6, -20.0, base_z))
    bm_fg.faces.new([v4, v3, v2, v1])
    bm_fg.faces.new([v5, v6, v7, v8])
    bm_fg.faces.new([v1, v2, v6, v5])
    bm_fg.faces.new([v2, v3, v7, v6])
    bm_fg.faces.new([v3, v4, v8, v7])
    bm_fg.faces.new([v4, v1, v5, v8])
    bmesh.ops.recalc_face_normals(bm_fg, faces=bm_fg.faces)
    me_fg = bpy.data.meshes.new("Mesh_Upper_Forecourt_Floor")
    bm_fg.to_mesh(me_fg)
    bm_fg.free()
    obj_fg = bpy.data.objects.new("Upper_Forecourt_Floor", me_fg)
    bpy.context.collection.objects.link(obj_fg)
    obj_fg.data.materials.append(materials['granite_floor'])
    apply_floor_planar_uv(obj_fg, uv_scale=1.0)

    # --------------------------------------------------------------------------
    # 2. AUTHENTIC CONSECRATED 3D TRISHUL (TRIDENT) MONUMENT FROM INTERNET
    # --------------------------------------------------------------------------
    # Per user: "ok remove the trishula and its base and get a similer looking trishul from the internet and add it"
    trishul_stl_path = "/home/mullainathan/Games/IshaGodot/assets/models/trishul_downloaded.stl"
    if os.path.exists(trishul_stl_path):
        bpy.ops.wm.stl_import(filepath=trishul_stl_path)
        obj_trishul = bpy.context.selected_objects[0]
        obj_trishul.name = "Sacred_3D_Trishul_Monument"

        # Optimize mesh cleanly for high-performance Forward+ Vulkan rendering
        mod_dec = obj_trishul.modifiers.new("Decimate", "DECIMATE")
        mod_dec.ratio = 0.40  # ~70k polygons: pristine curved silhouette and fast rendering
        bpy.context.view_layer.objects.active = obj_trishul
        bpy.ops.object.modifier_apply(modifier="Decimate")

        # Smooth shading
        for p in obj_trishul.data.polygons:
            p.use_smooth = True

        # Scale and position:
        # STL Trishul height is 7.508m. Scale factor 0.46 gives height ~3.45m.
        s_tri = 0.46
        obj_trishul.scale = Vector((s_tri, s_tri, s_tri))
        # Place upright standing in the center aisle at Y = -10.0m, Z = base_z (0.40m)
        obj_trishul.location = Vector((0.0, -10.00, base_z))
        obj_trishul.rotation_euler = Euler((0.0, 0.0, 0.0), "XYZ")

        # Assign authentic BlenderKit Old Copper PBR material
        obj_trishul.data.materials.clear()
        obj_trishul.data.materials.append(materials['copper'])
        apply_smart_uv(obj_trishul)
        obj_trishul.select_set(False)
        print(f"[TRISHUL] Authentic 3D Consecrated Trishul successfully installed at {obj_trishul.location}")

    # --------------------------------------------------------------------------
    # 3. THE TWO MONUMENTAL DIAMOND-CUT JALI PILLARS (AT Y = -20.00m)
    # --------------------------------------------------------------------------
    pillar_y = -20.00
    for px in [-3.00, 3.00]:
        side_name = "Right" if px < 0 else "Left"
        me_p = build_diamond_jali_pillar_mesh(side_name)
        obj_p = bpy.data.objects.new(f"Diamond_Jali_Pillar_{side_name}", me_p)
        obj_p.location = Vector((px, pillar_y, 0.0))
        bpy.context.collection.objects.link(obj_p)
        obj_p.data.materials.append(materials['pillar_stone'])
        apply_smart_uv(obj_p)

    # --------------------------------------------------------------------------
    # 4. MONUMENTAL NAGA ARCHITRAVE ON TOP OF BIG PILLARS (REPLACING NAGA PANEL)
    # --------------------------------------------------------------------------
    # Dark Carved Stone Architrave Beam (No rock backing block)
    bm_arch = bmesh.new()
    arch_w = 7.40
    arch_d = 0.85
    arch_z_bot = 4.25
    arch_h = 0.35
    bmesh.ops.create_cube(
        bm_arch, size=1.0,
        matrix=Matrix.Translation((0.0, pillar_y, arch_z_bot + arch_h / 2.0)) @
               Matrix.Scale(arch_w, 4, Vector((1, 0, 0))) @
               Matrix.Scale(arch_d, 4, Vector((0, 1, 0))) @
               Matrix.Scale(arch_h, 4, Vector((0, 0, 1)))
    )
    me_arch = bpy.data.meshes.new("Mesh_Monumental_Architrave_Beam")
    bm_arch.to_mesh(me_arch)
    bm_arch.free()
    obj_arch = bpy.data.objects.new("Monumental_Architrave_Beam", me_arch)
    bpy.context.collection.objects.link(obj_arch)
    obj_arch.data.materials.append(materials['pillar_stone'])
    apply_smart_uv(obj_arch)

    # Double-Sided Arched Naga Panel model from blend file (Visible & Patched)
    if os.path.exists(parts_blend_path):
        with bpy.data.libraries.load(parts_blend_path) as (data_from, data_to):
            if "on top inside the piller naga panel" in data_from.objects:
                data_to.objects = ["on top inside the piller naga panel"]

        if data_to.objects and data_to.objects[0]:
            raw_arch_naga = data_to.objects[0]
            bpy.context.collection.objects.link(raw_arch_naga)

            cs_an = raw_arch_naga.modifiers.get("CorrectiveSmooth")
            if cs_an:
                raw_arch_naga.modifiers.remove(cs_an)
            sub_an = raw_arch_naga.modifiers.get("Subdivision")
            if sub_an:
                sub_an.levels = 2
                sub_an.render_levels = 2
            disp_an = raw_arch_naga.modifiers.get("Displace")
            an_disp_path = "/home/mullainathan/Games/IshaGodot/assets/textures/devi_parts/arch_naga_disp.jpeg"
            if disp_an and disp_an.texture and os.path.exists(an_disp_path):
                img_disp_an = bpy.data.images.load(an_disp_path)
                img_disp_an.pack()
                disp_an.texture.image = img_disp_an

            # Evaluate mesh and duplicate faces with reversed normals for 100% two-sided solid visibility
            depsgraph = bpy.context.evaluated_depsgraph_get()
            eval_an = raw_arch_naga.evaluated_get(depsgraph)
            eval_mesh_an = eval_an.to_mesh()

            bm_an = bmesh.new()
            bm_an.from_mesh(eval_mesh_an)
            eval_an.to_mesh_clear()

            front_verts = list(bm_an.verts)
            front_faces = list(bm_an.faces)
            thick = 0.05
            for v in front_verts:
                v.co.z += thick / 2.0

            v_map = {}
            for v in front_verts:
                new_v = bm_an.verts.new((v.co.x, v.co.y, -v.co.z))
                v_map[v] = new_v

            bm_an.verts.ensure_lookup_table()
            uv_lay = bm_an.loops.layers.uv.active

            for f in front_faces:
                orig_loops = list(f.loops)
                new_face_verts = [v_map[l.vert] for l in reversed(orig_loops)]
                try:
                    new_f = bm_an.faces.new(new_face_verts)
                    if uv_lay:
                        for new_l, orig_l in zip(new_f.loops, reversed(orig_loops)):
                            new_l[uv_lay].uv = orig_l[uv_lay].uv
                except ValueError:
                    pass

            # Rotate: Rx(-90) * Rz(180) -> normal points directly +Y (towards entrance), up is +Z
            R_an = Matrix.Rotation(math.radians(-90), 3, "X") @ Matrix.Rotation(math.radians(180), 3, "Z")
            bmesh.ops.rotate(bm_an, cent=(0.0, 0.0, 0.0), matrix=R_an, verts=bm_an.verts)

            me_arch_naga = bpy.data.meshes.new("Mesh_Arch_Naga_DoubleSided")
            bm_an.to_mesh(me_arch_naga)
            bm_an.free()

            bpy.data.objects.remove(raw_arch_naga, do_unlink=True)

            obj_arch_naga = bpy.data.objects.new("Pillar_Naga_Architrave_Panel", me_arch_naga)
            bpy.context.collection.objects.link(obj_arch_naga)

            mat_an = bpy.data.materials.new("Mat_Arch_Naga")
            obj_arch_naga.data.materials.append(mat_an)
            setup_pbr_material(
                mat_an,
                albedo_path="/home/mullainathan/Games/IshaGodot/assets/textures/devi_parts/arch_naga_albedo.png",
                norm_path="/home/mullainathan/Games/IshaGodot/assets/textures/devi_parts/arch_naga_normal.png",
                rough_path="/home/mullainathan/Games/IshaGodot/assets/textures/devi_parts/arch_naga_roughness.png",
                metal_path="/home/mullainathan/Games/IshaGodot/assets/textures/devi_parts/arch_naga_metallic.png"
            )

            # Set to authentic 1.3400 aspect ratio (1080/806) spanning across the two big pillars
            # Visible serpent arch sits directly on top of architrave beam at Z = 4.60m
            obj_arch_naga.scale = Vector((3.41, 1.0, 2.545))
            obj_arch_naga.location = Vector((0.0, pillar_y + 0.02, 5.43))
            obj_arch_naga.select_set(False)
            print(f"[PARTS] Double-Sided Patched Pillar Naga Panel successfully installed at {obj_arch_naga.location}")

    # --------------------------------------------------------------------------
    # 5. EXACTLY 5 DESCENDING STEPS (FROM PILLAR THRESHOLD DOWN UNDER-DUG)
    # --------------------------------------------------------------------------
    bm_steps = bmesh.new()
    step_defs = [
        (-20.00, -20.45, 0.22),
        (-20.45, -20.90, 0.04),
        (-20.90, -21.35, -0.14),
        (-21.35, -21.80, -0.32),
        (-21.80, -22.25, -0.50)
    ]
    step_w = 7.00
    for ys, ye, z_top in step_defs:
        yd = abs(ye - ys)
        ymid = (ys + ye) / 2.0
        zh = z_top - (-0.75)
        zmid = z_top - zh / 2.0
        bmesh.ops.create_cube(
            bm_steps, size=1.0,
            matrix=Matrix.Translation((0.0, ymid, zmid)) @
                   Matrix.Scale(step_w, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(yd, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(zh, 4, Vector((0, 0, 1)))
        )
        # Nosing edge
        bmesh.ops.create_cube(
            bm_steps, size=1.0,
            matrix=Matrix.Translation((0.0, ye + 0.015, z_top - 0.015)) @
                   Matrix.Scale(step_w + 0.04, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(0.035, 4, Vector((0, 0, 1)))
        )

    # Flanking Side Terraces to fill all gaps from steps to triangular side walls
    # Spans from X = 3.5 to 7.6 on Right, and -7.6 to -3.5 on Left
    terrace_w = 4.10
    terrace_x_right = 3.5 + terrace_w / 2.0  # 5.55
    terrace_x_left = -terrace_x_right
    bmesh.ops.create_cube(
        bm_steps, size=1.0,
        matrix=Matrix.Translation((terrace_x_right, -21.125, -0.10)) @
               Matrix.Scale(terrace_w, 4, Vector((1, 0, 0))) @
               Matrix.Scale(2.25, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.70, 4, Vector((0, 0, 1)))
    )
    bmesh.ops.create_cube(
        bm_steps, size=1.0,
        matrix=Matrix.Translation((terrace_x_left, -21.125, -0.10)) @
               Matrix.Scale(terrace_w, 4, Vector((1, 0, 0))) @
               Matrix.Scale(2.25, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.70, 4, Vector((0, 0, 1)))
    )

    me_steps = bpy.data.meshes.new("Mesh_Sanctum_Descent_5Steps")
    bm_steps.to_mesh(me_steps)
    bm_steps.free()
    obj_steps = bpy.data.objects.new("Sanctum_Descent_5Steps", me_steps)
    bpy.context.collection.objects.link(obj_steps)
    obj_steps.data.materials.append(materials['granite_floor'])
    apply_box_uv(obj_steps, uv_scale=1.0)

    # --------------------------------------------------------------------------
    # 6. EXPANDED SUNKEN SUBTERRANEAN FLOOR (Z = -0.50m)
    # --------------------------------------------------------------------------
    bm_sunken = bmesh.new()
    # Front main sunken hall: Y from -22.25 to -30.00
    # X width at Y=-22.25 is [-6.8, 6.8], at Y=-30.00 is [-3.6, 3.6]
    # Height Z is -0.50 (thickness 0.25 down to -0.75)
    v1 = bm_sunken.verts.new((-6.8, -22.25, -0.75))
    v2 = bm_sunken.verts.new(( 6.8, -22.25, -0.75))
    v3 = bm_sunken.verts.new(( 3.6, -30.00, -0.75))
    v4 = bm_sunken.verts.new((-3.6, -30.00, -0.75))
    v5 = bm_sunken.verts.new((-6.8, -22.25, -0.50))
    v6 = bm_sunken.verts.new(( 6.8, -22.25, -0.50))
    v7 = bm_sunken.verts.new(( 3.6, -30.00, -0.50))
    v8 = bm_sunken.verts.new((-3.6, -30.00, -0.50))
    bm_sunken.faces.new([v4, v3, v2, v1])
    bm_sunken.faces.new([v5, v6, v7, v8])
    bm_sunken.faces.new([v1, v2, v6, v5])
    bm_sunken.faces.new([v2, v3, v7, v6])
    bm_sunken.faces.new([v3, v4, v8, v7])
    bm_sunken.faces.new([v4, v1, v5, v8])

    # Rear floor extending from Y=-30.00 to Y=-38.00 (rear apex)
    v9  = bm_sunken.verts.new((0.0, -38.00, -0.75))
    v10 = bm_sunken.verts.new((0.0, -38.00, -0.50))
    bm_sunken.faces.new([v9, v3, v4])
    bm_sunken.faces.new([v8, v7, v10])
    bm_sunken.faces.new([v3, v9, v10, v7])
    bm_sunken.faces.new([v9, v4, v8, v10])

    bmesh.ops.recalc_face_normals(bm_sunken, faces=bm_sunken.faces)
    me_sunken = bpy.data.meshes.new("Mesh_Vast_Sunken_Sanctum_Floor")
    bm_sunken.to_mesh(me_sunken)
    bm_sunken.free()
    obj_sunken = bpy.data.objects.new("Vast_Sunken_Sanctum_Floor", me_sunken)
    bpy.context.collection.objects.link(obj_sunken)
    obj_sunken.data.materials.append(materials['granite_floor'])
    apply_floor_planar_uv(obj_sunken, uv_scale=1.0)

    # --------------------------------------------------------------------------
    # 7. GRAND RAISED SANCTUM DAIS
    # --------------------------------------------------------------------------
    bm_dais = bmesh.new()
    dais_y = -30.50
    dais_w = 4.80
    dais_d = 1.00  # -30.00 to -31.00
    dais_h = 0.40  # Raised above sunken floor
    dais_top_z = sunken_z + dais_h  # -0.10m

    # Main Altar Platform
    bmesh.ops.create_cube(
        bm_dais, size=1.0,
        matrix=Matrix.Translation((0.0, dais_y, sunken_z + dais_h/2.0)) @
               Matrix.Scale(dais_w, 4, Vector((1, 0, 0))) @
               Matrix.Scale(dais_d, 4, Vector((0, 1, 0))) @
               Matrix.Scale(dais_h, 4, Vector((0, 0, 1)))
    )
    # Lotus rim
    bmesh.ops.create_cube(
        bm_dais, size=1.0,
        matrix=Matrix.Translation((0.0, dais_y, dais_top_z + 0.035)) @
               Matrix.Scale(dais_w + 0.16, 4, Vector((1, 0, 0))) @
               Matrix.Scale(dais_d + 0.16, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.07, 4, Vector((0, 0, 1)))
    )
    # Front ceremonial access step
    bmesh.ops.create_cube(
        bm_dais, size=1.0,
        matrix=Matrix.Translation((0.0, -30.00 + 0.15, sunken_z + dais_h * 0.25)) @
               Matrix.Scale(dais_w * 0.70, 4, Vector((1, 0, 0))) @
               Matrix.Scale(0.30, 4, Vector((0, 1, 0))) @
               Matrix.Scale(dais_h * 0.50, 4, Vector((0, 0, 1)))
    )
    # Rear Sanctum Niche Alcove Wall
    bmesh.ops.create_cube(
        bm_dais, size=1.0,
        matrix=Matrix.Translation((0.0, -31.10, sunken_z + 2.50)) @
               Matrix.Scale(5.40, 4, Vector((1, 0, 0))) @
               Matrix.Scale(0.40, 4, Vector((0, 1, 0))) @
               Matrix.Scale(5.00, 4, Vector((0, 0, 1)))
    )

    me_dais = bpy.data.meshes.new("Mesh_Sanctum_Altar_Peedam")
    bm_dais.to_mesh(me_dais)
    bm_dais.free()
    obj_dais = bpy.data.objects.new("Sanctum_Altar_Peedam", me_dais)
    bpy.context.collection.objects.link(obj_dais)
    obj_dais.data.materials.append(materials['granite_floor'])
    apply_box_uv(obj_dais, uv_scale=1.0)

    # --------------------------------------------------------------------------
    # 8. AUTHENTIC LINGA BHAIRAVI DEVI SANCTUM BAS-RELIEF PANEL
    # --------------------------------------------------------------------------
    devi_blend_path = "/home/mullainathan/Games/IshaGodot/assets/models/devi_panel.blend"
    if os.path.exists(devi_blend_path):
        with bpy.data.libraries.load(devi_blend_path) as (data_from, data_to):
            if "Plane" in data_from.objects:
                data_to.objects = ["Plane"]

        if data_to.objects and data_to.objects[0]:
            obj_devi = data_to.objects[0]
            bpy.context.collection.objects.link(obj_devi)
            obj_devi.name = "Devi_Sanctum_Panel"

            mat_devi = obj_devi.data.materials[0] if obj_devi.data.materials else None
            albedo_path = "/home/mullainathan/Games/IshaGodot/assets/textures/devi_panel/devi_panel_albedo.png"
            disp_path = "/home/mullainathan/Games/IshaGodot/assets/textures/devi_panel/devi_panel_displacement.png"
            norm_path = "/home/mullainathan/Games/IshaGodot/assets/textures/devi_panel/devi_panel_normal.png"
            rough_path = "/home/mullainathan/Games/IshaGodot/assets/textures/devi_panel/devi_panel_roughness.png"
            metal_path = "/home/mullainathan/Games/IshaGodot/assets/textures/devi_panel/devi_panel_metallic.png"

            if os.path.exists(disp_path):
                img_disp = bpy.data.images.load(disp_path)
                img_disp.pack()
                disp_mod = obj_devi.modifiers.get("Displace")
                if disp_mod and disp_mod.texture:
                    disp_mod.texture.image = img_disp

            sub_mod = obj_devi.modifiers.get("Subdivision")
            if sub_mod:
                sub_mod.levels = 2
                sub_mod.render_levels = 2

            cs_mod = obj_devi.modifiers.get("CorrectiveSmooth")
            if cs_mod:
                obj_devi.modifiers.remove(cs_mod)

            setup_pbr_material(mat_devi, albedo_path, norm_path, rough_path, metal_path)

            # Enforce 1:1 UV mapping directly from quad coordinates to guarantee pristine texture projection
            uv_layer = obj_devi.data.uv_layers.active
            if not uv_layer:
                uv_layer = obj_devi.data.uv_layers.new(name="UVMap")
            for loop in obj_devi.data.loops:
                vx = obj_devi.data.vertices[loop.vertex_index].co.x
                vy = obj_devi.data.vertices[loop.vertex_index].co.y
                uv_layer.data[loop.index].uv = ((vx + 1.0) * 0.5, (vy + 1.0) * 0.5)

            obj_devi.rotation_euler = Euler((math.radians(90), 0, math.radians(180)), "XYZ")
            scale_factor = 0.58
            obj_devi.scale = Vector((6.0 * scale_factor, 4.48 * scale_factor, 1.0 * scale_factor))
            obj_devi.location = Vector((0.0, -30.00, 1.30))
            obj_devi.select_set(False)
            print(f"[DEVI] Authentic Devi Sanctum Panel successfully installed at {obj_devi.location}")


def setup_architectural_lighting():
    base_z = 0.40
    ceiling_z = base_z + 5.20

    # 1. Twilight Ambient Sky Light
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_Twilight")
        bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    node_out = nodes.new('ShaderNodeOutputWorld')
    node_bg = nodes.new('ShaderNodeBackground')
    node_bg.inputs['Color'].default_value = (0.04, 0.08, 0.18, 1.0)
    node_bg.inputs['Strength'].default_value = 0.8
    links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])

    # 2. Warm Sunset Sun Fill (Golden hour evening light)
    sun_data = bpy.data.lights.new(name="Sun_Golden_Hour", type='SUN')
    sun_data.energy = 2.0
    sun_data.color = (1.0, 0.78, 0.52)
    sun_obj = bpy.data.objects.new(name="Sun_Golden_Hour", object_data=sun_data)
    sun_obj.location = Vector((18.0, 24.0, 14.0))
    point_at(sun_obj, Vector((0.0, 2.0, 2.5)))
    bpy.context.collection.objects.link(sun_obj)

    # Exterior corridor artificial lighting removed per user request: "remove the lighting which is in the coridoor"
    # The expanded outside corridor is now naturally lit by the open-sky ambient environment.

    # 3. VAST SUBTERRANEAN HALL ARCHITECTURAL ILLUMINATION
    # Trishul Monument Accent Spotlight (Center at Y = -10.0m)
    spot_trishul_data = bpy.data.lights.new(name="Spot_Trishul_Center", type='SPOT')
    spot_trishul_data.energy = 320.0
    spot_trishul_data.color = (1.0, 0.92, 0.72)
    spot_trishul_data.spot_size = math.radians(65.0)
    spot_trishul_data.spot_blend = 0.50
    spot_trishul_obj = bpy.data.objects.new(name="Spot_Trishul_Center", object_data=spot_trishul_data)
    spot_trishul_obj.location = Vector((0.0, -7.50, 6.20))
    point_at(spot_trishul_obj, Vector((0.0, -10.00, 2.77)))
    bpy.context.collection.objects.link(spot_trishul_obj)

    # Pillar Naga Architrave Accent Spotlight (At Y = -20.0m, Brightly illuminating Naga Panel)
    spot_arch_data = bpy.data.lights.new(name="Spot_Pillar_Arch", type='SPOT')
    spot_arch_data.energy = 450.0
    spot_arch_data.color = (1.0, 0.94, 0.78)
    spot_arch_data.spot_size = math.radians(75.0)
    spot_arch_data.spot_blend = 0.50
    spot_arch_obj = bpy.data.objects.new(name="Spot_Pillar_Arch", object_data=spot_arch_data)
    spot_arch_obj.location = Vector((0.0, -16.50, 6.20))
    point_at(spot_arch_obj, Vector((0.0, -20.00, 5.50)))
    bpy.context.collection.objects.link(spot_arch_obj)

    # Upper Forecourt Downlight (At Y = -5.0m)
    spot_h1 = bpy.data.lights.new(name="Spot_Hall_Front", type='SPOT')
    spot_h1.energy = 220.0
    spot_h1.color = (1.0, 0.88, 0.65)
    spot_h1.spot_size = math.radians(75.0)
    spot_h1.spot_blend = 0.50
    spot_h1_obj = bpy.data.objects.new(name="Spot_Hall_Front", object_data=spot_h1)
    spot_h1_obj.location = Vector((0.0, -5.0, 6.80))
    point_at(spot_h1_obj, Vector((0.0, -5.0, 0.40)))
    bpy.context.collection.objects.link(spot_h1_obj)

    # Mid Approach Hall Downlight (At Y = -15.0m)
    spot_h2 = bpy.data.lights.new(name="Spot_Hall_Mid", type='SPOT')
    spot_h2.energy = 220.0
    spot_h2.color = (1.0, 0.88, 0.65)
    spot_h2.spot_size = math.radians(75.0)
    spot_h2.spot_blend = 0.50
    spot_h2_obj = bpy.data.objects.new(name="Spot_Hall_Mid", object_data=spot_h2)
    spot_h2_obj.location = Vector((0.0, -15.0, 6.80))
    point_at(spot_h2_obj, Vector((0.0, -15.0, 0.40)))
    bpy.context.collection.objects.link(spot_h2_obj)

    # Far Sanctum Dais Altar Spotlight (Above Expanded Sunken Gap)
    spot_dais = bpy.data.lights.new(name="Spot_Sanctum_Dais", type='SPOT')
    spot_dais.energy = 260.0
    spot_dais.color = (1.0, 0.85, 0.55)
    spot_dais.spot_size = math.radians(65.0)
    spot_dais.spot_blend = 0.40
    spot_dais_obj = bpy.data.objects.new(name="Spot_Sanctum_Dais", object_data=spot_dais)
    spot_dais_obj.location = Vector((0.0, -27.50, 6.50))
    point_at(spot_dais_obj, Vector((0.0, -30.50, -0.10)))
    bpy.context.collection.objects.link(spot_dais_obj)

    # Focused Golden Spotlight directly illuminating the Devi Sanctum Panel
    spot_devi = bpy.data.lights.new(name="Spot_Devi_Sanctum", type='SPOT')
    spot_devi.energy = 650.0
    spot_devi.color = (1.0, 0.88, 0.65)
    spot_devi.spot_size = math.radians(50.0)
    spot_devi.spot_blend = 0.40
    spot_devi_obj = bpy.data.objects.new(name="Spot_Devi_Sanctum", object_data=spot_devi)
    spot_devi_obj.location = Vector((0.0, -27.50, 4.50))
    point_at(spot_devi_obj, Vector((0.0, -30.00, 1.30)))
    bpy.context.collection.objects.link(spot_devi_obj)


def setup_cameras():
    cameras = {}

    # Camera 1: Front Perspective (Expanded 14m Colonnade Corridor)
    cam1_data = bpy.data.cameras.new("Cam_01_Front_Perspective")
    cam1_data.lens = 28.0
    cam1_obj = bpy.data.objects.new("Cam_01_Front_Perspective", cam1_data)
    cam1_obj.location = Vector((18.0, 22.0, 3.2))
    point_at(cam1_obj, Vector((0.0, 7.0, 2.8)))
    bpy.context.collection.objects.link(cam1_obj)
    cameras['perspective'] = cam1_obj

    # Camera 2: Front Elevation of Expanded Corridor
    cam2_data = bpy.data.cameras.new("Cam_02_Front_Elevation_WaterReflect")
    cam2_data.lens = 24.0
    cam2_obj = bpy.data.objects.new("Cam_02_Front_Elevation_WaterReflect", cam2_data)
    cam2_obj.location = Vector((0.0, 24.0, 2.2))
    point_at(cam2_obj, Vector((0.0, 7.0, 2.8)))
    bpy.context.collection.objects.link(cam2_obj)
    cameras['water_reflect'] = cam2_obj

    # Camera 3: Colonnade Pillar Closeup & Black Ceiling Beams
    cam3_data = bpy.data.cameras.new("Cam_03_Pillar_Base_Closeup")
    cam3_data.lens = 38.0
    cam3_obj = bpy.data.objects.new("Cam_03_Pillar_Base_Closeup", cam3_data)
    cam3_obj.location = Vector((5.2, 16.0, 1.6))
    point_at(cam3_obj, Vector((2.4, 13.0, 2.2)))
    bpy.context.collection.objects.link(cam3_obj)
    cameras['closeup'] = cam3_obj

    # Camera 4: Triangular Sanctum Rear Elevation
    cam4_data = bpy.data.cameras.new("Cam_04_Sanctum_Triangular_Rear")
    cam4_data.lens = 28.0
    cam4_obj = bpy.data.objects.new("Cam_04_Sanctum_Triangular_Rear", cam4_data)
    cam4_obj.location = Vector((18.0, -32.0, 11.5))
    point_at(cam4_obj, Vector((0.0, -22.0, 4.5)))
    bpy.context.collection.objects.link(cam4_obj)
    cameras['rear_triangle'] = cam4_obj

    # Camera 5: Aerial Isometric View
    cam5_data = bpy.data.cameras.new("Cam_05_Aerial_Isometric")
    cam5_data.lens = 30.0
    cam5_obj = bpy.data.objects.new("Cam_05_Aerial_Isometric", cam5_data)
    cam5_obj.location = Vector((28.0, 20.0, 24.0))
    point_at(cam5_obj, Vector((0.0, -14.0, 3.5)))
    bpy.context.collection.objects.link(cam5_obj)
    cameras['aerial'] = cam5_obj

    # Camera 6: Interior Sanctum Eye Level (Inside Expanded Sunken Gap)
    cam6_data = bpy.data.cameras.new("Cam_06_Interior_Sanctum_Eye")
    cam6_data.lens = 28.0
    cam6_obj = bpy.data.objects.new("Cam_06_Interior_Sanctum_Eye", cam6_data)
    cam6_obj.location = Vector((0.0, -27.00, 1.25))
    point_at(cam6_obj, Vector((0.0, -30.00, 1.30)))
    bpy.context.collection.objects.link(cam6_obj)
    cameras['interior_eye'] = cam6_obj

    # Camera 7: Interior Devi Shrine Closeup (Framing Trinetra, Nose Ring, Bangles)
    cam7_data = bpy.data.cameras.new("Cam_07_Interior_Devi_Closeup")
    cam7_data.lens = 45.0
    cam7_obj = bpy.data.objects.new("Cam_07_Interior_Devi_Closeup", cam7_data)
    cam7_obj.location = Vector((0.0, -28.20, 1.35))
    point_at(cam7_obj, Vector((0.0, -30.00, 1.30)))
    bpy.context.collection.objects.link(cam7_obj)
    cameras['devi_closeup'] = cam7_obj

    # Camera 8: Central Double-Sided Trishul Monument Closeup
    cam8_data = bpy.data.cameras.new("Cam_08_Interior_Diya_Wall_34")
    cam8_data.lens = 32.0
    cam8_obj = bpy.data.objects.new("Cam_08_Interior_Diya_Wall_34", cam8_data)
    cam8_obj.location = Vector((-2.20, -7.50, 2.20))
    point_at(cam8_obj, Vector((0.0, -10.00, 2.70)))
    bpy.context.collection.objects.link(cam8_obj)
    cameras['interior_diya_34'] = cam8_obj

    # Camera 9: Porch Looking Through Open Doors past Trishul into Sanctum
    cam9_data = bpy.data.cameras.new("Cam_09_Porch_Looking_Inside")
    cam9_data.lens = 30.0
    cam9_obj = bpy.data.objects.new("Cam_09_Porch_Looking_Inside", cam9_data)
    cam9_obj.location = Vector((0.0, 3.8, 1.65))
    point_at(cam9_obj, Vector((0.0, -10.00, 2.70)))
    bpy.context.collection.objects.link(cam9_obj)
    cameras['porch_looking_inside'] = cam9_obj

    # Camera 10: Grand Interior Replica framing Open Sky, Trishul, Big Pillars, Patched Naga Panel, Raised Roof, 5 Steps, and Devi
    cam10_data = bpy.data.cameras.new("Cam_10_Devi_Interior_Replica")
    cam10_data.lens = 16.0
    cam10_obj = bpy.data.objects.new("Cam_10_Devi_Interior_Replica", cam10_data)
    cam10_obj.location = Vector((0.0, -1.20, 1.95))
    point_at(cam10_obj, Vector((0.0, -24.00, 2.75)))
    bpy.context.collection.objects.link(cam10_obj)
    cameras['interior_replica'] = cam10_obj

    # Camera 11: Looking straight up from forecourt floor at 1m roof beams, suspended metal chains and open sky
    cam11_data = bpy.data.cameras.new("Cam_11_Forecourt_Sky_Chains_Up")
    cam11_data.lens = 18.0
    cam11_obj = bpy.data.objects.new("Cam_11_Forecourt_Sky_Chains_Up", cam11_data)
    cam11_obj.location = Vector((0.0, -9.50, 1.45))
    point_at(cam11_obj, Vector((0.0, -9.48, 6.70)))
    bpy.context.collection.objects.link(cam11_obj)
    cameras['sky_chains_up'] = cam11_obj

    return cameras


# ==============================================================================
# 7. RENDER SHOWCASE & EXPORT
# ==============================================================================
def render_showcase(cameras):
    scene = bpy.context.scene
    try:
        scene.render.engine = 'BLENDER_EEVEE'
    except Exception:
        scene.render.engine = 'CYCLES'

    try:
        scene.eevee.use_raytracing = True
        scene.eevee.use_fast_gi = True
        scene.eevee.indirect_light_intensity = 1.2
        scene.eevee.direct_light_intensity = 1.0
        scene.eevee.taa_render_samples = 64
        scene.eevee.shadow_pool_size = 4096
    except Exception:
        pass

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False

    render_targets = [
        ('cam_01_front_perspective.png', cameras['perspective']),
        ('cam_02_front_elevation_reflect.png', cameras['water_reflect']),
        ('cam_03_pillar_diya_closeup.png', cameras['closeup']),
        ('cam_04_sanctum_triangular_rear.png', cameras['rear_triangle']),
        ('cam_05_aerial_isometric.png', cameras['aerial']),
        ('cam_06_interior_sanctum_eye.png', cameras['interior_eye']),
        ('cam_07_interior_devi_closeup.png', cameras['devi_closeup']),
        ('cam_08_interior_diya_wall_34.png', cameras['interior_diya_34']),
        ('cam_09_porch_looking_inside.png', cameras['porch_looking_inside']),
        ('cam_10_devi_interior_replica.png', cameras['interior_replica']),
        ('cam_11_forecourt_sky_chains_up.png', cameras['sky_chains_up']),
    ]

    for filename, cam_obj in render_targets:
        scene.camera = cam_obj
        filepath_cap = os.path.join(CAPTURES_DIR, filename)
        filepath_art = os.path.join(ARTIFACTS_DIR, filename)
        scene.render.filepath = filepath_cap
        bpy.ops.render.render(write_still=True)
        if os.path.exists(filepath_cap):
            shutil.copy2(filepath_cap, filepath_art)
            print(f"[RENDER] Saved showcase capture: {filepath_cap}")


def export_assets():
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND_PATH)
    print(f"[BLEND] Saved scene to {OUTPUT_BLEND_PATH}")

    bpy.ops.export_scene.gltf(
        filepath=OUTPUT_MODEL_PATH,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_materials='EXPORT',
        export_lights=False,
        export_cameras=True
    )
    print(f"[GLB] Exported 3D asset to {OUTPUT_MODEL_PATH}")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main():
    print("=" * 75)
    print("BUILDING COMPLETE LINGA BHAIRAVI TEMPLE (EXPANDED STEPPED INTERIOR)")
    print("=" * 75)

    clean_scene()
    materials = create_materials()

    # Exterior
    build_plinth_and_courtyard(materials)
    build_front_colonnade(materials)
    build_diya_wall_and_portal(materials)
    build_cantilever_canopy(materials)
    build_triangular_sanctum_envelope(materials)
    build_screens_and_amenities(materials)

    # Interior Sanctum & Mandapam (Expansive Subterranean Hall)
    build_interior_architecture(materials)

    # Lighting & Cameras
    setup_architectural_lighting()
    cameras = setup_cameras()

    print("[BUILD] Construction complete. Rendering multi-camera showcase...")
    render_showcase(cameras)

    print("[EXPORT] Exporting blend and GLB assets...")
    export_assets()

    print("[SUCCESS] Complete Linga Bhairavi Temple created successfully!")


if __name__ == "__main__":
    main()
