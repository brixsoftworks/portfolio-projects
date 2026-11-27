# 3D Models Directory — Nilambur Teak Wood

This directory holds 3D glTF/GLB models for interactive WebGL showcases powered by Three.js and `@react-three/fiber`.

## Supported Formats
- `.glb` (Binary glTF with embedded textures — recommended for production)
- `.gltf` + `.bin` + texture maps

## Catalog of 3D Models

### 1. `furniture/teak-lounge-chair.glb`
- **Asset Description**: Mid-century modern handcrafted teak lounge chair with Kerala brass joinery accents.
- **Recommended License**: CC0 or CC-BY (Poly Haven / Sketchfab)
- **Geometry**: ~24,000 polygons, Draco-compressed.
- **PBR Texture Sets**: 2K Diffuse, Normal, Roughness (using `/textures/wood/teak-grain.jpg`).

### 2. `furniture/teak-dining-table.glb`
- **Asset Description**: Live-edge Nilambur teak dining table with natural heartwood grain and oil finish.
- **Recommended License**: CC0 (Poly Haven)
- **Geometry**: ~18,000 polygons.

### 3. `interiors/nilambur-living-room.glb`
- **Asset Description**: Minimalist architectural living space with floor-to-ceiling teak acoustic wall panelling.
- **Recommended License**: Commercial License / Custom Studio Scan
- **Geometry**: ~45,000 polygons.

## Procedural Fallback Component
In addition to external `.glb` files, the project includes an interactive procedural 3D model component (`src/components/three/ProceduralTeakModel.tsx`) that renders real-time PBR-textured Nilambur Teak geometry using Three.js meshes and lighting.
