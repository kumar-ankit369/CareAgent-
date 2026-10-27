"""
schemas/notifications.py — Pydantic schemas for Patient Notifications & Alerts endpoints.
New feature: Push notification system for medication reminders, appointment alerts, and lab result alerts.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class NotificationChannel(str, Enum):
    in_app = "in_app"
    sms = "sms"
    email = "email"


class NotificationPriority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    critical = "critical"


class NotificationPreferenceRequest(BaseModel):
    medication_reminders: bool = Field(default=True, description="Receive medication dose reminders")
    appointment_reminders: bool = Field(default=True, description="Receive appointment reminders (24h + 1h before)")
    lab_result_alerts: bool = Field(default=True, description="Receive alerts when new lab results are added")
    channels: List[NotificationChannel] = Field(
        default=[NotificationChannel.in_app],
        description="Delivery channels for notifications"
    )
    quiet_hours_start: Optional[str] = Field("22:00", description="Start of quiet hours (no notifications)")
    quiet_hours_end: Optional[str] = Field("07:00", description="End of quiet hours")


class NotificationRecord(BaseModel):
    id: str
    patient_id: str
    type: str  # "medication_reminder" | "appointment_alert" | "lab_result" | "emergency"
    title: str
    body: str
    priority: NotificationPriority
    read: bool
    created_at: str
    action_url: Optional[str] = None
