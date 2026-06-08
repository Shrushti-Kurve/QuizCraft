import json, os, random
from dotenv import load_dotenv

load_dotenv()
genai_key = os.getenv("GOOGLE_API_KEY")
use_google_api = os.getenv("USE_GOOGLE_API") == "1"

def _local_generate(prompt: str, num_q: int) -> str:
  topic_line = next((line for line in prompt.splitlines() if line.strip().startswith("Topic:")), "Topic: General")
  topic = topic_line.split(":", 1)[1].strip() or "General"

  templates = [
    ("What best describes {topic} in practical terms?", "A concept or tool used to solve real-world problems", "A random keyword", "A type of database index", "A programming language only"),
    ("Which choice is most likely related to {topic}?", "An example, method, or application tied to the topic", "An unrelated sports term", "A hardware driver setting", "A file permission flag"),
    ("Why is {topic} useful?", "It helps organize, analyze, or automate work in that area", "It deletes all data automatically", "It replaces every other subject", "It only works offline"),
    ("What is a common challenge when learning {topic}?", "Understanding the concepts deeply and applying them correctly", "Typing faster than others", "Avoiding all examples", "Never making mistakes"),
    ("Which answer is the safest general approach for {topic}?", "Start with the basics, practice, then apply to problems", "Memorize one line and stop", "Guess the answer immediately", "Skip practice entirely"),
  ]

  items = []
  for i in range(num_q):
    q_tpl, correct, b, c, d = templates[i % len(templates)]
    wrong_options = [b, c, d]
    rotated = wrong_options[i % 3 :] + wrong_options[: i % 3]
    opts = [correct] + rotated
    random.shuffle(opts)
    letters = ["A", "B", "C", "D"]
    options = {letters[j]: opts[j] for j in range(4)}
    correct_letter = next(k for k, v in options.items() if v == correct)
    explanation = f"{correct}. In {topic}, focus on understanding the concept and practicing applied problems to master it."
    items.append({
      "question": q_tpl.format(topic=topic),
      "options": options,
      "correct_answer": correct_letter,
      "explanation": explanation,
    })

  return json.dumps(items)


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

  if genai_key and use_google_api:
    try:
      import google.generativeai as genai

      genai.configure(api_key=genai_key)
      model = genai.GenerativeModel("gemini-1.5-flash")
      response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.6)
      )
      text = response.text.strip()
      text = text.replace("```json", "").replace("```", "").strip()
      try:
        parsed = json.loads(text)
        # basic validation
        if isinstance(parsed, list) and parsed:
          valid = True
          for it in parsed:
            if not all(k in it for k in ("question", "options", "correct_answer", "explanation")):
              valid = False
              break
            if not isinstance(it.get("options"), dict) or len(it["options"]) != 4:
              valid = False
              break
          if valid:
            return parsed, None
      except Exception:
        pass
    except Exception:
      pass

  try:
    text = _local_generate(prompt, num_q)
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text), None
  except Exception as e:
    return None, f"Generation failed: {e}"