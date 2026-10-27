from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.app.core.security import get_current_user
from backend.app.agents.appointment_agent import AppointmentAgent
from backend.app.models import (
    StageBookingRequest, ConfirmBookingRequest, AppointmentSlot,
    AppointmentRecord, StageBookingResponse, ConfirmBookingResponse
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.get("/my")
def get_my_appointments(current_user: Dict[str, Any] = Depends(get_current_user)):
    patient_id = current_user.get("patient_id", "pat-101")
    return AppointmentAgent.get_upcoming_appointments(patient_id)

@router.get("/slots")
def get_open_slots(
    department: Optional[str] = Query(None),
    doctor: Optional[str] = Query(None)
):
    return AppointmentAgent.get_available_slots(department, doctor)

@router.post("/stage")
def stage_booking(
    req: StageBookingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    patient_id = current_user.get("patient_id", "pat-101")
    result = AppointmentAgent.stage_booking(patient_id, req.slot_id, req.reason)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.post("/confirm")
def confirm_booking(
    req: ConfirmBookingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    result = AppointmentAgent.confirm_booking(req.stage_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.delete("/{appointment_id}")
def cancel_appointment(
    appointment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    patient_id = current_user.get("patient_id", "pat-101")
    result = AppointmentAgent.cancel_appointment(appointment_id, patient_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
