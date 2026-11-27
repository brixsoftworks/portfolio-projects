"""
Generate photorealistic seamless PBR textures for Suryakund Waterfall:
- waterfall_albedo.png (vertical flowing water with white foam rapids and alpha transparency)
- waterfall_normal.png (tangent-space normal map of vertical water flow ripples)
- waterfall_roughness.png (glossy water channels vs rough aerated foam)
- waterfall_foam.png (concentric bubbling impact foam splash with alpha)
"""

import os
import numpy as np
from PIL import Image

output_dir = "/home/mullainathan/Games/IshaGodot/assets/textures"
os.makedirs(output_dir, exist_ok=True)

width, height = 1024, 2048

# Coordinate grid
u = np.linspace(0, 1, width, endpoint=False)
v = np.linspace(0, 1, height, endpoint=False)
uu, vv = np.meshgrid(u, v)

# Multi-frequency vertical flow noise
np.random.seed(42)

# Generate layered sinusoidal & turbulent flow pattern (seamless in V)
def generate_flow_pattern():
    # Primary vertical torrent ribbons
    h = np.zeros((height, width), dtype=np.float32)
    
    # Large flow bands
    h += 0.35 * np.sin(2.0 * np.pi * (uu * 12.0 + np.sin(2.0 * np.pi * vv * 3.0) * 0.3))
    # Medium fast rapids
    h += 0.25 * np.sin(2.0 * np.pi * (uu * 28.0 + vv * 2.0 + np.cos(2.0 * np.pi * uu * 6.0) * 0.4))
    # Fine turbulent ripples
    h += 0.20 * np.sin(2.0 * np.pi * (uu * 64.0 + np.sin(2.0 * np.pi * vv * 6.0) * 0.5))
    h += 0.12 * np.sin(2.0 * np.pi * (uu * 128.0 + vv * 4.0))
    # Micro foam chop
    h += 0.08 * np.sin(2.0 * np.pi * (uu * 256.0 + np.cos(2.0 * np.pi * vv * 8.0) * 0.8))
    
    # Normalize to [0, 1]
    h = (h - h.min()) / (h.max() - h.min())
    return h

print("Generating waterfall flow pattern...")
flow = generate_flow_pattern()

# 1. Albedo & Alpha Texture (RGBA)
# Deep water: (55, 120, 145)
# Mid water: (110, 185, 215)
# Aerated foam: (215, 235, 248)
# Pure white froth: (250, 252, 255)

albedo = np.zeros((height, width, 4), dtype=np.uint8)

# Foam mask: high peaks become dense white aerated foam
foam_mask = np.clip((flow - 0.52) / 0.35, 0.0, 1.0)
foam_mask = np.power(foam_mask, 1.5)

# Water gradient
r = np.clip(55 + flow * 70 + foam_mask * 125, 0, 255).astype(np.uint8)
g = np.clip(120 + flow * 75 + foam_mask * 55, 0, 255).astype(np.uint8)
b = np.clip(145 + flow * 75 + foam_mask * 35, 0, 255).astype(np.uint8)

# Alpha: clear water is ~45% transparent (115), foam is opaque (235)
a = np.clip(115 + flow * 40 + foam_mask * 85, 0, 240).astype(np.uint8)

# Subtle side edge feathering (so waterfall edges fade smoothly)
edge_dist = np.minimum(uu, 1.0 - uu) * 2.0
edge_fade = np.clip(edge_dist * 4.0, 0.0, 1.0)
edge_fade = np.power(edge_fade, 0.5)
a = (a.astype(np.float32) * edge_fade).astype(np.uint8)

albedo[..., 0] = r
albedo[..., 1] = g
albedo[..., 2] = b
albedo[..., 3] = a

albedo_path = os.path.join(output_dir, "waterfall_albedo.png")
Image.fromarray(albedo, mode="RGBA").save(albedo_path)
print(f"Saved: {albedo_path}")

# 2. Tangent-Space Normal Map (RGB)
# Compute partial derivatives via central differences (wrapping in V for seamless tiling)
dy = np.roll(flow, -1, axis=0) - np.roll(flow, 1, axis=0)
dx = np.roll(flow, -1, axis=1) - np.roll(flow, 1, axis=1)

# Normal strength scale
strength = 3.5
nx = -dx * strength
ny = -dy * strength
nz = np.ones_like(flow)

norm = np.sqrt(nx**2 + ny**2 + nz**2)
nx /= norm
ny /= norm
nz /= norm

normal_map = np.zeros((height, width, 3), dtype=np.uint8)
normal_map[..., 0] = np.clip((nx * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
normal_map[..., 1] = np.clip((ny * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
normal_map[..., 2] = np.clip((nz * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)

normal_path = os.path.join(output_dir, "waterfall_normal.png")
Image.fromarray(normal_map, mode="RGB").save(normal_path)
print(f"Saved: {normal_path}")

# 3. Roughness Map (Grayscale)
# Clear water is glossy (~15), aerated foam is rough (~95)
roughness = np.clip(18 + foam_mask * 75, 0, 255).astype(np.uint8)
rough_path = os.path.join(output_dir, "waterfall_roughness.png")
Image.fromarray(roughness, mode="L").save(rough_path)
print(f"Saved: {rough_path}")

# 4. Plunge Pool Impact Foam Texture (1024 x 1024 RGBA)
fw, fh = 1024, 1024
fu = np.linspace(-1, 1, fw)
fv = np.linspace(-1, 1, fh)
fuu, fvv = np.meshgrid(fu, fv)
rad = np.sqrt(fuu**2 + fvv**2)

# Concentric turbulent ripples + bubbling noise
foam_core = np.clip(1.0 - rad * 1.6, 0.0, 1.0)
foam_rings = np.sin(rad * 28.0) * 0.25 * np.clip(1.0 - rad, 0.0, 1.0)
np.random.seed(101)
churn_noise = 0.2 * np.sin(fuu * 22.0 + fvv * 18.0) + 0.15 * np.cos(fuu * 44.0 - fvv * 36.0)

foam_intensity = np.clip(foam_core * 0.85 + foam_rings + churn_noise * foam_core, 0.0, 1.0)
foam_alpha = np.clip(foam_intensity * 1.8 * np.clip(1.0 - rad * 1.1, 0.0, 1.0), 0.0, 1.0)
foam_alpha = np.power(foam_alpha, 1.2)

foam_img = np.zeros((fh, fw, 4), dtype=np.uint8)
foam_img[..., 0] = np.clip(225 + foam_intensity * 30, 0, 255).astype(np.uint8)
foam_img[..., 1] = np.clip(238 + foam_intensity * 17, 0, 255).astype(np.uint8)
foam_img[..., 2] = 255
foam_img[..., 3] = (foam_alpha * 220).astype(np.uint8)

foam_path = os.path.join(output_dir, "waterfall_foam.png")
Image.fromarray(foam_img, mode="RGBA").save(foam_path)
print(f"Saved: {foam_path}")
print("=== All photorealistic waterfall PBR textures generated successfully! ===")
