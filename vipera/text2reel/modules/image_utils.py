import os
import requests
from decouple import config

STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"
API_KEY = config('STABILITY_API_KEY')

def generate_image(prompt: str, output_path: str):
    """
    Generate a cinematic AI image using Stability.ai API.
    """
    if not API_KEY:
        raise ValueError("⚠️ Missing Stability API key! Set STABILITY_API_KEY in .env")

    print(f"🎨 Generating image for prompt: {prompt}")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "image/*",  # ✅ FIXED — API expects this, not image/png
    }

    files = {
        "none": (None, ""),  # 👈 just a placeholder to make it multipart/form-data
    }

    data = {
        "prompt": prompt,
        "aspect_ratio": "9:16",
        "output_format": "png",
    }

    response = requests.post(
        STABILITY_API_URL,
        headers=headers,
        files=files,
        data=data
    )

    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Image saved: {output_path}")
        return output_path
    else:
        print("❌ Image generation failed:", response.text)
        raise Exception(f"Image generation failed ({response.status_code}): {response.text}")




# from diffusers import StableDiffusionPipeline
# import torch, os

# def generate_image(prompt, output_path):
#     model_id = "runwayml/stable-diffusion-v1-5"
#     pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
#     pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#     image = pipe(prompt).images[0]
#     image.save(output_path)
#     return output_path