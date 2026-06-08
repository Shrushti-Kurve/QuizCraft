# 🎯 QuizCraft 🧠✨

**AI-powered, interactive multiple-choice quiz generator and evaluator built with Streamlit 🚀**

## 🌟 Features

✅ Generate MCQs for **any topic** (uses **Google Generative AI / Gemini** when enabled 🤖)
✅ Local **offline fallback generator** when API/model is unavailable 🔄
✅ Interactive quiz UI with **session state, scoring, explanations, and weak-area detection** 📊📝

## ⚡ Quick Start

### 1️⃣ Create and activate a Python environment (Recommended 🐍)

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ (Optional) Enable Google Generative API (Gemini) 🤖

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_key_here
USE_GOOGLE_API=1
```

### 4️⃣ Run the app locally 🚀

```bash
streamlit run app.py
```

## 🔍 How It Works

📌 **`app.py`** — Streamlit UI: collects **Topic**, **Branch**, and number of questions, renders quiz, evaluates answers, and displays results.

📌 **`quiz_gen.py`** — Generates quizzes. If `GOOGLE_API_KEY` and `USE_GOOGLE_API=1` are set, it tries the **Google Generative API**; otherwise, it uses a **local JSON fallback generator**. Responses are validated before use ✅

📌 **`nlp.py`** — Detects **weak topic areas** using a **Hugging Face zero-shot classifier** if `transformers` is available; otherwise, a keyword-based fallback is used 🧠

## 🔐 Environment Variables

🔑 **`GOOGLE_API_KEY`** — API key for Google Generative AI *(Optional)*
⚙️ **`USE_GOOGLE_API`** — Set to `1` to enable Google API usage; otherwise, the app uses the local generator.
