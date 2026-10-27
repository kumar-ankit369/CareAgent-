"""
api/health_summary.py — Patient Health Dashboard Summary API
New feature: Aggregated health score, risk stratification, and wellness snapshot for the patient dashboard.
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
from backend.app.core.security import get_current_user
from backend.app.agents.ehr_agent import EHRAgent
from backend.app.agents.medication_agent import MedicationAgent
from backend.app.agents.appointment_agent import AppointmentAgent
from backend.app.db.database import db

router = APIRouter(prefix="/health", tags=["Health Summary & Dashboard"])

RISK_THRESHOLDS = {
    "high_adherence": 85.0,   # % adherence for green
    "medium_adherence": 60.0, # % adherence for yellow
}


def _compute_health_score(adherence_pct: float, labs: list, vitals: list) -> Dict[str, Any]:
    """Simple rule-based health score (0–100) for dashboard display."""
    score = 100.0
    breakdown = {}

    # Adherence component (40% weight)
    adherence_score = min(adherence_pct, 100) * 0.4
    breakdown["medication_adherence"] = round(adherence_score, 1)
    score -= (40.0 - adherence_score)

    # Lab component — penalise elevated HbA1c (30% weight)
    lab_score = 30.0
    elevated_labs = [l for l in labs if l.get("interpretation") in ("High", "Critical")]
    lab_score -= len(elevated_labs) * 7
    breakdown["lab_results"] = round(max(lab_score, 0), 1)
    score -= (30.0 - max(lab_score, 0))

    # Vitals component (30% weight)
    vitals_score = 30.0
    critical_vitals = [v for v in vitals if v.get("alert_level") in ("critical_high", "critical_low")]
    elevated_vitals = [v for v in vitals if v.get("alert_level") in ("elevated", "high", "low")]
    vitals_score -= len(critical_vitals) * 10 + len(elevated_vitals) * 3
    breakdown["vitals"] = round(max(vitals_score, 0), 1)
    score -= (30.0 - max(vitals_score, 0))

    final = max(round(score, 1), 0)
    if final >= 80:
        status = "Good"
        color = "green"
    elif final >= 60:
        status = "Fair"
        color = "yellow"
    else:
        status = "Needs Attention"
        color = "red"

    return {"score": final, "status": status, "color": color, "breakdown": breakdown}


@router.get("/dashboard", summary="Comprehensive patient health dashboard snapshot")
def get_health_dashboard(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Returns a unified health dashboard object including:
    - Overall health score (0–100)
    - Active conditions
    - Medication adherence summary
    - Latest labs with flags
    - Recent vitals
    - Next appointment
    - Unread notification count
    """
    patient_id = current_user.get("patient_id", "pat-101")
    patient = db.patients.get(patient_id, {})

    labs = EHRAgent.get_latest_labs(patient_id)
    adh = MedicationAgent.calculate_adherence_summary(patient_id)
    meds = MedicationAgent.get_prescribed_medications(patient_id)
    apts = AppointmentAgent.get_upcoming_appointments(patient_id)
    conditions = [c for c in db.conditions if c["patient_id"] == patient_id]
    vitals = [v for v in db.vitals if v["patient_id"] == patient_id][-10:]
    unread = sum(1 for n in db.notifications if n["patient_id"] == patient_id and not n["read"])

    health_score = _compute_health_score(adh.get("adherence_rate_pct", 0), labs, vitals)

    return {
        "patient_id": patient_id,
        "patient_name": patient.get("name", "Patient"),
        "health_score": health_score,
        "active_conditions": [c["name"] for c in conditions],
        "medication_adherence": adh,
        "active_medications_count": len(meds),
        "lab_alerts": [l for l in labs if l.get("interpretation") in ("High", "Critical", "Low")],
        "recent_vitals_count": len(vitals),
        "vitals_alerts": [v for v in vitals if v.get("alert_level") != "normal"],
        "next_appointment": apts[0] if apts else None,
        "unread_notifications": unread,
    }


@router.get("/risk-stratification", summary="Patient risk stratification (doctor-facing)")
def get_risk_stratification(
    patient_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Doctor-facing risk stratification for a specific patient.
    Returns risk tier (low/medium/high/critical) with contributing factors.
    """
    adh = MedicationAgent.calculate_adherence_summary(patient_id)
    labs = EHRAgent.get_latest_labs(patient_id)
    vitals = [v for v in db.vitals if v["patient_id"] == patient_id]

    risk_factors = []
    risk_score = 0

    if adh.get("adherence_rate_pct", 100) < RISK_THRESHOLDS["medium_adherence"]:
        risk_factors.append("Low medication adherence (<60%)")
        risk_score += 30

    elevated_labs = [l for l in labs if l.get("interpretation") == "High"]
    if elevated_labs:
        risk_factors.append(f"{len(elevated_labs)} elevated lab value(s)")
        risk_score += len(elevated_labs) * 15

    critical_vitals = [v for v in vitals if v.get("alert_level") in ("critical_high", "critical_low")]
    if critical_vitals:
        risk_factors.append(f"{len(critical_vitals)} critical vital reading(s)")
        risk_score += len(critical_vitals) * 20

    if risk_score >= 60:
        tier = "high"
    elif risk_score >= 30:
        tier = "medium"
    elif risk_score > 0:
        tier = "low"
    else:
        tier = "minimal"

    return {
        "patient_id": patient_id,
        "risk_tier": tier,
        "risk_score": risk_score,
        "contributing_factors": risk_factors,
        "recommendation": "Immediate review recommended." if tier == "high" else "Routine monitoring."
    }
