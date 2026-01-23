from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "nsfwcheck"
    DEBUG: bool = False

    # Downstream Services
    # Default to local docker-compose names
    # In K8s, these are overridden via env variables
    URLSAFE_SERVICE_URL: str = "http://urlsafe:8000"
    IMAGESAFE_SERVICE_URL: str = "http://imagesafe:3000"

    # Check Thresholds
    NSFW_THRESHOLD: float = 0.6
    MALWARE_THRESHOLD: float = 0.5

    class Config:
        env_file = ".env"

settings = Settings()
