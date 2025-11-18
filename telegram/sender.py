# telegram/sender.py
import logging
from pathlib import Path
from typing import Union

import requests

from app.config import settings

logger = logging.getLogger(__name__)


def _check_config() -> bool:
    if not settings.TG_BOT_TOKEN or not settings.TG_CHAT_ID:
        logger.error(
            "Telegram 설정이 비어 있습니다. "
            "TG_BOT_TOKEN / TG_CHAT_ID 를 .env 에 설정하세요."
        )
        return False
    return True


def _api_base() -> str:
    return f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}"


def send_message(text: str) -> bool:
    if not _check_config():
        return False

    url = f"{_api_base()}/sendMessage"
    payload = {
        "chat_id": settings.TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Telegram message sent successfully")
        return True
    except Exception as e:
        logger.exception("Failed to send Telegram message: %s", e)
        return False


def send_file(file_path: Union[str, Path], caption: str = "") -> bool:
    if not _check_config():
        return False

    file_path = Path(file_path)
    if not file_path.exists():
        logger.error("send_file: file not found: %s", file_path)
        return False

    url = f"{_api_base()}/sendDocument"
    data = {
        "chat_id": settings.TG_CHAT_ID,
        "caption": caption,
        "parse_mode": "HTML",
    }

    try:
        with file_path.open("rb") as f:
            files = {"document": (file_path.name, f)}
            resp = requests.post(url, data=data, files=files, timeout=30)
            resp.raise_for_status()
        logger.info("Telegram file sent successfully: %s", file_path.name)
        return True
    except Exception as e:
        logger.exception("Failed to send Telegram file: %s", e)
        return False