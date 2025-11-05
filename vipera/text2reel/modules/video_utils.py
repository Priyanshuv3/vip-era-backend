from moviepy.editor import ColorClip, concatenate_videoclips, AudioFileClip, TextClip, CompositeVideoClip, VideoFileClip
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.editor import *

import os
from .config import OUTPUT_DIR
from PIL import Image

# Compatibility patch for Pillow 10+
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

def merge_clips(clip_paths,output_path):
    video_clips = []
    for path in clip_paths:
        video_clips.append(VideoFileClip(path))
    final = concatenate_videoclips(video_clips)
    final_path = os.path.join(output_path, "final_reel.mp4")
    final.write_videofile(final_path, fps=24, codec="libx264")
    return final_path


def create_scene_video(image_path, text, audio_path, output_path):
    # Target portrait size (9:16)
    target_w, target_h = 720, 1280

    # Load image
    img_clip = ImageClip(image_path)

    # Aspect ratio adjustment (fit with background blur)
    img_aspect = img_clip.w / img_clip.h
    target_aspect = target_w / target_h

    if img_aspect > target_aspect:
        # Image too wide → crop sides
        new_width = int(img_clip.h * target_aspect)
        img_clip = img_clip.crop(
            x_center=img_clip.w / 2,
            width=new_width
        )
    else:
        # Image too tall → crop top-bottom
        new_height = int(img_clip.w / target_aspect)
        img_clip = img_clip.crop(
            y_center=img_clip.h / 2,
            height=new_height
        )

    # Resize to portrait size
    background = img_clip.resize((target_w, target_h)).set_duration(5)

    # Add text overlay
    txt_clip = TextClip(
        text,
        fontsize=40,
        color='white',
        size=(target_w, None),
        method='caption',
        align='center'
    ).set_position(('center', 'bottom')).set_duration(5)

    # Load audio
    audio = AudioFileClip(audio_path).subclip(0, 5)

    # Combine everything
    video = CompositeVideoClip([background, txt_clip]).set_audio(audio)
    video = video.fadein(0.5).fadeout(0.5)

    # Export
    video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')

    return output_path



