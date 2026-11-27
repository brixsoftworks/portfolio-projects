"""
Generates high-fidelity PBR textures for the Sarva Dharma Sthambha at Dhyanalinga, Isha Yoga Center.
Creates:
- assets/textures/sarva_dharma_sthambha_diff.png (Albedo with white granite grain & carved relief)
- assets/textures/sarva_dharma_sthambha_nor.png (Chiseled normal map with carved depth)
- assets/textures/sarva_dharma_sthambha_rough.png (Micro-roughness variations in carved vs polished stone)
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TEXTURES_DIR = "/home/mullainathan/Games/IshaGodot/assets/textures"
os.makedirs(TEXTURES_DIR, exist_ok=True)

WIDTH = 2048
HEIGHT = 2048

# Create blank heightmap for carved reliefs (128 = neutral surface, <128 = carved in, >128 = embossed)
height_img = Image.new("L", (WIDTH, HEIGHT), 128)
draw = ImageDraw.Draw(height_img)

# Layout: 4 columns for 4 sides of the pillar, each 512px wide
# Column 0 (x: 0..512): Face 1 (Chakras, Ida/Pingala Serpents, Sun)
# Column 1 (x: 512..1024): Face 2 (Hinduism Om, Islam Crescent/Star, Christianity Cross)
# Column 2 (x: 1024..1536): Face 3 (Buddhism Wheel, Jainism Ahimsa, Taoism Yin-Yang)
# Column 3 (x: 1536..2048): Face 4 (Zoroastrianism Fire, Judaism Star, Shinto Torii)

COL_W = 512
MARGIN_X = 64

def draw_ring(drw, cx, cy, r_outer, r_inner, val, stroke=0):
    for r in range(int(r_inner), int(r_outer) + 1):
        drw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=val, width=stroke if stroke > 0 else 1)

def draw_lotus(drw, cx, cy, radius, num_petals, val):
    # Draw central bindu
    drw.ellipse([cx - radius*0.25, cy - radius*0.25, cx + radius*0.25, cy + radius*0.25], fill=val)
    # Draw petals
    for i in range(num_petals):
        angle = 2 * math.pi * i / num_petals
        px = cx + radius * 0.7 * math.cos(angle)
        py = cy + radius * 0.7 * math.sin(angle)
        pr = radius * 0.35
        drw.ellipse([px - pr, py - pr, px + pr, py + pr], outline=val, width=4)

# ==========================================
# COLUMN 0: CHAKRAS & IDA/PINGALA SERPENTS
# ==========================================
c0_cx = 256

# Top: Radiant Sun & Falling Leaves (y: 80..240)
sun_cy = 160
sun_r = 50
draw.ellipse([c0_cx - sun_r, sun_cy - sun_r, c0_cx + sun_r, sun_cy + sun_r], fill=180, outline=230, width=5)
# Sun rays
for a_deg in range(0, 360, 20):
    rad = math.radians(a_deg)
    x1 = c0_cx + (sun_r + 5) * math.cos(rad)
    y1 = sun_cy + (sun_r + 5) * math.sin(rad)
    x2 = c0_cx + (sun_r + 28) * math.cos(rad)
    y2 = sun_cy + (sun_r + 28) * math.sin(rad)
    draw.line([x1, y1, x2, y2], fill=220, width=4)

# 7 Chakras ascending vertically (y: 350 to 1850)
chakra_petals = [16, 2, 16, 12, 10, 6, 4] # Sahasrara down to Muladhara
chakra_names = ["Sahasrara", "Ajna", "Vishuddhi", "Anahata", "Manipura", "Swadhisthana", "Muladhara"]
chakra_y = np.linspace(340, 1820, 7)

# Draw Ida & Pingala entwined serpent sine waves
pts_ida = []
pts_pingala = []
for y in range(300, 1880, 5):
    t = (y - 300) / 1580.0
    phase = t * 6 * math.pi
    amp = 90 * math.sin(math.pi * t) # widen in center
    pts_ida.append((c0_cx - amp * math.sin(phase), y))
    pts_pingala.append((c0_cx + amp * math.sin(phase), y))

for i in range(len(pts_ida) - 1):
    draw.line([pts_ida[i], pts_ida[i+1]], fill=190, width=6)
    draw.line([pts_pingala[i], pts_pingala[i+1]], fill=190, width=6)

for idx, cy in enumerate(chakra_y):
    r = 38
    np_petals = chakra_petals[idx]
    draw_lotus(draw, c0_cx, cy, r, np_petals, 220)
    # Circular aura around each chakra
    draw.ellipse([c0_cx - r - 8, cy - r - 8, c0_cx + r + 8, cy + r + 8], outline=200, width=3)

# ==========================================
# COLUMN 1: HINDUISM, ISLAM, CHRISTIANITY
# ==========================================
c1_cx = 512 + 256

# 1. Hinduism: OM and Trishula (y: 200..600)
# Trishul emblem
ty = 320
draw.line([c1_cx, ty - 80, c1_cx, ty + 90], fill=220, width=8) # central prong
draw.line([c1_cx - 50, ty - 50, c1_cx - 50, ty + 10], fill=210, width=6) # left prong
draw.line([c1_cx + 50, ty - 50, c1_cx + 50, ty + 10], fill=210, width=6) # right prong
draw.arc([c1_cx - 50, ty - 10, c1_cx + 50, ty + 40], start=0, end=180, fill=210, width=6) # cradle
draw.ellipse([c1_cx - 25, ty + 15, c1_cx + 25, ty + 35], fill=200) # Damaru band
# OM Crescent and Dot
draw.ellipse([c1_cx - 10, ty - 110, c1_cx + 10, ty - 90], fill=230) # Bindu
draw.arc([c1_cx - 30, ty - 100, c1_cx + 30, ty - 70], start=0, end=180, fill=220, width=5) # Chandrabindu

# 2. Islam: Crescent & Star (y: 850..1250)
iy = 1050
# Crescent
draw.ellipse([c1_cx - 70, iy - 70, c1_cx + 70, iy + 70], fill=220)
draw.ellipse([c1_cx - 45, iy - 65, c1_cx + 75, iy + 65], fill=128) # cut out inner circle
# 5-pointed star
star_cx = c1_cx + 25
star_cy = iy - 10
star_pts = []
for k in range(10):
    r_k = 32 if k % 2 == 0 else 14
    ang = math.radians(k * 36 - 90)
    star_pts.append((star_cx + r_k * math.cos(ang), star_cy + r_k * math.sin(ang)))
draw.polygon(star_pts, fill=225)

# 3. Christianity: Latin Cross with Radiant Halo (y: 1450..1850)
cy = 1650
# Halo ring
draw.ellipse([c1_cx - 75, cy - 85, c1_cx + 75, cy + 65], outline=190, width=5)
# Vertical cross bar
draw.rounded_rectangle([c1_cx - 14, cy - 110, c1_cx + 14, cy + 90], radius=4, fill=225)
# Horizontal cross bar
draw.rounded_rectangle([c1_cx - 70, cy - 65, c1_cx + 70, cy - 37], radius=4, fill=225)

# ==========================================
# COLUMN 2: BUDDHISM, JAINISM, TAOISM
# ==========================================
c2_cx = 1024 + 256

# 1. Buddhism: Dharmachakra Wheel of Law (y: 200..600)
by = 380
bw_r = 75
draw.ellipse([c2_cx - bw_r, by - bw_r, c2_cx + bw_r, by + bw_r], outline=220, width=10)
draw.ellipse([c2_cx - 24, by - 24, c2_cx + 24, by + 24], fill=210)
# 8 Spokes
for k in range(8):
    ang = math.radians(k * 45)
    x1 = c2_cx + 22 * math.cos(ang)
    y1 = by + 22 * math.sin(ang)
    x2 = c2_cx + (bw_r - 5) * math.cos(ang)
    y2 = by + (bw_r - 5) * math.sin(ang)
    draw.line([x1, y1, x2, y2], fill=215, width=6)

# 2. Jainism: Ahimsa Palm & Wheel (y: 850..1250)
jy = 1050
# Upright palm silhouette
draw.rounded_rectangle([c2_cx - 36, jy - 30, c2_cx + 36, jy + 70], radius=14, fill=210)
# Fingers
for f_idx, fx in enumerate([-30, -10, 10, 30]):
    f_len = 55 if abs(f_idx - 1.5) < 1.0 else 44
    draw.rounded_rectangle([c2_cx + fx - 8, jy - 30 - f_len, c2_cx + fx + 8, jy - 20], radius=6, fill=210)
# Thumb
draw.rounded_rectangle([c2_cx - 48, jy - 15, c2_cx - 30, jy + 30], radius=6, fill=210)
# Ahimsa Wheel in center of palm
draw.ellipse([c2_cx - 18, jy + 10, c2_cx + 18, jy + 46], outline=128, width=3)
draw.ellipse([c2_cx - 6, jy + 22, c2_cx + 6, jy + 34], fill=128)

# 3. Taoism: Taijitu Yin-Yang (y: 1450..1850)
ty2 = 1650
ty_r = 75
draw.ellipse([c2_cx - ty_r, ty2 - ty_r, c2_cx + ty_r, ty2 + ty_r], outline=220, width=6)
# Half white fill
draw.pieslice([c2_cx - ty_r, ty2 - ty_r, c2_cx + ty_r, ty2 + ty_r], start=90, end=270, fill=215)
# S-curve halves
draw.ellipse([c2_cx - ty_r*0.5, ty2 - ty_r, c2_cx + ty_r*0.5, ty2], fill=215)
draw.ellipse([c2_cx - ty_r*0.5, ty2, c2_cx + ty_r*0.5, ty2 + ty_r], fill=128)
# Small dots
draw.ellipse([c2_cx - 10, ty2 - ty_r*0.5 - 10, c2_cx + 10, ty2 - ty_r*0.5 + 10], fill=128)
draw.ellipse([c2_cx - 10, ty2 + ty_r*0.5 - 10, c2_cx + 10, ty2 + ty_r*0.5 + 10], fill=215)

# ==========================================
# COLUMN 3: ZOROASTRIANISM, JUDAISM, SHINTO
# ==========================================
c3_cx = 1536 + 256

# 1. Zoroastrianism: Sacred Fire Altar (Atesh) (y: 200..600)
zy = 380
# Pedestal urn
draw.polygon([(c3_cx - 45, zy + 60), (c3_cx + 45, zy + 60), (c3_cx + 25, zy + 15), (c3_cx - 25, zy + 15)], fill=210)
draw.polygon([(c3_cx - 35, zy + 15), (c3_cx + 35, zy + 15), (c3_cx + 50, zy - 10), (c3_cx - 50, zy - 10)], fill=220)
# Sacred Flames rising
draw.polygon([(c3_cx, zy - 85), (c3_cx - 25, zy - 30), (c3_cx - 10, zy - 10), (c3_cx + 10, zy - 10), (c3_cx + 25, zy - 30)], fill=225)
draw.polygon([(c3_cx - 20, zy - 70), (c3_cx - 35, zy - 25), (c3_cx - 20, zy - 15)], fill=200)
draw.polygon([(c3_cx + 20, zy - 70), (c3_cx + 35, zy - 25), (c3_cx + 20, zy - 15)], fill=200)

# 2. Judaism: Star of David (Magen David) (y: 850..1250)
my = 1050
mr = 70
# Triangle 1 (pointing up)
t1 = []
for k in [0, 1, 2]:
    ang = math.radians(k * 120 - 90)
    t1.append((c3_cx + mr * math.cos(ang), my + mr * math.sin(ang)))
draw.polygon(t1, outline=220, width=7)

# Triangle 2 (pointing down)
t2 = []
for k in [0, 1, 2]:
    ang = math.radians(k * 120 + 90)
    t2.append((c3_cx + mr * math.cos(ang), my + mr * math.sin(ang)))
draw.polygon(t2, outline=220, width=7)

# 3. Shinto: Torii Sacred Shrine Gate (y: 1450..1850)
sy = 1650
# Two vertical pillars
draw.rounded_rectangle([c3_cx - 50, sy - 50, c3_cx - 36, sy + 70], radius=3, fill=220)
draw.rounded_rectangle([c3_cx + 36, sy - 50, c3_cx + 50, sy + 70], radius=3, fill=220)
# Top curved lintel (Kasagi)
draw.polygon([(c3_cx - 75, sy - 65), (c3_cx + 75, sy - 65), (c3_cx + 70, sy - 50), (c3_cx - 70, sy - 50)], fill=225)
# Second straight lintel (Shimaki / Nuki)
draw.rounded_rectangle([c3_cx - 60, sy - 38, c3_cx + 60, sy - 26], radius=2, fill=215)
# Center strut (Gakuzuka)
draw.rounded_rectangle([c3_cx - 6, sy - 50, c3_cx + 6, sy - 38], radius=1, fill=220)

# Add decorative column borders dividing the 4 faces
for div_x in [512, 1024, 1536]:
    draw.line([(div_x, 0), (div_x, HEIGHT)], fill=160, width=4)

# Apply gentle blur to smooth edges for organic hand-chiseled stone relief
height_smooth = height_img.filter(ImageFilter.GaussianBlur(radius=2.5))

# Load or generate white granite background
granite_path = os.path.join(TEXTURES_DIR, "white_granite_diff_2k.png")
if os.path.exists(granite_path):
    granite_bg = Image.open(granite_path).convert("RGB").resize((WIDTH, HEIGHT))
else:
    granite_bg = Image.new("RGB", (WIDTH, HEIGHT), (220, 220, 218))

# Compose Albedo: White granite with subtle darkened carved bevels
h_arr = np.array(height_smooth, dtype=np.float32) / 255.0
bg_arr = np.array(granite_bg, dtype=np.float32)

# Relief shading factor: 1.0 at 0.5 (128), brighter at peaks, slightly shadowed in crevices
relief_factor = (h_arr - 0.5) * 0.45 + 1.0
albedo_arr = np.clip(bg_arr * relief_factor[:, :, np.newaxis], 0, 255).astype(np.uint8)
albedo_img = Image.fromarray(albedo_arr)
albedo_out = os.path.join(TEXTURES_DIR, "sarva_dharma_sthambha_diff.png")
albedo_img.save(albedo_out)
print(f"Saved: {albedo_out}")

# Compute Sobel Normal Map from Heightmap
# Height gradient
gy, gx = np.gradient(h_arr * 20.0) # height scale
norm_z = np.ones_like(gx)
length = np.sqrt(gx*gx + gy*gy + norm_z*norm_z)
nx = (-gx / length) * 0.5 + 0.5
ny = (gy / length) * 0.5 + 0.5 # OpenGL normal format (+Y up)
nz = (norm_z / length) * 0.5 + 0.5

normal_arr = (np.stack([nx, ny, nz], axis=2) * 255).clip(0, 255).astype(np.uint8)
normal_img = Image.fromarray(normal_arr)
normal_out = os.path.join(TEXTURES_DIR, "sarva_dharma_sthambha_nor.png")
normal_img.save(normal_out)
print(f"Saved: {normal_out}")

# Roughness map: Carved relief has slightly higher roughness (chiseled matte ~0.65) than polished granite (~0.45)
rough_arr = (0.45 + np.abs(h_arr - 0.5) * 0.50).clip(0, 1.0)
rough_img = Image.fromarray((rough_arr * 255).astype(np.uint8))
rough_out = os.path.join(TEXTURES_DIR, "sarva_dharma_sthambha_rough.png")
rough_img.save(rough_out)
print(f"Saved: {rough_out}")
print("Sarva Dharma Sthambha PBR texture suite generated successfully!")
