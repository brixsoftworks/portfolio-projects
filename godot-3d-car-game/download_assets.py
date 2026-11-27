import urllib.request
import os
import time

cars = [
    "race.glb",
    "race-future.glb",
    "sedan-sports.glb",
    "suv-luxury.glb",
    "police.glb",
    "taxi.glb",
    "wheel-racing.glb",
    "wheel-default.glb",
    "cone.glb",
    "cone-flat.glb",
    "debris-tire.glb",
    "debris-spoiler-a.glb"
]

city_props = [
    "building-type-a.glb",
    "building-type-c.glb",
    "building-type-f.glb",
    "tree-large.glb",
    "tree-small.glb",
    "planter.glb",
    "fence.glb"
]

racing_props = [
    "barrierRed.glb",
    "barrierWhite.glb",
    "barrierWall.glb",
    "billboard.glb",
    "grandStand.glb",
    "grandStandCovered.glb",
    "flagCheckers.glb",
    "lightPostLarge.glb",
    "lightColored.glb",
    "grass.glb"
]

print("Downloading vehicle & prop assets...")
base_car_url = "https://raw.githubusercontent.com/Arslan12216775/kenney_car-kit/master/Models/GLB%20format/"
for c in cars:
    dest = os.path.join("/home/mullainathan/godot_3d_car_game/assets/cars", c)
    if not os.path.exists(dest):
        url = base_car_url + c
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"Downloaded car asset: {c} ({os.path.getsize(dest)} bytes)")
        except Exception as e:
            print(f"Failed to download {c}: {e}")

print("Downloading city assets...")
base_city_url = "https://raw.githubusercontent.com/Arslan12216775/kenney_car-kit/master/Models/City/"
for cp in city_props:
    dest = os.path.join("/home/mullainathan/godot_3d_car_game/assets/props", cp)
    if not os.path.exists(dest):
        url = base_city_url + cp
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"Downloaded city prop: {cp} ({os.path.getsize(dest)} bytes)")
        except Exception as e:
            print(f"Failed to download {cp}: {e}")

print("Downloading racing track kit assets...")
base_racing_url = "https://raw.githubusercontent.com/JiayuanZhu/SpeedRun/master/assets/kenney_racing-kit/Models/GLTF%20format/"
for rp in racing_props:
    dest = os.path.join("/home/mullainathan/godot_3d_car_game/assets/track", rp)
    if not os.path.exists(dest):
        url = base_racing_url + rp
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"Downloaded track prop: {rp} ({os.path.getsize(dest)} bytes)")
        except Exception as e:
            print(f"Failed to download {rp}: {e}")

print("All asset downloads completed!")
