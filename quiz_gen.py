import json, os
from dotenv import load_dotenv

load_dotenv()

# Read API key from env
_GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Try modern Google Generative Language client
genai_client = None
try:
    from google.ai import generativelanguage as gl
    try:
        genai_client = gl.TextServiceClient()
    except Exception:
        genai_client = None
except Exception:
    genai_client = None

# Fallback to older google.generativeai if present
genai_legacy = None
try:
    import google.generativeai as genai_legacy
    try:
        genai_legacy.configure(api_key=_GOOGLE_API_KEY)
    except Exception:
        genai_legacy = None
except Exception:
    genai_legacy = None

def generate_quiz(topic, branch, num_q=5):
    if (genai_client is None and genai_legacy is None) or not _GOOGLE_API_KEY:
        qs = []
        for i in range(num_q):
            qs.append({
                "question": f"Sample question {i+1} about {topic}",
                "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
                "correct_answer": "A",
                "explanation": "Explanation not available."
            })
        return qs, None

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

    try:
        text = None
        if genai_client is not None:
            try:
                resp = genai_client.generate_text(model="models/text-bison-001", prompt=prompt)
                text = getattr(resp, 'text', None) or getattr(resp, 'content', None) or str(resp)
            except Exception:
                # try alternative param name
                resp = genai_client.generate_text(model="models/text-bison-001", input=prompt)
                text = getattr(resp, 'text', None) or getattr(resp, 'content', None) or str(resp)
        elif genai_legacy is not None:
            model = genai_legacy.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt, generation_config=genai_legacy.types.GenerationConfig(temperature=0.6))
            text = response.text

        if text is None:
            raise RuntimeError("No response from generative client")

        text = text.strip()
        text = text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(text), None
        except Exception:
            return None, "Generation failed. Try again."
    except Exception as e:
        qs = []
        for i in range(num_q):
            qs.append({
                "question": f"Sample question {i+1} about {topic}",
                "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
                "correct_answer": "A",
                "explanation": "Explanation not available."
            })
        return qs, f"Generation error: {e}"