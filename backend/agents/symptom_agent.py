"""
TriageAI — Symptom Agent
Mirrors FinSight's Reporter Agent pattern: single-domain specialist.
Analyses ONLY symptom questionnaire data and returns a structured JSON assessment.
"""

import json
from tools.groq_utils import call_groq as call_claude, parse_llm_json

SYMPTOM_SYSTEM = """
You are an emergency physician specialising in symptom pattern recognition for a Malaysian hospital ED.
You analyse ONLY the symptom data provided — do not factor in vitals or visual observations.

Clinical urgency patterns to recognise:
- Sudden crushing chest pain radiating to arm/jaw = high cardiac risk (ACS/STEMI)
- Loss of consciousness = immediate neurological or cardiac risk
- Severe uncontrolled bleeding = haemorrhagic emergency
- Difficulty breathing = respiratory compromise
- Sudden severe headache = potential intracranial event (SAH)
- Abdominal pain + fever + vomiting = possible sepsis / surgical abdomen
- Gradual limb pain with weight-bearing = lower urgency musculoskeletal

Return ONLY a JSON object with these exact keys:
  recommended_zone: integer 1-5
  pattern_label: "e.g. possible ACS, musculoskeletal injury, GI illness, respiratory distress"
  urgency: "immediate" | "urgent" | "moderate" | "low"
  findings: "1-2 sentence clinical summary of the symptom picture"
  red_flags: ["specific red flag found", "...or empty list if none"]
  symptom_score: float 0-100 (100 = worst/most critical)

No markdown. Valid JSON only.
"""


def run_symptom_agent(symptoms: dict) -> dict:
    """Analyse symptom data and return structured assessment."""
    print("  [SYMPTOM AGENT] Analysing symptom patterns...")

    user = (
        f"Analyse these patient symptoms and return your structured assessment:\n"
        f"{json.dumps(symptoms, indent=2)}"
    )

    raw = call_claude(SYMPTOM_SYSTEM, user)
    result = parse_llm_json(raw)
    result["agent"] = "symptom"
    print(f"  [SYMPTOM AGENT] Zone {result.get('recommended_zone')} — {result.get('pattern_label')}")
    return result


if __name__ == "__main__":
    sample = {
        "pain_location": "chest", "pain_severity": 9, "onset_type": "sudden",
        "duration": "1-6hr", "chest_crushing": True, "chest_radiating": True,
        "abdomen_vomiting": False, "abdomen_fever": False,
        "limb_deformity": False, "limb_weight_bearing": True,
        "loss_of_consciousness": False, "difficulty_breathing": True,
        "bleeding_severe": False
    }
    import json as _json
    print(_json.dumps(run_symptom_agent(sample), indent=2))
