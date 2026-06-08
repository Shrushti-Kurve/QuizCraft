# nlp.py
import re

import streamlit as st

TOPICS = {
    "Data Science":       ["Statistics","Machine Learning","Python",
                           "Deep Learning","SQL","Feature Engineering"],
    "Computer Science":   ["Data Structures","Algorithms","OS",
                           "Networks","DBMS","OOP"],
    "Web Development":    ["HTML/CSS","JavaScript","React",
                           "Backend","Databases","Git"],
    "Electronics":        ["Digital Electronics","Analog Circuits",
                           "Signals","Microprocessors","Communication"],
    "Mechanical":         ["Thermodynamics","Fluid Mechanics",
                           "Manufacturing","Design","Materials"],
}

@st.cache_resource
def load_classifier():
    try:
        from transformers import pipeline
    except Exception:
        return None

    try:
        return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    except Exception:
        return None


def _keyword_fallback(wrong_questions, branch):
    topics = TOPICS.get(branch, ["Theory", "Concepts", "Problem Solving"])
    scores = {topic: 0 for topic in topics}
    text = " ".join(wrong_questions).lower()

    for topic in topics:
        words = re.findall(r"[a-z0-9]+", topic.lower())
        if any(word in text for word in words):
            scores[topic] += 2
        if topic.lower() in text:
            scores[topic] += 3

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    ranked = [item for item in ranked if item[1] > 0]
    if ranked:
        return ranked[:3]

    return [(topic, 1) for topic in topics[:3]]

def detect_weak_areas(wrong_questions, branch):
    if not wrong_questions:
        return []
    
    topics    = TOPICS.get(branch, ["Theory","Concepts","Problem Solving"])
    classifier = load_classifier()
    if classifier is None:
        return _keyword_fallback(wrong_questions, branch)
    scores    = {}
    
    for q in wrong_questions:
        result = classifier(q, topics)
        for t, s in zip(result['labels'], result['scores']):
            scores[t] = scores.get(t, 0) + s
    
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]