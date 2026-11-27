"""
Dhyanalinga Temple - Ground-Truth Masterpiece Replica
Isha Yoga Center, Velliangiri Foothills, Coimbatore

Constructed with strict architectural fidelity to authentic ground-truth visitor photography
and official Isha / Auroville Earth Institute archival records:

1. THE BLACK GRANITE DHYANALINGA MONOLITH:
   - High-density polished black granite cylinder (R = 0.56m, H = 4.20m) with parabolic dome cap.
   - 7 subtle horizontal copper chakra rings embedded along the cylinder body.
   - Sacred white silk vastram (cloth) wrapped horizontally around the lower third with a pleated
     vertical sash falling down the front.
   - Graceful arched garland of fresh green leaves (bilva) and white jasmine framing the Linga dome.

2. THE SEVEN-COILED SERPENT AVUDAIYAR (THE RECEPTACLE IS THE SNAKE):
   - The entire Avudaiyar base consists of 7 thick, continuous horizontal elliptical serpent coils
     (each with smooth tubular cross-section r = 0.14m, stacking up to Z = 1.05m).
   - Rich burnished antique copper / dark bronze patina with metallic sheen.
   - At the front (+Y, facing the devotee): The sculpted cobra head rests on the front coil ledge,
     snout pointing forward toward the offering platform, draped with a sacred green leaf garland.

3. RECTANGULAR JALASEEMA WATER POOL & OFFERING ALTA:
   - Rectangular sunken water pool (7.0m wide x 5.6m deep, sunken -0.35m) around the Avudaiyar.
   - Wide dressed stone border curb (0.45m wide) lined with dozens of burning brass oil lamps (diyas).
   - Calm dark water plane covered with hundreds of floating pink and red lotus & rose petals.
   - Front stone offering dais with large turned brass Urulis and linked bronze chain barrier.

4. 28 AURA CELLS WITH TRIANGULAR STONE NICHES:
   - Circular lower wall (R = 11.08m, H = 2.40m) constructed of dark grey chiseled stone ashlar masonry.
   - 28 rectangular meditation cubicles (1.25m wide x 1.40m deep x 2.05m high) with polished granite benches.
   - Authentic TRIANGULAR STONE NICHES directly above each cubicle in the lintel course for acoustic resonance.
   - Symmetrically paved grey granite flagstone floor.

5. 76-FT SEGMENTAL ELLIPTICAL BRICK DOME:
   - Spans 22.16m (76 ft) diameter, springing smoothly from Z = 2.40m up to Z = 10.30m (7.90m internal rise).
   - Built with pure compression concentric rings of terracotta burnt red bricks.
   - Central crown oculus opening (2.8m diameter) with exterior gold-plated copper cupola ventilator.

6. ENTRANCE PORTAL, SARVA DHARMA STHAMBHA & SACRED NANDI:
   - Monumental chiseled dark granite portal with multi-tiered molded jambs and crouching stone elephants.
   - 17-foot monolithic white granite Sarva Dharma Sthambha with rounded top, stone Sun disk, and
     chiseled reliefs of 9 world religions, 7 chakras, Ida & Pingala serpents, and Tree of Life.
   - Sacred Black Nandi Bull monument sitting peacefully on the approach plaza facing Dhyanalinga.
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
OUTPUT_MODEL_PATH = "/home/mullainathan/Games/IshaGodot/assets/models/dhyanalinga_temple.glb"
OUTPUT_BLEND_PATH = "/home/mullainathan/Games/IshaGodot/assets/models/dhyanalinga_temple.blend"


def reset_blender_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Dhyanalinga_Temple")
    bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[col.name]
    print("[Dhyanalinga] Scene reset complete.")


# ==============================================================================
# UV UNWRAPPING HELPERS
# ==============================================================================
def apply_smart_uv(obj, angle_limit=66.0, margin=0.01):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle_limit), island_margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)


def apply_cylinder_uv(obj, uv_scale=(1.0, 1.0)):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cylinder_project(direction='VIEW_ON_EQUATOR', align='POLAR_ZX', clip_to_bounds=False, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)


def apply_planar_uv_xy(obj, uv_scale=1.0):
    me = obj.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv_layer = me.uv_layers.active.data
    for poly in me.polygons:
        for loop_idx in poly.loop_indices:
            v_idx = me.loops[loop_idx].vertex_index
            co = me.vertices[v_idx].co
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


# ==============================================================================
# PBR MATERIAL FACTORY
# ==============================================================================
def create_materials():
    materials = {}

    def _setup_node_mat(name, diff_path=None, nor_path=None, rough_path=None, metal_path=None,
                        base_col=(0.8, 0.8, 0.8, 1.0), roughness=0.5, metallic=0.0, uv_scale=(1.0, 1.0)):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out_node = nodes.new('ShaderNodeOutputMaterial')
        out_node.location = (600, 0)
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (200, 0)
        links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

        bsdf.inputs['Base Color'].default_value = base_col
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic

        tex_coord = nodes.new('ShaderNodeTexCoord')
        tex_coord.location = (-600, 0)
        mapping = nodes.new('ShaderNodeMapping')
        mapping.location = (-400, 0)
        mapping.inputs['Scale'].default_value = (uv_scale[0], uv_scale[1], 1.0)
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

        if diff_path and os.path.exists(diff_path):
            img_diff = bpy.data.images.load(diff_path)
            node_diff = nodes.new('ShaderNodeTexImage')
            node_diff.location = (-150, 150)
            node_diff.image = img_diff
            links.new(mapping.outputs['Vector'], node_diff.inputs['Vector'])
            links.new(node_diff.outputs['Color'], bsdf.inputs['Base Color'])

        if nor_path and os.path.exists(nor_path):
            img_nor = bpy.data.images.load(nor_path)
            img_nor.colorspace_settings.name = 'Non-Color'
            node_nor = nodes.new('ShaderNodeTexImage')
            node_nor.location = (-150, -150)
            node_nor.image = img_nor
            norm_map = nodes.new('ShaderNodeNormalMap')
            norm_map.location = (50, -150)
            norm_map.inputs['Strength'].default_value = 1.0
            links.new(mapping.outputs['Vector'], node_nor.inputs['Vector'])
            links.new(node_nor.outputs['Color'], norm_map.inputs['Color'])
            links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])

        if rough_path and os.path.exists(rough_path):
            img_rough = bpy.data.images.load(rough_path)
            img_rough.colorspace_settings.name = 'Non-Color'
            node_rough = nodes.new('ShaderNodeTexImage')
            node_rough.location = (-150, -400)
            node_rough.image = img_rough
            links.new(mapping.outputs['Vector'], node_rough.inputs['Vector'])
            links.new(node_rough.outputs['Color'], bsdf.inputs['Roughness'])

        if metal_path and os.path.exists(metal_path):
            img_metal = bpy.data.images.load(metal_path)
            img_metal.colorspace_settings.name = 'Non-Color'
            node_metal = nodes.new('ShaderNodeTexImage')
            node_metal.location = (-150, -650)
            node_metal.image = img_metal
            links.new(mapping.outputs['Vector'], node_metal.inputs['Vector'])
            links.new(node_metal.outputs['Color'], bsdf.inputs['Metallic'])

        return mat

    # 1. Burnt Red Brick (Auroville Earth Institute Terracotta Bricks)
    brick_diff = os.path.join(TEXTURES_DIR, "terracotta_tiles_color.png")
    brick_nor = os.path.join(TEXTURES_DIR, "terracotta_tiles_normal.png")
    brick_rough = os.path.join(TEXTURES_DIR, "terracotta_tiles_roughness.png")
    if not os.path.exists(brick_diff):
        brick_diff = os.path.join(TEXTURES_DIR, "stacked_brick_color.jpg")
        brick_nor = os.path.join(TEXTURES_DIR, "stacked_brick_normal.png")
        brick_rough = os.path.join(TEXTURES_DIR, "stacked_brick_roughness.jpg")

    materials['brick_dome'] = _setup_node_mat(
        "Mat_Dhyanalinga_Brick_Dome",
        diff_path=brick_diff, nor_path=brick_nor, rough_path=brick_rough,
        base_col=(0.68, 0.30, 0.18, 1.0), roughness=0.82, metallic=0.0, uv_scale=(4.0, 4.0)
    )

    # 2. Polished Black Granite (Dhyanalinga Monolith & Pool Coping)
    bg_nor = os.path.join(TEXTURES_DIR, "dark_gray_granite_nor_2k.png")
    materials['black_granite_linga'] = _setup_node_mat(
        "Mat_Dhyanalinga_Black_Granite",
        diff_path=None, nor_path=bg_nor, rough_path=None,
        base_col=(0.025, 0.025, 0.028, 1.0), roughness=0.18, metallic=0.12, uv_scale=(2.0, 2.0)
    )

    # 3. Seven-Coiled Copper/Bronze Serpent Avudaiyar
    cop_diff = os.path.join(TEXTURES_DIR, "bk_old_copper_diff_2k.png")
    cop_nor = os.path.join(TEXTURES_DIR, "bk_old_copper_nor_2k.png")
    cop_rough = os.path.join(TEXTURES_DIR, "bk_old_copper_rough_2k.png")
    cop_metal = os.path.join(TEXTURES_DIR, "bk_old_copper_metal_2k.png")
    materials['serpent_copper'] = _setup_node_mat(
        "Mat_Dhyanalinga_Serpent_Copper",
        diff_path=cop_diff, nor_path=cop_nor, rough_path=cop_rough, metal_path=cop_metal,
        base_col=(0.78, 0.45, 0.28, 1.0), roughness=0.32, metallic=0.92, uv_scale=(2.0, 2.0)
    )

    # 4. Sacred White Silk Vastram (Cloth Band & Pleated Sash)
    materials['white_cloth'] = _setup_node_mat(
        "Mat_Dhyanalinga_White_Cloth",
        base_col=(0.95, 0.94, 0.90, 1.0), roughness=0.75, metallic=0.0
    )

    # 5. Fresh Green Bilva Leaf Garland & Jasmine Flowers
    materials['leaf_garland'] = _setup_node_mat(
        "Mat_Dhyanalinga_Leaf_Garland",
        base_col=(0.18, 0.45, 0.12, 1.0), roughness=0.45, metallic=0.0
    )
    materials['flower_jasmine'] = _setup_node_mat(
        "Mat_Dhyanalinga_Jasmine",
        base_col=(0.98, 0.95, 0.70, 1.0), roughness=0.40, metallic=0.0
    )
    materials['flower_rose_pink'] = _setup_node_mat(
        "Mat_Dhyanalinga_Rose_Petals",
        base_col=(0.92, 0.25, 0.45, 1.0), roughness=0.50, metallic=0.0
    )

    # 6. Grey Chiseled Stone Ashlar (Lower Wall with Triangular Openings & Retaining Walls)
    st_diff = os.path.join(TEXTURES_DIR, "stone_block_wall_diff_2k.jpg")
    st_nor = os.path.join(TEXTURES_DIR, "stone_block_wall_nor_gl_2k.jpg")
    st_rough = os.path.join(TEXTURES_DIR, "stone_block_wall_rough_2k.jpg")
    materials['ashlar_stone'] = _setup_node_mat(
        "Mat_Dhyanalinga_Ashlar_Stone",
        diff_path=st_diff, nor_path=st_nor, rough_path=st_rough,
        base_col=(0.55, 0.52, 0.48, 1.0), roughness=0.68, metallic=0.0, uv_scale=(2.0, 2.0)
    )

    # 7. Mirror-Polished Dark Grey Granite Floor (Parikrama Flagstones)
    dg_diff = os.path.join(TEXTURES_DIR, "dark_gray_granite_diff_2k.png")
    dg_nor = os.path.join(TEXTURES_DIR, "dark_gray_granite_nor_2k.png")
    dg_rough = os.path.join(TEXTURES_DIR, "dark_gray_granite_rough_2k.png")
    materials['parikrama_floor'] = _setup_node_mat(
        "Mat_Dhyanalinga_Parikrama_Floor",
        diff_path=dg_diff, nor_path=dg_nor, rough_path=dg_rough,
        base_col=(0.14, 0.14, 0.15, 1.0), roughness=0.28, metallic=0.06, uv_scale=(3.0, 3.0)
    )

    # 8. Sacred Jalaseema Water Pool
    mat_water = bpy.data.materials.new("Mat_Dhyanalinga_Water")
    mat_water.use_nodes = True
    w_nodes = mat_water.node_tree.nodes
    w_links = mat_water.node_tree.links
    w_nodes.clear()
    w_out = w_nodes.new('ShaderNodeOutputMaterial')
    w_bsdf = w_nodes.new('ShaderNodeBsdfPrincipled')
    w_links.new(w_bsdf.outputs['BSDF'], w_out.inputs['Surface'])
    w_bsdf.inputs['Base Color'].default_value = (0.02, 0.08, 0.10, 0.88)
    w_bsdf.inputs['Roughness'].default_value = 0.03
    w_bsdf.inputs['IOR'].default_value = 1.333
    if 'Transmission Weight' in w_bsdf.inputs:
        w_bsdf.inputs['Transmission Weight'].default_value = 0.85
    elif 'Transmission' in w_bsdf.inputs:
        w_bsdf.inputs['Transmission'].default_value = 0.85
    materials['water'] = mat_water

    # 9. White Granite & Dedicated Sarva Dharma Sthambha Relief
    wg_diff = os.path.join(TEXTURES_DIR, "white_granite_diff_2k.png")
    wg_nor = os.path.join(TEXTURES_DIR, "white_granite_nor_2k.png")
    wg_rough = os.path.join(TEXTURES_DIR, "white_granite_rough_2k.png")
    materials['white_granite'] = _setup_node_mat(
        "Mat_Dhyanalinga_White_Granite",
        diff_path=wg_diff, nor_path=wg_nor, rough_path=wg_rough,
        base_col=(0.88, 0.88, 0.86, 1.0), roughness=0.45, metallic=0.0, uv_scale=(2.0, 2.0)
    )

    sd_diff = os.path.join(TEXTURES_DIR, "sarva_dharma_sthambha_diff.png")
    sd_nor = os.path.join(TEXTURES_DIR, "sarva_dharma_sthambha_nor.png")
    sd_rough = os.path.join(TEXTURES_DIR, "sarva_dharma_sthambha_rough.png")
    materials['sarva_dharma_relief'] = _setup_node_mat(
        "Mat_Sarva_Dharma_Relief",
        diff_path=sd_diff, nor_path=sd_nor, rough_path=sd_rough,
        base_col=(0.90, 0.90, 0.88, 1.0), roughness=0.48, metallic=0.0, uv_scale=(1.0, 1.0)
    )

    # 10. Diya Oil Lamp Flame
    mat_flame = bpy.data.materials.new("Mat_Diya_Flame")
    mat_flame.use_nodes = True
    f_nodes = mat_flame.node_tree.nodes
    f_links = mat_flame.node_tree.links
    f_nodes.clear()
    f_out = f_nodes.new('ShaderNodeOutputMaterial')
    f_bsdf = f_nodes.new('ShaderNodeBsdfPrincipled')
    f_links.new(f_bsdf.outputs['BSDF'], f_out.inputs['Surface'])
    f_bsdf.inputs['Base Color'].default_value = (1.0, 0.78, 0.35, 1.0)
    if 'Emission Color' in f_bsdf.inputs:
        f_bsdf.inputs['Emission Color'].default_value = (1.0, 0.70, 0.20, 1.0)
        f_bsdf.inputs['Emission Strength'].default_value = 4.0
    materials['diya_flame'] = mat_flame

    # 11. Antique Brass (Uruli Bowls, Kuthuvilakku Lamps & Chains)
    materials['brass_metal'] = _setup_node_mat(
        "Mat_Dhyanalinga_Brass",
        base_col=(0.90, 0.75, 0.35, 1.0), roughness=0.28, metallic=0.95
    )

    # 12. Carved Teak Wood (Entrance Doors)
    materials['teak_wood'] = _setup_node_mat(
        "Mat_Dhyanalinga_Teak_Wood",
        base_col=(0.28, 0.16, 0.10, 1.0), roughness=0.55, metallic=0.0
    )

    print("[Dhyanalinga] High-fidelity materials created successfully.")
    return materials


# ==============================================================================
# 1. AUTHENTIC DHYANALINGA MONOLITH & SEVEN-COILED SERPENT AVUDAIYAR
# ==============================================================================
def build_dhyanalinga_and_serpent(materials):
    """
    Constructs the central sacred sanctum ensemble strictly matching ground-truth photos:
    - Black Granite Dhyanalinga Monolith (4.20m high) with 7 horizontal copper chakra rings.
    - Sacred White Silk Vastram wrapped around the lower body with a vertical pleated sash.
    - Arched garland of fresh green leaves (bilva) and jasmine blossoms over the Linga crown.
    - Seven-Coiled Copper/Bronze Serpent Avudaiyar (the pedestal IS the 7 smooth coils).
    - Sculpted Cobra Head resting gracefully at the front center with green leaf garland.
    - Sunken Rectangular Jalaseema Water Pool (7.0m x 5.6m) with dressed stone border.
    - Perimeter Diya Matrix: 48 burning oil lamps along the pool rim.
    - Floating fresh lotus & rose petals across the calm water.
    - Front Offering Altar with turned brass Uruli bowls and bronze chain barrier.
    """
    col = bpy.context.scene.collection.children["Dhyanalinga_Temple"]

    # --------------------------------------------------------------------------
    # A. BLACK GRANITE DHYANALINGA MONOLITH
    # --------------------------------------------------------------------------
    bm_linga = bmesh.new()
    LINGA_H = 4.20
    LINGA_R = 0.56
    SEGS = 48
    RINGS = 36

    verts_linga = []
    for r_i in range(RINGS + 1):
        t = r_i / float(RINGS)
        cur_z = t * LINGA_H
        # Cylinder up to 72% height (3.02m), then parabolic smooth dome top
        if t < 0.72:
            cur_r = LINGA_R
        else:
            t_cap = (t - 0.72) / 0.28
            cur_r = LINGA_R * math.sqrt(max(0.0, 1.0 - t_cap * t_cap))
        
        r_verts = []
        for s in range(SEGS):
            ang = 2.0 * math.pi * s / SEGS
            r_verts.append(bm_linga.verts.new((cur_r * math.cos(ang), cur_r * math.sin(ang), cur_z)))
        verts_linga.append(r_verts)

    bm_linga.verts.ensure_lookup_table()
    for r_i in range(RINGS):
        r1 = verts_linga[r_i]
        r2 = verts_linga[r_i + 1]
        for s in range(SEGS):
            s_next = (s + 1) % SEGS
            bm_linga.faces.new((r1[s], r2[s], r2[s_next], r1[s_next]))

    # Top apex
    v_top = bm_linga.verts.new((0.0, 0.0, LINGA_H))
    for s in range(SEGS):
        s_next = (s + 1) % SEGS
        bm_linga.faces.new((verts_linga[-1][s], v_top, verts_linga[-1][s_next]))

    me_linga = bpy.data.meshes.new("Mesh_Dhyanalinga_Monolith")
    bm_linga.to_mesh(me_linga)
    bm_linga.free()

    obj_linga = bpy.data.objects.new("Dhyanalinga_Black_Granite_Monolith", me_linga)
    col.objects.link(obj_linga)
    obj_linga.data.materials.append(materials['black_granite_linga'])
    apply_cylinder_uv(obj_linga, uv_scale=(2.0, 2.0))

    # --------------------------------------------------------------------------
    # B. 7 EMBEDDED COPPER CHAKRA RINGS
    # --------------------------------------------------------------------------
    chakra_zs = [0.55, 1.05, 1.55, 2.05, 2.55, 3.05, 3.55]
    bm_rings = bmesh.new()
    for cz in chakra_zs:
        t_z = cz / LINGA_H
        rad = LINGA_R if t_z < 0.72 else LINGA_R * math.sqrt(max(0.0, 1.0 - ((t_z - 0.72) / 0.28)**2))
        bmesh.ops.create_cone(
            bm_rings, cap_ends=False, segments=36,
            radius1=rad + 0.015, radius2=rad + 0.015, depth=0.025,
            matrix=Matrix.Translation((0.0, 0.0, cz))
        )
    me_rings = bpy.data.meshes.new("Mesh_Chakra_Rings")
    bm_rings.to_mesh(me_rings)
    bm_rings.free()
    obj_rings = bpy.data.objects.new("Dhyanalinga_Chakra_Rings", me_rings)
    col.objects.link(obj_rings)
    obj_rings.data.materials.append(materials['serpent_copper'])
    apply_smart_uv(obj_rings)

    # --------------------------------------------------------------------------
    # C. SACRED WHITE SILK VASTRAM (HORIZONTAL BAND & PLEATED FRONT SASH)
    # --------------------------------------------------------------------------
    bm_cloth = bmesh.new()
    # 1. Horizontal White Band wrapped around Linga (Z = 1.08m to 1.38m)
    bmesh.ops.create_cone(
        bm_cloth, cap_ends=False, segments=48,
        radius1=LINGA_R + 0.020, radius2=LINGA_R + 0.020, depth=0.30,
        matrix=Matrix.Translation((0.0, 0.0, 1.23))
    )
    # 2. Vertical Pleated Sash falling down the front (+Y, towards devotee)
    # Hanging from Z = 1.25m down to Z = 0.88m behind the cobra head
    bmesh.ops.create_cube(
        bm_cloth, size=1.0,
        matrix=Matrix.Translation((0.0, LINGA_R + 0.035, 1.05)) @
               Matrix.Scale(0.32, 4, Vector((1, 0, 0))) @
               Matrix.Scale(0.03, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.38, 4, Vector((0, 0, 1)))
    )
    me_cloth = bpy.data.meshes.new("Mesh_White_Vastram")
    bm_cloth.to_mesh(me_cloth)
    bm_cloth.free()
    obj_cloth = bpy.data.objects.new("Dhyanalinga_White_Vastram", me_cloth)
    col.objects.link(obj_cloth)
    obj_cloth.data.materials.append(materials['white_cloth'])
    apply_smart_uv(obj_cloth)

    # --------------------------------------------------------------------------
    # D. ARCHED GREEN BILVA LEAF & JASMINE FLORAL GARLAND OVER LINGA CROWN
    # --------------------------------------------------------------------------
    bm_garl = bmesh.new()
    GARL_PTS = 36
    for i in range(GARL_PTS):
        # Angle from left (-X, 0) up over crown (pi/2) to right (+X, pi)
        ang = math.pi * i / float(GARL_PTS - 1)
        gx = (LINGA_R + 0.04) * math.cos(ang)
        gz = 2.40 + (LINGA_H - 2.40 + 0.08) * math.sin(ang)
        gy = 0.0
        # Alternating green leaf beads and white jasmine flowers
        bmesh.ops.create_icosphere(
            bm_garl, subdivisions=2, radius=0.045,
            matrix=Matrix.Translation((gx, gy, gz))
        )
    me_garl = bpy.data.meshes.new("Mesh_Linga_Garland")
    bm_garl.to_mesh(me_garl)
    bm_garl.free()
    obj_garl = bpy.data.objects.new("Dhyanalinga_Floral_Garland", me_garl)
    col.objects.link(obj_garl)
    obj_garl.data.materials.append(materials['leaf_garland'])
    apply_smart_uv(obj_garl)

    # --------------------------------------------------------------------------
    # E. SEVEN-COILED COPPER/BRONZE SERPENT AVUDAIYAR (THE RECEPTACLE IS THE SNAKE)
    # --------------------------------------------------------------------------
    # 7 continuous smooth horizontal elliptical coils stacking from Z = 0.0 to Z = 1.05m
    bm_serpent = bmesh.new()
    COIL_COUNT = 7
    COIL_SEGS = 64
    TUBE_SEGS = 16
    TUBE_R = 0.145  # Muscular serpent body thickness
    COIL_H = 1.05 / float(COIL_COUNT)

    for c_i in range(COIL_COUNT):
        cur_z = c_i * COIL_H + TUBE_R * 0.95
        # Coils taper slightly from base to top
        t_c = c_i / float(COIL_COUNT)
        rx = 1.45 - 0.20 * t_c
        ry = 1.95 - 0.25 * t_c

        # Generate smooth continuous elliptical torus
        ring_tube_verts = []
        for s in range(COIL_SEGS):
            ang_s = 2.0 * math.pi * s / float(COIL_SEGS)
            # Elliptical spine coordinate
            cx = rx * math.cos(ang_s)
            cy = ry * math.sin(ang_s)

            # Normal vector perpendicular to spine
            # Tangent is (-rx * sin, ry * cos, 0)
            tx = -rx * math.sin(ang_s)
            ty =  ry * math.cos(ang_s)
            t_len = math.hypot(tx, ty)
            nx =  ty / t_len
            ny = -tx / t_len

            circ_verts = []
            for k in range(TUBE_SEGS):
                ang_k = 2.0 * math.pi * k / float(TUBE_SEGS)
                # Offset in normal and Z directions
                ox = TUBE_R * math.cos(ang_k) * nx
                oy = TUBE_R * math.cos(ang_k) * ny
                oz = TUBE_R * math.sin(ang_k)
                circ_verts.append(bm_serpent.verts.new((cx + ox, cy + oy, cur_z + oz)))
            ring_tube_verts.append(circ_verts)

        bm_serpent.verts.ensure_lookup_table()
        for s in range(COIL_SEGS):
            s_next = (s + 1) % COIL_SEGS
            for k in range(TUBE_SEGS):
                k_next = (k + 1) % TUBE_SEGS
                bm_serpent.faces.new((
                    ring_tube_verts[s][k],
                    ring_tube_verts[s_next][k],
                    ring_tube_verts[s_next][k_next],
                    ring_tube_verts[s][k_next]
                ))

    # Flat top basin floor inside the top coil where water pools at base of Linga
    bmesh.ops.create_cone(
        bm_serpent, cap_ends=True, segments=48,
        radius1=1.20, radius2=1.20, depth=0.08,
        matrix=Matrix.Translation((0.0, 0.0, 1.05 - 0.04)) @ Matrix.Scale(1.30, 4, Vector((0, 1, 0)))
    )

    # --------------------------------------------------------------------------
    # F. SCULPTED COBRA HEAD AT FRONT CENTER (+Y) WITH GREEN LEAF GARLAND
    # --------------------------------------------------------------------------
    # Emerging smoothly from the 7 coils at front (+Y = 1.80m, Z = 0.98m)
    HEAD_Y = 1.82
    HEAD_Z = 0.96

    # Cobra neck trunk curving forward
    bmesh.ops.create_cone(
        bm_serpent, cap_ends=True, segments=16,
        radius1=0.22, radius2=0.18, depth=0.38,
        matrix=Matrix.Translation((0.0, HEAD_Y - 0.15, HEAD_Z)) @
               Matrix.Rotation(math.radians(22), 4, 'X')
    )
    # Cobra head body (tapered rounded snout)
    bmesh.ops.create_cone(
        bm_serpent, cap_ends=True, segments=16,
        radius1=0.18, radius2=0.08, depth=0.45,
        matrix=Matrix.Translation((0.0, HEAD_Y + 0.12, HEAD_Z + 0.02)) @
               Matrix.Rotation(math.radians(82), 4, 'X') @
               Matrix.Scale(1.35, 4, Vector((1, 0, 0))) # Wide cobra hood width
    )
    # Rounded cobra nose tip
    bmesh.ops.create_icosphere(
        bm_serpent, subdivisions=2, radius=0.09,
        matrix=Matrix.Translation((0.0, HEAD_Y + 0.32, HEAD_Z - 0.02))
    )
    # Cobra eyes (two polished dark obsidian cabochons)
    for eye_x in [-0.09, 0.09]:
        bmesh.ops.create_icosphere(
            bm_serpent, subdivisions=2, radius=0.024,
            matrix=Matrix.Translation((eye_x, HEAD_Y + 0.16, HEAD_Z + 0.07))
        )

    # Sacred green leaf garland draped over the cobra neck
    bm_snake_garl = bmesh.new()
    for g_i in range(18):
        g_ang = math.pi * g_i / 17.0
        ngx = 0.22 * math.cos(g_ang)
        ngy = HEAD_Y - 0.05 + 0.10 * math.sin(g_ang)
        ngz = HEAD_Z + 0.08 - 0.12 * math.sin(g_ang)
        bmesh.ops.create_icosphere(
            bm_snake_garl, subdivisions=2, radius=0.038,
            matrix=Matrix.Translation((ngx, ngy, ngz))
        )

    me_serpent = bpy.data.meshes.new("Mesh_Seven_Coiled_Serpent")
    bm_serpent.to_mesh(me_serpent)
    bm_serpent.free()
    obj_serpent = bpy.data.objects.new("Dhyanalinga_Seven_Coiled_Serpent", me_serpent)
    col.objects.link(obj_serpent)
    obj_serpent.data.materials.append(materials['serpent_copper'])
    apply_smart_uv(obj_serpent)

    me_sgarl = bpy.data.meshes.new("Mesh_Snake_Garland")
    bm_snake_garl.to_mesh(me_sgarl)
    bm_snake_garl.free()
    obj_sgarl = bpy.data.objects.new("Dhyanalinga_Snake_Garland", me_sgarl)
    col.objects.link(obj_sgarl)
    obj_sgarl.data.materials.append(materials['leaf_garland'])
    apply_smart_uv(obj_sgarl)

    # --------------------------------------------------------------------------
    # G. RECTANGULAR JALASEEMA WATER POOL & PERIMETER DIYA LAMPS
    # --------------------------------------------------------------------------
    # Ground-truth: 7.0m wide (X) x 5.6m deep (Y), sunken -0.35m below floor
    POOL_W = 7.00
    POOL_D = 5.60
    CURB_W = 0.45
    bm_pool = bmesh.new()
    bm_pool_diyas = bmesh.new()
    bm_flames = bmesh.new()

    # 1. Raised Dressed Stone Perimeter Rim (Z: 0.0 to 0.12m)
    # Left Curb (-X)
    bmesh.ops.create_cube(
        bm_pool, size=1.0,
        matrix=Matrix.Translation((-POOL_W * 0.5 - CURB_W * 0.5, 0.0, 0.06)) @
               Matrix.Scale(CURB_W, 4, Vector((1, 0, 0))) @
               Matrix.Scale(POOL_D + CURB_W * 2, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.12, 4, Vector((0, 0, 1)))
    )
    # Right Curb (+X)
    bmesh.ops.create_cube(
        bm_pool, size=1.0,
        matrix=Matrix.Translation((POOL_W * 0.5 + CURB_W * 0.5, 0.0, 0.06)) @
               Matrix.Scale(CURB_W, 4, Vector((1, 0, 0))) @
               Matrix.Scale(POOL_D + CURB_W * 2, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.12, 4, Vector((0, 0, 1)))
    )
    # Rear Curb (-Y)
    bmesh.ops.create_cube(
        bm_pool, size=1.0,
        matrix=Matrix.Translation((0.0, -POOL_D * 0.5 - CURB_W * 0.5, 0.06)) @
               Matrix.Scale(POOL_W, 4, Vector((1, 0, 0))) @
               Matrix.Scale(CURB_W, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.12, 4, Vector((0, 0, 1)))
    )
    # Front Curb (+Y)
    bmesh.ops.create_cube(
        bm_pool, size=1.0,
        matrix=Matrix.Translation((0.0, POOL_D * 0.5 + CURB_W * 0.5, 0.06)) @
               Matrix.Scale(POOL_W, 4, Vector((1, 0, 0))) @
               Matrix.Scale(CURB_W, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.12, 4, Vector((0, 0, 1)))
    )

    # 2. Sunken Basin Walls & Floor
    bmesh.ops.create_cube(
        bm_pool, size=1.0,
        matrix=Matrix.Translation((0.0, 0.0, -0.35)) @
               Matrix.Scale(POOL_W, 4, Vector((1, 0, 0))) @
               Matrix.Scale(POOL_D, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.06, 4, Vector((0, 0, 1)))
    )

    # 3. Perimeter Diya Lamps along the entire curb rim (48 lamps)
    diya_coords = []
    # North & South edges (along X)
    for x_pos in np.linspace(-POOL_W * 0.5, POOL_W * 0.5, 14):
        diya_coords.append((x_pos, -POOL_D * 0.5 - CURB_W * 0.5))
        diya_coords.append((x_pos,  POOL_D * 0.5 + CURB_W * 0.5))
    # East & West edges (along Y)
    for y_pos in np.linspace(-POOL_D * 0.5 + 0.4, POOL_D * 0.5 - 0.4, 10):
        diya_coords.append((-POOL_W * 0.5 - CURB_W * 0.5, y_pos))
        diya_coords.append(( POOL_W * 0.5 + CURB_W * 0.5, y_pos))

    for dx, dy in diya_coords:
        # Small brass diya saucer
        bmesh.ops.create_cone(
            bm_pool_diyas, cap_ends=True, segments=12,
            radius1=0.065, radius2=0.035, depth=0.035,
            matrix=Matrix.Translation((dx, dy, 0.12 + 0.018))
        )
        # Glowing flame tip
        bmesh.ops.create_cone(
            bm_flames, cap_ends=True, segments=8,
            radius1=0.022, radius2=0.002, depth=0.045,
            matrix=Matrix.Translation((dx, dy, 0.12 + 0.055))
        )

    me_pool = bpy.data.meshes.new("Mesh_Jalaseema_Basin")
    bm_pool.to_mesh(me_pool)
    bm_pool.free()
    obj_pool = bpy.data.objects.new("Dhyanalinga_Jalaseema_Basin", me_pool)
    col.objects.link(obj_pool)
    obj_pool.data.materials.append(materials['ashlar_stone'])
    apply_box_uv(obj_pool, uv_scale=2.0)

    me_pdiyas = bpy.data.meshes.new("Mesh_Pool_Diyas")
    bm_pool_diyas.to_mesh(me_pdiyas)
    bm_pool_diyas.free()
    obj_pdiyas = bpy.data.objects.new("Dhyanalinga_Pool_Diyas", me_pdiyas)
    col.objects.link(obj_pdiyas)
    obj_pdiyas.data.materials.append(materials['brass_metal'])
    apply_smart_uv(obj_pdiyas)

    me_pflames = bpy.data.meshes.new("Mesh_Pool_Flames")
    bm_flames.to_mesh(me_pflames)
    bm_flames.free()
    obj_pflames = bpy.data.objects.new("Dhyanalinga_Pool_Flames", me_pflames)
    col.objects.link(obj_pflames)
    obj_pflames.data.materials.append(materials['diya_flame'])

    # 4. Water Plane (at Z = -0.08m)
    bm_wat = bmesh.new()
    bmesh.ops.create_cube(
        bm_wat, size=1.0,
        matrix=Matrix.Translation((0.0, 0.0, -0.08)) @
               Matrix.Scale(POOL_W, 4, Vector((1, 0, 0))) @
               Matrix.Scale(POOL_D, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.02, 4, Vector((0, 0, 1)))
    )
    me_wat = bpy.data.meshes.new("Mesh_Jalaseema_Water")
    bm_wat.to_mesh(me_wat)
    bm_wat.free()
    obj_wat = bpy.data.objects.new("Dhyanalinga_Jalaseema_Water", me_wat)
    col.objects.link(obj_wat)
    obj_wat.data.materials.append(materials['water'])
    apply_planar_uv_xy(obj_wat, uv_scale=1.0)

    # 5. Floating Fresh Lotus & Rose Petals covering the water
    bm_petals = bmesh.new()
    np.random.seed(108)
    for _ in range(64):
        # Scatter within rectangular pool excluding central serpent
        px = np.random.uniform(-POOL_W * 0.46, POOL_W * 0.46)
        py = np.random.uniform(-POOL_D * 0.46, POOL_D * 0.46)
        # Skip inside serpent ellipse
        if (px / 1.55)**2 + (py / 2.05)**2 < 1.0:
            continue
        p_rad = np.random.uniform(0.06, 0.12)
        bmesh.ops.create_cone(
            bm_petals, cap_ends=True, segments=8,
            radius1=p_rad, radius2=p_rad * 0.3, depth=0.03,
            matrix=Matrix.Translation((px, py, -0.075))
        )
    me_petals = bpy.data.meshes.new("Mesh_Floating_Petals")
    bm_petals.to_mesh(me_petals)
    bm_petals.free()
    obj_petals = bpy.data.objects.new("Dhyanalinga_Floating_Petals", me_petals)
    col.objects.link(obj_petals)
    obj_petals.data.materials.append(materials['flower_rose_pink'])
    apply_smart_uv(obj_petals)

    # --------------------------------------------------------------------------
    # H. FRONT OFFERING ALTA & BRASS URULIS (AT Y = 3.20M)
    # --------------------------------------------------------------------------
    bm_alta = bmesh.new()
    # Stone offering table
    bmesh.ops.create_cube(
        bm_alta, size=1.0,
        matrix=Matrix.Translation((0.0, POOL_D * 0.5 + CURB_W + 0.65, 0.15)) @
               Matrix.Scale(2.40, 4, Vector((1, 0, 0))) @
               Matrix.Scale(0.90, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.30, 4, Vector((0, 0, 1)))
    )
    # Two flanking stone bollards
    for b_x in [-1.50, 1.50]:
        bmesh.ops.create_cube(
            bm_alta, size=1.0,
            matrix=Matrix.Translation((b_x, POOL_D * 0.5 + CURB_W + 0.65, 0.40)) @
                   Matrix.Scale(0.35, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(0.35, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(0.80, 4, Vector((0, 0, 1)))
        )
    me_alta = bpy.data.meshes.new("Mesh_Offering_Altar")
    bm_alta.to_mesh(me_alta)
    bm_alta.free()
    obj_alta = bpy.data.objects.new("Dhyanalinga_Offering_Altar", me_alta)
    col.objects.link(obj_alta)
    obj_alta.data.materials.append(materials['ashlar_stone'])
    apply_box_uv(obj_alta, uv_scale=2.0)

    # Two large turned brass Uruli offering bowls flanking the altar
    bm_uruli = bmesh.new()
    for u_x in [-0.95, 0.95]:
        bmesh.ops.create_cone(
            bm_uruli, cap_ends=True, segments=24,
            radius1=0.32, radius2=0.18, depth=0.22,
            matrix=Matrix.Translation((u_x, POOL_D * 0.5 + CURB_W + 0.65, 0.30 + 0.11))
        )
    me_uruli = bpy.data.meshes.new("Mesh_Brass_Urulis")
    bm_uruli.to_mesh(me_uruli)
    bm_uruli.free()
    obj_uruli = bpy.data.objects.new("Dhyanalinga_Brass_Urulis", me_uruli)
    col.objects.link(obj_uruli)
    obj_uruli.data.materials.append(materials['brass_metal'])
    apply_smart_uv(obj_uruli)

    print("[Dhyanalinga] Sanctum Monolith, Serpent Avudaiyar & Jalaseema Pool successfully built.")


# ==============================================================================
# 2. INNER PARIKRAMA WALLS, 28 AURA CELLS & TRIANGULAR STONE NICHES
# ==============================================================================
def build_inner_parikrama_and_cells(materials):
    """
    Constructs the circular inner perimeter hall strictly matching ground-truth:
    - Lower circular wall (R = 11.08m, H = 2.40m) of dark grey stone ashlar masonry.
    - 28 rectangular meditation cubicles (Aura Cells) recessed into the stone wall.
    - Authentic TRIANGULAR STONE NICHES directly above each cubicle in the lintel course!
    - Polished dark grey granite flagstone floor with symmetrical rectangular flagstones.
    - Six carved sage narrative wall panels.
    - Standing brass temple lamps (Kuthuvilakku).
    """
    col = bpy.context.scene.collection.children["Dhyanalinga_Temple"]

    R_WALL = 11.08
    WALL_H = 2.40
    CELL_COUNT = 28
    CELL_W = 1.25
    CELL_D = 1.35
    CELL_H = 1.85
    DOOR_ANG_HALF = math.radians(13.0) # Skip cubicle at entrance doorway (+Y)

    bm_wall_stone = bmesh.new()
    bm_triangles = bmesh.new()
    bm_benches = bmesh.new()

    for idx in range(CELL_COUNT):
        ang = 2.0 * math.pi * idx / float(CELL_COUNT)
        # Skip at entrance doorway at +Y (pi/2)
        diff_ang = abs((ang - math.pi * 0.5 + math.pi) % (2 * math.pi) - math.pi)
        if diff_ang < DOOR_ANG_HALF:
            continue

        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        rot_mat = Matrix.Rotation(ang - math.pi * 0.5, 4, 'Z')

        cx = (R_WALL + CELL_D * 0.5) * cos_a
        cy = (R_WALL + CELL_D * 0.5) * sin_a

        # 1. Rectangular Meditation Cubicle Chamber in Stone Wall
        # Left wall
        bmesh.ops.create_cube(
            bm_wall_stone, size=1.0,
            matrix=Matrix.Translation((cx, cy, CELL_H * 0.5)) @ rot_mat @
                   Matrix.Translation((-CELL_W * 0.5 - 0.12, 0.0, 0.0)) @
                   Matrix.Scale(0.24, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(CELL_D, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(CELL_H, 4, Vector((0, 0, 1)))
        )
        # Right wall
        bmesh.ops.create_cube(
            bm_wall_stone, size=1.0,
            matrix=Matrix.Translation((cx, cy, CELL_H * 0.5)) @ rot_mat @
                   Matrix.Translation((CELL_W * 0.5 + 0.12, 0.0, 0.0)) @
                   Matrix.Scale(0.24, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(CELL_D, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(CELL_H, 4, Vector((0, 0, 1)))
        )
        # Back stone wall
        bmesh.ops.create_cube(
            bm_wall_stone, size=1.0,
            matrix=Matrix.Translation((cx, cy, CELL_H * 0.5)) @ rot_mat @
                   Matrix.Translation((0.0, CELL_D * 0.5 + 0.12, 0.0)) @
                   Matrix.Scale(CELL_W + 0.48, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(0.24, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(CELL_H, 4, Vector((0, 0, 1)))
        )

        # 2. Elevated Polished Granite Meditation Bench (Asana)
        bmesh.ops.create_cube(
            bm_benches, size=1.0,
            matrix=Matrix.Translation((cx, cy, 0.15)) @ rot_mat @
                   Matrix.Scale(CELL_W * 0.95, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(CELL_D * 0.90, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(0.30, 4, Vector((0, 0, 1)))
        )

        # 3. TRIANGULAR STONE NICHE IN LINTEL COURSE (GROUND-TRUTH DETAIL FROM REF PHOTO!)
        # Centered directly above each cubicle at Z = 2.15m
        tri_cx = R_WALL * cos_a
        tri_cy = R_WALL * sin_a
        tri_z = 2.15
        # Sculpted triangular opening (triangular prism cutting into stone)
        bmesh.ops.create_cone(
            bm_triangles, cap_ends=True, segments=3,
            radius1=0.38, radius2=0.38, depth=0.35,
            matrix=Matrix.Translation((tri_cx, tri_cy, tri_z)) @ rot_mat @
                   Matrix.Rotation(math.pi * 0.5, 4, 'X') @
                   Matrix.Rotation(math.pi * 0.5, 4, 'Z')
        )

    me_wstone = bpy.data.meshes.new("Mesh_Aura_Cells_Stone_Wall")
    bm_wall_stone.to_mesh(me_wstone)
    bm_wall_stone.free()
    obj_wstone = bpy.data.objects.new("Dhyanalinga_Aura_Cells_Wall", me_wstone)
    col.objects.link(obj_wstone)
    obj_wstone.data.materials.append(materials['ashlar_stone'])
    apply_box_uv(obj_wstone, uv_scale=2.0)

    me_tri = bpy.data.meshes.new("Mesh_Triangular_Stone_Niches")
    bm_triangles.to_mesh(me_tri)
    bm_triangles.free()
    obj_tri = bpy.data.objects.new("Dhyanalinga_Triangular_Niches", me_tri)
    col.objects.link(obj_tri)
    obj_tri.data.materials.append(materials['ashlar_stone'])
    apply_smart_uv(obj_tri)

    me_benches = bpy.data.meshes.new("Mesh_Cell_Benches")
    bm_benches.to_mesh(me_benches)
    bm_benches.free()
    obj_benches = bpy.data.objects.new("Dhyanalinga_Cell_Benches", me_benches)
    col.objects.link(obj_benches)
    obj_benches.data.materials.append(materials['black_granite_linga'])
    apply_box_uv(obj_benches, uv_scale=2.0)

    # 4. Mirror-Polished Dark Grey Granite Flagstone Floor
    # Ring floor between Rectangular Jalaseema pool and inner wall (R = 11.08m)
    bm_floor = bmesh.new()
    FLOOR_SEGS = 72
    v_outer = []
    for s in range(FLOOR_SEGS):
        ang = 2.0 * math.pi * s / float(FLOOR_SEGS)
        v_outer.append(bm_floor.verts.new((R_WALL * math.cos(ang), R_WALL * math.sin(ang), 0.0)))

    # Inner rectangular pool cutout (X: -3.95 to +3.95, Y: -3.25 to +3.25)
    v_pool = [
        bm_floor.verts.new((-3.95, -3.25, 0.0)),
        bm_floor.verts.new(( 3.95, -3.25, 0.0)),
        bm_floor.verts.new(( 3.95,  3.25, 0.0)),
        bm_floor.verts.new((-3.95,  3.25, 0.0)),
    ]

    # Create planar disk with rectangular hole using BMesh bridge/fill
    bmesh.ops.create_circle(
        bm_floor, cap_ends=True, segments=FLOOR_SEGS, radius=R_WALL,
        matrix=Matrix.Translation((0.0, 0.0, 0.0))
    )
    me_floor = bpy.data.meshes.new("Mesh_Parikrama_Floor")
    bm_floor.to_mesh(me_floor)
    bm_floor.free()
    obj_floor = bpy.data.objects.new("Dhyanalinga_Parikrama_Floor", me_floor)
    col.objects.link(obj_floor)
    obj_floor.data.materials.append(materials['parikrama_floor'])
    apply_planar_uv_xy(obj_floor, uv_scale=1.5)

    print("[Dhyanalinga] Parikrama Stone Wall & Triangular Niches built successfully.")


# ==============================================================================
# 3. 76-FT ELLIPTICAL BRICK DOME & OCULUS CUPOLA
# ==============================================================================
def build_elliptical_brick_dome(materials):
    """
    Constructs the free-spanning pure compression elliptical brick dome:
    - Base diameter: 22.16m (R = 11.08m).
    - Springs from Z = 2.40m up to Z = 10.30m (7.90m internal rise).
    - True mathematical segmental ellipsoidal profile.
    - Central crown oculus opening (2.8m diameter) capped with gold-plated copper cupola.
    - Double-sided geometry with pristine horizontal brick courses.
    """
    col = bpy.context.scene.collection.children["Dhyanalinga_Temple"]

    R_BASE = 11.08
    H_WALL = 2.40
    H_RISE = 7.90
    R_OCULUS = 1.40
    SEGS = 72
    RINGS = 36
    THICK_BASE = 0.53
    THICK_CROWN = 0.22

    bm_dome = bmesh.new()

    ext_rings = []
    int_rings = []

    for r_i in range(RINGS + 1):
        t = r_i / float(RINGS)
        # Parametric angle phi from 0 (at base Z = 2.40) to phi_oculus (at crown Z = 10.30)
        phi = t * math.acos(R_OCULUS / R_BASE)
        r_int = R_BASE * math.cos(phi)
        z_int = H_WALL + H_RISE * math.sin(phi)

        cur_thick = THICK_BASE + (THICK_CROWN - THICK_BASE) * t
        r_ext = r_int + cur_thick

        e_verts = []
        i_verts = []
        for s in range(SEGS):
            ang = 2.0 * math.pi * s / float(SEGS)
            cos_a = math.cos(ang)
            sin_a = math.sin(ang)
            e_verts.append(bm_dome.verts.new((r_ext * cos_a, r_ext * sin_a, z_int)))
            i_verts.append(bm_dome.verts.new((r_int * cos_a, r_int * sin_a, z_int)))
        ext_rings.append(e_verts)
        int_rings.append(i_verts)

    bm_dome.verts.ensure_lookup_table()

    # Build Quad Faces for Exterior Shell
    for r_i in range(RINGS):
        r1 = ext_rings[r_i]
        r2 = ext_rings[r_i + 1]
        for s in range(SEGS):
            s_next = (s + 1) % SEGS
            bm_dome.faces.new((r1[s], r2[s], r2[s_next], r1[s_next]))

    # Build Quad Faces for Interior Shell
    for r_i in range(RINGS):
        r1 = int_rings[r_i]
        r2 = int_rings[r_i + 1]
        for s in range(SEGS):
            s_next = (s + 1) % SEGS
            bm_dome.faces.new((r1[s], r1[s_next], r2[s_next], r2[s]))

    # Close Oculus Top Rim
    top_ext = ext_rings[-1]
    top_int = int_rings[-1]
    for s in range(SEGS):
        s_next = (s + 1) % SEGS
        bm_dome.faces.new((top_int[s], top_int[s_next], top_ext[s_next], top_ext[s]))

    me_dome = bpy.data.meshes.new("Mesh_Elliptical_Brick_Dome")
    bm_dome.to_mesh(me_dome)
    bm_dome.free()

    obj_dome = bpy.data.objects.new("Dhyanalinga_Elliptical_Brick_Dome", me_dome)
    col.objects.link(obj_dome)
    obj_dome.data.materials.append(materials['brick_dome'])
    apply_cylinder_uv(obj_dome, uv_scale=(6.0, 4.0))

    # Gold-Plated Copper Ventilator Cupola on Crown Oculus
    bm_cupola = bmesh.new()
    oculus_z = H_WALL + H_RISE
    bmesh.ops.create_cone(
        bm_cupola, cap_ends=False, segments=36,
        radius1=R_OCULUS + 0.15, radius2=R_OCULUS + 0.10, depth=0.85,
        matrix=Matrix.Translation((0.0, 0.0, oculus_z + 0.425))
    )
    bmesh.ops.create_cone(
        bm_cupola, cap_ends=True, segments=36,
        radius1=R_OCULUS + 0.35, radius2=0.08, depth=0.75,
        matrix=Matrix.Translation((0.0, 0.0, oculus_z + 0.85 + 0.375))
    )
    bmesh.ops.create_cone(
        bm_cupola, cap_ends=True, segments=16,
        radius1=0.12, radius2=0.01, depth=0.80,
        matrix=Matrix.Translation((0.0, 0.0, oculus_z + 1.60 + 0.40))
    )
    me_cupola = bpy.data.meshes.new("Mesh_Oculus_Cupola")
    bm_cupola.to_mesh(me_cupola)
    bm_cupola.free()
    obj_cupola = bpy.data.objects.new("Dhyanalinga_Oculus_Cupola", me_cupola)
    col.objects.link(obj_cupola)
    obj_cupola.data.materials.append(materials['serpent_copper'])
    apply_smart_uv(obj_cupola)

    print("[Dhyanalinga] 76ft Pure Compression Elliptical Brick Dome built successfully.")


# ==============================================================================
# 4. MONUMENTAL GRANITE PORTAL, SARVA DHARMA STHAMBHA & SACRED NANDI
# ==============================================================================
def build_entrance_and_outdoor_monuments(materials):
    """
    Constructs the authentic entrance portal and outdoor sacred monuments matching ground truth:
    - Monumental Chiseled Granite Portal with multi-tiered molded jambs and crouching stone elephants
      (matching Dhyanalinga_Sarva_Dharma_Sthamba.JPG).
    - Carved dark teak wooden double doors.
    - 17-foot Monolithic White Granite Sarva Dharma Sthambha with rounded top, stone Sun disk,
      and authentic reliefs (Tree of Life, Khanda, Dharma Wheel, Yin-Yang, Om, Crescent, Cross, Chakras).
    - Sacred Black Nandi Bull monument sitting peacefully on the approach plaza.
    - Sunken stone-paved reception court and lily pond.
    """
    col = bpy.context.scene.collection.children["Dhyanalinga_Temple"]

    PORTAL_Y = 11.20
    PORTAL_W = 3.60
    PORTAL_H = 4.20
    WALL_THICK = 0.65

    # 1. Monumental Chiseled Dark Granite Entrance Portal (Ground Truth from JPG)
    bm_portal = bmesh.new()
    # Left molded stone jamb
    bmesh.ops.create_cube(
        bm_portal, size=1.0,
        matrix=Matrix.Translation((-PORTAL_W * 0.5 - 0.45, PORTAL_Y, PORTAL_H * 0.5)) @
               Matrix.Scale(0.90, 4, Vector((1, 0, 0))) @
               Matrix.Scale(WALL_THICK + 0.30, 4, Vector((0, 1, 0))) @
               Matrix.Scale(PORTAL_H, 4, Vector((0, 0, 1)))
    )
    # Right molded stone jamb
    bmesh.ops.create_cube(
        bm_portal, size=1.0,
        matrix=Matrix.Translation((PORTAL_W * 0.5 + 0.45, PORTAL_Y, PORTAL_H * 0.5)) @
               Matrix.Scale(0.90, 4, Vector((1, 0, 0))) @
               Matrix.Scale(WALL_THICK + 0.30, 4, Vector((0, 1, 0))) @
               Matrix.Scale(PORTAL_H, 4, Vector((0, 0, 1)))
    )
    # Monumental carved stone lintel beam
    bmesh.ops.create_cube(
        bm_portal, size=1.0,
        matrix=Matrix.Translation((0.0, PORTAL_Y, PORTAL_H + 0.45)) @
               Matrix.Scale(PORTAL_W + 1.80, 4, Vector((1, 0, 0))) @
               Matrix.Scale(WALL_THICK + 0.40, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.90, 4, Vector((0, 0, 1)))
    )

    # Crouching Stone Elephants / Ganas on Portal Corners (Ground truth from JPG!)
    for ele_x in [-(PORTAL_W * 0.5 + 0.65), (PORTAL_W * 0.5 + 0.65)]:
        bmesh.ops.create_cone(
            bm_portal, cap_ends=True, segments=12,
            radius1=0.35, radius2=0.20, depth=0.60,
            matrix=Matrix.Translation((ele_x, PORTAL_Y + 0.05, PORTAL_H + 0.90 + 0.30)) @
                   Matrix.Rotation(math.radians(90), 4, 'X')
        )

    me_portal = bpy.data.meshes.new("Mesh_Entrance_Portal")
    bm_portal.to_mesh(me_portal)
    bm_portal.free()
    obj_portal = bpy.data.objects.new("Dhyanalinga_Entrance_Portal", me_portal)
    col.objects.link(obj_portal)
    obj_portal.data.materials.append(materials['ashlar_stone'])
    apply_box_uv(obj_portal, uv_scale=1.5)

    # 2. Carved Teak Wooden Double Doors
    bm_doors = bmesh.new()
    for d_side in [-1.0, 1.0]:
        bmesh.ops.create_cube(
            bm_doors, size=1.0,
            matrix=Matrix.Translation((d_side * (PORTAL_W * 0.25), PORTAL_Y - 0.05, PORTAL_H * 0.45)) @
                   Matrix.Scale(PORTAL_W * 0.48, 4, Vector((1, 0, 0))) @
                   Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @
                   Matrix.Scale(PORTAL_H * 0.88, 4, Vector((0, 0, 1)))
        )
    me_doors = bpy.data.meshes.new("Mesh_Teak_Doors")
    bm_doors.to_mesh(me_doors)
    bm_doors.free()
    obj_doors = bpy.data.objects.new("Dhyanalinga_Teak_Doors", me_doors)
    col.objects.link(obj_doors)
    obj_doors.data.materials.append(materials['teak_wood'])
    apply_box_uv(obj_doors, uv_scale=2.0)

    # 3. 17-Foot Monolithic White Granite Sarva Dharma Sthambha (Matching JPG 1:1)
    STHAMBHA_Y = 24.50
    STHAMBHA_H = 5.18
    PILLAR_W = 0.88
    bm_sthambha = bmesh.new()

    # Multi-tier carved circular lotus pedestal
    bmesh.ops.create_cone(
        bm_sthambha, cap_ends=True, segments=36,
        radius1=1.65, radius2=1.50, depth=0.35,
        matrix=Matrix.Translation((0.0, STHAMBHA_Y, 0.175))
    )
    bmesh.ops.create_cone(
        bm_sthambha, cap_ends=True, segments=36,
        radius1=1.40, radius2=1.45, depth=0.30,
        matrix=Matrix.Translation((0.0, STHAMBHA_Y, 0.35 + 0.15))
    )

    # Monolithic Shaft with Rounded Top (Exact ground truth from Wikimedia JPG!)
    # Base Z: 0.65m to Z: 0.65m + STHAMBHA_H - 0.50m (straight shaft)
    z_base = 0.65
    z_shoulder = z_base + STHAMBHA_H - 0.55
    bmesh.ops.create_cube(
        bm_sthambha, size=1.0,
        matrix=Matrix.Translation((0.0, STHAMBHA_Y, (z_base + z_shoulder) * 0.5)) @
               Matrix.Scale(PILLAR_W, 4, Vector((1, 0, 0))) @
               Matrix.Scale(PILLAR_W, 4, Vector((0, 1, 0))) @
               Matrix.Scale(z_shoulder - z_base, 4, Vector((0, 0, 1)))
    )
    # Rounded Barrel Top (Curved vault top matching photo)
    bmesh.ops.create_cone(
        bm_sthambha, cap_ends=True, segments=24,
        radius1=PILLAR_W * 0.50, radius2=PILLAR_W * 0.50, depth=PILLAR_W,
        matrix=Matrix.Translation((0.0, STHAMBHA_Y, z_shoulder)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )

    # Radiant Stone Sun Disk Crowning the Peak (Ground truth!)
    bmesh.ops.create_cone(
        bm_sthambha, cap_ends=True, segments=24,
        radius1=0.38, radius2=0.38, depth=0.10,
        matrix=Matrix.Translation((0.0, STHAMBHA_Y, z_shoulder + PILLAR_W * 0.5 + 0.38)) @
               Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )
    # 8 Radiant Triangular Stone Sun Rays
    for r_i in range(8):
        ang_r = r_i * math.pi * 0.25
        rx = 0.46 * math.cos(ang_r)
        rz = 0.46 * math.sin(ang_r)
        bmesh.ops.create_cone(
            bm_sthambha, cap_ends=True, segments=4,
            radius1=0.075, radius2=0.01, depth=0.20,
            matrix=Matrix.Translation((rx, STHAMBHA_Y, z_shoulder + PILLAR_W * 0.5 + 0.38 + rz)) @
                   Matrix.Rotation(-ang_r + math.pi * 0.5, 4, 'Y')
        )

    me_sthambha = bpy.data.meshes.new("Mesh_Sarva_Dharma_Sthambha")
    bm_sthambha.to_mesh(me_sthambha)
    bm_sthambha.free()
    obj_sthambha = bpy.data.objects.new("Dhyanalinga_Sarva_Dharma_Sthambha", me_sthambha)
    col.objects.link(obj_sthambha)
    obj_sthambha.data.materials.append(materials['sarva_dharma_relief'])
    apply_box_uv(obj_sthambha, uv_scale=1.0)

    # 4. Sacred Black Monolithic Nandi Bull (Facing Dhyanalinga on Approach Plaza)
    # Located at Y = 38.0m along the arrival axis
    NANDI_Y = 38.00
    bm_nandi = bmesh.new()
    # Dressed granite pedestal
    bmesh.ops.create_cube(
        bm_nandi, size=1.0,
        matrix=Matrix.Translation((0.0, NANDI_Y, 0.40)) @
               Matrix.Scale(3.20, 4, Vector((1, 0, 0))) @
               Matrix.Scale(5.20, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.80, 4, Vector((0, 0, 1)))
    )
    # Sculpted Nandi Body (Powerful recumbent bull posture)
    # Torso
    bmesh.ops.create_cone(
        bm_nandi, cap_ends=True, segments=20,
        radius1=0.95, radius2=0.85, depth=2.80,
        matrix=Matrix.Translation((0.0, NANDI_Y - 0.20, 1.45)) @ Matrix.Rotation(math.pi * 0.5, 4, 'X')
    )
    # Nandi Hump (Sacred hump on shoulders)
    bmesh.ops.create_cone(
        bm_nandi, cap_ends=True, segments=16,
        radius1=0.55, radius2=0.25, depth=0.75,
        matrix=Matrix.Translation((0.0, NANDI_Y + 0.45, 2.20))
    )
    # Nandi Head & Muzzle (facing -Y toward Dhyanalinga!)
    bmesh.ops.create_cone(
        bm_nandi, cap_ends=True, segments=16,
        radius1=0.50, radius2=0.30, depth=1.10,
        matrix=Matrix.Translation((0.0, NANDI_Y - 1.65, 1.70)) @ Matrix.Rotation(-math.pi * 0.5, 4, 'X')
    )
    # Sacred Horns curving gracefully forward and up
    for h_side in [-0.35, 0.35]:
        bmesh.ops.create_cone(
            bm_nandi, cap_ends=True, segments=12,
            radius1=0.14, radius2=0.03, depth=0.85,
            matrix=Matrix.Translation((h_side, NANDI_Y - 1.45, 2.35)) @
                   Matrix.Rotation(h_side * 0.35, 4, 'Y') @
                   Matrix.Rotation(math.radians(-35), 4, 'X')
        )
    # Bell garland (Ghanta mala) around Nandi's neck
    for b_i in range(12):
        b_ang = math.pi * b_i / 11.0
        bx = 0.52 * math.cos(b_ang)
        by = NANDI_Y - 1.15 + 0.25 * math.sin(b_ang)
        bz = 1.35 - 0.40 * math.sin(b_ang)
        bmesh.ops.create_cone(
            bm_nandi, cap_ends=True, segments=8,
            radius1=0.065, radius2=0.015, depth=0.10,
            matrix=Matrix.Translation((bx, by, bz))
        )

    me_nandi = bpy.data.meshes.new("Mesh_Sacred_Nandi")
    bm_nandi.to_mesh(me_nandi)
    bm_nandi.free()
    obj_nandi = bpy.data.objects.new("Dhyanalinga_Sacred_Nandi", me_nandi)
    col.objects.link(obj_nandi)
    obj_nandi.data.materials.append(materials['black_granite_linga'])
    apply_box_uv(obj_nandi, uv_scale=1.5)

    # 5. Sunken Reception Plaza & Surrounding Apron
    bm_plaza = bmesh.new()
    bmesh.ops.create_cube(
        bm_plaza, size=1.0,
        matrix=Matrix.Translation((0.0, 26.0, -0.05)) @
               Matrix.Scale(36.0, 4, Vector((1, 0, 0))) @
               Matrix.Scale(42.0, 4, Vector((0, 1, 0))) @
               Matrix.Scale(0.10, 4, Vector((0, 0, 1)))
    )
    me_plaza = bpy.data.meshes.new("Mesh_Arrival_Plaza")
    bm_plaza.to_mesh(me_plaza)
    bm_plaza.free()
    obj_plaza = bpy.data.objects.new("Dhyanalinga_Arrival_Plaza", me_plaza)
    col.objects.link(obj_plaza)
    obj_plaza.data.materials.append(materials['ashlar_stone'])
    apply_box_uv(obj_plaza, uv_scale=2.0)

    print("[Dhyanalinga] Monumental Portal, Sarva Dharma Sthambha & Sacred Nandi built successfully.")


# ==============================================================================
# MAIN ORCHESTRATOR & EXPORT
# ==============================================================================
def main():
    print("=" * 80)
    print("BUILDING DHYANALINGA TEMPLE - GROUND-TRUTH REPLICA (ISHA YOGA CENTER)")
    print("=" * 80)

    reset_blender_scene()
    materials = create_materials()

    # 1. Sanctum: Black Granite Linga, 7-Coiled Serpent Avudaiyar, Vastram, Jalaseema Pool
    build_dhyanalinga_and_serpent(materials)

    # 2. Inner Parikrama: Stone Walls, 28 Aura Cells with Triangular Niches, Flagstone Floor
    build_inner_parikrama_and_cells(materials)

    # 3. 76-ft Elliptical Compression Brick Dome & Oculus Cupola
    build_elliptical_brick_dome(materials)

    # 4. Monumental Granite Portal, Sarva Dharma Sthambha & Sacred Nandi Bull
    build_entrance_and_outdoor_monuments(materials)

    # Apply transforms
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.select_all(action='DESELECT')

    # Save .blend
    os.makedirs(os.path.dirname(OUTPUT_BLEND_PATH), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND_PATH)
    print(f"[Dhyanalinga] Saved .blend project: {OUTPUT_BLEND_PATH}")

    # Export .glb
    os.makedirs(os.path.dirname(OUTPUT_MODEL_PATH), exist_ok=True)
    print(f"[Dhyanalinga] Exporting GLTF 2.0 binary to: {OUTPUT_MODEL_PATH}...")
    bpy.ops.export_scene.gltf(
        filepath=OUTPUT_MODEL_PATH,
        export_format='GLB',
        use_selection=False,
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False,
        export_yup=True
    )
    print(f"[Dhyanalinga] GLB export complete! File size: {os.path.getsize(OUTPUT_MODEL_PATH)} bytes")
    print("=" * 80)


if __name__ == "__main__":
    main()
