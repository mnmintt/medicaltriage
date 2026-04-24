"""
XGBoost model training script for TriageAI.

Trains a multi-class classifier on synthetic clinical data to predict
triage zones (1-5) from vital signs, symptoms, and visual flags.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier
import joblib


# ─── Feature columns ──────────────────────────────────────────────────────────

NUMERIC_FEATURES = [
    "systolic_bp", "diastolic_bp", "heart_rate", "spo2",
    "temperature", "respiratory_rate", "pain_severity",
    "duration_hours",
]

BINARY_FEATURES = [
    "onset_sudden", "chest_crushing", "chest_radiating",
    "abdomen_vomiting", "abdomen_fever", "limb_deformity",
    "limb_weight_bearing", "loss_of_consciousness",
    "difficulty_breathing", "bleeding_severe",
    "pallor", "cyanosis", "diaphoresis",
    "gait_abnormality", "facial_grimacing",
]

CATEGORICAL_FEATURES = ["pain_location"]

ALL_PAIN_LOCATIONS = ["chest", "abdomen", "head", "limb", "back", "other"]


def prepare_features(df: pd.DataFrame, scaler: StandardScaler = None, fit: bool = False):
    """Transform raw data into model-ready feature matrix."""

    # One-hot encode pain_location
    location_dummies = pd.get_dummies(df["pain_location"], prefix="loc")
    # Ensure all location columns are present
    for loc in ALL_PAIN_LOCATIONS:
        col = f"loc_{loc}"
        if col not in location_dummies.columns:
            location_dummies[col] = 0
    location_dummies = location_dummies[[f"loc_{loc}" for loc in ALL_PAIN_LOCATIONS]]

    # Combine numeric + binary + one-hot features
    X = pd.concat([
        df[NUMERIC_FEATURES],
        df[BINARY_FEATURES],
        location_dummies,
    ], axis=1).astype(float)

    # Scale numeric features
    if fit:
        scaler = StandardScaler()
        X[NUMERIC_FEATURES] = scaler.fit_transform(X[NUMERIC_FEATURES])
    else:
        X[NUMERIC_FEATURES] = scaler.transform(X[NUMERIC_FEATURES])

    return X, scaler


def train():
    """Train XGBoost model and save artifacts."""
    data_path = os.path.join("backend", "data", "training_data.csv")
    if not os.path.exists(data_path):
        print("Training data not found. Run generate_training_data.py first.")
        return

    print("Loading training data...")
    df = pd.read_csv(data_path)
    print(f"  {len(df)} samples loaded")

    # Prepare features
    X, scaler = prepare_features(df, fit=True)
    y = df["zone"].values - 1  # XGBoost expects 0-indexed classes

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    # Train XGBoost
    print("\nTraining XGBoost classifier...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        objective="multi:softprob",
        num_class=5,
        eval_metric="mlogloss",
        use_label_encoder=False,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    zone_names = [f"Zone {i+1}" for i in range(5)]
    print(classification_report(y_test, y_pred, target_names=zone_names))

    # Feature importance (top 10)
    importance = model.feature_importances_
    feature_names = X.columns.tolist()
    top_features = sorted(zip(feature_names, importance), key=lambda x: -x[1])[:10]
    print("Top 10 Features:")
    for name, imp in top_features:
        print(f"  {name}: {imp:.4f}")

    # Save model artifacts
    model_dir = os.path.join("backend", "model")
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, "triage_model.joblib")
    scaler_path = os.path.join(model_dir, "scaler.joblib")
    features_path = os.path.join(model_dir, "feature_names.joblib")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(feature_names, features_path)

    print(f"\nModel saved -> {model_path}")
    print(f"Scaler saved -> {scaler_path}")
    print(f"Feature names saved -> {features_path}")


if __name__ == "__main__":
    train()
