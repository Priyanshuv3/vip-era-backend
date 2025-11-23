import os
import torch
from diffusers import AutoPipelineForText2Image

MODEL_ID = "stabilityai/sd-turbo"
DEVICE = "cpu"

# Global pipe cache
pipe_cache = None

def load_pipe():
    global pipe_cache

    if pipe_cache is not None:
        return pipe_cache

    print("[ImageGen] Loading SD-Turbo on CPU...")

    pipe = AutoPipelineForText2Image.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float32   # CPU requires float32
    ).to(DEVICE)

    # Turbo models use very low steps, no slicing needed
    pipe_cache = pipe
    return pipe_cache


def generate_image(prompt, output_path):
    pipe = load_pipe()

    result = pipe(
        prompt,
        num_inference_steps=4,   # Turbo recommended steps: 1–4
        guidance_scale=0.0       # Turbo = guidance 0
    )

    img = result.images[0]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)

    return output_path
