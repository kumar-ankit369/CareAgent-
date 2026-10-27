from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from backend.app.core.security import get_current_user
from backend.app.agents.ehr_agent import EHRAgent
from backend.app.db.database import db

router = APIRouter(prefix="/patients", tags=["Patient Records"])

@router.get("/profile")
def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    patient_id = current_user.get("patient_id", "pat-101")
    profile = EHRAgent.get_patient_profile(patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return profile

@router.get("/conditions")
def get_my_conditions(current_user: Dict[str, Any] = Depends(get_current_user)):
    patient_id = current_user.get("patient_id", "pat-101")
    return [c for c in db.conditions if c["patient_id"] == patient_id]
