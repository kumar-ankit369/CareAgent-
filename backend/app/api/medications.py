from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from backend.app.core.security import get_current_user
from backend.app.agents.medication_agent import MedicationAgent
from backend.app.models import LogAdherenceRequest

router = APIRouter(prefix="/medications", tags=["Medications & Adherence"])


@router.get("/prescribed")
def get_prescribed(current_user: Dict[str, Any] = Depends(get_current_user)):
    patient_id = current_user.get("patient_id", "pat-101")
    return MedicationAgent.get_prescribed_medications(patient_id)

@router.get("/schedule")
def get_daily_schedule(current_user: Dict[str, Any] = Depends(get_current_user)):
    patient_id = current_user.get("patient_id", "pat-101")
    return MedicationAgent.get_medication_schedule(patient_id)

@router.get("/adherence")
def get_adherence_metrics(current_user: Dict[str, Any] = Depends(get_current_user)):
    patient_id = current_user.get("patient_id", "pat-101")
    return MedicationAgent.calculate_adherence_summary(patient_id)

@router.post("/adherence/log")
def log_adherence(
    req: LogAdherenceRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    patient_id = current_user.get("patient_id", "pat-101")
    result = MedicationAgent.log_adherence_event(patient_id, req.medication_id, req.status)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
