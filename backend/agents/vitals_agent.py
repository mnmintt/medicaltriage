"""
TriageAI — Vitals Agent
Mirrors FinSight's Analyst Agent pattern: focused single-domain specialist.
Analyses ONLY vital signs and returns a structured JSON assessment.
"""

import json
from tools.groq_utils import call_groq as call_claude, parse_llm_json

VITALS_SYSTEM = """
You are a critical-care nurse specialising in vital-sign interpretation for a Malaysian hospital ED.
You analyse ONLY the vitals provided — do not infer from symptoms or visuals.

Malaysian Triage Scale vital thresholds:
- Zone 1 (Immediate): SpO2 < 88%, SBP < 80, HR > 150 or < 40, Temp < 35 or > 40, RR > 30
- Zone 2 (Very Urgent): SpO2 88-92%, SBP 80-100, HR 120-150, Temp 39-40, RR 25-30
- Zone 3 (Urgent): SpO2 92-95%, HR 100-120, Temp 38-39, RR 20-25
- Zone 4/5 (Semi-urgent/Non-urgent): All vitals near normal

Return ONLY a JSON object with these exact keys:
  recommended_zone: integer 1-5
  severity: "critical" | "high" | "moderate" | "low" | "normal"
  findings: "1-2 sentence clinical summary of the vitals"
  most_concerning_vital: "name of most worrying vital or null"
  vitals_score: float 0-100 (100 = worst/most critical)

No markdown. Valid JSON only.
"""


def run_vitals_agent(vitals: dict) -> dict:
    """Analyse vital signs and return structured assessment."""
    print("  [VITALS AGENT] Analysing vital signs...")

    user = (
        f"Analyse these patient vitals and return your structured assessment:\n"
        f"{json.dumps(vitals, indent=2)}"
    )

    raw = call_claude(VITALS_SYSTEM, user)
    result = parse_llm_json(raw)
    result["agent"] = "vitals"
    print(f"  [VITALS AGENT] Zone {result.get('recommended_zone')} — {result.get('severity')}")
    return result


if __name__ == "__main__":
    sample = {
        "systolic_bp": 88, "diastolic_bp": 58, "heart_rate": 128,
        "spo2": 90, "temperature": 38.9, "respiratory_rate": 27
    }
    import json as _json
    print(_json.dumps(run_vitals_agent(sample), indent=2))
