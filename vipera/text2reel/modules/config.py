import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUTPUT_DIR = os.path.join(BASE_DIR, "assets/output/")
AUDIO_DIR = os.path.join(BASE_DIR, "assets/audio/")
SCENE_DIR = os.path.join(BASE_DIR, "assets/scenes/")

for d in [OUTPUT_DIR, AUDIO_DIR, SCENE_DIR]:
    os.makedirs(d, exist_ok=True)

SCENE_COUNT_LIMIT = 5
