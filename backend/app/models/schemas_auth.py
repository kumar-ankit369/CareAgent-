"""
schemas/auth.py — Pydantic request/response models for Authentication endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    username: str = Field(..., example="john.doe", description="Username for authentication")
    password: str = Field(..., example="password123", description="User password")


class SwitchRoleRequest(BaseModel):
    role: str = Field(..., example="doctor", description="Target role: 'patient' or 'doctor'")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT Bearer token")
    token_type: str = Field(default="bearer")
    user: dict = Field(..., description="Authenticated user profile")


class UserProfile(BaseModel):
    username: str
    role: str
    name: str
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None
    specialty: Optional[str] = None
