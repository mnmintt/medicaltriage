"""
TriageAI — Visual Agent
Analyses ONLY visual observation flags (simulated camera AI output).
Returns a structured JSON assessment of the patient's visual presentation.
"""

import json
from tools.groq_utils import call_groq as call_claude, parse_llm_json

VISUAL_SYSTEM = """
You are a triage nurse trained in visual patient assessment for a Malaysian hospital ED.
You analyse ONLY the visual observation flags provided (true = detected by camera AI).

Clinical significance of visual flags:
- cyanosis: critical — tissue hypoxia, immediate concern
- pallor + diaphoresis together: shock or severe haemorrhage
- diaphoresis alone: pain, anxiety, or autonomic response
- gait_abnormality: neurological or orthopaedic concern
- facial_grimacing: significant pain burden
- cyanosis alone: Zone 1-2 risk regardless of other flags

Return ONLY a JSON object with these exact keys:
  recommended_zone: integer 1-5
  visual_severity: "critical" | "high" | "moderate" | "low" | "none"
  findings: "1-2 sentence interpretation of the visual presentation"
  shock_indicators: true | false
  visual_score: float 0-100 (100 = worst/most critical)

No markdown. Valid JSON only.
"""


def run_visual_agent(visual_flags: dict) -> dict:
    """Analyse visual flags and return structured assessment."""
    print("  [VISUAL AGENT] Analysing visual observations...")

    user = (
        f"Analyse these visual observation flags (true = detected) and return your assessment:\n"
        f"{json.dumps(visual_flags, indent=2)}"
    )

    raw = call_claude(VISUAL_SYSTEM, user)
    result = parse_llm_json(raw)
    result["agent"] = "visual"
    print(f"  [VISUAL AGENT] Zone {result.get('recommended_zone')} — {result.get('visual_severity')}")
    return result


if __name__ == "__main__":
    sample = {
        "pallor": True, "cyanosis": False, "diaphoresis": True,
        "gait_abnormality": False, "facial_grimacing": True
    }
    import json as _json
    print(_json.dumps(run_visual_agent(sample), indent=2))
