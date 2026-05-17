from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://performx:performx123@localhost:5432/performx_db"
    SECRET_KEY: str = "supersecretkey-change-in-production-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    APP_BASE_URL: str = "http://localhost:5173"

    DEBUG: bool = True

    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None

    TEAMS_WEBHOOK_URL: Optional[str] = None

    CRON_SECRET: str = ""  # Set in production Vercel env vars

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
