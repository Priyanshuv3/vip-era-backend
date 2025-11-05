from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize
from .config import SCENE_COUNT_LIMIT

nltk.download("punkt", quiet=True)

def split_text_into_scenes(long_text: str):
    sentences = sent_tokenize(long_text)
    scenes, chunk = [], ""
    for s in sentences:
        if len(chunk) + len(s) < 180:
            chunk += " " + s
        else:
            scenes.append(chunk.strip())
            chunk = s
    if chunk:
        scenes.append(chunk.strip())
    return scenes[:SCENE_COUNT_LIMIT]


def summarize_scene(scene_text: str):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    result = summarizer(scene_text, max_length=60, min_length=20, do_sample=False)
    return result[0]["summary_text"]
