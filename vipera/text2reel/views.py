from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .modules.text_processing import split_text_into_scenes, summarize_scene
from .modules.prompt_builder import build_prompt
from .modules.audio_utils import text_to_speech
from .modules.video_utils import merge_clips, create_scene_video
from .modules.image_utils import generate_image
import os
from datetime import datetime
from moviepy.config import change_settings

# Ensure ImageMagick path is set before MoviePy loads
change_settings({"IMAGEMAGICK_BINARY": "magick"})


@api_view(["POST"])
def generate_reel(request):
    try:
        text = request.data.get("text", "").strip()
        if not text:
            return Response(
                {"error": "No text provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # === Create timestamped folder structure ===
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        timestamp = datetime.now().strftime("reel_%d%b%y_%I-%M%p")
        session_dir = os.path.join(BASE_DIR, "assets", timestamp)
        audio_dir = os.path.join(session_dir, "audio")
        scene_dir = os.path.join(session_dir, "scenes")
        output_path = os.path.join(session_dir, "final_reel.mp4")

        for d in [audio_dir, scene_dir]:
            os.makedirs(d, exist_ok=True)

        # ============================================
        scenes = split_text_into_scenes(text)
        clip_paths = []

        for i, scene in enumerate(scenes, start=1):
            summary = summarize_scene(scene)
            prompt = build_prompt(summary)
            print(f"[Scene {i}] Prompt: {prompt}")

            # Generate TTS audio
            audio_path = text_to_speech(summary, i, output_dir=audio_dir)

            # Generate AI image for the scene
            image_path = os.path.join(scene_dir, f"scene_{i}.png")
            generate_image(prompt, image_path)

            # Create cinematic scene clip
            output_clip_path = os.path.join(scene_dir, f"scene_{i}.mp4")
            clip_path = create_scene_video(image_path, summary, audio_path, output_clip_path)
            clip_paths.append(clip_path)

        # Merge all scenes into one reel
        final_video = merge_clips(clip_paths, session_dir)


        return Response({
            "message": "Cinematic reel generated successfully!",
            "session_folder": session_dir,
            "video_path": final_video
        })

    except Exception as e:
        print("❌ Error:", e)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
