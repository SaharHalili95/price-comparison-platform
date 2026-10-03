from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List

INSECURE_JWT_SECRET_DEFAULT = "CHANGE-THIS-TO-A-RANDOM-64-CHAR-SECRET-IN-PRODUCTION"


class Settings(BaseSettings):
    """Application settings"""

    DATABASE_URL: str = "sqlite:///./price_comparison.db"
    API_TITLE: str = "Smart Price Comparison Platform"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://saharhalili95.github.io",
    ]

    # JWT Settings
    JWT_SECRET_KEY: str = INSECURE_JWT_SECRET_DEFAULT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Security Settings
    BCRYPT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True

    @model_validator(mode="after")
    def _reject_insecure_jwt_secret_outside_debug(self) -> "Settings":
        if not self.DEBUG and self.JWT_SECRET_KEY == INSECURE_JWT_SECRET_DEFAULT:
            raise RuntimeError(
                "JWT_SECRET_KEY is still set to the insecure placeholder value. "
                "Set a real random secret via the JWT_SECRET_KEY environment variable "
                "before running outside DEBUG mode."
            )
        return self


settings = Settings()
