import torch
from diffusers import StableDiffusionPipeline

def generate_image(prompt, output_path):
    """
    Generates a realistic AI image for a given prompt and saves it to disk.
    """
    print(f"[ImageGen] Generating image for prompt: {prompt}")
    
    model_id = "runwayml/stable-diffusion-v1-5"

    # Use half precision (float16) for GPU if available, else CPU-friendly setup
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch_dtype)
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

    image = pipe(prompt).images[0]
    image.save(output_path)
    
    print(f"[ImageGen] Image saved: {output_path}")
    return output_path


from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, AudioFileClip

def create_scene_video(image_path, text, audio_path, output_path):
    background = ImageClip(image_path).set_duration(5).resize(height=720)
    txt_clip = TextClip(
        text, fontsize=40, color='white', size=background.size, method='caption'
    ).set_position('center').set_duration(5)

    audio = AudioFileClip(audio_path)
    video = CompositeVideoClip([background, txt_clip]).set_audio(audio)
    video.write_videofile(output_path, fps=24)
