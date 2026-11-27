import re

# Read current build_lingabhairavi_temple.py
with open('/home/mullainathan/Games/IshaGodot/tools/build_lingabhairavi_temple.py', 'r') as f:
    orig_code = f.read()

# Let us verify the key function boundaries
assert 'def create_materials():' in orig_code
assert 'def build_interior_architecture(materials):' in orig_code
assert 'def build_devi_shrine(materials):' in orig_code
assert 'def build_interior_diya_matrix(materials):' in orig_code
assert 'def setup_architectural_lighting():' in orig_code
assert 'def setup_cameras():' in orig_code
assert 'def render_showcase(cameras):' in orig_code
assert 'def export_assets():' in orig_code

print("Original script loaded successfully, size:", len(orig_code))
