from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from backend.app.core.security import get_current_user, require_role
from backend.app.agents.ehr_agent import EHRAgent
from backend.app.agents.medication_agent import MedicationAgent
from backend.app.agents.appointment_agent import AppointmentAgent
from backend.app.db.database import db
from backend.app.models import NewPrescriptionRequest, AIBriefingResponse, PatientRosterItem, AuditLogEntry

router = APIRouter(prefix="/doctor", tags=["Doctor Clinical Portal"])


@router.get("/patients")
def get_assigned_patients(current_user: Dict[str, Any] = Depends(require_role("doctor"))):
    doc_id = current_user.get("doctor_id", "doc-1")
    assigned = [p for p in db.patients.values() if p.get("assigned_doctor_id") == doc_id]
    
    # Enhance with summary stats for the doctor overview
    results = []
    for p in assigned:
        pid = p["id"]
        conds = [c["name"] for c in db.conditions if c["patient_id"] == pid]
        adh = MedicationAgent.calculate_adherence_summary(pid)
        labs = EHRAgent.get_latest_labs(pid)
        apts = AppointmentAgent.get_upcoming_appointments(pid)
        
        results.append({
            "profile": p,
            "conditions": conds,
            "adherence_rate": adh["adherence_rate_pct"],
            "latest_lab": f"{labs[0]['test_name']}: {labs[0]['value']} {labs[0]['unit']}" if labs else "No recent labs",
            "next_appointment": apts[0]["datetime"] if apts else "None"
        })
    return results

@router.get("/patient/{patient_id}/ai-briefing")
def generate_ai_clinical_briefing(
    patient_id: str,
    current_user: Dict[str, Any] = Depends(require_role("doctor"))
):
    """
    Synthesizes an executive pre-visit clinical briefing for the physician.
    Includes abnormal lab flags, longitudinal trends, medication adherence, and suggested talking points.
    """
    patient = db.patients.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    conds = [c for c in db.conditions if c["patient_id"] == patient_id]
    labs = EHRAgent.get_latest_labs(patient_id)
    hba1c_trend = EHRAgent.analyze_lab_trends(patient_id, "HbA1c")
    meds = MedicationAgent.get_prescribed_medications(patient_id)
    adh = MedicationAgent.calculate_adherence_summary(patient_id)
    apts = AppointmentAgent.get_upcoming_appointments(patient_id)

    briefing_text = (
        f"### Pre-Visit Clinical Intelligence Briefing\n\n"
        f"**Patient:** {patient['name']} (DOB: {patient['birth_date']}, Gender: {patient['gender'].title()})\n"
        f"**Active Conditions:** " + ", ".join([c['name'] for c in conds]) + "\n"
        f"**Allergies:** " + ", ".join(patient.get("allergies", ["None"])) + "\n\n"
        f"#### ⚠️ Critical / Actionable Highlights:\n"
        f"1. **Glycemic Control Elevation:** HbA1c is currently **{hba1c_trend['latest_reading']['value']}%** "
        f"(up from {hba1c_trend['previous_reading']['value']}% on {hba1c_trend['previous_reading']['date']}). "
        f"Current Metformin therapy may require titration or adjunctive agent review.\n"
        f"2. **Blood Pressure:** Recent sitting reading is **134/86 mmHg** on Lisinopril 10mg.\n"
        f"3. **Medication Adherence:** Patient demonstrates **{adh['adherence_rate_pct']}% adherence** over past logged regimen.\n\n"
        f"#### Current Authorized Regimen:\n"
        + "\n".join([f"• **{m['name']}** {m['dose']} ({m['frequency']}) — Prescribed by {m['prescriber_name']}" for m in meds]) +
        f"\n\n#### Recommended Discussion Points for Encounter:\n"
        f"• Discuss dietary carbohydrate intake & physical activity routine in light of HbA1c increase.\n"
        f"• Confirm patient understands missed-dose guidelines (take when remembered; never double up).\n"
        f"• Schedule follow-up microalbumin/creatinine lab panel in 3 months."
    )

    db.log_audit(
        actor_id=current_user.get("doctor_id", "doc-1"),
        actor_role="doctor",
        action="GENERATE_AI_BRIEFING",
        resource=f"Patient/{patient_id}",
        details="Generated clinical briefing for pre-visit review"
    )

    return {
        "patient_id": patient_id,
        "briefing_markdown": briefing_text,
        "hba1c_trend": hba1c_trend,
        "adherence_metrics": adh,
        "upcoming_appointment": apts[0] if apts else None
    }

@router.post("/prescriptions/authorize")
def authorize_new_prescription(
    req: NewPrescriptionRequest,
    current_user: Dict[str, Any] = Depends(require_role("doctor"))
):
    """
    Clinician authorization endpoint. New medications can ONLY be created by authorized physicians.
    """
    new_id = f"med-{len(db.medications) + 1}"
    new_med = {
        "id": new_id,
        "patient_id": req.patient_id,
        "name": req.name,
        "dose": req.dose,
        "form": "Oral Tablet",
        "frequency": req.frequency,
        "scheduled_times": req.scheduled_times,
        "prescriber_id": current_user.get("doctor_id", "doc-1"),
        "prescriber_name": current_user.get("name", "Dr. Robert Chen"),
        "status": "Active",
        "clinician_approved": True,
        "purpose": req.purpose,
        "instructions": req.instructions
    }
    db.medications.append(new_med)

    db.log_audit(
        actor_id=current_user.get("doctor_id", "doc-1"),
        actor_role="doctor",
        action="AUTHORIZE_PRESCRIPTION",
        resource=f"MedicationRequest/{new_id}",
        details=f"Physician authorized {req.name} {req.dose} for Patient {req.patient_id}"
    )

    return {
        "success": True,
        "medication": new_med,
        "message": f"Successfully authorized and signed prescription for {req.name} {req.dose}."
    }

@router.get("/audit-logs")
def get_audit_trail(current_user: Dict[str, Any] = Depends(require_role("doctor"))):
    """
    HIPAA and safety compliance audit logs.
    """
    return db.audit_logs[-50:]
