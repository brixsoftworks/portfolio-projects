"""
Suryakund South Grand Stepped Ghats Builder
Builds full-width (48m wall-to-wall) descending stone steps on the South side:
- Matches the North grand stairs in width: X in [-24.0, +24.0m] (48m wide!)
- Descends all the way down from South Mandapam (Z = 9.60m, Y = -28.0m) to Pool Promenade (Z = 1.60m, Y = -7.5m)
- Removes blocking retaining wall faces and balustrades across the 48m stair opening
- Adds flanking retaining wall extensions along West and East (X in [-24.8, -24.0] and [24.0, 24.8])
"""

import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector

def build_south_steps():
    print("=== Building Suryakund South Grand Steps (Full Width 48m, Z: 9.60m down to 1.60m) ===")

    col_name = "Suryakund_Complex"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

    mat_granite = bpy.data.materials.get("Mat_SarpaVasal_Granite")

    # 1. Clean existing South stairs object if any
    old_south_stairs = bpy.data.objects.get("Suryakund_South_Stairs")
    if old_south_stairs:
        bpy.data.objects.remove(old_south_stairs, do_unlink=True)

    # 2. Update Suryakund_Retaining_Walls: remove blocking South wall faces across X in [-23.8, 23.8]
    rw = bpy.data.objects.get("Suryakund_Retaining_Walls")
    if rw:
        bm_rw = bmesh.new()
        bm_rw.from_mesh(rw.data)
        
        # Identify faces at Y < -10.0 that block the central 48m stair opening
        faces_to_del = [
            f for f in bm_rw.faces
            if any(v.co.y < -10.0 for v in f.verts) and any(abs(v.co.x) < 23.8 for v in f.verts)
        ]
        if faces_to_del:
            bmesh.ops.delete(bm_rw, geom=faces_to_del, context='FACES_ONLY')
            print(f"Removed {len(faces_to_del)} blocking South retaining wall faces!")

        # Also add flanking side wall faces along West (X in [-24.8, -24.0]) and East (X in [24.0, 24.8]) from Y = -10.5 to -28.0
        # Check if already present
        has_flank = any(all(v.co.y < -15.0 for v in f.verts) for f in bm_rw.faces)
        if not has_flank:
            uv_rw = bm_rw.loops.layers.uv.verify()
            # West flanking wall (inner face facing East at X = -24.0, Y from -10.5 to -28.0, Z from 1.60 to 9.60)
            vw0 = bm_rw.verts.new((-24.0, -10.5, 1.60))
            vw1 = bm_rw.verts.new((-24.0, -28.0, 1.60))
            vw2 = bm_rw.verts.new((-24.0, -28.0, 9.60))
            vw3 = bm_rw.verts.new((-24.0, -10.5, 9.60))
            fw = bm_rw.faces.new((vw0, vw1, vw2, vw3))
            fw.normal_update()

            # East flanking wall (inner face facing West at X = 24.0, Y from -10.5 to -28.0, Z from 1.60 to 9.60)
            ve0 = bm_rw.verts.new((24.0, -28.0, 1.60))
            ve1 = bm_rw.verts.new((24.0, -10.5, 1.60))
            ve2 = bm_rw.verts.new((24.0, -10.5, 9.60))
            ve3 = bm_rw.verts.new((24.0, -28.0, 9.60))
            fe = bm_rw.faces.new((ve0, ve1, ve2, ve3))
            fe.normal_update()

        bm_rw.to_mesh(rw.data)
        bm_rw.free()
        rw.data.update()

    # 3. Build Full-Width 48m South Grand Steps (Y in [-28.0m, -7.5m], Z in [1.60m, 9.60m])
    bm_stairs = bmesh.new()
    uv_stairs = bm_stairs.loops.layers.uv.new("UVMap")

    n_steps = 24
    y_step_pts = np.linspace(-7.5, -28.0, n_steps + 1)
    z_step_pts = np.linspace(1.60, 9.60, n_steps + 1)

    n_blocks_wide = 16  # 16 ashlar stone blocks across the 48m width (3m wide blocks)
    x_bounds = np.linspace(-24.0, 24.0, n_blocks_wide + 1)

    for s in range(n_steps):
        y_front = y_step_pts[s]
        y_back = y_step_pts[s + 1]
        z_bot = z_step_pts[s]
        z_top = z_step_pts[s + 1]

        for b in range(n_blocks_wide):
            xb0 = x_bounds[b]
            xb1 = x_bounds[b + 1]

            # Horizontal Tread Face
            vt0 = bm_stairs.verts.new((xb0, y_front, z_top))
            vt1 = bm_stairs.verts.new((xb1, y_front, z_top))
            vt2 = bm_stairs.verts.new((xb1, y_back, z_top))
            vt3 = bm_stairs.verts.new((xb0, y_back, z_top))
            ft = bm_stairs.faces.new((vt0, vt3, vt2, vt1))
            
            u_off = (b * 0.31 + s * 0.27) % 3.0
            v_off = (s * 0.43) % 3.0
            ft.loops[0][uv_stairs].uv = (u_off, v_off)
            ft.loops[1][uv_stairs].uv = (u_off, v_off + 0.3)
            ft.loops[2][uv_stairs].uv = (u_off + 0.6, v_off + 0.3)
            ft.loops[3][uv_stairs].uv = (u_off + 0.6, v_off)

            # Vertical Riser Face (facing North toward the pool)
            vr0 = bm_stairs.verts.new((xb0, y_front, z_bot))
            vr1 = bm_stairs.verts.new((xb1, y_front, z_bot))
            vr2 = bm_stairs.verts.new((xb1, y_front, z_top))
            vr3 = bm_stairs.verts.new((xb0, y_front, z_top))
            fr = bm_stairs.faces.new((vr0, vr1, vr2, vr3))
            
            fr.loops[0][uv_stairs].uv = (u_off, v_off + 0.3)
            fr.loops[1][uv_stairs].uv = (u_off + 0.6, v_off + 0.3)
            fr.loops[2][uv_stairs].uv = (u_off + 0.6, v_off + 0.5)
            fr.loops[3][uv_stairs].uv = (u_off, v_off + 0.5)

    mesh_stairs = bpy.data.meshes.new("Suryakund_South_Stairs")
    bm_stairs.to_mesh(mesh_stairs)
    bm_stairs.free()
    if mat_granite:
        mesh_stairs.materials.append(mat_granite)
    obj_stairs = bpy.data.objects.new("Suryakund_South_Stairs", mesh_stairs)
    col.objects.link(obj_stairs)
    print("Built 48m Full-Width South Grand Descent Steps from Z = 9.60m down to Z = 1.60m!")

if __name__ == "__main__":
    build_south_steps()
