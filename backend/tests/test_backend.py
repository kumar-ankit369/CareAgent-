import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.agents.safety_guard import SafetyGuard
from backend.app.agents.ehr_agent import EHRAgent
from backend.app.agents.appointment_agent import AppointmentAgent
from backend.app.agents.medication_agent import MedicationAgent
from backend.app.core.security import create_access_token

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["guardrails_active"] is True

def test_emergency_guardrail_short_circuit():
    query = "I have acute chest pain and my left arm is going numb"
    res = SafetyGuard.evaluate_query(query)
    assert res is not None
    assert res["guardrail_triggered"] == "EMERGENCY_TRIAGE"
    assert res["short_circuit"] is True
    assert "911" in res["response"]

def test_medication_safety_invariant():
    query = "I missed my morning dose, can I double my dose tonight?"
    res = SafetyGuard.evaluate_query(query)
    assert res is not None
    assert res["guardrail_triggered"] == "MEDICATION_SAFETY_INVARIANT"
    assert "Never double up" in res["response"]
    assert res["short_circuit"] is True

def test_appointment_two_step_confirmation():
    # 1. Search available slots
    slots = AppointmentAgent.get_available_slots()
    assert len(slots) > 0
    slot = slots[0]

    # 2. Stage booking (must NOT directly confirm)
    stage_res = AppointmentAgent.stage_booking("pat-101", slot["id"], "General Checkup")
    assert stage_res["success"] is True
    assert stage_res["requires_confirmation"] is True
    stage_id = stage_res["staged_booking"]["stage_id"]

    # 3. Explicitly confirm booking
    confirm_res = AppointmentAgent.confirm_booking(stage_id)
    assert confirm_res["success"] is True
    assert confirm_res["appointment"]["status"] == "confirmed"

def test_ehr_longitudinal_lab_trend():
    trend = EHRAgent.analyze_lab_trends("pat-101", "HbA1c")
    assert trend["found"] is True
    assert trend["test_name"] == "HbA1c"
    assert trend["trend_direction"] == "INCREASED"
    assert trend["latest_reading"]["value"] == 7.4
    assert trend["previous_reading"]["value"] == 6.8
    assert len(trend["suggested_doctor_questions"]) > 0

def test_medication_adherence_logging():
    initial = MedicationAgent.calculate_adherence_summary("pat-101")
    res = MedicationAgent.log_adherence_event("pat-101", "med-1", "taken")
    assert res["success"] is True
    updated = MedicationAgent.calculate_adherence_summary("pat-101")
    assert updated["total_logged"] == initial["total_logged"] + 1

def test_rbac_doctor_endpoint_protection():
    # Patient token should be forbidden on /api/doctor/patients
    patient_token = create_access_token({"sub": "john.doe", "role": "patient", "patient_id": "pat-101"})
    resp = client.get("/api/doctor/patients", headers={"Authorization": f"Bearer {patient_token}"})
    assert resp.status_code == 403

    # Doctor token should succeed
    doctor_token = create_access_token({"sub": "dr.robert.chen", "role": "doctor", "doctor_id": "doc-1", "name": "Dr. Robert Chen"})
    resp2 = client.get("/api/doctor/patients", headers={"Authorization": f"Bearer {doctor_token}"})
    assert resp2.status_code == 200
    assert len(resp2.json()) > 0
