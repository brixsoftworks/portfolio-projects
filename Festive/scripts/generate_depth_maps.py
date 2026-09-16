import os
import glob
from transformers import pipeline
from PIL import Image
import torch

# Initialize the pipeline
print("Loading model...")
pipe = pipeline(task="depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=0 if torch.cuda.is_available() else -1)
print("Model loaded.")

input_dir = "public/images/festivals"
# Get all jpg and png files
image_paths = glob.glob(os.path.join(input_dir, "*.jpg")) + glob.glob(os.path.join(input_dir, "*.png"))

for path in image_paths:
    if "_depth" in path:
        continue # Skip already generated depth maps

    basename = os.path.basename(path)
    name, ext = os.path.splitext(basename)
    out_path = os.path.join(input_dir, f"{name}_depth{ext}")

    if os.path.exists(out_path):
        print(f"Skipping {basename}, depth map already exists.")
        continue

    print(f"Processing {basename}...")
    try:
        image = Image.open(path).convert('RGB')
        result = pipe(image)
        depth_image = result["depth"]
        depth_image.save(out_path)
        print(f"Saved depth map to {out_path}")
    except Exception as e:
        print(f"Error processing {path}: {e}")

print("Done.")
