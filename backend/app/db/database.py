import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class HospitalDatabase:
    """
    In-memory / JSON persisted healthcare database modeling HL7 FHIR resources,
    audit logs, adherence records, and appointment slots.
    """
    def __init__(self):
        self.patients: Dict[str, Dict[str, Any]] = {}
        self.doctors: Dict[str, Dict[str, Any]] = {}
        self.observations: List[Dict[str, Any]] = []
        self.medications: List[Dict[str, Any]] = []
        self.adherence_logs: List[Dict[str, Any]] = []
        self.appointments: List[Dict[str, Any]] = []
        self.available_slots: List[Dict[str, Any]] = []
        self.conditions: List[Dict[str, Any]] = []
        self.audit_logs: List[Dict[str, Any]] = []
        self.clinical_knowledge: List[Dict[str, str]] = []
        # ── New tables added in v2 ─────────────────────────────────────────
        self.vitals: List[Dict[str, Any]] = []                  # Patient-reported vital signs
        self.notifications: List[Dict[str, Any]] = []           # In-app notification feed
        self.notification_preferences: Dict[str, Any] = {}     # Per-patient preferences
        # ───────────────────────────────────────────────────────────────────
        self._seed_data()

    def _seed_data(self):
        # 1. Doctors
        self.doctors = {
            "doc-1": {
                "id": "doc-1",
                "name": "Dr. Robert Chen",
                "specialty": "Cardiology",
                "department": "Cardiology",
                "email": "robert.chen@hospital.org",
                "room": "Cardiology Wing, Suite 402"
            },
            "doc-2": {
                "id": "doc-2",
                "name": "Dr. Lisa Patel",
                "specialty": "Endocrinology",
                "department": "Endocrinology & Metabolism",
                "email": "lisa.patel@hospital.org",
                "room": "Metabolic Center, Suite 210"
            },
            "doc-3": {
                "id": "doc-3",
                "name": "Dr. David Kim",
                "specialty": "Dermatology",
                "department": "Dermatology",
                "email": "david.kim@hospital.org",
                "room": "Outpatient Pavilion, Suite 105"
            }
        }

        # 2. Patients
        self.patients = {
            "pat-101": {
                "id": "pat-101",
                "name": "John Doe",
                "first_name": "John",
                "last_name": "Doe",
                "gender": "male",
                "birth_date": "1978-04-15",
                "phone": "+1-555-019-2834",
                "email": "john.doe@patient.hospital.org",
                "assigned_doctor_id": "doc-1",
                "allergies": ["Penicillin"],
                "blood_type": "O+"
            },
            "pat-102": {
                "id": "pat-102",
                "name": "Jane Smith",
                "first_name": "Jane",
                "last_name": "Smith",
                "gender": "female",
                "birth_date": "1985-09-22",
                "phone": "+1-555-018-7741",
                "email": "jane.smith@patient.hospital.org",
                "assigned_doctor_id": "doc-2",
                "allergies": ["Sulfa"],
                "blood_type": "A+"
            }
        }

        # 3. Conditions (Diagnoses)
        self.conditions = [
            {
                "id": "cond-1",
                "patient_id": "pat-101",
                "code": "E11.9",
                "name": "Type 2 Diabetes Mellitus",
                "clinical_status": "Active",
                "diagnosed_date": "2023-02-10",
                "notes": "Dietary modification and oral hypoglycemic agents prescribed."
            },
            {
                "id": "cond-2",
                "patient_id": "pat-101",
                "code": "I10",
                "name": "Essential Hypertension",
                "clinical_status": "Active",
                "diagnosed_date": "2022-08-14",
                "notes": "Target systolic BP < 130 mmHg."
            },
            {
                "id": "cond-3",
                "patient_id": "pat-102",
                "code": "J45.909",
                "name": "Mild Intermittent Asthma",
                "clinical_status": "Active",
                "diagnosed_date": "2024-01-05",
                "notes": "Albuterol rescue inhaler as needed."
            }
        ]

        # 4. Lab Observations (Longitudinal history for John Doe)
        self.observations = [
            # HbA1c history: showing increase from 6.8% to 7.4%
            {
                "id": "obs-1",
                "patient_id": "pat-101",
                "test_name": "HbA1c",
                "code": "4548-4",
                "category": "Laboratory",
                "value": 7.4,
                "unit": "%",
                "reference_range": {"low": 4.0, "high": 5.6, "target": "< 7.0"},
                "interpretation": "High (Above clinical diabetic target)",
                "date": "2026-08-28",
                "notes": "Reflects past 3-month glycemic control. Increased from previous 6.8%."
            },
            {
                "id": "obs-2",
                "patient_id": "pat-101",
                "test_name": "HbA1c",
                "code": "4548-4",
                "category": "Laboratory",
                "value": 6.8,
                "unit": "%",
                "reference_range": {"low": 4.0, "high": 5.6, "target": "< 7.0"},
                "interpretation": "Elevated (Near target)",
                "date": "2026-05-15",
                "notes": "Adequate baseline on Metformin 500mg."
            },
            {
                "id": "obs-3",
                "patient_id": "pat-101",
                "test_name": "Fasting Blood Glucose",
                "code": "1558-6",
                "category": "Laboratory",
                "value": 142,
                "unit": "mg/dL",
                "reference_range": {"low": 70, "high": 99, "target": "80-130"},
                "interpretation": "High",
                "date": "2026-08-28",
                "notes": "Collected after 10-hour fast."
            },
            {
                "id": "obs-4",
                "patient_id": "pat-101",
                "test_name": "Total Cholesterol",
                "code": "2093-3",
                "category": "Lipid Panel",
                "value": 195,
                "unit": "mg/dL",
                "reference_range": {"low": 125, "high": 200, "target": "< 200"},
                "interpretation": "Normal / Desirable",
                "date": "2026-08-28",
                "notes": "Stable compared to 198 mg/dL on 2026-05-15."
            },
            {
                "id": "obs-5",
                "patient_id": "pat-101",
                "test_name": "Blood Pressure",
                "code": "85354-9",
                "category": "Vitals",
                "value": "134/86",
                "unit": "mmHg",
                "reference_range": {"low": 90, "high": 120, "target": "< 130/80"},
                "interpretation": "Stage 1 Elevated",
                "date": "2026-08-28",
                "notes": "Sitting position, right arm."
            }
        ]

        # 5. Clinician-Approved Medication Requests (Strictly authorized)
        self.medications = [
            {
                "id": "med-1",
                "patient_id": "pat-101",
                "name": "Metformin",
                "dose": "500 mg",
                "form": "Oral Tablet",
                "frequency": "Twice daily with meals",
                "scheduled_times": ["08:00 AM", "08:00 PM"],
                "prescriber_id": "doc-1",
                "prescriber_name": "Dr. Robert Chen",
                "status": "Active",
                "clinician_approved": True,
                "purpose": "Blood sugar regulation in Type 2 Diabetes",
                "instructions": "Take with breakfast and dinner to reduce GI discomfort. Do not double dose if missed."
            },
            {
                "id": "med-2",
                "patient_id": "pat-101",
                "name": "Lisinopril",
                "dose": "10 mg",
                "form": "Oral Tablet",
                "frequency": "Once daily in the morning",
                "scheduled_times": ["09:00 AM"],
                "prescriber_id": "doc-1",
                "prescriber_name": "Dr. Robert Chen",
                "status": "Active",
                "clinician_approved": True,
                "purpose": "Blood pressure management and kidney protection",
                "instructions": "Take consistently at the same time each morning. Notify clinic if dry cough develops."
            }
        ]

        # 6. Medication Adherence Logs (Past 14 doses)
        self.adherence_logs = [
            {"id": "adh-1", "patient_id": "pat-101", "medication_id": "med-1", "timestamp": "2026-09-04 08:05:00", "status": "taken"},
            {"id": "adh-2", "patient_id": "pat-101", "medication_id": "med-1", "timestamp": "2026-09-04 20:15:00", "status": "taken"},
            {"id": "adh-3", "patient_id": "pat-101", "medication_id": "med-2", "timestamp": "2026-09-04 09:00:00", "status": "taken"},
            {"id": "adh-4", "patient_id": "pat-101", "medication_id": "med-1", "timestamp": "2026-09-05 08:10:00", "status": "taken"},
            {"id": "adh-5", "patient_id": "pat-101", "medication_id": "med-2", "timestamp": "2026-09-05 09:05:00", "status": "taken"}
        ]

        # 7. Appointments (Existing scheduled visits)
        self.appointments = [
            {
                "id": "apt-1",
                "patient_id": "pat-101",
                "patient_name": "John Doe",
                "doctor_id": "doc-1",
                "doctor_name": "Dr. Robert Chen",
                "department": "Cardiology",
                "datetime": "2026-09-08 10:30 AM",
                "status": "confirmed",
                "reason": "Routine hypertension follow-up & recent lab review",
                "location": "Cardiology Wing, Suite 402"
            }
        ]

        # 8. Available Slots for Booking
        self.available_slots = [
            {"id": "slot-1", "doctor_id": "doc-1", "doctor_name": "Dr. Robert Chen", "department": "Cardiology", "datetime": "2026-09-10 09:30 AM"},
            {"id": "slot-2", "doctor_id": "doc-1", "doctor_name": "Dr. Robert Chen", "department": "Cardiology", "datetime": "2026-09-10 02:00 PM"},
            {"id": "slot-3", "doctor_id": "doc-2", "doctor_name": "Dr. Lisa Patel", "department": "Endocrinology", "datetime": "2026-09-09 11:00 AM"},
            {"id": "slot-4", "doctor_id": "doc-2", "doctor_name": "Dr. Lisa Patel", "department": "Endocrinology", "datetime": "2026-09-11 03:30 PM"},
            {"id": "slot-5", "doctor_id": "doc-3", "doctor_name": "Dr. David Kim", "department": "Dermatology", "datetime": "2026-09-09 10:00 AM"},
            {"id": "slot-6", "doctor_id": "doc-3", "doctor_name": "Dr. David Kim", "department": "Dermatology", "datetime": "2026-09-12 01:30 PM"}
        ]

        # 9. Hospital Clinical Protocols & Guidelines (RAG base)
        self.clinical_knowledge = [
            {
                "topic": "HbA1c Evaluation",
                "content": "For adults with Type 2 Diabetes, the general target is HbA1c < 7.0%. A level >= 7.0% suggests suboptimal glycemic control over the preceding 2 to 3 months. Any change in pharmacological therapy must be evaluated and authorized by the prescribing clinician."
            },
            {
                "topic": "Missed Dose Protocol",
                "content": "If a patient misses a dose of Metformin or Lisinopril: Take it as soon as remembered unless it is almost time for the next scheduled dose. Never double up on pills or take two doses at once to make up for a missed dose. Consult your doctor or pharmacist if unsure."
            },
            {
                "topic": "Hypertension Guidelines",
                "content": "Stage 1 Hypertension is defined as systolic BP 130-139 or diastolic 80-89 mmHg. Lifestyle modifications including sodium restriction, physical activity, and medication adherence are recommended. Doctor consultation required for persistent readings above target."
            },
            {
                "topic": "Emergency Symptoms Protocol",
                "content": "Symptoms requiring immediate emergency care (911 or nearest ER): Severe chest pressure or crushing sensation, left arm radiating pain, sudden facial drooping or weakness in limbs, sudden speech difficulty, severe acute shortness of breath, loss of consciousness. AI must route directly to emergency contact."
            }
        ]

    def _seed_vitals_and_notifications(self):
        """Seeds demo vitals and notifications for pat-101."""
        from datetime import timezone
        # Seed vitals
        self.vitals = [
            {"id": "vital-1", "patient_id": "pat-101", "vital_type": "blood_pressure",
             "value": "134/86", "unit": "mmHg", "timestamp": "2026-10-18T08:30:00+00:00",
             "notes": "Morning reading, fasted", "alert_level": "elevated"},
            {"id": "vital-2", "patient_id": "pat-101", "vital_type": "heart_rate",
             "value": "72", "unit": "bpm", "timestamp": "2026-10-18T08:30:00+00:00",
             "notes": None, "alert_level": "normal"},
            {"id": "vital-3", "patient_id": "pat-101", "vital_type": "spo2",
             "value": "97", "unit": "%", "timestamp": "2026-10-19T09:00:00+00:00",
             "notes": None, "alert_level": "normal"},
            {"id": "vital-4", "patient_id": "pat-101", "vital_type": "glucose",
             "value": "142", "unit": "mg/dL", "timestamp": "2026-10-19T07:45:00+00:00",
             "notes": "Post-breakfast", "alert_level": "high"},
            {"id": "vital-5", "patient_id": "pat-101", "vital_type": "weight",
             "value": "84.2", "unit": "kg", "timestamp": "2026-10-20T07:00:00+00:00",
             "notes": None, "alert_level": "normal"},
        ]
        # Seed notifications
        self.notifications = [
            {"id": "notif-1", "patient_id": "pat-101", "type": "medication_reminder",
             "title": "💊 Medication Reminder", "body": "It's time to take your Metformin HCl (500mg). Take with food.",
             "priority": "normal", "read": True, "created_at": "2026-10-20T08:00:00+00:00", "action_url": None},
            {"id": "notif-2", "patient_id": "pat-101", "type": "lab_result_abnormal",
             "title": "🧬 Abnormal Lab Result — Action Needed",
             "body": "⚠️ Your HbA1c result (7.4 %) is outside the normal range. Please contact your doctor.",
             "priority": "high", "read": False, "created_at": "2026-10-21T10:00:00+00:00", "action_url": None},
            {"id": "notif-3", "patient_id": "pat-101", "type": "appointment_reminder_24h",
             "title": "📅 Appointment Tomorrow",
             "body": "Reminder: You have an appointment with Dr. Robert Chen tomorrow at 10:00 AM.",
             "priority": "normal", "read": False, "created_at": "2026-10-21T09:00:00+00:00", "action_url": None},
        ]
        # Default notification preferences for pat-101
        self.notification_preferences["pat-101"] = {
            "medication_reminders": True,
            "appointment_reminders": True,
            "lab_result_alerts": True,
            "channels": ["in_app"],
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "07:00"
        }

    # Helper logging method
    def log_audit(self, actor_id: str, actor_role: str, action: str, resource: str, details: str):
        from datetime import timezone
        entry = {
            "id": f"aud-{len(self.audit_logs) + 1}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor_id": actor_id,
            "actor_role": actor_role,
            "action": action,
            "resource": resource,
            "details": details
        }
        self.audit_logs.append(entry)
        return entry

db = HospitalDatabase()
db._seed_vitals_and_notifications()

