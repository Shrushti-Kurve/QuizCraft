# quiz_gen.py
import google.generativeai as genai
import json, os
from dotenv import load_dotenv

load_dotenv()
genai_key = os.getenv("GOOGLE_API_KEY")
if genai_key:
  try:
    genai.configure(api_key=genai_key)
  except Exception:
    pass


def _local_generate(prompt: str) -> str:
  try:
    from transformers import pipeline
  except Exception:
    raise RuntimeError("Local transformers fallback requires the 'transformers' package.")

  model_name = "google/flan-t5-small"
  gen = pipeline("text2text-generation", model=model_name)
  out = gen(prompt, max_length=512, do_sample=False)
  return out[0]["generated_text"]


def generate_quiz(topic, branch, num_q=5):
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

  # Try Google Generative API if key is present
  if genai_key:
    try:
      model = genai.GenerativeModel("gemini-1.5-flash")
      response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.6)
      )
      text = response.text.strip()
      text = text.replace("```json", "").replace("```", "").strip()
      try:
        return json.loads(text), None
      except Exception:
        pass
    except Exception:
      pass

  # Local fallback
  try:
    text = _local_generate(prompt)
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text), None
  except Exception as e:
    return None, f"Generation failed: {e}"