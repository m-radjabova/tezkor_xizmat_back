import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    return int(value.strip())


def _get_list_env(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseModel):
    APP_NAME: str = "Tezkor Xizmat API"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "").strip()
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256").strip()
    ACCESS_TOKEN_EXPIRE_MINUTES: int = _get_int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    REFRESH_TOKEN_EXPIRE_DAYS: int = _get_int_env("REFRESH_TOKEN_EXPIRE_DAYS", 7)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "").strip()
    IMAGEKIT_PUBLIC_KEY: str = os.getenv("IMAGEKIT_PUBLIC_KEY", "").strip()
    IMAGEKIT_PRIVATE_KEY: str = os.getenv("IMAGEKIT_PRIVATE_KEY", "").strip()
    IMAGEKIT_URL_ENDPOINT: str = os.getenv("IMAGEKIT_URL_ENDPOINT", "").strip().rstrip("/")
    FIREBASE_SERVICE_ACCOUNT_BASE64: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_BASE64", "").strip()
    CORS_ORIGINS: list[str] = _get_list_env(
        "CORS_ORIGINS",
        ["http://localhost:5173", "http://127.0.0.1:5173",],
    )


settings = Settings()
