from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize

nltk.download("punkt", quiet=True)

def split_text_into_scenes(text):
    scenes = []
    chunk = ""

    for s in sent_tokenize(text):
        s = s.strip()
        
        if len(s) > 220:
            # Break long sentence into smaller chunks
            parts = [s[i:i+220] for i in range(0, len(s), 220)]
            scenes.extend(parts)
        else:
            scenes.append(s)
    
    return scenes


def summarize_scene(scene_text: str):
    summarizer = pipeline("summarization", model="t5-small")
    result = summarizer(scene_text, max_length=40, min_length=10, do_sample=False)
    return result[0]["summary_text"]


