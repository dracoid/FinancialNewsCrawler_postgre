# telegram/sender.py
import logging
from typing import Optional

import requests

from app.config import settings

logger = logging.getLogger(__name__)


def _check_config() -> bool:
    if not settings.TG_BOT_TOKEN or not settings.TG_CHAT_ID:
        logger.warning(
            "Telegram not configured: TG_BOT_TOKEN or TG_CHAT_ID is empty. "
            "Check your .env file."
        )
        return False
    return True


def send_message(text: str) -> None:
    """
    텍스트 메시지 한 건을 텔레그램으로 전송.
    """
    if not _check_config():
        return

    url = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": settings.TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        resp = requests.post(url, data=data, timeout=10)
        if not resp.ok:
            logger.error(
                "Telegram send_message failed: %s - %s",
                resp.status_code,
                resp.text,
            )
    except Exception as e:
        logger.error("Telegram send_message exception: %s", e)


def send_file(file_path: str, caption: Optional[str] = None) -> None:
    """
    파일(엑셀 등)을 텔레그램으로 전송.
    """
    if not _check_config():
        return

    url = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendDocument"
    data = {"chat_id": settings.TG_CHAT_ID}
    if caption:
        data["caption"] = caption

    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            resp = requests.post(url, data=data, files=files, timeout=60)

        if not resp.ok:
            logger.error(
                "Telegram send_file failed: %s - %s",
                resp.status_code,
                resp.text,
            )
    except FileNotFoundError:
        logger.error("Telegram send_file: file not found: %s", file_path)
    except Exception as e:
        logger.error("Telegram send_file exception: %s", e)
