"""
Suryakund Full-Width Builder & High-Definition Multi-Angle Renderer (v5)
Executes build_suryakund_base.py and renders 4 comprehensive verification captures:
1. suryakund_01_south_to_north.png (View across pool looking North at 48m grand steps)
2. suryakund_02_walkthrough_descent.png (Standing at top of 48m steps looking down into pool)
3. suryakund_03_aerial_overview.png (High aerial isometric view showing full 48m width)
4. suryakund_04_water_rasalingas.png (Close-up front view of the 3 Rasalingas in energized water)
"""

import bpy
import math
from mathutils import Vector
import os
import sys
import importlib

# Ensure tool directory is on path
tools_dir = "/home/mullainathan/Games/IshaGodot/tools"
if tools_dir not in sys.path:
    sys.path.append(tools_dir)

import build_suryakund_base
importlib.reload(build_suryakund_base)

def point_camera_at(cam_obj, target_pos):
    target_vec = Vector(target_pos)
    cam_pos = cam_obj.location
    direction = target_vec - cam_pos
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def run():
    print(">>> 1. Building Suryakund Base with 48m wall-to-wall steps (v5)...")
    build_suryakund_base.build_suryakund_base()

    scene = bpy.context.scene

    # Renderer settings
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

    # Lighting Setup
    sun = bpy.data.objects.get("Suryakund_Sun_Light")
    if not sun:
        sun_data = bpy.data.lights.new(name="Suryakund_Sun_Light", type='SUN')
        sun = bpy.data.objects.new(name="Suryakund_Sun_Light", object_data=sun_data)
        scene.collection.objects.link(sun)
    sun.data.energy = 4.5
    sun.data.color = (1.0, 0.96, 0.88)
    sun.location = (20.0, -12.0, 30.0)
    sun.rotation_euler = (math.radians(52.0), math.radians(18.0), math.radians(-35.0))

    fill = bpy.data.objects.get("Suryakund_Fill_Light")
    if not fill:
        fill_data = bpy.data.lights.new(name="Suryakund_Fill_Light", type='SUN')
        fill = bpy.data.objects.new(name="Suryakund_Fill_Light", object_data=fill_data)
        scene.collection.objects.link(fill)
    fill.data.energy = 2.0
    fill.data.color = (0.75, 0.85, 0.95)
    fill.rotation_euler = (math.radians(65.0), math.radians(-20.0), math.radians(145.0))

    # Camera setup
    cam = bpy.data.objects.get("Render_Cam")
    if not cam:
        cam_data = bpy.data.cameras.new(name="Render_Cam")
        cam = bpy.data.objects.new(name="Render_Cam", object_data=cam_data)
        scene.collection.objects.link(cam)
    scene.camera = cam
    cam.data.clip_start = 0.2
    cam.data.clip_end = 500.0

    output_dir = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures"
    os.makedirs(output_dir, exist_ok=True)

    shots = [
        {
            "name": "suryakund_01_south_to_north.png",
            "pos": (0.0, -9.0, 3.8),
            "target": (0.0, 14.0, 4.5),
            "lens": 22.0
        },
        {
            "name": "suryakund_02_walkthrough_descent.png",
            "pos": (0.0, 25.0, 7.8),
            "target": (0.0, 1.0, 1.4),
            "lens": 22.0
        },
        {
            "name": "suryakund_03_aerial_overview.png",
            "pos": (0.0, -26.0, 22.0),
            "target": (0.0, 9.0, 3.5),
            "lens": 24.0
        },
        {
            "name": "suryakund_04_water_rasalingas.png",
            "pos": (0.0, -9.0, 2.5),
            "target": (0.0, 0.0, 2.0),
            "lens": 24.0
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

    # Save mainfile
    blend_path = "/home/mullainathan/Downloads/Untitled.blend"
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"Saved mainfile to {blend_path}")

    # Export production GLB
    glb_export_path = "/home/mullainathan/Games/IshaGodot/assets/models/suryakund_base.glb"
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

        import shutil
        shutil.copyfile(glb_export_path, "/home/mullainathan/Downloads/suryakund_base.glb")
        print("Copied GLB to /home/mullainathan/Downloads/suryakund_base.glb")

if __name__ == "__main__":
    run()
