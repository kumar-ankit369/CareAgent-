"""
agents/notification_agent.py — Smart Notification & Reminder Agent
Generates in-app notifications for medication reminders, appointment alerts, lab result updates,
and critical vital warnings. Respects patient quiet-hour preferences.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.db.database import db

NOTIFICATION_TEMPLATES = {
    "medication_reminder": {
        "title": "💊 Medication Reminder",
        "priority": "normal",
        "template": "It's time to take your {medication_name} ({dose}). {instructions}"
    },
    "appointment_reminder_24h": {
        "title": "📅 Appointment Tomorrow",
        "priority": "normal",
        "template": "Reminder: You have an appointment with {doctor_name} tomorrow at {time}."
    },
    "appointment_reminder_1h": {
        "title": "📅 Appointment in 1 Hour",
        "priority": "high",
        "template": "Your appointment with {doctor_name} is in 1 hour ({time}). Please prepare."
    },
    "lab_result_ready": {
        "title": "🧬 New Lab Result Available",
        "priority": "normal",
        "template": "Your {test_name} result ({value} {unit}) has been added to your health record."
    },
    "lab_result_abnormal": {
        "title": "🧬 Abnormal Lab Result — Action Needed",
        "priority": "high",
        "template": "⚠️ Your {test_name} result ({value} {unit}) is outside the normal range. Please contact your doctor."
    },
    "vital_critical": {
        "title": "🚨 Critical Vital Reading Detected",
        "priority": "critical",
        "template": "Your {vital_type} reading ({value} {unit}) is in a critical range. Contact your healthcare provider immediately."
    },
    "low_adherence": {
        "title": "📊 Medication Adherence Alert",
        "priority": "high",
        "template": "Your medication adherence has dropped to {rate}%. Missing doses can affect your treatment outcomes."
    },
    "prescription_authorized": {
        "title": "✅ New Prescription Authorized",
        "priority": "normal",
        "template": "Dr. {doctor_name} has authorized a new prescription: {medication_name} {dose}."
    }
}


class NotificationAgent:
    """
    Generates, stores, and manages patient notifications.
    Integrates with the in-memory notification store in db.notifications.
    """

    @classmethod
    def _next_id(cls) -> str:
        return f"notif-{len(db.notifications) + 1}"

    @classmethod
    def _is_quiet_hours(cls, patient_id: str) -> bool:
        """Check if current time falls within the patient's configured quiet hours."""
        prefs = db.notification_preferences.get(patient_id, {})
        quiet_start = prefs.get("quiet_hours_start", "22:00")
        quiet_end = prefs.get("quiet_hours_end", "07:00")
        now = datetime.now(timezone.utc).strftime("%H:%M")
        # Simple range check (doesn't handle midnight wrap — production would use proper tz handling)
        return quiet_start <= now or now <= quiet_end

    @classmethod
    def push(
        cls,
        patient_id: str,
        notification_type: str,
        context: Optional[Dict[str, Any]] = None,
        override_priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates and stores a notification for a patient.
        Critical notifications bypass quiet hours.
        """
        template = NOTIFICATION_TEMPLATES.get(notification_type, {
            "title": "📬 New Notification",
            "priority": "normal",
            "template": "You have a new update from CareAgent."
        })
        priority = override_priority or template["priority"]
        body = template["template"]

        if context:
            try:
                body = body.format(**context)
            except KeyError:
                pass  # Leave unformatted if context keys are missing

        # Quiet hours: suppress non-critical notifications
        if priority not in ("critical", "high") and cls._is_quiet_hours(patient_id):
            return {"suppressed": True, "reason": "quiet_hours"}

        record = {
            "id": cls._next_id(),
            "patient_id": patient_id,
            "type": notification_type,
            "title": template["title"],
            "body": body,
            "priority": priority,
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "action_url": None
        }
        db.notifications.append(record)
        return {"sent": True, "notification": record}

    @classmethod
    def push_medication_reminder(cls, patient_id: str, medication: Dict[str, Any]) -> Dict[str, Any]:
        return cls.push(
            patient_id=patient_id,
            notification_type="medication_reminder",
            context={"medication_name": medication["name"], "dose": medication["dose"], "instructions": medication.get("instructions", "")}
        )

    @classmethod
    def push_lab_result_alert(cls, patient_id: str, observation: Dict[str, Any]) -> Dict[str, Any]:
        notif_type = "lab_result_abnormal" if observation.get("interpretation") in ("High", "Low", "Critical") else "lab_result_ready"
        return cls.push(
            patient_id=patient_id,
            notification_type=notif_type,
            context={"test_name": observation["test_name"], "value": observation["value"], "unit": observation["unit"]}
        )

    @classmethod
    def push_vital_alert(cls, patient_id: str, vital: Dict[str, Any]) -> Dict[str, Any]:
        return cls.push(
            patient_id=patient_id,
            notification_type="vital_critical",
            context={"vital_type": vital["vital_type"].replace("_", " "), "value": vital["value"], "unit": vital["unit"]},
            override_priority="critical"
        )

    @classmethod
    def push_prescription_notification(cls, patient_id: str, medication: Dict[str, Any], doctor_name: str) -> Dict[str, Any]:
        return cls.push(
            patient_id=patient_id,
            notification_type="prescription_authorized",
            context={"doctor_name": doctor_name, "medication_name": medication["name"], "dose": medication["dose"]}
        )
