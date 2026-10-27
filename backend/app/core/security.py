from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
try:
    from jose import jwt, JWTError
except ImportError:
    import jwt
    JWTError = Exception
from backend.app.core.config import settings


security = HTTPBearer(auto_error=False)

# Demo credentials for easy testing & portal switching
DEMO_USERS = {
    "patient_demo": {
        "username": "john.doe",
        "role": "patient",
        "patient_id": "pat-101",
        "name": "John Doe",
        "doctor_id": "doc-1"
    },
    "doctor_demo": {
        "username": "dr.robert.chen",
        "role": "doctor",
        "doctor_id": "doc-1",
        "name": "Dr. Robert Chen",
        "specialty": "Cardiology"
    }
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    # Default to patient demo if no bearer token passed (for effortless testing/demo)
    if not credentials:
        return DEMO_USERS["patient_demo"]
        
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role", "patient")
        if username is None:
            return DEMO_USERS["patient_demo"]
        return {
            "username": username,
            "role": role,
            "patient_id": payload.get("patient_id", "pat-101"),
            "doctor_id": payload.get("doctor_id", "doc-1"),
            "name": payload.get("name", "John Doe")
        }
    except Exception:
        return DEMO_USERS["patient_demo"]

def require_role(required_role: str):
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires role: {required_role}"
            )
        return current_user
    return role_checker
