"""
api/notifications.py — Patient Notifications & Smart Reminders API
New feature: In-app notification feed, medication reminders, appointment alerts, lab result push.
"""
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any
from datetime import datetime, timezone
from backend.app.core.security import get_current_user
from backend.app.db.database import db
from backend.app.models.schemas_notifications import NotificationPreferenceRequest

router = APIRouter(prefix="/notifications", tags=["Notifications & Reminders"])


@router.get("/", summary="Get all notifications for the current patient")
def get_notifications(
    unread_only: bool = Query(False, description="If true, returns only unread notifications"),
    limit: int = Query(50, description="Max number of notifications to return"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieves the in-app notification feed for the authenticated patient."""
    patient_id = current_user.get("patient_id", "pat-101")
    notifs = [
        n for n in db.notifications
        if n["patient_id"] == patient_id and (not unread_only or not n["read"])
    ]
    return {
        "patient_id": patient_id,
        "unread_count": sum(1 for n in notifs if not n["read"]),
        "notifications": notifs[-limit:]
    }


@router.post("/{notification_id}/read", summary="Mark a notification as read")
def mark_as_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Marks a specific notification as read."""
    patient_id = current_user.get("patient_id", "pat-101")
    for n in db.notifications:
        if n["id"] == notification_id and n["patient_id"] == patient_id:
            n["read"] = True
            return {"success": True, "notification_id": notification_id}
    return {"success": False, "detail": "Notification not found"}


@router.post("/read-all", summary="Mark all notifications as read")
def mark_all_read(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Marks all notifications for the patient as read."""
    patient_id = current_user.get("patient_id", "pat-101")
    count = 0
    for n in db.notifications:
        if n["patient_id"] == patient_id and not n["read"]:
            n["read"] = True
            count += 1
    return {"success": True, "marked_read": count}


@router.get("/preferences", summary="Get notification preferences")
def get_preferences(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the patient's notification delivery preferences."""
    patient_id = current_user.get("patient_id", "pat-101")
    prefs = db.notification_preferences.get(patient_id, {
        "medication_reminders": True,
        "appointment_reminders": True,
        "lab_result_alerts": True,
        "channels": ["in_app"],
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "07:00"
    })
    return prefs


@router.put("/preferences", summary="Update notification preferences")
def update_preferences(
    req: NotificationPreferenceRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Updates the patient's notification preferences."""
    patient_id = current_user.get("patient_id", "pat-101")
    db.notification_preferences[patient_id] = req.model_dump()
    return {"success": True, "preferences": db.notification_preferences[patient_id]}
