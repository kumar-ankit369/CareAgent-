from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.auth import router as auth_router
from backend.app.api.chat import router as chat_router
from backend.app.api.patients import router as patients_router
from backend.app.api.reports import router as reports_router
from backend.app.api.appointments import router as appointments_router
from backend.app.api.medications import router as medications_router
from backend.app.api.doctor import router as doctor_router
from backend.app.api.vitals import router as vitals_router
from backend.app.api.notifications import router as notifications_router
from backend.app.api.health_summary import router as health_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Enterprise-grade, permission-aware Agentic AI Hospital Assistant. "
        "Features: HL7 FHIR EHR records, multi-agent orchestration, clinical safety guardrails, "
        "vitals monitoring, smart notifications, health dashboard, and dual patient/doctor portals."
    ),
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers — v1 core
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(patients_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(appointments_router, prefix="/api")
app.include_router(medications_router, prefix="/api")
app.include_router(doctor_router, prefix="/api")
# Register API routers — v2 new features
app.include_router(vitals_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(health_router, prefix="/api")

@app.get("/", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": "2.0.0",
        "fhir_version": "R4",
        "guardrails_active": True,
        "features": [
            "multi-agent-orchestration",
            "hl7-fhir-ehr",
            "vitals-monitoring",
            "smart-notifications",
            "health-dashboard",
            "risk-stratification",
            "hipaa-audit-trail"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
