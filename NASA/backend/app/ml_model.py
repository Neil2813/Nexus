# app/ml_model.py
"""
Small local ML model to generate insights on dataset descriptions.
This trains a tiny TF-IDF + LogisticRegression classifier at startup on a small synthetic corpus.
It is intentionally lightweight so it runs anywhere.
"""
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os
from typing import List, Dict

MODEL_PATH = "./data/local_ml_model.joblib"
os.makedirs("./data", exist_ok=True)

class LocalMLModel:
    def __init__(self):
        self.model = None
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception:
                self.model = None
        if not self.model:
            self._train_default()

    def _train_default(self):
        # synthetic dataset
        texts = [
            "microgravity cell differentiation protein expression",
            "radiation exposure DNA damage repair",
            "plant growth in space microgravity photosynthesis",
            "mouse muscle atrophy microgravity physiology",
            "bacterial growth antibiotic resistance spaceflight",
            "epigenomics sequencing data RNA-seq microgravity",
            "spacecraft thermal environment hardware payload"
        ]
        labels = ["microgravity", "radiation", "microgravity", "microgravity", "microbiology", "genomics", "hardware"]
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1,2), max_features=2000)),
            ("clf", LogisticRegression(max_iter=1000))
        ])
        pipeline.fit(texts, labels)
        self.model = pipeline
        joblib.dump(self.model, MODEL_PATH)

    def predict_tags(self, texts: List[str]) -> List[Dict[str, float]]:
        # returns label and confidence score
        preds = self.model.predict(texts)
        probs = self.model.predict_proba(texts)
        labels = list(self.model.named_steps["clf"].classes_)
        results = []
        for p, pr in zip(preds, probs):
            # map classes to prob dictionary
            class_probs = {labels[i]: float(pr[i]) for i in range(len(labels))}
            results.append({"pred": p, "probs": class_probs})
        return results

# instantiate a singleton
local_ml = LocalMLModel()
