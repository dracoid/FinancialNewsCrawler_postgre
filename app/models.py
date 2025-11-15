# app/models.py
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsArticle:
    """
    파이프라인 전체에서 공통으로 사용하는 뉴스 데이터 모델.
    DB news_history 테이블 구조와 1:1로 거의 매칭.
    """
    published_raw: str          # published (원본 문자열)
    published_dt: datetime      # published_dt (표준화된 datetime)
    category: str               # category
    ticker: str                 # ticker
    source_name: str            # source_name
    title: str                  # title
    link: str                   # link
