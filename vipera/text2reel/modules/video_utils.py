from moviepy.editor import (
    ImageClip,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    VideoFileClip,
    concatenate_videoclips,
    CompositeAudioClip,
    vfx,
)
import os
from .config import OUTPUT_DIR
from PIL import Image

# Pillow 10+ compatibility
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


# -------------------------------------------------------
# MERGE CLIPS (with smooth crossfade transitions)
# -------------------------------------------------------

def merge_clips(clip_paths, output_path):
    clips = [VideoFileClip(c) for c in clip_paths]

    # --- IMPORTANT FIX ---
    if len(clips) == 1:
        # no merge needed, just save/return the single clip
        final_path = os.path.join(output_path, "final_reel.mp4")
        clips[0].write_videofile(final_path, fps=24, codec='libx264', audio_codec='aac')
        return final_path

    # If more than 1 clip → apply transitions
    final_video = concatenate_videoclips(clips, transition=0.5, method="compose")

    # Correct audio merging
    audio_tracks = []
    current_time = 0
    for c in clips:
        audio_tracks.append(c.audio.set_start(current_time))
        current_time += c.duration

    final_audio = CompositeAudioClip(audio_tracks)

    final_video = final_video.set_audio(final_audio)

    final_path = os.path.join(output_path, "final_reel.mp4")
    final_video.write_videofile(final_path, fps=24, codec='libx264', audio_codec='aac')
    
    return final_path



# -------------------------------------------------------
# CREATE INDIVIDUAL SCENE VIDEO (stable)
# -------------------------------------------------------

def create_scene_video(image_path, text, audio_path, output_path):
    # 9:16 portrait
    target_w, target_h = 720, 1280

    # Load image
    img_clip = ImageClip(image_path)

    # Aspect ratio crop
    img_aspect = img_clip.w / img_clip.h
    target_aspect = target_w / target_h

    if img_aspect > target_aspect:
        new_width = int(img_clip.h * target_aspect)
        img_clip = img_clip.crop(
            x_center=img_clip.w / 2,
            width=new_width
        )
    else:
        new_height = int(img_clip.w / target_aspect)
        img_clip = img_clip.crop(
            y_center=img_clip.h / 2,
            height=new_height
        )

    # Load audio safely
    try:
        audio = AudioFileClip(audio_path)
        scene_duration = audio.duration
    except Exception as e:
        print("⚠️ Audio failed to load:", e)
        audio = None
        scene_duration = 5.0

    # -------- FIXED KEN BURNS EFFECT ----------
    # Instead of scaling factor, use resize(lambda t)
    def zoom_in(t):
        # 1.00 → 1.07 over full clip
        factor = 1.00 + 0.07 * (t / scene_duration)
        return factor

    background = (
        img_clip
        .resize((target_w, target_h))
        .resize(zoom_in)
        .set_duration(scene_duration)
    )

    # Text overlay
    txt_clip = (
        TextClip(
            text,
            fontsize=40,
            color="white",
            size=(target_w - 100, None),
            method="caption",
            align="center"
        )
        .set_position(("center", "bottom"))
        .set_duration(scene_duration)
        .fadein(0.3)
        .fadeout(0.3)
    )

    # Combine video + audio
    final_clip = CompositeVideoClip([background, txt_clip])
    if audio:
        final_clip = final_clip.set_audio(audio)

    # Export
    final_clip.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    return output_path
