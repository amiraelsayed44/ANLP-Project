from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

class GeminiClient:
    def __init__(self, api_key: str = None):
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
            
        self.client = genai.Client(api_key=api_key)

    def generate_suggestions(self, cv_text: str) -> list[str]:
        prompt = f"""
        Analyze the following CV. First, detect if it is written in English or Arabic. 
        Provide 3 specific, actionable suggestions for improvement IN THE SAME LANGUAGE as the CV. 
        Do not include introductory text, just the bullet points:
        
        {cv_text}
        """
        
        response = self.client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt
        )
        
        return [s.strip().strip('-* ') for s in response.text.split("\n") if s.strip()]
    
    @classmethod
    def create_client(cls):
        return cls()