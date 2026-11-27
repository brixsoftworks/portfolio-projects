#!/usr/bin/env python3
"""
Reconstruct 3D Watertight Sarpa Vasal Gateway in sarpavasal.blend
- Preserves the exact front face displaced geometry and UV mapping without modification.
- Analyzes the image alpha channel (485071861_1795533299749824.png) to delete all transparent/alpha regions:
    * Outer background transparent areas
    * Inner dual-archway portal transparent openings (creating hollow walk-through archways)
- Builds solid, watertight side jambs/walls and a sculpted back facade by analyzing the front face.
- Sets materials to 100% opaque solid stone (no transparency artifacts).
- Saves sarpavasal.blend and renders multi-angle verification captures.
"""

import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
from PIL import Image
import numpy as np
import os
import time
import math

def reconstruct_sarpavasal():
    blend_path = "/home/mullainathan/Downloads/sarpavasal.blend"
    img_path = "/home/mullainathan/Downloads/485071861_1795533299749824.png"
    out_dir = "/home/mullainathan/.gemini/antigravity-cli/brain/7c778545-bdb4-4784-a4ae-4940abcb220f/captures"
    os.makedirs(out_dir, exist_ok=True)

    print(f"[Sarpa Vasal 3D] Opening {blend_path}...")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    obj = bpy.data.objects.get("Plane")
    if not obj:
        print("[Sarpa Vasal 3D] Error: Object 'Plane' not found!")
        return

    # 1. Load image and alpha channel
    if not os.path.exists(img_path):
        print(f"[Sarpa Vasal 3D] Error: Image {img_path} not found!")
        return
    pil_img = Image.open(img_path)
    alpha_arr = np.array(pil_img)[:, :, 3]
    h_img, w_img = alpha_arr.shape
    print(f"[Sarpa Vasal 3D] Source image loaded: {w_img}x{h_img}")

    # 2. Evaluate mesh with subdivision, displace, and corrective smooth
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    me_eval = bpy.data.meshes.new_from_object(obj_eval)
    print(f"[Sarpa Vasal 3D] Evaluated front face: {len(me_eval.vertices)} verts, {len(me_eval.polygons)} faces")

    # 3. Create BMesh and remove transparent/alpha regions
    bm = bmesh.new()
    bm.from_mesh(me_eval)

    # Compute UV / pixel coordinates for each vertex
    # In Plane: X in [-1, 1], Y in [-1, 1]
    xs = np.array([v.co.x for v in bm.verts])
    ys = np.array([v.co.y for v in bm.verts])
    us = np.clip((xs + 1.0) / 2.0, 0.0, 1.0)
    vs = np.clip((ys + 1.0) / 2.0, 0.0, 1.0)
    pxs = (us * (w_img - 1)).astype(int)
    pys = ((1.0 - vs) * (h_img - 1)).astype(int)
    alphas = alpha_arr[pys, pxs]

    transp_indices = np.where(alphas < 50)[0]
    bm.verts.ensure_lookup_table()
    verts_to_delete = [bm.verts[i] for i in transp_indices]
    print(f"[Sarpa Vasal 3D] Deleting {len(verts_to_delete)} transparent vertices (outer bounds & arch openings)...")
    bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')

    # Remove any loose wire edges
    wire_edges = [e for e in bm.edges if len(e.link_faces) == 0]
    if wire_edges:
        bmesh.ops.delete(bm, geom=wire_edges, context='EDGES')

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    print(f"[Sarpa Vasal 3D] Cleaned front facade: {len(bm.verts)} verts, {len(bm.faces)} faces")

    # 4. Record front boundary edges BEFORE adding back faces
    boundary_edges = [e for e in bm.edges if e.is_boundary]
    print(f"[Sarpa Vasal 3D] Identified {len(boundary_edges)} boundary edges (perimeter + 2 inner archways)")

    # 5. Build Back Face by analyzing front face depth
    # Front relief spans Z in [-0.47, +0.42].
    # Gateway thickness T = 1.00m (in local scale Z=1.0).
    # Sculpted back facade: pillars and architraves project outward on both front and back!
    t_depth = 1.00 # 1.00m solid architectural gateway thickness
    front_verts = list(bm.verts)
    vert_map_back = {}

    for v in front_verts:
        # Analyzed depth: back projects outward matching front structural prominence
        z_back = -t_depth - (v.co.z + 0.47) * 0.35
        vb = bm.verts.new((v.co.x, v.co.y, z_back))
        vert_map_back[v] = vb

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # 6. Create back faces with reversed winding (normals point outward towards -Z)
    uv_layer = bm.loops.layers.uv.active
    front_faces = list(bm.faces)
    for f in front_faces:
        back_f_verts = [vert_map_back[v] for v in reversed(f.verts)]
        fb = bm.faces.new(back_f_verts)
        fb.material_index = 0
        if uv_layer:
            # Horizontally mirror U for symmetrical architectural alignment on the back
            for idx, l in enumerate(fb.loops):
                orig_uv = f.loops[len(f.loops) - 1 - idx][uv_layer].uv
                l[uv_layer].uv = (1.0 - orig_uv.x, orig_uv.y)

    # 7. Create side quads connecting front boundary edges to back boundary edges
    # Connects outer perimeter walls AND inner door jambs/archways
    for e in boundary_edges:
        v0, v1 = e.verts[0], e.verts[1]
        f = e.link_faces[0]
        f_verts = list(f.verts)
        idx0 = f_verts.index(v0)
        idx1 = f_verts.index(v1)
        is_forward = ((idx0 + 1) % len(f_verts) == idx1)
        if is_forward:
            fs = bm.faces.new((v1, v0, vert_map_back[v0], vert_map_back[v1]))
        else:
            fs = bm.faces.new((v0, v1, vert_map_back[v1], vert_map_back[v0]))
        fs.material_index = 1 # Assigned to dedicated granite stone material for side jambs
        if uv_layer:
            u_edge = (v0.co.x + 1.0) / 2.0
            v_edge = (v0.co.y + 1.0) / 2.0
            fs.loops[0][uv_layer].uv = (u_edge, v_edge)
            fs.loops[1][uv_layer].uv = (u_edge, v_edge)
            fs.loops[2][uv_layer].uv = (u_edge, v_edge)
            fs.loops[3][uv_layer].uv = (u_edge, v_edge)

    # Clean any wire edges
    wire_edges_after = [e for e in bm.edges if len(e.link_faces) == 0]
    if wire_edges_after:
        bmesh.ops.delete(bm, geom=wire_edges_after, context='EDGES')

    # Recalculate face normals outward across the entire closed watertight solid
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    # Verification: check manifoldness
    open_edges = [e for e in bm.edges if e.is_boundary]
    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    print(f"[Sarpa Vasal 3D] Watertight Solid: {len(bm.verts)} verts, {len(bm.faces)} faces")
    print(f"[Sarpa Vasal 3D] Open boundary edges: {len(open_edges)} (Expected: 0)")
    print(f"[Sarpa Vasal 3D] Non-manifold edges: {len(non_manifold_edges)} (Expected: 0)")

    # 8. Assign new mesh to object and remove old modifiers
    new_mesh = bpy.data.meshes.new("SarpaVasal_Solid_Mesh")
    bm.to_mesh(new_mesh)
    bm.free()

    obj.modifiers.clear()
    obj.data = new_mesh
    print("[Sarpa Vasal 3D] Updated Plane object with watertight solid mesh and cleared old modifiers")

    # 9. Materials Setup:
    # Slot 0: Material.001 (front and back photo texture, OPAQUE mode)
    mat_facade = bpy.data.materials.get("Material.001")
    if mat_facade and mat_facade.use_nodes:
        # Disconnect alpha from BSDF Alpha or set alpha to 1.0
        bsdf = mat_facade.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            # Remove any link to Alpha input
            for link in list(mat_facade.node_tree.links):
                if link.to_node == bsdf and link.to_socket.name == "Alpha":
                    mat_facade.node_tree.links.remove(link)
            bsdf.inputs["Alpha"].default_value = 1.0
            bsdf.inputs["Roughness"].default_value = 0.85
            bsdf.inputs["Metallic"].default_value = 0.0

    # Slot 1: Material_SarpaVasal_Granite (for side walls, jambs, and arch reveals)
    mat_granite = bpy.data.materials.get("Material_SarpaVasal_Granite")
    if not mat_granite:
        mat_granite = bpy.data.materials.new(name="Material_SarpaVasal_Granite")
    mat_granite.use_nodes = True
    g_nodes = mat_granite.node_tree.nodes
    g_links = mat_granite.node_tree.links
    g_nodes.clear()
    g_out = g_nodes.new(type='ShaderNodeOutputMaterial')
    g_bsdf = g_nodes.new(type='ShaderNodeBsdfPrincipled')
    # Matching Dravidian granite stone tone:
    g_bsdf.inputs['Base Color'].default_value = (0.68, 0.60, 0.55, 1.0)
    g_bsdf.inputs['Roughness'].default_value = 0.82
    g_bsdf.inputs['Metallic'].default_value = 0.0
    g_links.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])

    new_mesh.materials.clear()
    if mat_facade:
        new_mesh.materials.append(mat_facade)
    new_mesh.materials.append(mat_granite)
    print("[Sarpa Vasal 3D] Assigned Slot 0 (Facade Opaque) and Slot 1 (Dravidian Granite Jambs)")

    # 10. Save updated sarpavasal.blend
    print(f"[Sarpa Vasal 3D] Saving updated scene to {blend_path}...")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # 11. Render multi-angle verification previews
    print("[Sarpa Vasal 3D] Setting up camera and studio lighting for verification renders...")
    # Add warm sun/studio light (Front key)
    light_data = bpy.data.lights.new(name="Studio_Sun", type='SUN')
    light_data.energy = 4.0
    light_data.color = (1.0, 0.96, 0.90)
    light_obj = bpy.data.objects.new(name="Studio_Sun", object_data=light_data)
    light_obj.rotation_euler = Euler((math.radians(45), math.radians(25), math.radians(30)), 'XYZ')
    bpy.context.scene.collection.objects.link(light_obj)

    # Rear key light for illuminating back facade
    fill_data = bpy.data.lights.new(name="Rear_Sun", type='SUN')
    fill_data.energy = 4.0
    fill_data.color = (0.95, 0.96, 1.0)
    fill_obj = bpy.data.objects.new(name="Rear_Sun", object_data=fill_data)
    dir_rear = Vector((0.3, -0.4, 1.0))
    fill_obj.rotation_euler = dir_rear.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(fill_obj)

    cam_data = bpy.data.cameras.new(name="Render_Cam")
    cam_data.lens = 45.0
    cam_data.clip_start = 0.1
    cam_data.clip_end = 200.0
    cam_obj = bpy.data.objects.new(name="Render_Cam", object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'

    shots = [
        {
            "name": "sarpavasal_01_front_3q.png",
            "pos": Vector((6.5, 0.5, 9.0)),
            "target": Vector((0.0, 0.0, 0.0))
        },
        {
            "name": "sarpavasal_02_side_view.png",
            "pos": Vector((11.0, 0.0, -0.4)),
            "target": Vector((0.0, 0.0, -0.4))
        },
        {
            "name": "sarpavasal_03_back_3q.png",
            "pos": Vector((-6.5, 0.5, -9.0)),
            "target": Vector((0.0, 0.0, -0.4))
        },
        {
            "name": "sarpavasal_04_portal_through_view.png",
            "pos": Vector((-1.1, -1.0, 5.0)),
            "target": Vector((-1.1, -1.0, -5.0))
        }
    ]

    for shot in shots:
        cam_obj.location = shot["pos"]
        # Look at target:
        # Note: in Blender coordinates, X is width, Y is height, Z is depth!
        direction = shot["target"] - cam_obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()

        shot_path = os.path.join(out_dir, shot["name"])
        bpy.context.scene.render.filepath = shot_path
        print(f"[Sarpa Vasal 3D] Rendering {shot['name']}...")
        bpy.ops.render.render(write_still=True)
        print(f"[Sarpa Vasal 3D] Saved {shot_path}")

    # Remove temporary render objects and re-save
    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.objects.remove(light_obj, do_unlink=True)
    bpy.data.objects.remove(fill_obj, do_unlink=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[Sarpa Vasal 3D] Finished! Clean sarpavasal.blend saved.")

if __name__ == "__main__":
    reconstruct_sarpavasal()
