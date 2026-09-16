import argparse
import hashlib
import json
import os
import re
import sys

import torch
from diffusers import StableDiffusionPipeline

MODEL = "stabilityai/sd-turbo"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS = "/tmp/opencode/sd_prompts.json"
SRC_TS = os.path.join(ROOT, "src", "data", "festivals.ts")
DEST = os.path.join(ROOT, "public", "images", "festivals")


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate festival logos with sd-turbo.")
    parser.add_argument("--limit", type=int, default=0, help="only first N (0 = all)")
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--seed-base", type=int, default=42)
    args = parser.parse_args()

    prompts = json.load(open(PROMPTS))
    content = open(SRC_TS).read()
    names = list(dict.fromkeys(re.findall(r'M\("([^"]+)"', content)))
    if args.limit:
        names = names[: args.limit]
    print(f"target: {len(names)} festivals")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    print(f"[1/3] Loading {MODEL} on {device} ...")

    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL,
        torch_dtype=dtype,
        safety_checker=None,
        requires_safety_checker=False,
    )
    pipe = pipe.to(device)
    if device == "cuda":
        pipe.enable_attention_slicing()

    os.makedirs(DEST, exist_ok=True)
    ok = 0
    for name in names:
        slug = slugify(name)
        out_path = os.path.join(DEST, f"{slug}.jpg")
        prompt = prompts.get(name, {}).get("prompt", name)
        seed = args.seed_base + int(hashlib.md5(slug.encode()).hexdigest(), 16) % 1_000_000
        generator = torch.Generator(device=device).manual_seed(seed)
        try:
            image = pipe(
                prompt=prompt,
                num_inference_steps=args.steps,
                guidance_scale=0.0,
                height=args.size,
                width=args.size,
                generator=generator,
            ).images[0]
            image.convert("RGB").save(out_path, "JPEG", quality=92)
            ok += 1
            print(f"[ok] {slug}")
        except Exception as e:
            print(f"[fail] {slug}: {e}")
    print(f"[3/3] generated {ok}/{len(names)} -> {DEST}")


if __name__ == "__main__":
    sys.exit(main())
