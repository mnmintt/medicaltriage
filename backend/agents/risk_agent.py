"""
TriageAI — Risk Agent
Cross-signal hidden risk detector — sees ALL patient data simultaneously.
Also receives specialist agent conclusions so it can flag disagreement
between agents as a risk signal in its own right.
"""

import json
from tools.groq_utils import call_groq as call_claude, parse_llm_json

RISK_SYSTEM = """
You are a patient safety officer and senior emergency physician for a Malaysian hospital ED.
Your role is to detect non-obvious clinical risks by looking across ALL patient signals simultaneously.
Individual agents analyse single domains. You find the dangerous COMBINATIONS they might each miss.

Patterns to look for:
- Normal BP but tachycardia + pallor = compensated shock (will decompensate suddenly)
- Low pain score but cyanosis = patient cannot report distress (cognitive impairment / severe illness)
- Sudden onset + chest pain + diaphoresis = silent MI (especially elderly/diabetic)
- Normal vitals but loss of consciousness = syncope / neurological event
- Gradual onset but high fever + vomiting = sepsis masquerading as GI illness
- Breathing difficulty + low SpO2 + facial grimacing = severe respiratory failure
- Chest pain + tachycardia + diaphoresis + pallor together = cardiogenic shock risk

Agent disagreement rule:
- If specialist agents recommend different zones (e.g. vitals=Zone 2, symptom=Zone 4),
  treat the disagreement itself as a risk signal. It means the picture is unclear
  and the patient should be escalated and flagged for nurse review.

Return ONLY a JSON object with these exact keys:
  recommended_zone: integer 1-5
  hidden_risks: ["cross-signal risk found", "...or empty list if none"]
  escalate: true | false
  findings: "1-2 sentence summary of cross-signal analysis"
  risk_score: float 0-100 (100 = highest hidden risk)

No markdown. Valid JSON only.
"""


def run_risk_agent(vitals: dict, symptoms: dict, visual_flags: dict,
                   vitals_out: dict = None, symptom_out: dict = None,
                   visual_out: dict = None) -> dict:
    """Detect cross-signal hidden risks across all patient data.

    Args:
        vitals, symptoms, visual_flags: raw patient input dicts
        vitals_out, symptom_out, visual_out: specialist agent conclusions (optional).
            When provided, the risk agent can flag inter-agent disagreement.
    """
    print("  [RISK AGENT] Scanning for cross-signal hidden risks...")

    # Build the agent disagreement section if conclusions are available
    agent_context = ""
    if vitals_out and symptom_out and visual_out:
        zones = {
            "vitals":  vitals_out.get("recommended_zone"),
            "symptom": symptom_out.get("recommended_zone"),
            "visual":  visual_out.get("recommended_zone"),
        }
        unique_zones = set(z for z in zones.values() if z is not None)
        disagreement = len(unique_zones) > 1

        agent_context = (
            f"\nSPECIALIST AGENT CONCLUSIONS:\n"
            f"  Vitals agent  → Zone {zones['vitals']}  | {vitals_out.get('severity', '?')} | {vitals_out.get('findings', '')}\n"
            f"  Symptom agent → Zone {zones['symptom']} | {symptom_out.get('urgency', '?')} | {symptom_out.get('findings', '')}\n"
            f"  Visual agent  → Zone {zones['visual']}  | {visual_out.get('visual_severity', '?')} | {visual_out.get('findings', '')}\n"
            f"  Agent disagreement: {disagreement} (zones: {list(zones.values())})\n"
        )

    user = (
        f"Analyse ALL patient data for hidden cross-signal risks:\n\n"
        f"VITALS: {json.dumps(vitals)}\n"
        f"SYMPTOMS: {json.dumps(symptoms)}\n"
        f"VISUAL FLAGS: {json.dumps(visual_flags)}\n"
        f"{agent_context}\n"
        f"Return your cross-signal risk assessment."
    )

    raw = call_claude(RISK_SYSTEM, user)
    result = parse_llm_json(raw)
    result["agent"] = "risk"
    escalate = result.get("escalate", False)
    print(f"  [RISK AGENT] Zone {result.get('recommended_zone')} — escalate={escalate}")
    return result


if __name__ == "__main__":
    vitals = {"systolic_bp": 110, "diastolic_bp": 70, "heart_rate": 125,
              "spo2": 94, "temperature": 37.2, "respiratory_rate": 18}
    symptoms = {"pain_location": "chest", "pain_severity": 3, "onset_type": "sudden",
                "duration": "1-6hr", "chest_crushing": False, "chest_radiating": False,
                "loss_of_consciousness": False, "difficulty_breathing": False,
                "bleeding_severe": False, "abdomen_vomiting": False, "abdomen_fever": False,
                "limb_deformity": False, "limb_weight_bearing": True}
    visual = {"pallor": True, "cyanosis": False, "diaphoresis": True,
              "gait_abnormality": False, "facial_grimacing": False}

    # Simulate specialist outputs showing disagreement
    vitals_out = {"recommended_zone": 2, "severity": "high",
                  "findings": "Tachycardia with borderline SpO2."}
    symptom_out = {"recommended_zone": 4, "urgency": "low",
                   "findings": "Low pain score, no red flags reported."}
    visual_out = {"recommended_zone": 3, "visual_severity": "moderate",
                  "findings": "Pallor and diaphoresis noted."}

    import json as _json
    print(_json.dumps(
        run_risk_agent(vitals, symptoms, visual,
                       vitals_out=vitals_out,
                       symptom_out=symptom_out,
                       visual_out=visual_out),
        indent=2
    ))