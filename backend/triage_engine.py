"""
TriageAI Classification Engine.

Responsible ONLY for:
1. Feature extraction from raw patient inputs
2. XGBoost model inference (predict_proba)

All clinical rule logic, scoring, override detection, and explanation
generation have been moved to the Groq AI swarm (agents/).
"""

import os
import numpy as np
import pandas as pd
import joblib

from models import VitalsInput, SymptomInput, VisualFlags


NUMERIC_FEATURES = [
    "systolic_bp", "diastolic_bp", "heart_rate", "spo2",
    "temperature", "respiratory_rate", "pain_severity",
    "duration_hours",
]

ALL_PAIN_LOCATIONS = ["chest", "abdomen", "head", "limb", "back", "other"]

DURATION_MAP = {"<1hr": 0.5, "1-6hr": 3, "6-24hr": 12, ">24hr": 36}


class TriageEngine:
    """XGBoost triage model — feature extraction and inference only."""

    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.join(os.path.dirname(__file__), "model")

        self.model         = joblib.load(os.path.join(model_dir, "triage_model.joblib"))
        self.scaler        = joblib.load(os.path.join(model_dir, "scaler.joblib"))
        self.feature_names = joblib.load(os.path.join(model_dir, "feature_names.joblib"))
        print(f"TriageEngine loaded: {len(self.feature_names)} features")

    def _extract_features(
        self, vitals: VitalsInput, symptoms: SymptomInput, visual: VisualFlags
    ) -> pd.DataFrame:
        row = {
            "systolic_bp":           vitals.systolic_bp,
            "diastolic_bp":          vitals.diastolic_bp,
            "heart_rate":            vitals.heart_rate,
            "spo2":                  vitals.spo2,
            "temperature":           vitals.temperature,
            "respiratory_rate":      vitals.respiratory_rate,
            "pain_severity":         symptoms.pain_severity,
            "duration_hours":        DURATION_MAP.get(symptoms.duration, 3),
            "onset_sudden":          1 if symptoms.onset_type == "sudden" else 0,
            "chest_crushing":        int(symptoms.chest_crushing),
            "chest_radiating":       int(symptoms.chest_radiating),
            "abdomen_vomiting":      int(symptoms.abdomen_vomiting),
            "abdomen_fever":         int(symptoms.abdomen_fever),
            "limb_deformity":        int(symptoms.limb_deformity),
            "limb_weight_bearing":   int(symptoms.limb_weight_bearing),
            "loss_of_consciousness": int(symptoms.loss_of_consciousness),
            "difficulty_breathing":  int(symptoms.difficulty_breathing),
            "bleeding_severe":       int(symptoms.bleeding_severe),
            "pallor":                int(visual.pallor),
            "cyanosis":              int(visual.cyanosis),
            "diaphoresis":           int(visual.diaphoresis),
            "gait_abnormality":      int(visual.gait_abnormality),
            "facial_grimacing":      int(visual.facial_grimacing),
        }

        for loc in ALL_PAIN_LOCATIONS:
            row[f"loc_{loc}"] = 1 if symptoms.pain_location == loc else 0

        df = pd.DataFrame([row])
        df[NUMERIC_FEATURES] = self.scaler.transform(df[NUMERIC_FEATURES])
        return df[self.feature_names]

    def predict(
        self, vitals: VitalsInput, symptoms: SymptomInput, visual: VisualFlags
    ) -> dict:
        """
        Run XGBoost inference. Returns raw ML output only — no clinical rules.

        Returns:
            {
                "zone": int,           # 1-indexed predicted zone
                "confidence": float,   # % confidence in predicted class
                "probabilities": dict  # zone_1..zone_5 probabilities
            }
        """
        features = self._extract_features(vitals, symptoms, visual)
        proba = self.model.predict_proba(features)[0]
        predicted_class = int(np.argmax(proba))
        ml_zone = predicted_class + 1
        ml_confidence = round(float(proba[predicted_class]) * 100, 1)

        return {
            "zone": ml_zone,
            "confidence": ml_confidence,
            "probabilities": {
                f"zone_{i+1}": round(float(p) * 100, 1)
                for i, p in enumerate(proba)
            },
        }
