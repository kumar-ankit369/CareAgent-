from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class FHIRIdentifier(BaseModel):
    system: str = "http://hospital.example.org/patients"
    value: str

class FHIRHumanName(BaseModel):
    use: str = "official"
    family: str
    given: List[str]
    prefix: Optional[List[str]] = None

    @property
    def full_name(self) -> str:
        given_str = " ".join(self.given)
        prefix_str = f"{' '.join(self.prefix)} " if self.prefix else ""
        return f"{prefix_str}{given_str} {self.family}"

class FHIRPatient(BaseModel):
    resourceType: str = "Patient"
    id: str
    identifier: List[FHIRIdentifier] = []
    active: bool = True
    name: List[FHIRHumanName]
    gender: str
    birthDate: str
    telecom: List[Dict[str, str]] = []
    address: Optional[List[Dict[str, str]]] = None

class ReferenceRange(BaseModel):
    low: Optional[float] = None
    high: Optional[float] = None
    unit: str
    text: Optional[str] = None

class FHIRObservation(BaseModel):
    resourceType: str = "Observation"
    id: str
    status: str = "final"
    code: str  # LOINC or test code e.g. "4548-4"
    display: str  # e.g. "Hemoglobin A1c"
    subject_id: str
    effectiveDateTime: str
    valueQuantity: Dict[str, Any]  # {"value": 7.4, "unit": "%"}
    referenceRange: Optional[List[ReferenceRange]] = None
    interpretation: Optional[str] = None  # "NORMAL", "HIGH", "CRITICAL"
    notes: Optional[str] = None

class FHIRMedicationRequest(BaseModel):
    resourceType: str = "MedicationRequest"
    id: str
    status: str = "active"
    intent: str = "order"
    subject_id: str
    medicationCodeableConcept: Dict[str, Any]  # {"name": "Metformin", "dose": "500mg"}
    dosageInstruction: List[Dict[str, Any]]  # {"timing": "Twice daily with meals", "route": "Oral"}
    authoredOn: str
    requester_name: str  # Attending clinician who signed off
    clinician_approved: bool = True

class FHIRAppointment(BaseModel):
    resourceType: str = "Appointment"
    id: str
    status: str  # "proposed", "pending_confirmation", "booked", "cancelled"
    description: str
    start: str
    end: str
    department: str
    participant: List[Dict[str, str]]  # Actor patient and practitioner
    clinician_name: str
    location: str = "Main Hospital Wing - Suite 304"

class FHIRCondition(BaseModel):
    resourceType: str = "Condition"
    id: str
    clinicalStatus: str = "active"
    verificationStatus: str = "confirmed"
    code_text: str  # e.g. "Type 2 Diabetes Mellitus"
    subject_id: str
    onsetDateTime: str
    recordedDate: str

class AuditLogEntry(BaseModel):
    id: str
    timestamp: str
    actor_id: str
    actor_role: str
    action: str
    resource: str
    details: str
