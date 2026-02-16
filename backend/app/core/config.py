from pydantic_settings import BaseSettings
from typing import List


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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
