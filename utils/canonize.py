import re


def canonize(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())
