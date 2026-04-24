"""
TriageAI Orchestrator Agent
Receives patient data → fans out to specialist agents → returns full triage result.

Pipeline:
  1. vitals_agent  ]
  2. symptom_agent ]— run in parallel (no inter-dependencies)
  3. visual_agent  ]
  4. risk_agent      — cross-signal detection; receives specialist conclusions too
  5. coordinator     — synthesises everything → final zone, narratives, scores
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_orchestrator(vitals: dict, symptoms: dict, visual_flags: dict,
                     xgboost_result: dict, queue_stats: dict) -> dict:
    """Entry point: receives patient data, returns full triage result dict."""
    print(f"\n[ORCHESTRATOR] New triage request received")
    print(f"[ORCHESTRATOR] Launching specialist agents in parallel...\n")

    from agents.vitals_agent import run_vitals_agent
    from agents.symptom_agent import run_symptom_agent
    from agents.visual_agent import run_visual_agent
    from agents.risk_agent import run_risk_agent
    from agents.coordinator import run_coordinator

    # Steps 1-3 — Run specialist agents in parallel.
    # None of these depend on each other, so there is no reason to run them
    # sequentially. ThreadPoolExecutor is appropriate here because each call
    # is I/O-bound (a Groq API request), not CPU-bound, so the GIL is not
    # a bottleneck.
    vitals_out = None
    symptom_out = None
    visual_out = None

    futures = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures["vitals"]  = executor.submit(run_vitals_agent,  vitals)
        futures["symptom"] = executor.submit(run_symptom_agent, symptoms)
        futures["visual"]  = executor.submit(run_visual_agent,  visual_flags)

        print("[ORCHESTRATOR] >> Vitals, Symptom, Visual agents launched in parallel")

        # Collect results as they complete; log each one as it arrives
        for key, future in futures.items():
            try:
                result = future.result()
                if key == "vitals":
                    vitals_out = result
                elif key == "symptom":
                    symptom_out = result
                elif key == "visual":
                    visual_out = result
                print(f"  [{key.upper()} AGENT] Done — Zone {result.get('recommended_zone')}")
            except Exception as e:
                print(f"  [{key.upper()} AGENT] ERROR: {e}")
                # Provide a safe fallback so the pipeline can continue
                fallback = {"agent": key, "recommended_zone": 3, "error": str(e)}
                if key == "vitals":
                    vitals_out = fallback
                elif key == "symptom":
                    symptom_out = fallback
                elif key == "visual":
                    visual_out = fallback

    # Step 4 — Risk agent runs after the specialists so it can see their
    # conclusions, not just the raw data. Agent disagreement (e.g. vitals
    # says Zone 2, symptom says Zone 4) is itself a clinical risk signal.
    print("\n[ORCHESTRATOR] >> Launching Risk Agent (with specialist conclusions)...")
    risk_out = run_risk_agent(
        vitals=vitals,
        symptoms=symptoms,
        visual_flags=visual_flags,
        vitals_out=vitals_out,
        symptom_out=symptom_out,
        visual_out=visual_out,
    )

    # Step 5 — Coordinator synthesises all outputs into a final decision
    print("\n[ORCHESTRATOR] >> Passing all agent outputs to Coordinator...")
    result = run_coordinator(
        vitals_out=vitals_out,
        symptom_out=symptom_out,
        visual_out=visual_out,
        risk_out=risk_out,
        xgboost_result=xgboost_result,
        queue_stats=queue_stats,
    )

    print("\n[ORCHESTRATOR] Swarm execution complete. Returning result to server.\n")
    return result


if __name__ == "__main__":
    sample = {
        "vitals": {"systolic_bp": 90, "diastolic_bp": 60, "heart_rate": 130,
                   "spo2": 91, "temperature": 38.5, "respiratory_rate": 26},
        "symptoms": {"pain_location": "chest", "pain_severity": 8, "onset_type": "sudden",
                     "duration": "1-6hr", "chest_crushing": True, "chest_radiating": True,
                     "abdomen_vomiting": False, "abdomen_fever": False,
                     "limb_deformity": False, "limb_weight_bearing": True,
                     "loss_of_consciousness": False, "difficulty_breathing": True,
                     "bleeding_severe": False},
        "visual_flags": {"pallor": True, "cyanosis": False, "diaphoresis": True,
                         "gait_abnormality": False, "facial_grimacing": True},
        "xgboost_result": {"zone": 2, "confidence": 78.0,
                           "probabilities": {"zone_1": 15, "zone_2": 78,
                                             "zone_3": 5,  "zone_4": 1, "zone_5": 1}},
        "queue_stats": {1: 0, 2: 2, 3: 5, 4: 8, 5: 3},
    }
    result = run_orchestrator(**sample)
    print(json.dumps(result, indent=2))