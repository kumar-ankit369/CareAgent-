from typing import Dict, Any, List, Optional
import uuid
from backend.app.db.database import db

class AppointmentAgent:
    """
    Appointment management agent with explicit two-phase confirmation gating.
    An appointment is never committed without explicit user confirmation.
    """
    _staged_bookings: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_upcoming_appointments(cls, patient_id: str) -> List[Dict[str, Any]]:
        return [apt for apt in db.appointments if apt["patient_id"] == patient_id and apt["status"] != "cancelled"]

    @classmethod
    def search_doctors_and_departments(cls, query: Optional[str] = None) -> List[Dict[str, Any]]:
        if not query:
            return list(db.doctors.values())
        q = query.lower()
        return [
            doc for doc in db.doctors.values()
            if q in doc["name"].lower() or q in doc["specialty"].lower() or q in doc["department"].lower()
        ]

    @classmethod
    def get_available_slots(cls, department: Optional[str] = None, doctor_name: Optional[str] = None) -> List[Dict[str, Any]]:
        slots = db.available_slots
        if department:
            dept_lower = department.lower()
            slots = [s for s in slots if dept_lower in s["department"].lower()]
        if doctor_name:
            doc_lower = doctor_name.lower()
            slots = [s for s in slots if doc_lower in s["doctor_name"].lower()]
        return slots

    @classmethod
    def stage_booking(cls, patient_id: str, slot_id: str, reason: str = "Consultation") -> Dict[str, Any]:
        slot = next((s for s in db.available_slots if s["id"] == slot_id), None)
        if not slot:
            return {"success": False, "error": "Selected appointment slot is no longer available."}

        patient = db.patients.get(patient_id)
        patient_name = patient["name"] if patient else "Patient"

        stage_id = f"stage-{uuid.uuid4().hex[:8]}"
        staged_data = {
            "stage_id": stage_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "slot_id": slot_id,
            "doctor_id": slot["doctor_id"],
            "doctor_name": slot["doctor_name"],
            "department": slot["department"],
            "datetime": slot["datetime"],
            "reason": reason,
            "status": "pending_confirmation"
        }
        cls._staged_bookings[stage_id] = staged_data

        return {
            "success": True,
            "requires_confirmation": True,
            "staged_booking": staged_data,
            "message": (
                f"I found a slot with **{slot['doctor_name']}** ({slot['department']}) on **{slot['datetime']}**.\n\n"
                "⚠️ **Please confirm below to lock in this appointment reservation.**"
            )
        }

    @classmethod
    def confirm_booking(cls, stage_id: str) -> Dict[str, Any]:
        staged = cls._staged_bookings.get(stage_id)
        if not staged:
            return {"success": False, "error": "Staged booking expired or not found. Please select a slot again."}

        new_apt_id = f"apt-{len(db.appointments) + 1}"
        confirmed_appointment = {
            "id": new_apt_id,
            "patient_id": staged["patient_id"],
            "patient_name": staged["patient_name"],
            "doctor_id": staged["doctor_id"],
            "doctor_name": staged["doctor_name"],
            "department": staged["department"],
            "datetime": staged["datetime"],
            "status": "confirmed",
            "reason": staged["reason"],
            "location": f"{staged['department']} Outpatient Suite"
        }

        # Commit to DB
        db.appointments.append(confirmed_appointment)
        # Remove available slot
        db.available_slots = [s for s in db.available_slots if s["id"] != staged["slot_id"]]
        # Remove from staged
        del cls._staged_bookings[stage_id]

        # Audit log
        db.log_audit(
            actor_id=staged["patient_id"],
            actor_role="patient",
            action="CONFIRM_APPOINTMENT",
            resource=f"Appointment/{new_apt_id}",
            details=f"Booked appointment with {staged['doctor_name']} on {staged['datetime']}"
        )

        return {
            "success": True,
            "appointment": confirmed_appointment,
            "message": (
                f"✅ **Appointment Confirmed!**\n\n"
                f"• **Doctor:** {confirmed_appointment['doctor_name']}\n"
                f"• **Department:** {confirmed_appointment['department']}\n"
                f"• **Date & Time:** {confirmed_appointment['datetime']}\n"
                f"• **Location:** {confirmed_appointment['location']}\n\n"
                "A reminder has also been added to your hospital portal calendar."
            )
        }

    @classmethod
    def cancel_appointment(cls, appointment_id: str, patient_id: str) -> Dict[str, Any]:
        apt = next((a for a in db.appointments if a["id"] == appointment_id and a["patient_id"] == patient_id), None)
        if not apt:
            return {"success": False, "error": "Appointment not found or not authorized to cancel."}

        apt["status"] = "cancelled"
        db.log_audit(
            actor_id=patient_id,
            actor_role="patient",
            action="CANCEL_APPOINTMENT",
            resource=f"Appointment/{appointment_id}",
            details=f"Cancelled appointment with {apt['doctor_name']} on {apt['datetime']}"
        )
        return {
            "success": True,
            "message": f"Appointment with {apt['doctor_name']} on {apt['datetime']} has been cancelled."
        }
