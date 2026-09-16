import argparse
import os
import sys

import torch
from diffusers import StableDiffusionPipeline

MODEL = "stabilityai/sd-turbo"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an image with Stable Diffusion (sd-turbo).")
    parser.add_argument("--prompt", default="a premium Diwali diya set on a clean white background, e-commerce product photography, studio lighting, high detail")
    parser.add_argument("--out", default="sample.png", help="Output filename inside image-gen/output/")
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

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
    pipe.set_progress_bar_config(disable=False)

    if device == "cuda":
        pipe.enable_attention_slicing()

    generator = torch.Generator(device=device).manual_seed(args.seed)
    print(f"[2/3] Generating ({args.steps} steps, {args.size}x{args.size}) ...")

    image = pipe(
        prompt=args.prompt,
        num_inference_steps=args.steps,
        guidance_scale=0.0,
        height=args.size,
        width=args.size,
        generator=generator,
    ).images[0]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, args.out)
    image.save(out_path)
    print(f"[3/3] Saved: {out_path}")


if __name__ == "__main__":
    sys.exit(main())
