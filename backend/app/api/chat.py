from fastapi import APIRouter, Depends
from typing import Optional, Dict, Any
from backend.app.core.security import get_current_user
from backend.app.agents.orchestrator import AgentOrchestrator
from backend.app.models import ChatMessageRequest

router = APIRouter(prefix="/chat", tags=["Agent Chat"])

@router.post("/send", summary="Send message to Agentic AI Orchestrator")

async def send_chat_message(
    req: ChatMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    # Enforce permission-aware context: patients can only query their own context
    patient_id = req.patient_id or current_user.get("patient_id", "pat-101")
    if current_user.get("role") == "patient":
        patient_id = current_user.get("patient_id", "pat-101")

    result = await AgentOrchestrator.process_patient_message(patient_id, req.message)
    return result
