from fastapi import APIRouter, Depends, Query, UploadFile, File
from typing import Dict, Any, List, Optional
from backend.app.core.security import get_current_user
from backend.app.agents.ehr_agent import EHRAgent
from backend.app.db.database import db
from backend.app.models import MockUploadLabRequest, LabObservation, LabTrendAnalysis, LabUploadResponse

router = APIRouter(prefix="/reports", tags=["Lab Reports & Diagnostics"])


@router.get("/latest")
def get_latest_labs(current_user: Dict[str, Any] = Depends(get_current_user)):
    patient_id = current_user.get("patient_id", "pat-101")
    return EHRAgent.get_latest_labs(patient_id)

@router.get("/trends")
def get_lab_trends(
    test_name: str = Query("HbA1c", description="Test name to compare longitudinally"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    patient_id = current_user.get("patient_id", "pat-101")
    return EHRAgent.analyze_lab_trends(patient_id, test_name)

@router.post("/upload")
def upload_lab_report(
    payload: MockUploadLabRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Simulated document parser: accepts report details, validates reference ranges,
    stores the FHIR Observation in the database, and returns clinical insight.
    """
    patient_id = current_user.get("patient_id", "pat-101")
    new_id = f"obs-{len(db.observations) + 1}"
    
    interp = "High" if payload.value > 7.0 else "Normal"
    new_obs = {
        "id": new_id,
        "patient_id": patient_id,
        "test_name": payload.test_name,
        "code": "4548-4" if "hba1c" in payload.test_name.lower() else "CUSTOM-1",
        "category": "Laboratory",
        "value": payload.value,
        "unit": payload.unit,
        "reference_range": {"low": 4.0, "high": 5.6, "target": payload.target},
        "interpretation": interp,
        "date": payload.date,
        "notes": f"Uploaded by patient via portal parser."
    }
    db.observations.insert(0, new_obs)
    
    db.log_audit(
        actor_id=patient_id,
        actor_role="patient",
        action="UPLOAD_LAB_REPORT",
        resource=f"Observation/{new_id}",
        details=f"Uploaded report for {payload.test_name}: {payload.value} {payload.unit}"
    )

    trend = EHRAgent.analyze_lab_trends(patient_id, payload.test_name)

    return {
        "success": True,
        "observation": new_obs,
        "trend_analysis": trend,
        "message": f"Successfully parsed and ingested {payload.test_name} result into your medical record."
    }
