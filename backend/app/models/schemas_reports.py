"""
schemas/reports.py — Pydantic request/response models for Lab Reports & Diagnostics endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class MockUploadLabRequest(BaseModel):
    test_name: str = Field(..., example="HbA1c", description="Name of the diagnostic test")
    value: float = Field(..., example=7.4, description="Numeric test result value")
    unit: str = Field(..., example="%", description="Unit of measurement")
    target: str = Field(default="< 7.0%", description="Clinical target / reference range string")
    date: str = Field(..., example="2026-10-15", description="Date of the test (ISO 8601)")


class LabObservation(BaseModel):
    id: str
    patient_id: str
    test_name: str
    code: str
    category: str
    value: float
    unit: str
    reference_range: Dict[str, Any]
    interpretation: str  # "Normal" | "High" | "Low" | "Critical"
    date: str
    notes: Optional[str] = None


class LabTrendAnalysis(BaseModel):
    test_name: str
    patient_id: str
    latest_reading: Dict[str, Any]
    previous_reading: Dict[str, Any]
    delta: float
    delta_pct: float
    trend_direction: str  # "improving" | "worsening" | "stable"
    clinical_note: str


class LabUploadResponse(BaseModel):
    success: bool
    observation: LabObservation
    trend_analysis: Dict[str, Any]
    message: str
