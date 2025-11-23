from gtts import gTTS
import os

def text_to_speech(scene_text, index, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"scene_{index}.mp3")

    tts = gTTS(text=scene_text, lang="en")
    tts.save(file_path)

    return file_path
