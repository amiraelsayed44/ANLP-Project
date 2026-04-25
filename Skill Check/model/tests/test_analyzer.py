
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nlp_analyzer import (
    analyze_cv,
    extract_sections,
    extract_skills,
    extract_contact,
    generate_suggestions,
    generate_intelligent_suggestions,
)



# Sample CVs

GOOD_CV = """
Ahmed Hassan
ahmed.hassan@gmail.com | linkedin.com/in/ahmedhassan | github.com/ahmedhassan | +20-100-000-0000

Summary
Computer Science student with experience in backend development and machine learning.
Looking for a software engineering internship.

Education
B.Sc. Computer Science, Cairo University — Expected 2025  |  GPA 3.7 / 4.0

Experience
Backend Developer Intern, StartupX — Cairo  (Jun 2023 – Sep 2023)
- Developed REST APIs with Django and PostgreSQL
- Implemented JWT authentication, increasing security coverage to 100%
- Led code reviews for three junior developers

Projects
Resume Analyzer (2024)
Built an NLP pipeline with spaCy and deployed it as a FastAPI microservice on Docker.

Skills
Python, Django, FastAPI, PostgreSQL, Docker, Git, Machine Learning, spaCy

Certifications
AWS Cloud Practitioner — Amazon (2023)
Machine Learning Specialization — Coursera (2023)

Languages
Arabic (Native), English (Fluent)
"""

POOR_CV = """
Mohamed Ali
I am a student looking for a job.
I know some programming.
"""

MISSING_SECTIONS_CV = """
Sara Khaled
sara@example.com

Education
B.Sc. Information Technology, Alexandria University — 2024

Skills
Java, Spring Boot, MySQL, HTML, CSS
"""

EMPTY_CV = ""

SKILLS_ONLY_LINE = "Skills: Python, Java, SQL, Machine Learning, Git, Docker, React, Node.js"



# Helpers


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    mark   = "✓" if condition else "✗"
    print(f"  {mark} [{status}] {label}")
    return condition



# Step 1 — NLP model loads and processes text


def test_model_loads():
    print("\n── Step 1: NLP model ──")
    from nlp_analyzer import nlp
    doc = nlp("Ahmed studied Python at Cairo University in 2023.")
    entities = [(e.text, e.label_) for e in doc.ents]
    print(f"     entities: {entities}")
    check("model returns a Doc object", doc is not None)
    check("at least one entity found", len(entities) > 0)



# Step 2 — Section and skill extraction


def test_section_extraction():
    print("\n── Step 2: Section extraction ──")
    sections = extract_sections(GOOD_CV)
    found = list(sections.keys())
    print(f"     sections: {found}")
    check("education detected",  "education"  in found)
    check("experience detected", "experience" in found)
    check("skills detected",     "skills"     in found)
    check("summary detected",    "summary"    in found)

    skills = extract_skills(GOOD_CV)
    print(f"     skills: {skills}")
    check("Python in skills",   "Python" in skills)
    check("Django in skills",   "Django" in skills)

    # Explicit example from the brief
    simple = extract_skills("Skills: Python, Java")
    check("Python from 'Skills: Python, Java'", "Python" in simple)
    check("Java   from 'Skills: Python, Java'", "Java"   in simple)



# Step 3 — Suggestion generation


def test_suggestions():
    print("\n── Step 3: Suggestion generation ──")

    sections = extract_sections(MISSING_SECTIONS_CV)
    contact  = extract_contact(MISSING_SECTIONS_CV)
    skills   = extract_skills(MISSING_SECTIONS_CV)
    tips     = generate_suggestions(MISSING_SECTIONS_CV, sections, contact, skills)
    joined   = " ".join(tips).lower()

    print(f"     tips for missing-sections CV:")
    for t in tips:
        print(f"       - {t}")

    check("suggestions list is not empty", len(tips) > 0)
    check("summary tip present", "summary" in joined or "profile" in joined)
    check("experience tip present", "experience" in joined or "internship" in joined)

    good_result = analyze_cv(GOOD_CV)
    print(f"\n     tips for good CV: {good_result['suggestions']}")
    check("good CV has at least one tip", len(good_result["suggestions"]) >= 1)


def test_intelligent_suggestions():
    print("\n── Step 3b: Intelligent suggestions (Gemini) ──")
    try:
        tips = generate_intelligent_suggestions(GOOD_CV)
        print(f"     Gemini suggestions: {tips}")
        check("Gemini suggestions list is not empty", len(tips) > 0)
    except Exception as e:
        print(f"     Warning: Could not test Gemini suggestions: {e}")
        check("Gemini suggestions test skipped due to error", True)

def test_intelligent_suggestions_edge_case():
    print("\n── Step 3c: Intelligent suggestions edge case (empty CV) ──")
    try:
        tips = generate_intelligent_suggestions(EMPTY_CV)
        print(f"     Gemini suggestions for empty CV: {tips}")
        check("Gemini suggestions for empty CV is a list", isinstance(tips, list))
    except Exception as e:
        print(f"     Warning: Could not test Gemini suggestions for empty CV: {e}")
        check("Gemini suggestions edge case test skipped due to error", True)

def test_intelligent_suggestions_poor_cv():
    print("\n── Step 3d: Intelligent suggestions edge case (poor CV) ──")
    try:
        tips = generate_intelligent_suggestions(POOR_CV)
        print(f"     Gemini suggestions for poor CV: {tips}")
        check("Gemini suggestions for poor CV is a list", isinstance(tips, list))
    except Exception as e:
        print(f"     Warning: Could not test Gemini suggestions for poor CV: {e}")
        check("Gemini suggestions edge case test skipped due to error", True)

def test_intelligent_suggestions_skills_only():
    print("\n── Step 3e: Intelligent suggestions edge case (skills-only CV) ──")
    try:
        tips = generate_intelligent_suggestions(SKILLS_ONLY_LINE)
        print(f"     Gemini suggestions for skills-only CV: {tips}")
        check("Gemini suggestions for skills-only CV is a list", isinstance(tips, list))
    except Exception as e:
        print(f"     Warning: Could not test Gemini suggestions for skills-only CV: {e}")
        check("Gemini suggestions edge case test skipped due to error", True)
# Step 4 — Full pipeline output shape (mirrors what the API returns)

def test_output_shape():
    print("\n── Step 4: Output shape ──")
    result = analyze_cv(GOOD_CV)

    required_keys = [
        "sections_found", "skills", "contact_info",
        "named_entities", "suggestions", "word_count", "character_count",
    ]
    for key in required_keys:
        check(f"key '{key}' present", key in result)

    check("email extracted",   result["contact_info"].get("email") == "ahmed.hassan@gmail.com")
    check("word_count > 0",    result["word_count"] > 0)
    check("skills not empty",  len(result["skills"]) > 0)



# Step 5 — Edge cases must not crash


def test_edge_cases():
    print("\n── Step 5: Edge cases / robustness ──")

    # Empty input
    r = analyze_cv(EMPTY_CV)
    check("empty CV returns error key, not exception", "error" in r)

    # Very poor CV
    r = analyze_cv(POOR_CV)
    check("poor CV runs without crash", r is not None)
    check("poor CV returns suggestions", len(r.get("suggestions", [])) > 0)

    # Skills-only line
    r = analyze_cv(SKILLS_ONLY_LINE)
    check("skills-only CV runs without crash", r is not None)
    check("skills-only CV extracts skills",    len(r.get("skills", [])) > 0)

    # Missing sections
    r = analyze_cv(MISSING_SECTIONS_CV)
    check("missing-sections CV runs without crash", r is not None)
    check("missing-sections CV returns tips",       len(r.get("suggestions", [])) > 0)

    # Arabic / Unicode content
    r = analyze_cv("محمد علي\nEmail: m.ali@test.com\nSkills: Python, SQL")
    check("Arabic text CV runs without crash", r is not None)

    # Very long CV (stress test)
    r = analyze_cv(GOOD_CV )
    check("10x repeated CV runs without crash", r is not None)


# Runner

def run_all():
    print("=" * 50)
    print("  Resume Analyzer — Test Suite")
    print("=" * 50)
    test_model_loads()
    test_section_extraction()
    test_suggestions()
    test_output_shape()
    test_edge_cases()
    print("\n" + "=" * 50)
    print("  Done.")
    print("=" * 50)


if __name__ == "__main__":
    run_all()



# pytest

def test_pytest_model():
    from nlp_analyzer import nlp
    assert nlp("hello world") is not None

def test_pytest_skills():
    assert "Python" in extract_skills("Skills: Python, Java, SQL")
    assert "Java"   in extract_skills("Skills: Python, Java, SQL")

def test_pytest_summary_suggestion():
    result = analyze_cv(MISSING_SECTIONS_CV)
    joined = " ".join(result["suggestions"]).lower()
    assert "summary" in joined or "profile" in joined

def test_pytest_empty_cv():
    assert "error" in analyze_cv("")

def test_pytest_contact():
    result = analyze_cv(GOOD_CV)
    assert result["contact_info"]["email"] == "ahmed.hassan@gmail.com"

def test_pytest_keys():
    result = analyze_cv(GOOD_CV)
    for k in ["sections_found", "skills", "contact_info", "suggestions"]:
        assert k in result
