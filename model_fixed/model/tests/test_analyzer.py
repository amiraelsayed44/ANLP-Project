import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nlp_analyzer import analyze_cv, extract_sections, extract_skills, extract_contact

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

Projects
Resume Analyzer (2024)
Built an NLP pipeline with spaCy and deployed it as a FastAPI microservice.

Skills
Python, Django, FastAPI, PostgreSQL, Docker, Git, spaCy

Certifications
AWS Cloud Practitioner — Amazon (2023)

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

Skills
Python, Java
"""


def test_good_cv_sections():
    result = analyze_cv(GOOD_CV)
    assert "education"  in result["sections_found"]
    assert "experience" in result["sections_found"]
    assert "skills"     in result["sections_found"]


def test_good_cv_contact():
    contact = extract_contact(GOOD_CV)
    assert contact.get("email") == "ahmed.hassan@gmail.com"
    assert "linkedin" in contact
    assert "github"   in contact


def test_good_cv_skills():
    skills = extract_skills(GOOD_CV)
    assert len(skills) > 0


def test_poor_cv_suggestions():
    result = analyze_cv(POOR_CV)
    assert len(result["suggestions"]) > 0
    # Should flag missing sections
    text = " ".join(result["suggestions"]).lower()
    assert any(word in text for word in ["summary", "education", "experience", "نبذة", "تعليم"])


def test_missing_sections_suggestions():
    result = analyze_cv(MISSING_SECTIONS_CV)
    found  = result["sections_found"]
    assert "summary"    not in found
    assert "experience" not in found


def test_empty_cv():
    result = analyze_cv("   ")
    assert "error" in result


def test_word_count():
    result = analyze_cv(GOOD_CV)
    assert result["word_count"] > 50
    assert result["character_count"] > 200
