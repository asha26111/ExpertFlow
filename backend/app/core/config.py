from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database — SQLite by default, no setup needed
    DATABASE_URL: str = "sqlite:///./data/deepseek_edu.db"

    # JWT
    SECRET_KEY: str = "super-secret-key-change-this-in-production-minimum-32-chars!!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Gemini API — get free key at https://aistudio.google.com
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Anthropic Claude — fallback when Gemini quota is exceeded or content is blocked
    # Get a free key at https://console.anthropic.com
    ANTHROPIC_API_KEY: str = ""

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    APP_NAME: str = "ExpertFlow"
    DEBUG: bool = True

    def get_cors_origins(self) -> List[str]:
        return ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

# Auto-switch to SQLite if .env still has a PostgreSQL URL that doesn't connect
if "postgresql" in settings.DATABASE_URL or "postgres" in settings.DATABASE_URL:
    try:
        import sqlalchemy
        e = sqlalchemy.create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 3})
        with e.connect() as c:
            c.execute(sqlalchemy.text("SELECT 1"))
    except Exception:
        print("⚠️  PostgreSQL unreachable — switching to SQLite automatically")
        settings.DATABASE_URL = "sqlite:///./data/deepseek_edu.db"

if settings.DATABASE_URL.startswith("sqlite"):
    os.makedirs("./data", exist_ok=True)
