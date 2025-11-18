# pipeline/export_daily.py
import logging
from datetime import date
from pathlib import Path
from typing import Tuple, Optional

import pandas as pd

from app.config import settings
from db.repository import fetch_articles_for_date

logger = logging.getLogger(__name__)


def export_for_date(target_date: date) -> Tuple[Optional[Path], int]:
    """
    news_history 에서 target_date 기준 기사들을 조회해서
    엑셀 파일로 저장하고, (파일경로, 행 개수)를 반환.
    데이터가 없으면 (None, 0) 반환.
    """
    rows = fetch_articles_for_date(target_date)

    if not rows:
        logger.info("export_for_date(%s): no rows to export", target_date)
        return None, 0

    df = pd.DataFrame(rows)

    # 정렬
    sort_cols = [c for c in ["ticker", "published_dt", "id"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols)

    export_dir: Path = settings.EXPORT_DIR
    export_dir.mkdir(parents=True, exist_ok=True)

    filename = f"news_{target_date.strftime('%Y%m%d')}.xlsx"
    file_path = export_dir / filename

    df.to_excel(file_path, index=False)

    logger.info(
        "export_for_date(%s): %d rows -> %s (exists=%s)",
        target_date,
        len(df),
        file_path,
        file_path.exists(),
    )

    return file_path, len(df)