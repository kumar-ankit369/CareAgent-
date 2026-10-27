"""
schemas/medications.py — Pydantic request/response models for Medication & Adherence endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class AdherenceStatus(str, Enum):
    taken = "taken"
    skipped = "skipped"
    late = "late"


class LogAdherenceRequest(BaseModel):
    medication_id: str = Field(..., description="ID of the medication to log")
    status: AdherenceStatus = Field(..., description="Adherence status: taken | skipped | late")
    notes: Optional[str] = Field(None, description="Optional patient note about this log entry")


class MedicationRecord(BaseModel):
    id: str
    patient_id: str
    name: str
    dose: str
    form: str
    frequency: str
    scheduled_times: List[str]
    prescriber_name: str
    status: str
    clinician_approved: bool
    purpose: str
    instructions: str


class AdherenceSummary(BaseModel):
    patient_id: str
    total_doses_logged: int
    taken: int
    skipped: int
    late: int
    adherence_rate_pct: float
    streak_days: int
