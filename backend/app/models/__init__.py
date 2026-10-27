# Models Package — Pydantic request/response schemas
from backend.app.models.schemas_auth import LoginRequest, SwitchRoleRequest, TokenResponse, UserProfile
from backend.app.models.schemas_chat import ChatMessageRequest, AgentChatResponse
from backend.app.models.schemas_appointments import (
    StageBookingRequest, ConfirmBookingRequest, AppointmentSlot,
    AppointmentRecord, StageBookingResponse, ConfirmBookingResponse
)
from backend.app.models.schemas_medications import (
    LogAdherenceRequest, MedicationRecord, AdherenceSummary, AdherenceStatus
)
from backend.app.models.schemas_doctor import (
    NewPrescriptionRequest, AIBriefingResponse, PatientRosterItem, AuditLogEntry
)
from backend.app.models.schemas_reports import (
    MockUploadLabRequest, LabObservation, LabTrendAnalysis, LabUploadResponse
)
from backend.app.models.schemas_vitals import (
    LogVitalRequest, VitalReading, VitalsTrendResponse
)
from backend.app.models.schemas_notifications import (
    NotificationRecord, NotificationPreferenceRequest
)
