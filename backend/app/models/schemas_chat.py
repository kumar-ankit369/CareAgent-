"""
schemas/chat.py — Pydantic request/response models for Agent Chat endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ChatMessageRequest(BaseModel):
    message: str = Field(..., example="What are my latest HbA1c results?", description="Natural-language message to the AI agent")
    patient_id: Optional[str] = Field(None, description="Target patient ID (doctors only; patients use their own)")


class AgentChatResponse(BaseModel):
    agent: str = Field(..., description="Agent that handled the request (e.g. ehr, appointment, medication)")
    intent: str = Field(..., description="Detected clinical intent")
    response: str = Field(..., description="AI-generated response text")
    actions: Optional[List[Dict[str, Any]]] = Field(None, description="Structured action cards returned with the response")
    safety_triggered: bool = Field(default=False, description="True if the emergency safety guardrail was activated")
    emergency_level: Optional[str] = Field(None, description="'critical' | 'warning' | None")
