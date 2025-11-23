import re

# ------------------------------
# 1. TOPIC KEYWORDS (Auto Detection)
# ------------------------------

TOPIC_MAP = {
    "networking": [
        "dns", "resolver", "ip address", "domain", "server",
        "tcp", "udp", "packet", "http", "https", "latency", "routing"
    ],
    "video_tech": [
        "bitrate", "codec", "h.264", "fps", "resolution", 
        "compression", "audio", "aac", "wav", "frame", "pixel"
    ],
    "biology": [
        "digestion", "enzyme", "stomach", "cell", "organ",
        "blood", "heart", "brain", "neuron", "intestine"
    ],
    "ai_ml": [
        "neural network", "transformer", "ai model", "dataset",
        "machine learning", "attention", "token", "embedding"
    ],
    "computer_science": [
        "processor", "cpu", "memory", "ram", "algorithm",
        "database", "index", "query", "data structure"
    ],
    "space": [
        "planet", "galaxy", "universe", "black hole",
        "astronomy", "nebula", "cosmic", "asteroid"
    ],
    "finance": [
        "market", "stock", "investment", "trading",
        "inflation", "economy", "finance", "tax", "gdp"
    ],
    "psychology": [
        "mindset", "behavior", "emotion", "memory",
        "motivation", "anxiety", "stress"
    ],
    "history": [
        "ancient", "civilization", "empire", "war",
        "battle", "kingdom", "historical"
    ]
}

# ------------------------------
# 2. PROMPT TEMPLATES
# ------------------------------

TEMPLATES = {
    "networking": (
        "Cinematic 3D visualization of {text}, glowing blue cyber lines, "
        "digital data flow, futuristic neon grids, packet movement, "
        "sharp edges, high-tech lighting, 4K detail."
    ),
    "video_tech": (
        "Cinematic digital illustration of {text}, pixel grids, frame sequences, "
        "floating bitrate graphs, neon compression effects, motion blur elements, "
        "high realism, 4K studio lighting."
    ),
    "biology": (
        "Highly detailed medical 3D illustration of {text}, anatomical cutaway, "
        "realistic organs, biological textures, soft clinical lighting, "
        "educational diagram style, 4K resolution."
    ),
    "ai_ml": (
        "Futuristic neural network visualization of {text}, glowing nodes, "
        "attention pathways, digital brain aesthetic, sci-fi lighting, "
        "complex patterns, 4K clarity."
    ),
    "computer_science": (
        "Cinematic tech diagram of {text}, processor circuits, memory grids, "
        "electric signals, neon highlights, crisp technical aesthetic, "
        "hyper-detailed, 4K render."
    ),
    "space": (
        "Epic cosmic scene of {text}, galaxies, starfields, nebula clouds, "
        "deep space glow, cinematic astrophysics style, 4K illustration."
    ),
    "finance": (
        "Clean infographic-style cinematic illustration of {text}, stock charts, "
        "luxury gold-blue palette, glowing trend lines, modern business aesthetic, "
        "4K resolution."
    ),
    "psychology": (
        "Emotional cinematic illustration of {text}, human mind symbolism, "
        "expressive abstract shapes, soft lighting, deep colors, 4K art style."
    ),
    "history": (
        "Dramatic historical illustration of {text}, ancient textures, old parchment "
        "colors, realistic artifacts, cinematic lighting, 4K detail."
    ),
    "generic": (
        "Cinematic illustration of {text}, dramatic lighting, realistic textures, "
        "4K ultra-detailed artwork."
    )
}

# ------------------------------
# 3. TOPIC DETECTION FUNCTION
# ------------------------------

def detect_topic(text: str) -> str:
    text_lower = text.lower()

    for topic, keywords in TOPIC_MAP.items():
        for word in keywords:
            if word in text_lower:
                return topic

    return "generic"

# ------------------------------
# 4. BUILD PROMPT (MAIN FUNCTION)
# ------------------------------

def build_prompt(scene_text: str) -> str:
    topic = detect_topic(scene_text)
    template = TEMPLATES.get(topic, TEMPLATES["generic"])
    return template.format(text=scene_text)
