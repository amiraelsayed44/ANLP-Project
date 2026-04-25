import sys
import os

# Ensure Python can find your modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nlp_analyzer import analyze_cv

# A tiny sample CV to test the AI
SAMPLE_CV = """
Alex Johnson
alex@email.com
Experience: 
I worked at Google for 2 years doing some coding.
Skills: Python, HTML
"""

def test_live_ai():
    print("Sending CV to Gemini... (This might take a few seconds)")
    
    # Notice we explicitly pass use_ai=True here!
    result = analyze_cv(SAMPLE_CV, use_ai=True)
    
    print("\n=== AI Suggestions Received ===")
    for tip in result.get("suggestions", []):
        print(f"💡 {tip}")

if __name__ == "__main__":
    test_live_ai()