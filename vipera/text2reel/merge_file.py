import os
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

# Your session
session_dir = r"E:\GithubRepo\VipEra\vipera-backend\vipera\assets\reel_23Nov25_05-16PM"
scene_dir = os.path.join(session_dir, "scenes")
audio_dir = os.path.join(session_dir, "audio")

def generate_final_reel():
    print("🔍 Loading scene videos...")
    scene_files = sorted(
        [
            os.path.join(scene_dir, f)
            for f in os.listdir(scene_dir)
            if f.startswith("scene_") and f.endswith(".mp4") and not f.startswith("fixed_")
        ],
        key=lambda x: int(os.path.basename(x).replace("scene_", "").replace(".mp4", ""))
    )

    print("🔍 Loading audio tracks...")
    audio_files = sorted(
        [
            os.path.join(audio_dir, f)
            for f in os.listdir(audio_dir)
            if f.startswith("scene_") and f.endswith(".mp3")
        ],
        key=lambda x: int(os.path.basename(x).replace("scene_", "").replace(".mp3", ""))
    )

    # Safety check
    if len(scene_files) != len(audio_files):
        print("❌ ERROR: Mismatch between number of videos and audio files!")
        print("Videos:", len(scene_files), "Audios:", len(audio_files))
        return

    print("🎬 Preparing video clips...")
    videos = [VideoFileClip(v).without_audio() for v in scene_files]

    print("🎧 Preparing audio clips...")
    audios = [AudioFileClip(a) for a in audio_files]

    print("🔗 Merging video sequence...")
    final_video = concatenate_videoclips(videos, method="compose")

    print("🔗 Merging audio sequence...")
    final_audio = concatenate_audioclips(audios)

    print("🎞 Attaching final audio to video...")
    final = final_video.set_audio(final_audio)

    output_path = os.path.join(session_dir, "FINAL_REEL_FIXED.mp4")

    print("💾 Exporting final reel...")
    final.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

    print("\n✅ DONE! Final reel saved at:\n", output_path)
    return output_path


if __name__ == "__main__":
    generate_final_reel()
