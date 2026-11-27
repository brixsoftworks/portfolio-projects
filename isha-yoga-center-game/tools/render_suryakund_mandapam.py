"""
Suryakund Complex Renderer (v12 - 3-Pillar Side Mandapams, Subterranean Pool & Solid Plinths)
Renders 5 high-definition architectural captures:
1. suryakund_v12_01_outer_steps_south.png (Outer steps side at South looking up 48m exterior steps from outside arrival plaza)
2. suryakund_v12_02_north_mandapam_ground_level.png (North side at World Floor Z = 0.0m showing open central aisle and slender pillars)
3. suryakund_v12_03_side_mandapam_3_pillars_aisle.png (Looking down side mandapam aisle clearly showing 3 columns across gallery width)
4. suryakund_v12_04_subterranean_pool_3quarter_view.png (3/4 view of subterranean pool pit, tiered steps, turquoise water & 3 Rasalingas)
5. suryakund_v12_05_high_aerial_full_complex.png (High 3/4 aerial showing widened 3-pillar complex, subterranean pool, and solid plinths)
"""

import bpy
import math
from mathutils import Vector
import os
import sys
import importlib

tools_dir = "/home/mullainathan/Games/IshaGodot/tools"
if tools_dir not in sys.path:
    sys.path.append(tools_dir)

import build_suryakund_exterior_steps
importlib.reload(build_suryakund_exterior_steps)

import build_suryakund_mandapam
importlib.reload(build_suryakund_mandapam)

def point_camera_at(cam_obj, target_pos):
    target_vec = Vector(target_pos)
    cam_pos = cam_obj.location
    direction = target_vec - cam_pos
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def run():
    print(">>> 1. Building Suryakund Complex (v12 - 3 Pillars Side Mandapams)...")
    build_suryakund_mandapam.build_suryakund_mandapam()

    scene = bpy.context.scene

    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        try:
            scene.render.engine = 'BLENDER_EEVEE'
        except Exception:
            pass

    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    # 1. World Sky Lighting
    world = scene.world
    if world and world.node_tree:
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node:
            bg_node.inputs['Color'].default_value = (0.58, 0.70, 0.85, 1.0)
            bg_node.inputs['Strength'].default_value = 1.25

    # 2. Sun Lighting
    sun = bpy.data.objects.get("Suryakund_Sun_Light")
    if sun:
        sun.data.energy = 5.5
        sun.data.color = (1.0, 0.96, 0.90)
        sun.location = (50.0, -40.0, 52.0)
        sun.rotation_euler = (math.radians(45.0), math.radians(20.0), math.radians(-35.0))

    fill = bpy.data.objects.get("Suryakund_Fill_Light")
    if fill:
        fill.data.energy = 3.2
        fill.data.color = (0.80, 0.88, 0.98)
        fill.location = (-45.0, 35.0, 38.0)
        fill.rotation_euler = (math.radians(60.0), math.radians(-15.0), math.radians(140.0))

    # Soft ambient interior fill lights (elevated high at Z=7.5m with low energy to eliminate harsh glare)
    mandapam_light = bpy.data.objects.get("Mandapam_Interior_Light")
    if not mandapam_light:
        light_data = bpy.data.lights.new(name="Mandapam_Interior_Light", type='POINT')
        mandapam_light = bpy.data.objects.new(name="Mandapam_Interior_Light", object_data=light_data)
        scene.collection.objects.link(mandapam_light)
    mandapam_light.data.energy = 8000.0
    mandapam_light.data.color = (1.0, 0.94, 0.86)
    mandapam_light.location = (0.0, 0.0, 7.8)
    try:
        mandapam_light.data.specular_factor = 0.0
        mandapam_light.data.shadow_soft_size = 4.0
    except Exception:
        pass

    stair_light = bpy.data.objects.get("Mandapam_Stair_Light")
    if not stair_light:
        stair_light_data = bpy.data.lights.new(name="Mandapam_Stair_Light", type='POINT')
        stair_light = bpy.data.objects.new(name="Mandapam_Stair_Light", object_data=stair_light_data)
        scene.collection.objects.link(stair_light)
    stair_light.data.energy = 6000.0
    stair_light.data.color = (1.0, 0.95, 0.88)
    stair_light.location = (0.0, 18.0, 7.5)
    try:
        stair_light.data.specular_factor = 0.0
        stair_light.data.shadow_soft_size = 4.0
    except Exception:
        pass

    north_light = bpy.data.objects.get("Mandapam_North_Light")
    if not north_light:
        north_light_data = bpy.data.lights.new(name="Mandapam_North_Light", type='POINT')
        north_light = bpy.data.objects.new(name="Mandapam_North_Light", object_data=north_light_data)
        scene.collection.objects.link(north_light)
    north_light.data.energy = 7000.0
    north_light.data.color = (1.0, 0.96, 0.90)
    north_light.location = (0.0, 42.0, 7.5)
    try:
        north_light.data.specular_factor = 0.0
        north_light.data.shadow_soft_size = 4.0
    except Exception:
        pass

    west_light = bpy.data.objects.get("Mandapam_West_Light")
    if not west_light:
        west_light_data = bpy.data.lights.new(name="Mandapam_West_Light", type='POINT')
        west_light = bpy.data.objects.new(name="Mandapam_West_Light", object_data=west_light_data)
        scene.collection.objects.link(west_light)
    west_light.data.energy = 6000.0
    west_light.data.color = (1.0, 0.95, 0.88)
    west_light.location = (-33.5, 10.0, 7.5)
    try:
        west_light.data.specular_factor = 0.0
        west_light.data.shadow_soft_size = 4.0
    except Exception:
        pass

    cam = bpy.data.objects.get("Render_Cam")
    if not cam:
        cam_data = bpy.data.cameras.new(name="Render_Cam")
        cam = bpy.data.objects.new(name="Render_Cam", object_data=cam_data)
        scene.collection.objects.link(cam)
    scene.camera = cam
    cam.data.clip_start = 0.2
    cam.data.clip_end = 800.0

    output_dir = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures"
    os.makedirs(output_dir, exist_ok=True)

    shots = [
        # Shot 1: Looking UP at 48m exterior steps and South elevated portal (Z = 3.50m) from outside arrival plaza (Z = 0.0m)
        {
            "name": "suryakund_v18_01_outer_steps_south.png",
            "pos": (0.0, -56.0, 1.8),
            "target": (0.0, -25.0, 5.0),
            "lens": 22.0
        },
        # Shot 2: North Mandapam looking down the grand staircase at 3D King Cobra Naga carving on square rock & central pillar reaching dome
        {
            "name": "suryakund_v18_02_north_mandapam_grand_stairs_naga_pillar.png",
            "pos": (0.0, 31.0, 2.8),
            "target": (0.0, 14.5, 4.0),
            "lens": 28.0
        },
        # Shot 3: 3/4 Perspective from steps landing showing square 8x8m rock thickness (depth = width), plain granite side, and central pillar meeting arch rib / dome flush
        {
            "name": "suryakund_v18_03_thick_rock_pillar_3q_side_landing.png",
            "pos": (-17.0, 24.0, 3.5),
            "target": (0.0, 13.0, 7.0),
            "lens": 22.0
        },
        # Shot 4: From lower pool steps looking UP at monolithic solid granite back face grounded down to -4.50m and central pillar reaching dome ceiling
        {
            "name": "suryakund_v18_04_pool_looking_up_naga_back_and_pillar.png",
            "pos": (-12.0, -1.0, 0.5),
            "target": (0.0, 12.5, 7.5),
            "lens": 22.0
        },
        # Shot 5: Subterranean pool wall-to-wall (no left space), water at 3rd step, 3 Rasalingas 3/4 soaked & 8.81m waterfall plunging from top of wall!
        {
            "name": "suryakund_v18_05_subterranean_pool_waterfall_linga.png",
            "pos": (-14.0, 9.2, -1.2),
            "target": (0.0, -7.5, -1.0),
            "lens": 20.0
        },
        # Shot 6: High 3/4 aerial view showing full complex, square 8x8m rock, and central pillar supporting the vault
        {
            "name": "suryakund_v18_06_high_aerial_full_complex.png",
            "pos": (82.0, -45.0, 48.0),
            "target": (0.0, 10.0, 2.0),
            "lens": 22.0
        }
    ]

    for shot in shots:
        cam.location = shot["pos"]
        cam.data.lens = shot["lens"]
        point_camera_at(cam, shot["target"])
        bpy.context.view_layer.update()
        out_path = os.path.join(output_dir, shot["name"])
        scene.render.filepath = out_path
        print(f"Rendering {shot['name']}...")
        bpy.ops.render.render(write_still=True)
        print(f"Saved: {out_path}")

    # Save blend file
    blend_path = "/home/mullainathan/Downloads/Untitled.blend"
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"Saved mainfile to {blend_path}")

    # Export production GLB
    glb_export_path = "/home/mullainathan/Games/IshaGodot/assets/models/suryakund_complex.glb"
    os.makedirs(os.path.dirname(glb_export_path), exist_ok=True)
    
    col = bpy.data.collections.get("Suryakund_Complex")
    if col:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in col.objects:
            obj.select_set(True)
        bpy.ops.export_scene.gltf(
            filepath=glb_export_path,
            use_selection=True,
            export_format='GLB',
            export_materials='EXPORT',
            export_apply=True
        )
        print(f"Exported GLB to {glb_export_path}")

if __name__ == "__main__":
    run()
