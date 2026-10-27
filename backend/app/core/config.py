from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env from the backend/ directory, regardless of CWD
_BACKEND_DIR = Path(__file__).parent.parent.parent  # backend/

class Settings(BaseSettings):
    PROJECT_NAME: str = "CareAgent — Agentic AI Hospital Assistant"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "careagent_super_secret_jwt_key_2026_healthcare_phi"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    DATABASE_URL: str = "sqlite:///./careagent.db"
    
    # AI / LLM Configuration
    # Place your Gemini API Key in backend/.env: GEMINI_API_KEY=AIzaSy...
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Groq API configuration (https://console.groq.com/keys)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Application Environment
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

settings = Settings()

