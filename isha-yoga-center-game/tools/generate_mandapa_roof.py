import numpy as np
import trimesh
from PIL import Image
import os

def create_mandapa_roof():
    # Parameters
    slab_thick = 0.30       # User requirement: 0.3 m thick
    half_x = 5.80           # Half-width (X = 11.6m total)
    half_z = 5.30           # Half-depth (Z = 10.6m total)
    slider_width = 0.80     # Width of perimeter edge slider
    inner_half_x = half_x - slider_width  # 5.0m
    inner_half_z = half_z - slider_width  # 4.5m
    slider_drop = 0.14      # Slider drops from 0.30 to 0.16m
    fascia_y = slab_thick - slider_drop   # 0.16m
    dome_radius = 0.92      # User requirement: radius of the hole under (0.92m)
    dome_height = 0.68      # Proportional height of the hemispherical dome

    print(f"Generating Mandapa Roof: slab={half_x*2}x{half_z*2}m, thickness={slab_thick}m")
    print(f"Edge slider width={slider_width}m, drop={slider_drop}m, fascia={fascia_y}m")
    print(f"Central dome radius={dome_radius}m, height={dome_height}m")

if __name__ == "__main__":
    create_mandapa_roof()
