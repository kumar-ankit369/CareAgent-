"""
schemas/appointments.py — Pydantic request/response models for Appointment endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class StageBookingRequest(BaseModel):
    slot_id: str = Field(..., example="slot-mon-9am", description="Slot ID returned from GET /appointments/slots")
    reason: Optional[str] = Field("Routine consultation", description="Patient-reported reason for visit")


class ConfirmBookingRequest(BaseModel):
    stage_id: str = Field(..., description="Staging ID returned from POST /appointments/stage")


class AppointmentSlot(BaseModel):
    slot_id: str
    doctor_id: str
    doctor_name: str
    department: str
    datetime: str
    available: bool


class AppointmentRecord(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    doctor_name: str
    department: str
    datetime: str
    reason: str
    status: str  # "confirmed" | "staged" | "cancelled"


class StageBookingResponse(BaseModel):
    success: bool
    stage_id: str
    message: str
    appointment: AppointmentRecord


class ConfirmBookingResponse(BaseModel):
    success: bool
    appointment: AppointmentRecord
    message: str
