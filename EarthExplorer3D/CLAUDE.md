# 3D Modeling & Image-to-3D Instructions for Claude

## [MANDATE] STRICT MANDATE: NO CRUDE PRIMITIVES FOR IMAGE-TO-3D
When the user provides an image, photo, sketch, or turnaround and asks to turn it into a 3D model:
- **NEVER** build crude approximations made of raw orbs, spheres, cylinders, or blocks.
- **NEVER** use `bpy.ops.mesh.primitive_*_add` to fake an object that has intricate organic or mechanical contours.
- The user requires accurate, detailed, textured 3D models that faithfully match the provided image.

---

##  THE TWO ACCURATE IMAGE-TO-3D PIPELINES

### 1. Neural AI Image-to-3D Generation (Fast, High-Fidelity, Full Textures)
Use the dedicated neural image-to-3D tools:
- **`blender-mcp`'s `generate_3d` tool:**
  ```python
  generate_3d(
      image="/path/to/user/image.png",
      provider="auto",  # Options: auto, tripo, hunyuan3d, meshy, hyper3d
      quality="high"
  )
  ```
  This generates high-density textured quad/triangle meshes with PBR materials and automatically imports the resulting `.glb` into the active Blender scene.
- **`image-to-3d` / `meshy-3d-generation` / `tripo-studio` skills:**
  Use these skills to send the image directly to neural reconstruction models.

---

### 2. High-Precision Structural Reconstruction (`blender-image-to-3d` & `reference-to-3d`)
When authoring or custom-rigging assets in Blender:
1. **Camera Calibration:** Set camera focal length and perspective to match the reference view (`scripts/init_master.py`).
2. **Silhouette Extraction:** Use OpenCV contour extraction (`contour-to-mesh`) to extract the exact 2D perimeter and sub-parts instead of guessing dimensions.
3. **UV Mapping & Texture Projection:** Use `atlas-uv-fitting` and `blender-uv-texturing` to project and map the reference image directly onto the front and side UV coordinates.
4. **PBR Materials:** Configure `Principled BSDF` with normal maps, roughness, and metalness (`blender-materials`).
5. **Gated Comparison:** Run `scripts/compose_review.py --measure` to compare the render overlay against the source image. Ensure IoU and silhouette match before declaring completion.
6. **Game Export:** Export clean `.fbx` / `.glb` with applied transforms directly to `/home/mullainathan/Projects/EarthExplorer3D/Assets/Models/`.
