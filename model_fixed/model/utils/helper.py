import re


_ARABIC_RE   = re.compile(r"[\u0600-\u06FF]")


def is_arabic(text: str) -> bool:
    return bool(_ARABIC_RE.search(text))


def lang(text: str) -> str:
    return "ar" if is_arabic(text) else "en"

