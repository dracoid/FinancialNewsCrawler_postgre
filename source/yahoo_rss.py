# app/source/yahoo_rss.py
import feedparser
import dateparser
from typing import List

from app.models import NewsArticle
from rss_config.loader import load_rss_list

YAHOO_RSS_TEMPLATE = "http://finance.yahoo.com/rss/headline?s={ticker}"


class YahooRssSource:
    source_name = "Yahoo Finance"

    def fetch_articles(self) -> List[NewsArticle]:
        feeds = load_rss_list()
        articles: List[NewsArticle] = []

        for feed_cfg in feeds:
            url = YAHOO_RSS_TEMPLATE.format(ticker=feed_cfg.ticker)
            parsed = feedparser.parse(url)

            for entry in parsed.entries:
                published_raw = entry.get("published", "")
                published_dt = dateparser.parse(published_raw, fuzzy=True)

                articles.append(
                    NewsArticle(
                        published_raw=published_raw,
                        published_dt=published_dt,
                        category=feed_cfg.category,
                        ticker=feed_cfg.ticker,
                        source_name=self.source_name,
                        title=entry.title,
                        link=entry.link,
                    )
                )

        return articles
