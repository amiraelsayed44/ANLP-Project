"""
nlp_analyzer.py
---------------
Core NLP pipeline for the Resume Analyzer.
Uses spaCy for named-entity recognition and rule-based section parsing.
"""

import re
import spacy

from utils.gemini_client import GeminiClient
from utils.constants import (
    SECTION_HEADERS,
    CRITICAL_SECTIONS,
    MISSING_SECTION_MESSAGES_EN,
    MISSING_SECTION_MESSAGES_AR,
)


# Model loading

def load_model():
    try:
        nlp = spacy.load("xx_ent_wiki_sm")
        return nlp
    except OSError:
        raise RuntimeError(
            "spaCy model missing. Run:  python -m spacy download en_core_web_sm"
        )


nlp = load_model()

def is_arabic(text: str) -> bool:
    """Check if the text contains Arabic characters."""
    return bool(re.search(r'[\u0600-\u06FF]', text))

# Section detection

def extract_sections(cv_text: str) -> dict:
    """
    Walk the CV line by line. When a short line matches a known section
    keyword it becomes the new active section; everything below it belongs
    to that section until the next header is found.
    """
    sections: dict[str, str] = {}
    current_section = "header"
    buffer: list[str] = []

    for line in cv_text.split("\n"):
        stripped = line.strip()

        matched = None
        if stripped and len(stripped) < 60:
            for name, pattern in SECTION_HEADERS.items():
                if re.search(pattern, stripped, re.IGNORECASE):
                    matched = name
                    break

        if matched:
            if buffer:
                sections[current_section] = "\n".join(buffer).strip()
            current_section = matched
            buffer = []
        else:
            buffer.append(stripped)

    if buffer:
        sections[current_section] = "\n".join(buffer).strip()

    return sections


def extract_skills(cv_text: str) -> list[str]:
   
    skills: list[str] = []

    # Rule-based pass: grab the comma/bullet list after the skills header
    match = re.search(
        r"(skills|technologies|tools|المهارات|تقنيات|أدوات)[:\-\s]+(.*?)(\n\n|\Z)", # تمت إضافة الكلمات العربية هنا
        cv_text,
        re.IGNORECASE | re.DOTALL,
    )
    if match:
        raw = match.group(2)
        candidates = re.split(r"[,•|\n/]+", raw)
        skills = [s.strip() for s in candidates if 2 < len(s.strip()) < 40]

    # NER pass: pick up tech-stack proper nouns the rule missed
    doc = nlp(cv_text[:5000])
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT") and len(ent.text) < 30:
            cleaned = ent.text.strip()
            if cleaned not in skills:
                skills.append(cleaned)

    return list(dict.fromkeys(skills))  # remove duplicates, keep order


def extract_contact(cv_text: str) -> dict:
    """Return any email, phone, LinkedIn, and GitHub found in the text."""
    info: dict[str, str] = {}

    m = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", cv_text)
    if m:
        info["email"] = m.group()

    m = re.search(r"(\+?\d[\d\s\-().]{7,15}\d)", cv_text)
    if m:
        info["phone"] = m.group().strip()

    m = re.search(r"linkedin\.com/in/[\w\-]+", cv_text, re.IGNORECASE)
    if m:
        info["linkedin"] = "https://" + m.group()

    m = re.search(r"github\.com/[\w\-]+", cv_text, re.IGNORECASE)
    if m:
        info["github"] = "https://" + m.group()

    return info


# Suggestion engine

def generate_suggestions(
    cv_text: str,
    sections: dict,
    contact: dict,
    skills: list,
) -> list[str]:
    
    tips: list[str] = []
    found = set(sections.keys())
    
    # اختيار لغة النصائح بناءً على محتوى السيرة الذاتية
    is_ar = is_arabic(cv_text)
    messages = MISSING_SECTION_MESSAGES_AR if is_ar else MISSING_SECTION_MESSAGES_EN

    # Missing critical sections
    for sec in CRITICAL_SECTIONS:
        if sec not in found:
            tips.append(messages[sec])

    # Missing nice-to-have sections
    for sec in ("projects", "certifications"):
        if sec not in found:
            tips.append(messages[sec])

    # Contact completeness
    if "email" not in contact:
        tips.append("لم يتم العثور على بريد إلكتروني." if is_ar else "No email address detected.")
    if "linkedin" not in contact:
        tips.append("إضافة رابط لينكد إن يزيد من فرصك." if is_ar else "Adding a LinkedIn profile URL improves recruiter visibility.")

    if len(cv_text.split()) < 100:
        tips.append("السيرة الذاتية قصيرة جداً، أضف المزيد من التفاصيل." if is_ar else "The CV looks very short. Expand each section.")

    if not tips:
        tips.append("تبدو السيرة الذاتية ممتازة!" if is_ar else "No major issues found.")

    return tips

def generate_intelligent_suggestions(cv_text: str) -> list[str]:
    """Use Gemini to generate suggestions based on the CV content."""
    try:
        client = GeminiClient.create_client()
        return client.generate_suggestions(cv_text)
    except Exception as e:
        print(f"Warning: Could not fetch intelligent suggestions: {e}")
        return []

# Main entry point
def analyze_cv(cv_text: str, use_ai: bool = False) -> dict:
   
    if not cv_text or not cv_text.strip():
        return {"error": "CV text is empty."}

    sections    = extract_sections(cv_text)
    skills      = extract_skills(cv_text)
    contact     = extract_contact(cv_text)
    
    basic_suggestions = generate_suggestions(cv_text, sections, contact, skills)
    
    if use_ai:
        llm_suggestions = generate_intelligent_suggestions(cv_text)
        if len(llm_suggestions) > 0:
            all_suggestions = llm_suggestions
        else:
            all_suggestions = basic_suggestions
    else:
        all_suggestions = basic_suggestions

    doc = nlp(cv_text[:5000])
    entities = [
        {"text": ent.text, "label": ent.label_}
        for ent in doc.ents
        if ent.label_ in ("ORG", "PERSON", "GPE", "PRODUCT", "DATE")
    ]

    return {
        "sections_found":   list(k for k in sections if k != "header"),
        "skills":           skills,
        "contact_info":     contact,
        "named_entities":   entities[:20],
        "suggestions":      all_suggestions, 
        "word_count":       len(cv_text.split()),
        "character_count":  len(cv_text),
    }