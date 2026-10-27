"""
schemas/vitals.py — Pydantic schemas for Patient Vitals Monitoring endpoints.
New feature: Vitals tracking (BP, heart rate, SpO2, temperature, weight).
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class LogVitalRequest(BaseModel):
    vital_type: str = Field(
        ...,
        example="blood_pressure",
        description="Type of vital: blood_pressure | heart_rate | spo2 | temperature | weight | glucose"
    )
    value: str = Field(..., example="128/82", description="Reading value (string to support BP like '128/82 mmHg')")
    unit: str = Field(..., example="mmHg", description="Unit of the vital sign reading")
    notes: Optional[str] = Field(None, description="Patient notes about this reading (e.g. 'after exercise')")


class VitalReading(BaseModel):
    id: str
    patient_id: str
    vital_type: str
    value: str
    unit: str
    timestamp: str
    notes: Optional[str] = None
    alert_level: Optional[str] = None  # "normal" | "elevated" | "critical"


class VitalsTrendResponse(BaseModel):
    vital_type: str
    readings: List[VitalReading]
    latest: VitalReading
    average: Optional[str] = None
    trend: str  # "stable" | "improving" | "worsening"
    alert_message: Optional[str] = None
