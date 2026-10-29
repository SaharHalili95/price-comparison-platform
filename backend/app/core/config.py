from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List

# Every placeholder value that has ever appeared in this repo's config
# default or its .env.example, so copying either file verbatim is caught -
# not just the one hardcoded in Settings below.
INSECURE_JWT_SECRET_DEFAULT = "CHANGE-THIS-TO-A-RANDOM-64-CHAR-SECRET-IN-PRODUCTION"
KNOWN_PLACEHOLDER_JWT_SECRETS = {
    INSECURE_JWT_SECRET_DEFAULT,
    "your-super-secret-key-change-in-production-min-64-chars",
}
MIN_JWT_SECRET_LENGTH = 32


class Settings(BaseSettings):
    """Application settings"""

    DATABASE_URL: str = "postgresql+psycopg://salsmart:salsmart@localhost:5432/salsmart"
    API_TITLE: str = "SalSmart"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://saharhalili95.github.io",
    ]

    # Sign in with Google: the OAuth client ID from Google Cloud Console. Empty disables the endpoint.
    GOOGLE_CLIENT_ID: str = ""

    # Price alerts: the ingestion publishes to RabbitMQ (empty disables publishing), the notifier sends email.
    RABBITMQ_URL: str = ""
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ALERT_FROM: str = "SalSmart <alerts@salsmart.local>"

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
        if self.DEBUG:
            return self
        if self.JWT_SECRET_KEY in KNOWN_PLACEHOLDER_JWT_SECRETS:
            raise RuntimeError(
                "JWT_SECRET_KEY is still set to a known placeholder value "
                f"({self.JWT_SECRET_KEY!r}). Set a real random secret via the "
                "JWT_SECRET_KEY environment variable before running outside DEBUG mode."
            )
        if len(self.JWT_SECRET_KEY) < MIN_JWT_SECRET_LENGTH:
            raise RuntimeError(
                f"JWT_SECRET_KEY is only {len(self.JWT_SECRET_KEY)} characters - "
                f"set at least {MIN_JWT_SECRET_LENGTH} random characters via the "
                "JWT_SECRET_KEY environment variable before running outside DEBUG mode."
            )
        return self


settings = Settings()
