# telegram/sender.py
import logging
from pathlib import Path
from typing import Union, List

import requests

from app.config import settings

logger = logging.getLogger(__name__)


def _get_chat_ids() -> List[str]:
    """
    .env 의 TG_CHAT_ID 에 쉼표(,)로 여러 개를 넣으면
    모두 리스트로 반환한다.
    예: "111,222,333" -> ["111", "222", "333"]
    """
    raw = (settings.TG_CHAT_ID or "").strip()
    if not raw:
        return []
    return [cid.strip() for cid in raw.split(",") if cid.strip()]


def _check_config() -> bool:
    if not settings.TG_BOT_TOKEN:
        logger.error(
            "Telegram 설정이 비어 있습니다. "
            "TG_BOT_TOKEN 를 .env 에 설정하세요."
        )
        return False

    chat_ids = _get_chat_ids()
    if not chat_ids:
        logger.error(
            "Telegram 설정이 비어 있습니다. "
            "TG_CHAT_ID 를 .env 에 설정하세요."
        )
        return False

    return True


def _api_base() -> str:
    return f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}"


def send_message(text: str) -> bool:
    """여러 chat_id 에 동일한 메시지를 전송."""
    if not _check_config():
        return False

    chat_ids = _get_chat_ids()
    url = f"{_api_base()}/sendMessage"

    all_ok = True
    for cid in chat_ids:
        payload = {
            "chat_id": cid,
            "text": text,
            "parse_mode": "HTML",
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("Telegram message sent successfully to chat_id=%s", cid)
        except Exception as e:
            all_ok = False
            logger.exception("Failed to send Telegram message to %s: %s", cid, e)

    return all_ok


def send_file(file_path: Union[str, Path], caption: str = "") -> bool:
    """여러 chat_id 에 동일한 파일(문서)을 전송."""
    if not _check_config():
        return False

    file_path = Path(file_path)
    if not file_path.exists():
        logger.error("send_file: file not found: %s", file_path)
        return False

    chat_ids = _get_chat_ids()
    url = f"{_api_base()}/sendDocument"

    all_ok = True
    for cid in chat_ids:
        data = {
            "chat_id": cid,
            "caption": caption,
            "parse_mode": "HTML",
        }
        try:
            with file_path.open("rb") as f:
                files = {"document": (file_path.name, f)}
                resp = requests.post(url, data=data, files=files, timeout=30)
                resp.raise_for_status()
            logger.info(
                "Telegram file sent successfully to chat_id=%s: %s",
                cid,
                file_path.name,
            )
        except Exception as e:
            all_ok = False
            logger.exception(
                "Failed to send Telegram file to %s: %s", cid, e
            )

    return all_ok