import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from nlp_analyzer import analyze_cv

ARABIC_CV = """
أحمد محمد
ahmed.mohamed@email.com | +201001234567 | linkedin.com/in/ahmed-mohamed | github.com/ahmedm

الملخص:
مهندس برمجيات شغوف ومتخصص في تطوير الواجهات الخلفية (Backend Development) بخبرة تزيد عن عامين في بناء تطبيقات ويب سريعة وقابلة للتوسع. أمتلك خبرة قوية في تصميم قواعد البيانات وبناء واجهات برمجة التطبيقات (RESTful APIs). أسعى للانضمام إلى فريق عمل ديناميكي لتوظيف مهاراتي في حل المشكلات البرمجية المعقدة.

الخبرة العملية:
مطور واجهات خلفية (Backend Developer) | شركة الحلول التقنية المتقدمة | يناير 2023 - الحاضر
- تصميم وتطوير واجهات برمجة تطبيقات (APIs) آمنة باستخدام إطار عمل Django REST Framework.
- تحسين أداء استعلامات قواعد البيانات (PostgreSQL)، مما أدى إلى تسريع وقت الاستجابة بنسبة 30%.
- دمج خدمات الطرف الثالث (Third-party integrations) مثل بوابات الدفع الإلكتروني وخدمات إرسال البريد.
- العمل باستخدام منهجية (Agile/Scrum) والمشاركة الفعالة في مراجعة الأكواد (Code Reviews).

التعليم:
بكالوريوس هندسة الحاسبات | جامعة القاهرة
سنة التخرج: 2022 | التقدير العام: جيد جداً (مع مرتبة الشرف)

المشاريع:
نظام إدارة الموارد البشرية (HR Management System):
- تطبيق ويب متكامل لإدارة إجازات ورواتب الموظفين.
- التقنيات المستخدمة: Python, FastAPI, Docker, PostgreSQL.
- تم نشر التطبيق على خوادم AWS باستخدام Docker Containers.

أداة تحليل السير الذاتية بالذكاء الاصطناعي:
- أداة لتحليل نصوص السير الذاتية واستخراج المهارات باستخدام معالجة اللغات الطبيعية (NLP).
- التقنيات المستخدمة: Python, spaCy, Gemini API.

المهارات:
Python, Django, FastAPI, PostgreSQL, MySQL, Docker, Git, Linux, REST APIs, Object-Oriented Programming (OOP)

اللغات:
العربية (اللغة الأم)، الإنجليزية (مستوى احترافي - C1)
"""

def test_arabic():
    print("Analyzing Arabic CV... (This might take a few seconds)")
    
    result = analyze_cv(ARABIC_CV, use_ai=False) 
    
    print("\n=== Sections Found ===")
    print(result.get("sections_found"))
    
    print("\n=== Skills Extracted ===")
    print(result.get("skills"))

    print("\n=== Contact Info Extracted ===")
    print(result.get("contact_info"))

    print("\n=== Entities Extracted ===")
    print(result.get("entities"))

    print("\n=== Suggestions Generated ===")
    for tip in result.get("suggestions", []):
        print(f" {tip}")
    
    print("\n=== AI Suggestions Received ===")
    for tip in result.get("suggestions", []):
        print(f" {tip}")

if __name__ == "__main__":
    test_arabic()