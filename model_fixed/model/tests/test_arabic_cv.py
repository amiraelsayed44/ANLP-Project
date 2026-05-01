import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nlp_analyzer import analyze_cv

# نموذج سيرة ذاتية عربية للاختبار
ARABIC_CV = """
أحمد محمد
ahmed.mohamed@email.com | +201001234567 | linkedin.com/in/ahmed-mohamed | github.com/ahmedm

الملخص:
مهندس برمجيات شغوف ومتخصص في تطوير الواجهات الخلفية بخبرة تزيد عن عامين.
أسعى للانضمام إلى فريق عمل ديناميكي لتوظيف مهاراتي في حل المشكلات البرمجية المعقدة.

الخبرة العملية:
مطور واجهات خلفية | شركة الحلول التقنية المتقدمة | يناير 2023 - الحاضر
- تصميم وتطوير واجهات برمجة تطبيقات آمنة باستخدام Django REST Framework.
- تحسين أداء استعلامات PostgreSQL مما أدى إلى تسريع وقت الاستجابة بنسبة 30%.

التعليم:
بكالوريوس هندسة الحاسبات | جامعة القاهرة
سنة التخرج: 2022 | التقدير العام: جيد جداً

المهارات:
Python, Django, FastAPI, PostgreSQL, Docker, Git

اللغات:
العربية (اللغة الأم)، الإنجليزية (مستوى احترافي)
"""


def test_arabic_sections_detected():
    result = analyze_cv(ARABIC_CV, use_ai=False)
    found  = result['sections_found']
    # يجب إن الموديل يكتشف على الأقل قسم واحد من الأقسام الأساسية
    assert any(s in found for s in ['summary', 'experience', 'education', 'skills'])


def test_arabic_contact():
    result  = analyze_cv(ARABIC_CV, use_ai=False)
    contact = result['contact_info']
    # يجب إن الإيميل واللينكد إن يتعرفوا صح
    assert contact.get('email') == 'ahmed.mohamed@email.com'
    assert 'linkedin' in contact


def test_arabic_suggestions_in_arabic():
    result   = analyze_cv(ARABIC_CV, use_ai=False)
    all_text = ' '.join(result['suggestions'])
    # الاقتراحات لازم تكون بالعربي لأن الـ CV عربي
    assert any('\u0600' <= ch <= '\u06FF' for ch in all_text), \
        'Expected Arabic suggestions for an Arabic CV'
