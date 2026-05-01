import re
import spacy
from pathlib import Path

from utils.gemini_client import get_suggestions
from utils.constants import (
    SECTION_HEADERS,
    CRITICAL_SECTIONS,
    OPTIONAL_SECTIONS,
    MISSING_SECTION_MESSAGES,
    NER_LABELS,
)
from utils.helper import is_arabic,lang

_FINETUNED_PATH = Path(__file__).parent / "fine_tuning" / "model_output"
_SKILLS_PATTERN = re.compile(
    r"(skills|technologies|tools|المهارات|تقنيات|أدوات)[:\-\s]+(.+?)(\n\n|\Z)",
    re.IGNORECASE | re.DOTALL,
)

_EMAIL_RE    = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}")
_PHONE_RE    = re.compile(r"(\+?\d[\d\s\-().]{7,15}\d)")
_LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)
_GITHUB_RE   = re.compile(r"github\.com/[\w\-]+", re.IGNORECASE)


def _load_model() -> spacy.language.Language:
    if _FINETUNED_PATH.exists():
        try:
            return spacy.load(str(_FINETUNED_PATH))
        except Exception:
            pass
    try:
        return spacy.load("xx_ent_wiki_sm")
    except OSError:
        raise RuntimeError("Run: python -m spacy download xx_ent_wiki_sm")


_nlp = _load_model()


# ── extractors ────────────────────────────────────────────────────────────────

def extract_sections(cv_text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = "header"
    buffer:  list[str] = []

    for line in cv_text.splitlines():
        stripped = line.strip()
        matched  = None

        if stripped and len(stripped) < 60:
            for name, pattern in SECTION_HEADERS.items():
                if re.search(pattern, stripped, re.IGNORECASE):
                    matched = name
                    break

        if matched:
            if buffer:
                sections[current] = "\n".join(buffer).strip()
            current = matched
            buffer  = []
        else:
            buffer.append(stripped)

    if buffer:
        sections[current] = "\n".join(buffer).strip()

    return sections


def extract_skills(cv_text: str) -> list[str]:
    skills: list[str] = []

    m = _SKILLS_PATTERN.search(cv_text)
    if m:
        skills = [s.strip() for s in re.split(r"[,•|\n/]+", m.group(2))
                  if 2 < len(s.strip()) < 40]

    for ent in _nlp(cv_text[:5000]).ents:
        if ent.label_ in ("SKILLS", "ORG", "PRODUCT") and len(ent.text) < 30:
            token = ent.text.strip()
            if token not in skills:
                skills.append(token)

    return list(dict.fromkeys(skills))


def extract_contact(cv_text: str) -> dict[str, str]:
    info: dict[str, str] = {}

    for key, pattern in [
        ("email",    _EMAIL_RE),
        ("phone",    _PHONE_RE),
    ]:
        m = pattern.search(cv_text)
        if m:
            info[key] = m.group().strip()

    for key, pattern in [
        ("linkedin", _LINKEDIN_RE),
        ("github",   _GITHUB_RE),
    ]:
        m = pattern.search(cv_text)
        if m:
            info[key] = "https://" + m.group()

    return info


def extract_entities(cv_text: str) -> list[dict]:
    doc = _nlp(cv_text[:5000])
    return [
        {"text": ent.text, "label": ent.label_}
        for ent in doc.ents
        if ent.label_ in NER_LABELS
    ][:20]


# ── suggestions ───────────────────────────────────────────────────────────────

def _rule_based_suggestions(cv_text: str, sections: dict, contact: dict) -> list[str]:
    lang     = lang(cv_text)
    messages = MISSING_SECTION_MESSAGES[lang]
    tips:    list[str] = []
    found    = set(sections)

    for sec in CRITICAL_SECTIONS + OPTIONAL_SECTIONS:
        if sec not in found:
            tips.append(messages[sec])

    if "email" not in contact:
        tips.append(messages["contact"])

    if "linkedin" not in contact:
        tip = ("إضافة رابط لينكد إن يزيد من فرصك."
               if lang == "ar"
               else "Adding a LinkedIn profile URL improves recruiter visibility.")
        tips.append(tip)

    if len(cv_text.split()) < 100:
        tips.append("السيرة الذاتية قصيرة جداً، أضف المزيد من التفاصيل."
                    if lang == "ar"
                    else "The CV looks very short. Expand each section.")

    return tips or [("تبدو السيرة الذاتية ممتازة!" if lang == "ar" else "No major issues found.")]


# ── public API ────────────────────────────────────────────────────────────────

def analyze_cv(cv_text: str, use_ai: bool = False) -> dict:
    if not cv_text or not cv_text.strip():
        return {"error": "CV text is empty."}

    sections = extract_sections(cv_text)
    skills   = extract_skills(cv_text)
    contact  = extract_contact(cv_text)
    entities = extract_entities(cv_text)

    if use_ai:
        try:
            suggestions = get_suggestions(cv_text)
        except Exception:
            suggestions = _rule_based_suggestions(cv_text, sections, contact)
    else:
        suggestions = _rule_based_suggestions(cv_text, sections, contact)

    return {
        "sections_found":  [k for k in sections if k != "header"],
        "skills":          skills,
        "contact_info":    contact,
        "named_entities":  entities,
        "suggestions":     suggestions,
        "word_count":      len(cv_text.split()),
        "character_count": len(cv_text),
    }
