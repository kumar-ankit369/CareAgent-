from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from backend.app.core.security import create_access_token, DEMO_USERS, get_current_user
from backend.app.models import LoginRequest, SwitchRoleRequest, TokenResponse, UserProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse, summary="User authentication")
def login(req: LoginRequest):
    # Quick demo login
    if req.username == "doctor" or "dr" in req.username.lower():
        user = DEMO_USERS["doctor_demo"]
    else:
        user = DEMO_USERS["patient_demo"]
        
    token = create_access_token({
        "sub": user["username"],
        "role": user["role"],
        "patient_id": user.get("patient_id"),
        "doctor_id": user.get("doctor_id"),
        "name": user["name"]
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/switch-demo-role", response_model=TokenResponse, summary="Switch active demo persona")
def switch_demo_role(req: SwitchRoleRequest):
    if req.role.lower() == "doctor":
        user = DEMO_USERS["doctor_demo"]
    else:
        user = DEMO_USERS["patient_demo"]
        
    token = create_access_token({
        "sub": user["username"],
        "role": user["role"],
        "patient_id": user.get("patient_id"),
        "doctor_id": user.get("doctor_id"),
        "name": user["name"]
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me")
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return current_user
