# quiz_gen.py
import google.generativeai as genai
import json, os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_quiz(topic, branch, num_q=5):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Generate {num_q} MCQ questions for a college student.
    Branch: {branch}
    Topic: {topic}

    Rules:
    - Questions must test real understanding, not just memory
    - All 4 options must be plausible
    - Explanation must teach the concept clearly

    Return ONLY a JSON array. No markdown. No extra text.
    [
      {{
        "question": "...",
        "options": {{"A":"...","B":"...","C":"...","D":"..."}},
        "correct_answer": "A",
        "explanation": "..."
      }}
    ]
    """
    
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.6)
    )
    
    text = response.text.strip()
    text = text.replace("```json","").replace("```","").strip()
    
    try:
        return json.loads(text), None
    except:
        return None, "Generation failed. Try again."