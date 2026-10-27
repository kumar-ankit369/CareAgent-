"""
api/vitals.py — Vitals Monitoring API
New feature: Patients log blood pressure, heart rate, SpO2, temperature, glucose, weight.
Doctors receive automated alerts on critical readings.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from backend.app.core.security import get_current_user
from backend.app.db.database import db
from backend.app.models.schemas_vitals import LogVitalRequest, VitalReading, VitalsTrendResponse

router = APIRouter(prefix="/vitals", tags=["Vitals Monitoring"])

# Reference ranges for alert classification
VITAL_ALERT_RULES = {
    "blood_pressure": {
        "critical_high": lambda v: int(v.split("/")[0]) >= 180 if "/" in v else False,
        "elevated": lambda v: 130 <= int(v.split("/")[0]) < 180 if "/" in v else False,
    },
    "heart_rate": {
        "critical_high": lambda v: float(v) > 150,
        "critical_low": lambda v: float(v) < 40,
        "elevated": lambda v: 100 <= float(v) <= 150,
    },
    "spo2": {
        "critical_low": lambda v: float(v) < 90,
        "low": lambda v: 90 <= float(v) < 95,
    },
    "glucose": {
        "critical_high": lambda v: float(v) > 400,
        "high": lambda v: 180 < float(v) <= 400,
        "low": lambda v: float(v) < 70,
    },
}

def _classify_alert(vital_type: str, value: str) -> str:
    rules = VITAL_ALERT_RULES.get(vital_type, {})
    for level, check in rules.items():
        try:
            if check(value):
                return level
        except Exception:
            pass
    return "normal"


@router.post("/log", summary="Log a new vital sign reading")
def log_vital(
    req: LogVitalRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Patient logs a self-measured vital sign (BP, HR, SpO2, temperature, glucose, weight).
    Critical readings automatically raise an alert flag.
    """
    patient_id = current_user.get("patient_id", "pat-101")
    new_id = f"vital-{len(db.vitals) + 1}"
    alert_level = _classify_alert(req.vital_type, req.value)

    record = {
        "id": new_id,
        "patient_id": patient_id,
        "vital_type": req.vital_type,
        "value": req.value,
        "unit": req.unit,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "notes": req.notes,
        "alert_level": alert_level,
    }
    db.vitals.append(record)

    db.log_audit(
        actor_id=patient_id,
        actor_role="patient",
        action="LOG_VITAL",
        resource=f"Vital/{new_id}",
        details=f"Logged {req.vital_type}: {req.value} {req.unit} — Alert: {alert_level}"
    )

    response = {"success": True, "vital": record, "alert_level": alert_level}
    if alert_level in ("critical_high", "critical_low"):
        response["warning"] = (
            "⚠️ Critical reading detected. Please contact your healthcare provider immediately "
            "or call emergency services if you feel unwell."
        )
    return response


@router.get("/history", summary="Get vitals history for a specific type")
def get_vitals_history(
    vital_type: str = Query("blood_pressure", description="Vital type to retrieve"),
    limit: int = Query(30, description="Number of most recent records to return"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Returns the last N readings for a specific vital type."""
    patient_id = current_user.get("patient_id", "pat-101")
    readings = [
        v for v in db.vitals
        if v["patient_id"] == patient_id and v["vital_type"] == vital_type
    ][-limit:]
    return {"vital_type": vital_type, "count": len(readings), "readings": readings}


@router.get("/summary", summary="Get latest reading of all vital types")
def get_vitals_summary(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the most recent reading for every vital type logged by the patient."""
    patient_id = current_user.get("patient_id", "pat-101")
    all_vitals = [v for v in db.vitals if v["patient_id"] == patient_id]

    summary = {}
    for v in all_vitals:
        vt = v["vital_type"]
        if vt not in summary:
            summary[vt] = v  # First occurrence is latest (newest first assumed)

    return {"patient_id": patient_id, "latest_readings": summary}


@router.get("/alerts", summary="Get unresolved critical vital alerts")
def get_vital_alerts(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns all vital readings flagged as elevated or critical for review."""
    patient_id = current_user.get("patient_id", "pat-101")
    alerts = [
        v for v in db.vitals
        if v["patient_id"] == patient_id and v.get("alert_level") not in ("normal", None)
    ]
    return {"patient_id": patient_id, "alert_count": len(alerts), "alerts": alerts}
