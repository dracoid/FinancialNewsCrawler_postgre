# source/yahoo_rss.py
import logging
from typing import List

import dateparser
import feedparser
import requests

from app.models import NewsArticle
from rss_config.loader import load_rss_list

logger = logging.getLogger(__name__)

# 야후가 실제로 사용하는 feed 서버 주소
YAHOO_RSS_TEMPLATE = (
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
)


class YahooRssSource:
    source_name = "Yahoo Finance"

    def __init__(self, max_per_ticker: int = 3):
        # 각 티커별로 가져올 최대 기사 개수
        self.max_per_ticker = max_per_ticker

    def fetch_articles(self) -> List[NewsArticle]:
        feeds = load_rss_list()
        logger.info("YahooRssSource: loaded %d tickers from rss_list.xlsx", len(feeds))

        articles: List[NewsArticle] = []

        for feed_cfg in feeds:
            url = YAHOO_RSS_TEMPLATE.format(ticker=feed_cfg.ticker)
            logger.info(
                "Fetching RSS for %s (%s): %s",
                feed_cfg.name,
                feed_cfg.ticker,
                url,
            )

            # 1) HTTP로 RSS 내용을 가져온다.
            try:
                resp = requests.get(
                    url,
                    timeout=10,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                resp.raise_for_status()
            except Exception as e:
                logger.warning("  -> HTTP request failed for %s: %s", url, e)
                continue

            # 2) feedparser 로 파싱
            parsed = feedparser.parse(resp.content)

            if getattr(parsed, "bozo", False):
                logger.warning(
                    "  -> feed parse error for %s: %s",
                    url,
                    getattr(parsed, "bozo_exception", None),
                )

            # 3) 최신 max_per_ticker 개만 사용
            entries = parsed.entries[: self.max_per_ticker]
            logger.info(
                "  -> %d entries returned, taking %d",
                len(parsed.entries),
                len(entries),
            )

            for entry in entries:
                # pubDate 또는 published 필드에서 날짜 문자열 추출
                published_raw = (
                    entry.get("published", "") or entry.get("pubDate", "")
                )

                if not published_raw:
                    logger.warning(
                        "  -> skip entry without published/pubDate: %s",
                        entry.get("title"),
                    )
                    continue

                # dateparser 로 datetime 파싱 (fuzzy 인자 없이)
                published_dt = dateparser.parse(published_raw)
                if published_dt is None:
                    logger.warning(
                        "  -> skip entry with unparseable date '%s': %s",
                        published_raw,
                        entry.get("title"),
                    )
                    continue

                # timestamp without time zone 컬럼에 맞추기 위해 tz 제거
                if published_dt.tzinfo is not None:
                    published_dt = published_dt.replace(tzinfo=None)

                articles.append(
                    NewsArticle(
                        published_raw=published_raw,
                        published_dt=published_dt,
                        category=feed_cfg.category,
                        ticker=feed_cfg.ticker,
                        source_name=self.source_name,
                        title=(entry.get("title") or "").strip(),
                        link=(entry.get("link") or "").strip(),
                    )
                )

        logger.info("YahooRssSource: total %d articles collected", len(articles))
        return articles