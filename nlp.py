# nlp.py
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
    from transformers import pipeline
    return pipeline("zero-shot-classification",
                    model="facebook/bart-large-mnli")

def detect_weak_areas(wrong_questions, branch):
    if not wrong_questions:
        return []
    
    topics    = TOPICS.get(branch, ["Theory","Concepts","Problem Solving"])
    classifier = load_classifier()
    scores    = {}
    
    for q in wrong_questions:
        result = classifier(q, topics)
        for t, s in zip(result['labels'], result['scores']):
            scores[t] = scores.get(t, 0) + s
    
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]