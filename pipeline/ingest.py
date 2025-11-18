# pipeline/ingest.py
import logging
from typing import List

from app.logging_config import setup_logging
from app.models import NewsArticle
from db.repository import insert_articles
from source.yahoo_rss import YahooRssSource


logger = logging.getLogger(__name__)


def run_ingest() -> None:
    """
    1) Yahoo RSS 에서 기사 수집
    2) DB(news_history)에 저장
    """
    setup_logging()

    logger.info("Starting ingest pipeline...")

    source = YahooRssSource()
    articles: List[NewsArticle] = source.fetch_articles()

    logger.info("Fetched %d articles from Yahoo RSS", len(articles))

    inserted = insert_articles(articles)
    logger.info("Insert done. attempted=%d", inserted)

    logger.info("Ingest pipeline finished.")
