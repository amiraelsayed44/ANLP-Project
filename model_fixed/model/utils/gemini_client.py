import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

_PROMPT_TEMPLATE = """
Analyze the following CV and detect whether it is written in English or Arabic. 
Provide exactly 3 specific, actionable improvement suggestions in the same language as the CV.

Output requirements:
- Return only 3 bullet points
- No preamble, explanation, or extra text

Examples:

CV:
Software Engineer with experience in Node.js and MongoDB. Worked on backend APIs.

Output:
- Add measurable achievements (e.g., reduced response time by X% or handled Y requests/sec)
- Include specific projects with links (GitHub or portfolio) to showcase your work
- Expand on technologies and tools used (e.g., frameworks, testing tools, cloud services)

CV:
مهندس برمجيات لديه خبرة في تطوير الويب باستخدام جافاسكريبت. عمل على بعض المشاريع.

Output:
- أضف إنجازات رقمية واضحة (مثل تحسين الأداء بنسبة معينة أو عدد المستخدمين)
- اذكر المشاريع بالتفصيل مع روابط (GitHub أو معرض أعمال)
- وضّح التقنيات والأدوات المستخدمة بشكل أدق (مثل الأطر، أدوات الاختبار، أو الخدمات السحابية)

CV:
{cv_text}

Output:
"""



def get_suggestions(cv_text: str) -> list[str]:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY is not set.")

    client   = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=_PROMPT_TEMPLATE.format(cv_text=cv_text),
    )
    return [line.strip().strip("-* ") for line in response.text.splitlines() if line.strip()]
