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
    try:
        from transformers import pipeline
        return pipeline("zero-shot-classification",
                        model="facebook/bart-large-mnli")
    except Exception:
        # Fallback dummy classifier if transformers isn't installed or fails.
        class DummyClassifier:
            def __call__(self, sequence, candidate_labels):
                # return equal low-confidence scores so app can continue
                n = len(candidate_labels)
                return {
                    'labels': candidate_labels,
                    'scores': [1.0 / n] * n
                }

        return DummyClassifier()

def detect_weak_areas(wrong_questions, branch):
    if not wrong_questions:
        return []
    
    topics    = TOPICS.get(branch, ["Theory","Concepts","Problem Solving"])
    classifier = load_classifier()
    scores    = {}
    
    for q in wrong_questions:
        try:
            result = classifier(q, topics)
        except Exception:
            # If classifier fails for any reason, assign all topics equal score
            result = {'labels': topics, 'scores': [1.0 / len(topics)] * len(topics)}
        for t, s in zip(result['labels'], result['scores']):
            scores[t] = scores.get(t, 0) + s
    
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]