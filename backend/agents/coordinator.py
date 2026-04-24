"""
TriageAI — Coordinator Agent
The senior emergency physician. Mirrors FinSight's Reporter Agent:
takes all specialist outputs + XGBoost signal → produces the final structured result.

Outputs:
  - final_zone (1-5)
  - confidence
  - clinical_narrative (for nurse dashboard)
  - patient_explanation (for patient display screen)
  - flagged_for_nurse, flag_reasons
  - composite scores
"""

import json
from datetime import datetime, timezone
from tools.groq_utils import call_groq as call_claude, parse_llm_json

COORDINATOR_SYSTEM = """
You are the senior emergency physician and triage coordinator for a Malaysian hospital ED.
You receive assessments from four specialist AI agents plus an XGBoost ML model prediction.
Your job is to synthesise everything into one authoritative final triage decision.

Malaysian Triage Scale:
  Zone 1 — Red — Life-threatening, immediate resuscitation
  Zone 2 — Orange — Very urgent, seen within 10 minutes
  Zone 3 — Yellow — Urgent, seen within 30 minutes
  Zone 4 — Green — Semi-urgent, seen within 60 minutes
  Zone 5 — Blue — Non-urgent, seen within 120 minutes

Decision rules:
1. If agents disagree, use the most conservative (lowest zone number = more urgent) when uncertain.
2. Give serious weight to the risk agent if it recommends escalation (escalate: true).
3. confidence: high (≥85) if all agree, moderate (60-84) if mixed, low (<60) if opposing.
4. XGBoost ML confidence: if xgboost confidence < 60%, treat the 
   ML prediction as a weak signal only — rely more on agent reasoning.
   If XGBoost confidence >= 80%, it carries strong weight.
5. patient_explanation: empathetic plain language for patient display screen.
   Include: their zone colour and number, roughly how long they will wait, what to do if they feel worse.
   Do NOT use medical jargon. Keep it reassuring and clear.
6. flagged_for_nurse: true if escalate=true, or confidence < 70, or zone_agreement=false, or Zone 1/2.

Return ONLY a JSON object with these exact keys:
  final_zone: integer 1-5
  confidence: float 0-100
  flagged_for_nurse: true | false
  zone_agreement: true | false
  clinical_narrative: "nurse-facing clinical summary, 2-3 sentences"
  patient_explanation: "patient-facing plain-language explanation, 3-4 sentences"
  flag_reasons: ["safety concern for nurse", "...or empty list"]
  vitals_score: float 0-100
  symptom_score: float 0-100
  visual_score: float 0-100
  composite_score: float 0-100

No markdown. Valid JSON only.
"""


def run_coordinator(vitals_out: dict, symptom_out: dict, visual_out: dict,
                    risk_out: dict, xgboost_result: dict, queue_stats: dict) -> dict:
    """Synthesise all agent outputs into final triage result."""
    print("  [COORDINATOR] Synthesising all agent outputs into final decision...")

    user = (
        f"Synthesise all agent assessments into a final triage decision.\n\n"
        f"VITALS AGENT: {json.dumps(vitals_out)}\n"
        f"SYMPTOM AGENT: {json.dumps(symptom_out)}\n"
        f"VISUAL AGENT: {json.dumps(visual_out)}\n"
        f"RISK AGENT: {json.dumps(risk_out)}\n"
        f"XGBOOST ML: {json.dumps(xgboost_result)}\n"
        f"CURRENT QUEUE (patients waiting per zone): {json.dumps(queue_stats)}\n\n"
        f"Generate the final triage decision."
    )

    raw = call_claude(COORDINATOR_SYSTEM, user, max_tokens=1000)
    data = parse_llm_json(raw)

    if "error" not in data:
        data["generated_at"] = datetime.now(timezone.utc).isoformat()

    # Build the full structured return (mirrors FinSight's reporter return structure)
    zone = data.get("final_zone", xgboost_result.get("zone", 3))
    confidence = data.get("confidence", 50.0)

    xgb_zone = xgboost_result.get("zone", "?")
    xgb_conf = xgboost_result.get("confidence", "?")
 
    if xgb_zone != zone:
        print(
            f"  [COORDINATOR] *** DIVERGENCE DETECTED ***\n"
            f"    XGBoost predicted : Zone {xgb_zone} (confidence {xgb_conf}%)\n"
            f"    Coordinator final : Zone {zone} (confidence {confidence}%)\n"
            f"    Reason            : {data.get('flag_reasons', ['(none logged)'])}"
        )
    else:
        print(
            f"  [COORDINATOR] Final Zone {zone} — confidence {confidence}%"
            f" [XGBoost agreed at {xgb_conf}%]"
        )

    return {
        "final_zone": zone,
        "confidence": confidence,
        "flagged_for_nurse": data.get("flagged_for_nurse", True),
        "zone_agreement": data.get("zone_agreement", True),
        "clinical_narrative": data.get("clinical_narrative", "Clinical assessment completed."),
        "patient_explanation": data.get("patient_explanation",
            f"You have been assessed and placed in Zone {zone}. A nurse will see you shortly."),
        "flag_reasons": data.get("flag_reasons", []),
        "scores": {
            "vitals_score": data.get("vitals_score", 0),
            "symptom_score": data.get("symptom_score", 0),
            "visual_score": data.get("visual_score", 0),
            "composite_score": data.get("composite_score", 0),
        },
        "agent_outputs": {
            "vitals": vitals_out,
            "symptom": symptom_out,
            "visual": visual_out,
            "risk": risk_out,
            "coordinator": data,
        },
        "swarm_ok": True,
        "generated_at": data.get("generated_at", ""),
    }
