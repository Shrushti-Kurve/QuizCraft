# quiz_gen.py
import json, os
from dotenv import load_dotenv

load_dotenv()

# Try to import Google generative AI; if unavailable, we'll use a local fallback.
try:
  import google.generativeai as genai
  _GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
  try:
    genai.configure(api_key=_GOOGLE_API_KEY)
  except Exception:
    # configuration failed; continue and use fallback at call time
    genai = None
except Exception:
  genai = None

def generate_quiz(topic, branch, num_q=5):
  # If the Google generative API isn't available or configured, return a simple local quiz.
  if genai is None or not os.getenv("GOOGLE_API_KEY"):
    qs = []
    for i in range(num_q):
      qs.append({
        "question": f"Sample question {i+1} about {topic}",
        "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
        "correct_answer": "A",
        "explanation": "This is a sample explanation. Replace with AI-generated content by setting GOOGLE_API_KEY."
      })
    return qs, None

  try:
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
    text = text.replace("```json", "").replace("```", "").strip()

    try:
      return json.loads(text), None
    except Exception:
      return None, "Generation failed. Try again."
  except Exception as e:
    # If remote generation fails (model not found, API error, etc.),
    # return a simple local fallback quiz so the app remains usable.
    qs = []
    for i in range(num_q):
      qs.append({
        "question": f"Sample question {i+1} about {topic}",
        "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
        "correct_answer": "A",
        "explanation": "This is a sample explanation. Replace with AI-generated content by configuring a supported model and API key."
      })
    return qs, f"Generation error: {e}"