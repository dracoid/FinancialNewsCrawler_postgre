# db/repository.py
from datetime import date
from typing import Iterable, List, Dict, Any

import logging

from app.models import NewsArticle
from db.connection import get_connection

logger = logging.getLogger(__name__)


def insert_articles(articles: Iterable[NewsArticle]) -> int:
    """
    news_history 테이블에 기사 여러 건을 한 번에 INSERT.

    - 같은 링크라도 서로 다른 ticker 에서 온 뉴스는 각각 저장하고 싶다.
    - 하지만 동일한 (link, ticker) 조합이 스케줄 실행 등으로 여러 번 들어오는 것은 막고 싶다.

    그래서 DB 쪽에는 UNIQUE (link, ticker) 제약을 두고,
    여기서는 ON CONFLICT (link, ticker) DO NOTHING 으로 중복을 무시한다.
    """
    articles = list(articles)
    if not articles:
        logger.info("insert_articles: nothing to insert")
        return 0

    sql = """
        INSERT INTO public.news_history
            (published, published_dt, category, ticker, source_name, title, link)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (link, ticker) DO NOTHING;
    """

    data = [
        (
            a.published_raw,
            a.published_dt,
            a.category,
            a.ticker,
            a.source_name,
            a.title,
            a.link,
        )
        for a in articles
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, data)
        conn.commit()

    logger.info("insert_articles: attempted=%d", len(data))
    return len(data)
    # 실제로 몇 건이 INSERT 되었는지 알고 싶으면
    # executemany 대신 반복문으로 실행하면서 cur.rowcount 를 누적하는 방식도 가능.


def fetch_articles_for_date(target_date: date) -> List[Dict[str, Any]]:
    """
    published_dt 기준으로 특정 날짜의 기사를 모두 가져온다.
    반환값: dict 리스트 (pandas DataFrame 으로 만들기 좋음)
    """
    sql = """
        SELECT id, published, published_dt, category, ticker,
               source_name, title, link
        FROM public.news_history
        WHERE DATE(published_dt) = %s
        ORDER BY ticker, published_dt, id;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (target_date,))
            rows = cur.fetchall()

    logger.info("fetch_articles_for_date(%s): %d rows", target_date, len(rows))
    return rows