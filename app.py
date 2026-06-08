# app.py
import streamlit as st
from quiz_gen import generate_quiz
from nlp import detect_weak_areas

st.set_page_config(page_title="QuizCraft", page_icon="📝", layout="centered")

# Session state init
for k, v in {
    "questions": None, "answers": {}, "submitted": False,
    "topic": ""
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Header ──
st.title("📝 QuizCraft")
st.write("Generate AI-powered quizzes on any topic. Know your weak areas instantly.")
st.divider()

# ── Input ──
if not st.session_state.questions or st.session_state.submitted:
    topic = st.text_input("Topic",
                          placeholder="e.g. Random Forest, SQL Joins, Recursion")
    
    num_q = st.slider("Number of questions", 3, 10, 5)
    
    if st.button("🎯 Generate Quiz", type="primary", use_container_width=True):
        if topic:
            with st.spinner("Generating questions with AI..."):
                qs, err = generate_quiz(topic, num_q)
            if qs:
                st.session_state.questions = qs
                st.session_state.topic     = topic
                st.session_state.answers   = {}
                st.session_state.submitted = False
                st.rerun()
            else:
                st.error(err)
        else:
            st.warning("Enter a topic first")

# ── Quiz ──
if st.session_state.questions and not st.session_state.submitted:
    st.subheader(f"Topic: {st.session_state.topic}")
    st.divider()
    
    for i, q in enumerate(st.session_state.questions):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        opts = [f"{k}:  {v}" for k, v in q['options'].items()]
        choice = st.radio("", opts, key=f"q_{i}",
                          label_visibility="collapsed")
        if choice:
            st.session_state.answers[i] = choice[0]
        st.write("")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Submit Quiz ✅", type="primary", use_container_width=True):
            if len(st.session_state.answers) == len(st.session_state.questions):
                st.session_state.submitted = True
                st.rerun()
            else:
                st.warning("Answer all questions first!")
    with col2:
        if st.button("Start Over 🔄", use_container_width=True):
            st.session_state.questions = None
            st.rerun()

# ── Results ──
if st.session_state.submitted:
    st.subheader("Results 📊")
    
    correct, wrong_qs = 0, []
    
    for i, q in enumerate(st.session_state.questions):
        ua = st.session_state.answers.get(i, "")
        ca = q["correct_answer"]

        if ua == ca:
            st.success(f"✅ Q{i+1}: Correct")
            correct += 1
        else:
            ua_text = q["options"].get(ua, ua)
            ca_text = q["options"].get(ca, ca)
            st.error(f"❌ Q{i+1}: You chose {ua}: {ua_text} — Correct: {ca}: {ca_text}")
            with st.expander("💡 Explanation"):
                st.write("**Question:**", q["question"])
                st.write("**Your answer:**", f"{ua}: {ua_text}")
                st.write("**Correct answer:**", f"{ca}: {ca_text}")
                st.write("")
                st.write(q["explanation"])
            wrong_qs.append(q["question"])
    
    total = len(st.session_state.questions)
    pct   = (correct / total) * 100
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Score",    f"{pct:.0f}%")
    c2.metric("Correct",  f"{correct}/{total}")
    c3.metric("Wrong",    f"{total - correct}/{total}")
    
    # Weak areas
    if wrong_qs:
        st.divider()
        st.subheader("🎯 Your Weak Areas")
        st.write("Based on what you got wrong, focus on these:")
        
        with st.spinner("Analysing with NLP..."):
            weak = detect_weak_areas(wrong_qs)
        
        if weak:
            for i, (topic_w, _) in enumerate(weak, 1):
                st.warning(f"{i}. {topic_w}")
        
        st.info("💡 Tip: Search these topics on YouTube or ask your professor.")
    
    if st.button("Take Another Quiz 🔄", use_container_width=True, type="primary"):
        st.session_state.questions = None
        st.session_state.submitted = False
        st.rerun()