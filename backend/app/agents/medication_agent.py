from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.db.database import db

class MedicationAgent:
    """
    Medication agent for clinician-approved regimens, intake reminders,
    and longitudinal adherence tracking.
    """

    @classmethod
    def get_prescribed_medications(cls, patient_id: str) -> List[Dict[str, Any]]:
        return [med for med in db.medications if med["patient_id"] == patient_id and med["status"] == "Active"]

    @classmethod
    def get_medication_schedule(cls, patient_id: str) -> List[Dict[str, Any]]:
        meds = cls.get_prescribed_medications(patient_id)
        schedule = []
        for med in meds:
            for time_str in med.get("scheduled_times", []):
                schedule.append({
                    "medication_id": med["id"],
                    "medication_name": med["name"],
                    "dose": med["dose"],
                    "time": time_str,
                    "frequency": med["frequency"],
                    "instructions": med["instructions"]
                })
        # Sort schedule by time
        schedule.sort(key=lambda x: x["time"])
        return schedule

    @classmethod
    def log_adherence_event(cls, patient_id: str, medication_id: str, status: str) -> Dict[str, Any]:
        """
        Status: "taken", "skipped", "delayed"
        """
        med = next((m for m in db.medications if m["id"] == medication_id and m["patient_id"] == patient_id), None)
        if not med:
            return {"success": False, "error": "Prescription record not found."}

        event = {
            "id": f"adh-{len(db.adherence_logs) + 1}",
            "patient_id": patient_id,
            "medication_id": medication_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status.lower()
        }
        db.adherence_logs.append(event)

        db.log_audit(
            actor_id=patient_id,
            actor_role="patient",
            action="LOG_ADHERENCE",
            resource=f"MedicationRequest/{medication_id}",
            details=f"Marked {med['name']} as {status}"
        )

        return {
            "success": True,
            "event": event,
            "message": f"Recorded {med['name']} as **{status.upper()}** for today."
        }

    @classmethod
    def calculate_adherence_summary(cls, patient_id: str) -> Dict[str, Any]:
        patient_logs = [l for l in db.adherence_logs if l["patient_id"] == patient_id]
        total = len(patient_logs)
        if total == 0:
            return {
                "total_logged": 0,
                "taken_count": 0,
                "adherence_rate_pct": 100.0,
                "summary": "No missed doses logged yet."
            }
        
        taken = sum(1 for l in patient_logs if l["status"] == "taken")
        pct = round((taken / total) * 100, 1)

        return {
            "total_logged": total,
            "taken_count": taken,
            "adherence_rate_pct": pct,
            "summary": f"You have logged {taken} of your last {total} scheduled doses as taken ({pct}% adherence)."
        }
