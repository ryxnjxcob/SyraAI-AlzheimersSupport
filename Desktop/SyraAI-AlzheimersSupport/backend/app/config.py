from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "Sara"
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int
    MONGODB_URI: str
    DB_NAME: str

    TWILIO_SID: str | None = None
    TWILIO_TOKEN: str | None = None
    TWILIO_FROM: str | None = None
    ALERT_EMAIL_TO: str | None = None

    class Config:
        # Absolute path to ensure .env is found no matter where uvicorn runs
        env_file = str(Path(__file__).resolve().parent.parent / ".env")
        env_file_encoding = "utf-8"


settings = Settings()
