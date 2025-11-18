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
    link + ticker 에 UNIQUE 인덱스를 걸어두고
    ON CONFLICT (link, ticker) DO NOTHING 으로 중복을 무시.
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
    # cur.rowcount 를 별도로 모아야 하지만, 여기서는 attempted 개수만 반환.


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


def fetch_latest_articles_for_ticker(
    ticker: str,
    limit: int = 3,
) -> List[Dict[str, Any]]:
    """
    특정 ticker 에 대해, 날짜 제한 없이 가장 최근 기사 몇 개를 가져온다.
    오늘 뉴스가 하나도 없을 때 fallback 용도로 사용.
    """
    sql = """
        SELECT id, published, published_dt, category, ticker,
               source_name, title, link
        FROM public.news_history
        WHERE ticker = %s
        ORDER BY published_dt DESC, id DESC
        LIMIT %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (ticker, limit))
            rows = cur.fetchall()

    logger.info(
        "fetch_latest_articles_for_ticker(%s, limit=%d): %d rows",
        ticker,
        limit,
        len(rows),
    )
    return rows