"""
Pydantic models for TriageAI request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import IntEnum


class Zone(IntEnum):
    """Malaysian Triage Scale zones."""
    ZONE_1 = 1  # Red — Life-threatening
    ZONE_2 = 2  # Orange — Very urgent
    ZONE_3 = 3  # Yellow — Urgent
    ZONE_4 = 4  # Green — Semi-urgent
    ZONE_5 = 5  # Blue — Non-urgent


ZONE_COLOURS = {
    1: "Red",
    2: "Orange",
    3: "Yellow",
    4: "Green",
    5: "Blue",
}

ZONE_LABELS = {
    1: "Life-threatening — resuscitation required",
    2: "Very urgent — may deteriorate rapidly",
    3: "Urgent — stable but requires prompt attention",
    4: "Semi-urgent — minor illness or injury",
    5: "Non-urgent — can be seen by GP or clinic",
}

ZONE_TARGET_TIMES = {
    1: 0,    # Immediate
    2: 10,   # 10 minutes
    3: 30,   # 30 minutes
    4: 60,   # 60 minutes
    5: 120,  # 120 minutes
}


# ─── Request Models ──────────────────────────────────────────────────────────

class VitalsInput(BaseModel):
    """Objective vital sign measurements from hardware/sliders."""
    systolic_bp: float = Field(..., ge=40, le=260, description="Systolic blood pressure (mmHg)")
    diastolic_bp: float = Field(..., ge=20, le=160, description="Diastolic blood pressure (mmHg)")
    heart_rate: float = Field(..., ge=20, le=220, description="Heart rate (bpm)")
    spo2: float = Field(..., ge=50, le=100, description="Oxygen saturation (%)")
    temperature: float = Field(..., ge=30, le=43, description="Body temperature (°C)")
    respiratory_rate: float = Field(..., ge=4, le=60, description="Respiratory rate (breaths/min)")


class SymptomInput(BaseModel):
    """Structured symptom questionnaire responses."""
    pain_location: str = Field(..., description="Body area: chest, abdomen, head, limb, back, other")
    pain_severity: int = Field(..., ge=0, le=10, description="Pain scale 0-10")
    onset_type: str = Field(..., description="sudden or gradual")
    duration: str = Field(..., description="<1hr, 1-6hr, 6-24hr, >24hr")
    # Branching symptom flags
    chest_crushing: bool = Field(False, description="Chest pain: crushing/pressure-like?")
    chest_radiating: bool = Field(False, description="Chest pain: radiates to arm/jaw?")
    abdomen_vomiting: bool = Field(False, description="Abdominal: vomiting present?")
    abdomen_fever: bool = Field(False, description="Abdominal: fever present?")
    limb_deformity: bool = Field(False, description="Limb: visible deformity?")
    limb_weight_bearing: bool = Field(True, description="Limb: can bear weight?")
    loss_of_consciousness: bool = Field(False, description="Reported loss of consciousness?")
    difficulty_breathing: bool = Field(False, description="Difficulty breathing?")
    bleeding_severe: bool = Field(False, description="Severe or uncontrolled bleeding?")


class VisualFlags(BaseModel):
    """Simulated visual AI detection flags (camera-based in production)."""
    pallor: bool = Field(False, description="Skin paleness detected")
    cyanosis: bool = Field(False, description="Bluish discolouration detected")
    diaphoresis: bool = Field(False, description="Visible sweating detected")
    gait_abnormality: bool = Field(False, description="Abnormal gait/mobility detected")
    facial_grimacing: bool = Field(False, description="Pain-related facial expression detected")


class TriageRequest(BaseModel):
    """Full triage assessment request combining all three input layers."""
    vitals: VitalsInput
    symptoms: SymptomInput
    visual_flags: VisualFlags
    patient_name: Optional[str] = Field(None, description="Optional patient identifier")
    language: str = Field("en", description="Display language: en, ms, zh, ta")


# ─── Response Models ─────────────────────────────────────────────────────────

class InputBreakdown(BaseModel):
    """Breakdown of scoring by input layer."""
    vitals_score: float
    symptom_score: float
    visual_score: float
    composite_score: float
    critical_overrides: list[str] = Field(default_factory=list)


class TriageResult(BaseModel):
    """AI classification result."""
    zone: int = Field(..., ge=1, le=5)
    zone_colour: str
    zone_label: str
    confidence: float = Field(..., ge=0, le=100)
    composite_score: float
    flagged_for_nurse: bool
    flag_reasons: list[str] = Field(default_factory=list)
    input_breakdown: InputBreakdown
    explanation: str
    estimated_wait_minutes: int
    queue_position: int
    # Swarm fields (populated by Groq agent pipeline)
    clinical_narrative: Optional[str] = None
    agent_outputs: Optional[dict] = None
    xgboost_prediction: Optional[dict] = None
    swarm_ok: bool = True


class PatientRecord(BaseModel):
    """Stored patient session record."""
    id: str
    patient_name: Optional[str] = None
    triage_result: TriageResult
    vitals: VitalsInput
    symptoms: SymptomInput
    visual_flags: VisualFlags
    triaged_at: datetime
    status: str = "waiting"  # waiting, in_treatment, discharged
    nurse_override_zone: Optional[int] = None
    nurse_override_reason: Optional[str] = None
    effective_zone: int  # After any overrides


class ZoneOverrideRequest(BaseModel):
    """Nurse override request."""
    new_zone: int = Field(..., ge=1, le=5)
    reason: str = Field(..., min_length=1)


class QueueStats(BaseModel):
    """Queue statistics per zone."""
    zone_counts: dict[int, int]
    total_patients: int
    flagged_count: int

