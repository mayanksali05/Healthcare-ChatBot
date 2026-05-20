import re


def clean_text(text):

    # Fix joined words like "Bananasare"
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # Remove multiple spaces/newlines
    text = re.sub(r"\s+", " ", text)

    # Remove weird characters
    text = re.sub(r"[^\w\s\.,:%\-\(\)]", "", text)

    # Remove promotional junk
    junk_phrases = [
        "Join Bezzy",
        "Connect with us",
        "ADVERTISEMENT"
    ]

    for phrase in junk_phrases:
        text = text.replace(phrase, "")

    # Fix common contractions
    contractions = {
        r"\bTheyre\b": "They're",
        r"\btheyre\b": "they're",
        r"\bYoure\b": "You're",
        r"\byoure\b": "you're",
        r"\bDont\b": "Don't",
        r"\bdont\b": "don't",
        r"\bCant\b": "Can't",
        r"\bcant\b": "can't",
        r"\bIm\b": "I'm",
        r"\bim\b": "I'm"
    }

    for pattern, replacement in contractions.items():
        text = re.sub(pattern, replacement, text)

    return text.strip()