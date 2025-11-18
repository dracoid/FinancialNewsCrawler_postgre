# app/config.py
from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


# 프로젝트 루트 경로 (app/ 의 부모)
BASE_DIR = Path(__file__).resolve().parent.parent

# 루트에 있는 .env 파일 로드
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

    # 파일 export 위치 (로컬/도커 공통)
    EXPORT_DIR: Path = Path(os.getenv("EXPORT_DIR", BASE_DIR / "output"))


settings = Settings()
