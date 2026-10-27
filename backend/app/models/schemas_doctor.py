"""
schemas/doctor.py — Pydantic request/response models for Doctor Clinical Portal endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class NewPrescriptionRequest(BaseModel):
    patient_id: str = Field(..., description="FHIR Patient resource ID")
    name: str = Field(..., example="Metformin HCl", description="Medication name")
    dose: str = Field(..., example="500mg", description="Dose amount and unit")
    frequency: str = Field(..., example="Twice daily", description="Administration frequency")
    scheduled_times: List[str] = Field(..., example=["08:00", "20:00"], description="ISO time strings for scheduled doses")
    instructions: str = Field(..., example="Take with food", description="Patient instructions")
    purpose: str = Field(..., example="Type 2 Diabetes glycemic control", description="Clinical indication")


class AIBriefingResponse(BaseModel):
    patient_id: str
    briefing_markdown: str
    hba1c_trend: dict
    adherence_metrics: dict
    upcoming_appointment: Optional[dict] = None


class PatientRosterItem(BaseModel):
    profile: dict
    conditions: List[str]
    adherence_rate: float
    latest_lab: str
    next_appointment: str
    risk_score: Optional[str] = None


class AuditLogEntry(BaseModel):
    timestamp: str
    actor_id: str
    actor_role: str
    action: str
    resource: str
    details: str
