import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

_PROMPT = """You are a professional CV reviewer.
Analyze the CV below. Detect the language (English or Arabic) and respond in the SAME language.
Give exactly 3 specific, actionable suggestions to improve this CV.
Format: return only the 3 suggestions as a numbered list, nothing else.

CV:
{cv_text}"""


def get_suggestions(cv_text: str) -> list[str]:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY is not set.")

    client   = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=_PROMPT.format(cv_text=cv_text[:3000]),
    )
    lines = [
        line.strip().lstrip("123.-) ").strip()
        for line in response.text.splitlines()
        if line.strip() and line.strip()[0].isdigit()
    ]
    return lines[:3]
