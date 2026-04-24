"""
Synthetic training data generator for the TriageAI XGBoost model.

Generates patient records with realistic vital signs, symptom profiles,
and visual flags. Labels are assigned using clinical thresholds from
the Malaysian Triage Scale and published medical literature.
"""

import numpy as np
import pandas as pd
import os

SEED = 42
NUM_SAMPLES = 6000  # 1200 per zone


def generate_vitals(zone: int, n: int, rng: np.random.Generator) -> dict:
    """Generate vital signs appropriate for a given triage zone."""

    if zone == 1:  # Critical
        systolic = rng.normal(75, 12, n).clip(40, 100)
        diastolic = rng.normal(40, 10, n).clip(20, 60)
        hr = np.concatenate([
            rng.normal(160, 15, n // 2).clip(140, 220),  # Tachycardic
            rng.normal(35, 5, n - n // 2).clip(20, 45),  # Bradycardic
        ])
        rng.shuffle(hr)
        spo2 = rng.normal(82, 5, n).clip(50, 90)
        temp = np.concatenate([
            rng.normal(40.5, 0.5, n // 2).clip(40, 43),  # Hyperthermia
            rng.normal(34, 0.8, n - n // 2).clip(30, 35),  # Hypothermia
        ])
        rng.shuffle(temp)
        resp_rate = rng.normal(35, 6, n).clip(25, 60)

    elif zone == 2:  # Very urgent
        systolic = rng.normal(92, 10, n).clip(70, 115)
        diastolic = rng.normal(55, 8, n).clip(35, 75)
        hr = rng.normal(120, 18, n).clip(90, 155)
        spo2 = rng.normal(90, 3, n).clip(84, 95)
        temp = np.concatenate([
            rng.normal(39.5, 0.5, n // 2).clip(38.5, 41),
            rng.normal(35.5, 0.5, n - n // 2).clip(34.5, 36.5),
        ])
        rng.shuffle(temp)
        resp_rate = rng.normal(28, 4, n).clip(22, 40)

    elif zone == 3:  # Urgent
        systolic = rng.normal(130, 15, n).clip(100, 165)
        diastolic = rng.normal(82, 10, n).clip(60, 105)
        hr = rng.normal(100, 12, n).clip(75, 130)
        spo2 = rng.normal(95, 1.5, n).clip(91, 98)
        temp = rng.normal(38.3, 0.5, n).clip(37, 39.5)
        resp_rate = rng.normal(22, 3, n).clip(16, 30)

    elif zone == 4:  # Semi-urgent
        systolic = rng.normal(122, 10, n).clip(105, 145)
        diastolic = rng.normal(78, 7, n).clip(60, 95)
        hr = rng.normal(80, 10, n).clip(60, 105)
        spo2 = rng.normal(97, 1, n).clip(95, 100)
        temp = rng.normal(37.2, 0.4, n).clip(36.2, 38)
        resp_rate = rng.normal(17, 2, n).clip(12, 22)

    else:  # Zone 5 — Non-urgent
        systolic = rng.normal(118, 8, n).clip(105, 140)
        diastolic = rng.normal(75, 6, n).clip(60, 90)
        hr = rng.normal(72, 8, n).clip(55, 95)
        spo2 = rng.normal(98, 0.7, n).clip(96, 100)
        temp = rng.normal(36.8, 0.3, n).clip(36.0, 37.5)
        resp_rate = rng.normal(15, 1.5, n).clip(10, 19)

    return {
        "systolic_bp": np.round(systolic, 1),
        "diastolic_bp": np.round(diastolic, 1),
        "heart_rate": np.round(hr, 1),
        "spo2": np.round(spo2, 1),
        "temperature": np.round(temp, 1),
        "respiratory_rate": np.round(resp_rate, 1),
    }


def generate_symptoms(zone: int, n: int, rng: np.random.Generator) -> dict:
    """Generate symptom profiles appropriate for a given triage zone."""

    locations = ["chest", "abdomen", "head", "limb", "back", "other"]

    if zone == 1:
        pain_location = rng.choice(["chest", "head", "abdomen"], n, p=[0.5, 0.3, 0.2])
        pain_severity = rng.integers(8, 11, n)
        onset_type = rng.choice(["sudden", "gradual"], n, p=[0.85, 0.15])
        duration = rng.choice(["<1hr", "1-6hr"], n, p=[0.8, 0.2])
        chest_crushing = (pain_location == "chest") & (rng.random(n) > 0.15)
        chest_radiating = (pain_location == "chest") & (rng.random(n) > 0.25)
        loss_of_consciousness = rng.random(n) > 0.4
        difficulty_breathing = rng.random(n) > 0.2
        bleeding_severe = rng.random(n) > 0.65

    elif zone == 2:
        pain_location = rng.choice(["chest", "abdomen", "head", "limb"], n, p=[0.3, 0.3, 0.2, 0.2])
        pain_severity = rng.integers(6, 10, n)
        onset_type = rng.choice(["sudden", "gradual"], n, p=[0.6, 0.4])
        duration = rng.choice(["<1hr", "1-6hr", "6-24hr"], n, p=[0.5, 0.35, 0.15])
        chest_crushing = (pain_location == "chest") & (rng.random(n) > 0.35)
        chest_radiating = (pain_location == "chest") & (rng.random(n) > 0.5)
        loss_of_consciousness = rng.random(n) > 0.75
        difficulty_breathing = rng.random(n) > 0.4
        bleeding_severe = rng.random(n) > 0.8

    elif zone == 3:
        pain_location = rng.choice(locations, n, p=[0.1, 0.25, 0.15, 0.25, 0.15, 0.1])
        pain_severity = rng.integers(4, 8, n)
        onset_type = rng.choice(["sudden", "gradual"], n, p=[0.35, 0.65])
        duration = rng.choice(["<1hr", "1-6hr", "6-24hr", ">24hr"], n, p=[0.15, 0.35, 0.35, 0.15])
        chest_crushing = np.zeros(n, dtype=bool)
        chest_radiating = np.zeros(n, dtype=bool)
        loss_of_consciousness = rng.random(n) > 0.92
        difficulty_breathing = rng.random(n) > 0.7
        bleeding_severe = np.zeros(n, dtype=bool)

    elif zone == 4:
        pain_location = rng.choice(locations, n, p=[0.02, 0.12, 0.08, 0.45, 0.23, 0.1])
        pain_severity = rng.integers(2, 6, n)
        onset_type = rng.choice(["sudden", "gradual"], n, p=[0.2, 0.8])
        duration = rng.choice(["1-6hr", "6-24hr", ">24hr"], n, p=[0.25, 0.4, 0.35])
        chest_crushing = np.zeros(n, dtype=bool)
        chest_radiating = np.zeros(n, dtype=bool)
        loss_of_consciousness = np.zeros(n, dtype=bool)
        difficulty_breathing = rng.random(n) > 0.9
        bleeding_severe = np.zeros(n, dtype=bool)

    else:  # Zone 5
        pain_location = rng.choice(locations, n, p=[0.01, 0.05, 0.05, 0.4, 0.19, 0.3])
        pain_severity = rng.integers(0, 4, n)
        onset_type = rng.choice(["sudden", "gradual"], n, p=[0.05, 0.95])
        duration = rng.choice(["6-24hr", ">24hr"], n, p=[0.3, 0.7])
        chest_crushing = np.zeros(n, dtype=bool)
        chest_radiating = np.zeros(n, dtype=bool)
        loss_of_consciousness = np.zeros(n, dtype=bool)
        difficulty_breathing = np.zeros(n, dtype=bool)
        bleeding_severe = np.zeros(n, dtype=bool)

    abdomen_vomiting = ((pain_location == "abdomen") & (rng.random(n) > (0.3 if zone <= 2 else 0.6))).astype(bool)
    abdomen_fever = ((pain_location == "abdomen") & (rng.random(n) > (0.3 if zone <= 3 else 0.7))).astype(bool)
    limb_deformity = ((pain_location == "limb") & (rng.random(n) > (0.4 if zone <= 3 else 0.8))).astype(bool)
    limb_weight_bearing = ~((pain_location == "limb") & (rng.random(n) > (0.3 if zone <= 3 else 0.7)))

    return {
        "pain_location": pain_location,
        "pain_severity": pain_severity,
        "onset_type": onset_type,
        "duration": duration,
        "chest_crushing": chest_crushing.astype(int),
        "chest_radiating": chest_radiating.astype(int),
        "abdomen_vomiting": abdomen_vomiting.astype(int),
        "abdomen_fever": abdomen_fever.astype(int),
        "limb_deformity": limb_deformity.astype(int),
        "limb_weight_bearing": limb_weight_bearing.astype(int),
        "loss_of_consciousness": loss_of_consciousness.astype(int),
        "difficulty_breathing": difficulty_breathing.astype(int),
        "bleeding_severe": bleeding_severe.astype(int),
    }


def generate_visual_flags(zone: int, n: int, rng: np.random.Generator) -> dict:
    """Generate visual detection flags appropriate for a given triage zone."""

    if zone == 1:
        pallor = (rng.random(n) > 0.25).astype(int)
        cyanosis = (rng.random(n) > 0.3).astype(int)
        diaphoresis = (rng.random(n) > 0.2).astype(int)
        gait_abnormality = (rng.random(n) > 0.35).astype(int)
        facial_grimacing = (rng.random(n) > 0.15).astype(int)

    elif zone == 2:
        pallor = (rng.random(n) > 0.45).astype(int)
        cyanosis = (rng.random(n) > 0.7).astype(int)
        diaphoresis = (rng.random(n) > 0.4).astype(int)
        gait_abnormality = (rng.random(n) > 0.5).astype(int)
        facial_grimacing = (rng.random(n) > 0.3).astype(int)

    elif zone == 3:
        pallor = (rng.random(n) > 0.7).astype(int)
        cyanosis = (rng.random(n) > 0.92).astype(int)
        diaphoresis = (rng.random(n) > 0.7).astype(int)
        gait_abnormality = (rng.random(n) > 0.65).astype(int)
        facial_grimacing = (rng.random(n) > 0.45).astype(int)

    elif zone == 4:
        pallor = (rng.random(n) > 0.88).astype(int)
        cyanosis = (rng.random(n) > 0.97).astype(int)
        diaphoresis = (rng.random(n) > 0.9).astype(int)
        gait_abnormality = (rng.random(n) > 0.8).astype(int)
        facial_grimacing = (rng.random(n) > 0.6).astype(int)

    else:  # Zone 5
        pallor = (rng.random(n) > 0.95).astype(int)
        cyanosis = np.zeros(n, dtype=int)
        diaphoresis = (rng.random(n) > 0.96).astype(int)
        gait_abnormality = (rng.random(n) > 0.92).astype(int)
        facial_grimacing = (rng.random(n) > 0.85).astype(int)

    return {
        "pallor": pallor,
        "cyanosis": cyanosis,
        "diaphoresis": diaphoresis,
        "gait_abnormality": gait_abnormality,
        "facial_grimacing": facial_grimacing,
    }


def generate_dataset(num_samples: int = NUM_SAMPLES, seed: int = SEED) -> pd.DataFrame:
    """Generate the full synthetic training dataset."""
    rng = np.random.default_rng(seed)
    samples_per_zone = num_samples // 5

    all_rows = []

    for zone in range(1, 6):
        n = samples_per_zone
        vitals = generate_vitals(zone, n, rng)
        symptoms = generate_symptoms(zone, n, rng)
        visual = generate_visual_flags(zone, n, rng)

        for i in range(n):
            row = {
                "zone": zone,
                # Vitals
                "systolic_bp": vitals["systolic_bp"][i],
                "diastolic_bp": vitals["diastolic_bp"][i],
                "heart_rate": vitals["heart_rate"][i],
                "spo2": vitals["spo2"][i],
                "temperature": vitals["temperature"][i],
                "respiratory_rate": vitals["respiratory_rate"][i],
                # Symptoms
                "pain_location": symptoms["pain_location"][i],
                "pain_severity": symptoms["pain_severity"][i],
                "onset_sudden": 1 if symptoms["onset_type"][i] == "sudden" else 0,
                "duration_hours": {"<1hr": 0.5, "1-6hr": 3, "6-24hr": 12, ">24hr": 36}[symptoms["duration"][i]],
                "chest_crushing": symptoms["chest_crushing"][i],
                "chest_radiating": symptoms["chest_radiating"][i],
                "abdomen_vomiting": symptoms["abdomen_vomiting"][i],
                "abdomen_fever": symptoms["abdomen_fever"][i],
                "limb_deformity": symptoms["limb_deformity"][i],
                "limb_weight_bearing": symptoms["limb_weight_bearing"][i],
                "loss_of_consciousness": symptoms["loss_of_consciousness"][i],
                "difficulty_breathing": symptoms["difficulty_breathing"][i],
                "bleeding_severe": symptoms["bleeding_severe"][i],
                # Visual
                "pallor": visual["pallor"][i],
                "cyanosis": visual["cyanosis"][i],
                "diaphoresis": visual["diaphoresis"][i],
                "gait_abnormality": visual["gait_abnormality"][i],
                "facial_grimacing": visual["facial_grimacing"][i],
            }
            all_rows.append(row)

    df = pd.DataFrame(all_rows)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)  # Shuffle

    return df


if __name__ == "__main__":
    print("Generating synthetic training data...")
    df = generate_dataset()

    os.makedirs("backend/data", exist_ok=True)
    output_path = os.path.join("backend", "data", "training_data.csv")
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} samples -> {output_path}")
    print(f"\nZone distribution:\n{df['zone'].value_counts().sort_index()}")
    print(f"\nSample row:\n{df.iloc[0].to_dict()}")
