"""
nlp_analyzer.py
---------------
Core NLP pipeline for the Resume Analyzer.
Uses spaCy for named-entity recognition and rule-based section parsing.
"""

import re
import spacy


# Model loading

def load_model():
    try:
        nlp = spacy.load("en_core_web_sm")
        return nlp
    except OSError:
        raise RuntimeError(
            "spaCy model missing. Run:  python -m spacy download en_core_web_sm"
        )


nlp = load_model()

# Section detection

SECTION_HEADERS = {
    "contact":        r"(contact|phone|linkedin|github|address)",
    "summary":        r"(summary|profile|objective|about\s*me|personal\s*statement)",
    "education":      r"(education|academic|university|degree|school|college)",
    "experience":     r"(experience|employment|work\s*history|internship|career)",
    "skills":         r"(skills|technologies|tools|competencies)",
    "projects":       r"(projects|portfolio|work\s*samples)",
    "certifications": r"(certif|license|credential|course|training)",
    "awards":         r"(award|honor|achievement|scholarship)",
    "languages":      r"(language|spoken|fluency)",
    "references":     r"(reference|recommendation)",
}


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
        r"(skills|technologies|tools)[:\-\s]+(.*?)(\n\n|\Z)",
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

CRITICAL_SECTIONS = ["summary", "education", "experience", "skills"]

MISSING_SECTION_MESSAGES = {
    "summary":        "Add a Profile Summary (2-3 sentences about yourself and your goals).",
    "education":      "Add an Education section with your degree, university, and graduation year.",
    "experience":     "Add a Work Experience or Internship section.",
    "skills":         "Add a Skills section listing your technical and soft skills.",
    "projects":       "Add a Projects section — even academic or personal projects count.",
    "certifications": "Add any Certifications or online courses you have completed.",
    "contact":        "Make sure your contact info (email, LinkedIn) is clearly listed.",
}

ACTION_VERBS = [
    "developed", "built", "led", "managed", "designed",
    "implemented", "created", "improved", "analyzed", "achieved",
]


def generate_suggestions(
    cv_text: str,
    sections: dict,
    contact: dict,
    skills: list,
) -> list[str]:
    
    tips: list[str] = []
    found = set(sections.keys())

    # Missing critical sections
    for sec in CRITICAL_SECTIONS:
        if sec not in found:
            tips.append(MISSING_SECTION_MESSAGES[sec])

    # Missing nice-to-have sections
    for sec in ("projects", "certifications"):
        if sec not in found:
            tips.append(MISSING_SECTION_MESSAGES[sec])

    # Contact completeness
    if "email" not in contact:
        tips.append("No email address detected — make sure it is present.")
    if "linkedin" not in contact:
        tips.append("Adding a LinkedIn profile URL improves recruiter visibility.")

    # Length check
    if len(cv_text.split()) < 100:
        tips.append("The CV looks very short. Expand each section with more detail.")

    # Weak experience bullets
    if "experience" in found:
        exp_lower = sections["experience"].lower()
        verb_hits = [v for v in ACTION_VERBS if v in exp_lower]
        if len(verb_hits) < 2:
            tips.append(
                'Use strong action verbs in your Experience bullets '
                '(e.g. "Developed", "Led", "Improved").'
            )

    # Skills section present but empty
    if "skills" in found and not skills:
        tips.append("Skills section found but appears empty — list specific tools and languages.")

    if not tips:
        tips.append("No major issues found. Tailor the CV for each application.")

    return tips


# Main entry point


def analyze_cv(cv_text: str) -> dict:
   
    if not cv_text or not cv_text.strip():
        return {"error": "CV text is empty."}

    sections    = extract_sections(cv_text)
    skills      = extract_skills(cv_text)
    contact     = extract_contact(cv_text)
    suggestions = generate_suggestions(cv_text, sections, contact, skills)

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
        "suggestions":      suggestions,
        "word_count":       len(cv_text.split()),
        "character_count":  len(cv_text),
    }

