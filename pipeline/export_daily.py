# pipeline/export_daily.py
import os
from datetime import date
import logging

import pandas as pd

from app.config import settings
from db.repository import fetch_articles_for_date

logger = logging.getLogger(__name__)


def export_for_date(target_date: date) -> str:
    """
    news_history에서 target_date(YYYY-MM-DD) 기준 기사들을 조회해서
    엑셀 파일로 저장하고, 파일 경로를 반환한다.
    데이터가 없으면 빈 문자열("")을 반환.
    """
    rows = fetch_articles_for_date(target_date)

    if not rows:
        logger.info("export_for_date(%s): no rows to export", target_date)
        return ""

    df = pd.DataFrame(rows)

    # 출력 디렉토리 생성
    export_dir = settings.EXPORT_DIR
    os.makedirs(export_dir, exist_ok=True)

    filename = f"news_{target_date.isoformat()}.xlsx"
    filepath = os.path.join(export_dir, filename)

    df.to_excel(filepath, index=False)
    logger.info("export_for_date(%s): %d rows -> %s", target_date, len(df), filepath)

    return filepath


def export_today_to_excel() -> str:
    """
    오늘 날짜 기준으로 export_for_date 호출하는 헬퍼.
    """
    return export_for_date(date.today())
