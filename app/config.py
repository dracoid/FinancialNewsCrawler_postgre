# app/config.py
from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


@dataclass
class Settings:
    # DB 설정
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "FinancialNews")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # Telegram
    TG_BOT_TOKEN: str = os.getenv("TG_BOT_TOKEN", "")
    TG_CHAT_ID: str = os.getenv("TG_CHAT_ID", "")

    # EXPORT_DIR: .env에 절대경로면 그대로, 상대경로면 BASE_DIR 기준
    _export_dir_env: str = os.getenv("EXPORT_DIR", "output")

    @property
    def EXPORT_DIR(self) -> Path:
        path = Path(self._export_dir_env)
        if path.is_absolute():
            return path
        return (BASE_DIR / path).resolve()


settings = Settings()