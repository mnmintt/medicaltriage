"""
TriageAI API Server
Mirrors FinSight's server.py pattern exactly:
  Flask + CORS → calls orchestrator → returns structured JSON.

Routes:
  GET  /api/health
  POST /api/triage          — submit patient for triage (runs AI swarm)
  GET  /api/patients        — list active waiting patients
  GET  /api/patients/<id>   — get single patient record
  PATCH /api/patients/<id>/override — nurse zone override
  DELETE /api/patients/<id> — discharge patient
  GET  /api/queue-stats     — zone counts + flagged count
  GET  /api/demo            — mock result for UI testing (no API calls)
"""

import os
import sys
import uuid
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Ensure backend root is on path so `agents` and `tools` are importable (mirrors FinSight)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import run_orchestrator

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"))
CORS(app)

# ─── In-memory store (mirrors FinSight's simple dict pattern) ────────────────
patients: dict[str, dict] = {}

# XGBoost engine (optional — graceful fallback if model files missing)
engine = None


def _load_engine():
    global engine
    try:
        from triage_engine import TriageEngine
        engine = TriageEngine()
        print("[OK] TriageEngine (XGBoost) loaded")
    except Exception as e:
        print(f"[WARN] TriageEngine not loaded: {e} — will use zone 3 as XGBoost fallback")


# ─── Zone metadata ────────────────────────────────────────────────────────────
ZONE_COLOURS = {1: "Red", 2: "Orange", 3: "Yellow", 4: "Green", 5: "Blue"}
ZONE_LABELS = {
    1: "Life-threatening — resuscitation required",
    2: "Very urgent — may deteriorate rapidly",
    3: "Urgent — stable but requires prompt attention",
    4: "Semi-urgent — minor illness or injury",
    5: "Non-urgent — can be seen by GP or clinic",
}


def estimate_wait_time(zone: int, queue_position: int) -> int:
    base = {1: 0, 2: 10, 3: 30, 4: 55, 5: 100}
    per_patient = {1: 0, 2: 3, 3: 5, 4: 8, 5: 10}
    return base[zone] + (queue_position - 1) * per_patient[zone]


def get_queue_stats() -> dict:
    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for p in patients.values():
        if p["status"] == "waiting":
            counts[p["effective_zone"]] += 1
    return counts


def get_queue_position(zone: int) -> int:
    return sum(1 for p in patients.values()
               if p["effective_zone"] == zone and p["status"] == "waiting") + 1


def xgboost_predict(vitals: dict, symptoms: dict, visual_flags: dict) -> dict:
    """Run XGBoost if available, else return a safe default."""
    if engine is None:
        return {"zone": 3, "confidence": 50.0,
                "probabilities": {"zone_1": 5, "zone_2": 15, "zone_3": 50, "zone_4": 20, "zone_5": 10}}
    try:
        from models import VitalsInput, SymptomInput, VisualFlags
        v = VitalsInput(**vitals)
        s = SymptomInput(**symptoms)
        vf = VisualFlags(**visual_flags)
        return engine.predict(v, s, vf)
    except Exception as e:
        print(f"[XGBoost ERROR] {e}")
        return {"zone": 3, "confidence": 50.0,
                "probabilities": {"zone_1": 5, "zone_2": 15, "zone_3": 50, "zone_4": 20, "zone_5": 10}}


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "TriageAI — Claude Swarm Edition",
        "engine_loaded": engine is not None,
        "active_patients": len(patients),
        "swarm": "llama-3.1-8b-instant (Groq)",
    })


@app.route("/api/triage", methods=["POST"])
def submit_triage():
    """
    POST /api/triage
    Body: { vitals, symptoms, visual_flags, patient_name?, language? }
    Returns: full patient record with triage result
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    vitals = data.get("vitals", {})
    symptoms = data.get("symptoms", {})
    visual_flags = data.get("visual_flags", {})
    patient_name = data.get("patient_name")

    if not vitals or not symptoms or not visual_flags:
        return jsonify({"error": "Missing vitals, symptoms, or visual_flags"}), 400

    try:
        # Step 1 — XGBoost raw prediction (ML signal for swarm)
        xgboost_result = xgboost_predict(vitals, symptoms, visual_flags)
        print(f"[XGBoost] Zone {xgboost_result['zone']} confidence {xgboost_result['confidence']}%")

        # Step 2 — Claude swarm via orchestrator (mirrors FinSight's run_orchestrator call)
        queue_stats = get_queue_stats()
        swarm_result = run_orchestrator(
            vitals=vitals,
            symptoms=symptoms,
            visual_flags=visual_flags,
            xgboost_result=xgboost_result,
            queue_stats=queue_stats,
        )

        # Step 3 — Build patient record
        zone = swarm_result["final_zone"]
        confidence = swarm_result["confidence"]
        scores = swarm_result["scores"]
        queue_pos = get_queue_position(zone)
        wait_mins = estimate_wait_time(zone, queue_pos)

        patient_id = str(uuid.uuid4())[:8].upper()

        record = {
            "id": patient_id,
            "patient_name": patient_name,
            "status": "waiting",
            "effective_zone": zone,
            "triaged_at": datetime.now().isoformat(),
            "nurse_override_zone": None,
            "nurse_override_reason": None,

            # Raw inputs (for swarm panel display)
            "vitals": vitals,
            "symptoms": symptoms,
            "visual_flags": visual_flags,

            # Full triage result — all text from Claude swarm
            "triage_result": {
                "zone": zone,
                "zone_colour": ZONE_COLOURS[zone],
                "zone_label": ZONE_LABELS[zone],
                "confidence": confidence,
                "composite_score": scores["composite_score"],
                "flagged_for_nurse": swarm_result["flagged_for_nurse"],
                "flag_reasons": swarm_result["flag_reasons"],

                # 100% from Claude swarm — never from templates
                "explanation": swarm_result["patient_explanation"],
                "clinical_narrative": swarm_result["clinical_narrative"],

                "estimated_wait_minutes": wait_mins,
                "queue_position": queue_pos,

                "input_breakdown": {
                    "vitals_score": scores["vitals_score"],
                    "symptom_score": scores["symptom_score"],
                    "visual_score": scores["visual_score"],
                    "composite_score": scores["composite_score"],
                    "critical_overrides": swarm_result["flag_reasons"],
                },

                # Swarm transparency
                "agent_outputs": swarm_result["agent_outputs"],
                "xgboost_prediction": xgboost_result,
                "swarm_ok": swarm_result["swarm_ok"],
            }
        }

        patients[patient_id] = record
        return jsonify(record)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/patients", methods=["GET"])
def list_patients():
    active = [p for p in patients.values() if p["status"] == "waiting"]
    return jsonify(sorted(active, key=lambda p: (p["effective_zone"], p["triaged_at"])))


@app.route("/api/patients/<patient_id>", methods=["GET"])
def get_patient(patient_id):
    if patient_id not in patients:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(patients[patient_id])


@app.route("/api/patients/<patient_id>/override", methods=["PATCH"])
def override_zone(patient_id):
    if patient_id not in patients:
        return jsonify({"error": "Patient not found"}), 404
    body = request.get_json()
    nz = body.get("new_zone")
    reason = body.get("reason", "")
    if not nz or nz not in range(1, 6):
        return jsonify({"error": "Invalid zone"}), 400

    p = patients[patient_id]
    p["nurse_override_zone"] = nz
    p["nurse_override_reason"] = reason
    p["effective_zone"] = nz
    p["triage_result"]["zone"] = nz
    p["triage_result"]["zone_colour"] = ZONE_COLOURS[nz]
    p["triage_result"]["zone_label"] = ZONE_LABELS[nz]
    p["triage_result"]["estimated_wait_minutes"] = estimate_wait_time(nz, get_queue_position(nz))
    p["triage_result"]["queue_position"] = get_queue_position(nz)
    return jsonify(p)


@app.route("/api/patients/<patient_id>", methods=["DELETE"])
def discharge_patient(patient_id):
    if patient_id not in patients:
        return jsonify({"error": "Patient not found"}), 404
    del patients[patient_id]
    return jsonify({"detail": "Patient discharged"})


@app.route("/api/queue-stats", methods=["GET"])
def queue_statistics():
    counts = get_queue_stats()
    flagged = sum(
        1 for p in patients.values()
        if p["triage_result"]["flagged_for_nurse"] and p["status"] == "waiting"
    )
    return jsonify({
        "zone_counts": counts,
        "total_patients": sum(counts.values()),
        "flagged_count": flagged,
    })


@app.route("/api/demo", methods=["GET"])
def demo():
    """Mock result for UI testing — no API calls consumed. Mirrors FinSight /demo."""
    mock = {
        "id": "DEMO001",
        "patient_name": "Demo Patient",
        "status": "waiting",
        "effective_zone": 2,
        "triaged_at": datetime.now().isoformat(),
        "nurse_override_zone": None,
        "nurse_override_reason": None,
        "vitals": {
            "systolic_bp": 90, "diastolic_bp": 60, "heart_rate": 128,
            "spo2": 91, "temperature": 38.5, "respiratory_rate": 26
        },
        "symptoms": {
            "pain_location": "chest", "pain_severity": 8, "onset_type": "sudden",
            "duration": "1-6hr", "chest_crushing": True, "chest_radiating": True,
            "difficulty_breathing": True, "loss_of_consciousness": False,
            "bleeding_severe": False, "abdomen_vomiting": False, "abdomen_fever": False,
            "limb_deformity": False, "limb_weight_bearing": True
        },
        "visual_flags": {
            "pallor": True, "cyanosis": False, "diaphoresis": True,
            "gait_abnormality": False, "facial_grimacing": True
        },
        "triage_result": {
            "zone": 2, "zone_colour": "Orange", "zone_label": "Very urgent — may deteriorate rapidly",
            "confidence": 88.0, "composite_score": 82.0,
            "flagged_for_nurse": True,
            "flag_reasons": ["Possible ACS pattern: crushing chest pain with radiation and diaphoresis"],
            "explanation": "You have been assessed as Zone 2 (Orange) — Very Urgent. Based on your symptoms and vital signs, you will be seen by a doctor within 10 minutes. Please remain seated and inform a nurse immediately if your chest pain worsens, you feel faint, or experience any new symptoms.",
            "clinical_narrative": "Patient presents with classic ACS pattern: sudden-onset crushing chest pain radiating with diaphoresis and pallor. Tachycardia and borderline hypoxia noted. Immediate cardiology review warranted.",
            "estimated_wait_minutes": 10,
            "queue_position": 1,
            "input_breakdown": {
                "vitals_score": 72.0, "symptom_score": 90.0,
                "visual_score": 65.0, "composite_score": 82.0,
                "critical_overrides": ["Possible ACS pattern"]
            },
            "agent_outputs": {
                "vitals": {
                    "agent": "vitals", "recommended_zone": 2,
                    "severity": "high", "vitals_score": 72.0,
                    "findings": "Tachycardia at 128bpm with borderline SpO2 of 91% and hypotension.",
                    "most_concerning_vital": "heart_rate"
                },
                "symptom": {
                    "agent": "symptom", "recommended_zone": 2,
                    "pattern_label": "Possible ACS", "urgency": "urgent",
                    "symptom_score": 90.0,
                    "findings": "Classic ACS presentation: sudden crushing chest pain radiating with breathing difficulty.",
                    "red_flags": ["Crushing chest pain", "Radiation pattern", "Difficulty breathing"]
                },
                "visual": {
                    "agent": "visual", "recommended_zone": 2,
                    "visual_severity": "high", "visual_score": 65.0,
                    "findings": "Pallor and diaphoresis together suggest sympathetic activation consistent with cardiac event.",
                    "shock_indicators": True
                },
                "risk": {
                    "agent": "risk", "recommended_zone": 2,
                    "escalate": True, "risk_score": 85.0,
                    "hidden_risks": ["Pallor + diaphoresis + tachycardia = possible compensated cardiogenic shock"],
                    "findings": "Cross-signal pattern strongly suggests early cardiogenic shock with ACS aetiology."
                },
                "coordinator": {
                    "final_zone": 2, "confidence": 88.0, "zone_agreement": True,
                    "flagged_for_nurse": True,
                    "clinical_narrative": "Patient presents with classic ACS pattern: sudden-onset crushing chest pain radiating with diaphoresis and pallor. Tachycardia and borderline hypoxia noted. Immediate cardiology review warranted.",
                    "patient_explanation": "You have been assessed as Zone 2 (Orange) — Very Urgent. Based on your symptoms and vital signs, you will be seen by a doctor within 10 minutes. Please remain seated and inform a nurse immediately if your chest pain worsens, you feel faint, or experience any new symptoms.",
                    "flag_reasons": ["Possible ACS pattern: crushing chest pain with radiation and diaphoresis"],
                    "vitals_score": 72.0, "symptom_score": 90.0,
                    "visual_score": 65.0, "composite_score": 82.0
                }
            },
            "xgboost_prediction": {"zone": 2, "confidence": 78.0,
                                   "probabilities": {"zone_1": 15, "zone_2": 78, "zone_3": 5, "zone_4": 1, "zone_5": 1}},
            "swarm_ok": True
        }
    }
    return jsonify(mock)


if __name__ == "__main__":
    _load_engine()
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
