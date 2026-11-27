import bpy
import os
import sys

tools_dir = "/home/mullainathan/Games/IshaGodot/tools"
if tools_dir not in sys.path:
    sys.path.append(tools_dir)

import build_lingabhairavi_temple

def save_blend():
    scene = build_lingabhairavi_temple.clean_scene()
    materials = build_lingabhairavi_temple.create_materials()
    build_lingabhairavi_temple.build_lingabhairavi_temple(materials)
    build_lingabhairavi_temple.setup_lighting(scene, materials['paving'])
    
    # Setup default showcase camera
    cam_data = bpy.data.cameras.new("Showcase_Camera")
    cam_obj = bpy.data.objects.new("Showcase_Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (22.0, 26.0, 7.5)
    build_lingabhairavi_temple.point_camera_at(cam_obj, (0.0, 6.5, 4.0))
    cam_data.lens = 28.0
    
    # Save blend files
    out_blend = "/home/mullainathan/Games/IshaGodot/assets/models/lingabhairavi_temple.blend"
    downloads_blend = "/home/mullainathan/Downloads/lingabhairavi_temple.blend"
    
    os.makedirs(os.path.dirname(out_blend), exist_ok=True)
    os.makedirs(os.path.dirname(downloads_blend), exist_ok=True)
    
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"Saved: {out_blend} ({os.path.getsize(out_blend)} bytes)")
    
    bpy.ops.wm.save_as_mainfile(filepath=downloads_blend)
    print(f"Saved: {downloads_blend} ({os.path.getsize(downloads_blend)} bytes)")

if __name__ == "__main__":
    save_blend()
