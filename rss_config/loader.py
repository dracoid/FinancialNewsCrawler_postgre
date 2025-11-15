# app/rss_config/loader.py
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd


@dataclass
class RssFeedConfig:
    """rss_list.xlsx 한 줄을 표현하는 설정 값."""
    category: str   # 예: "1.지수", "2.지표", "3.종목"
    name: str       # 예: "S&P 500", "NASDAQ", "Fermi America LLC"
    ticker: str     # 예: "^GSPC", "^IXIC", "FRMI"


# 이 파일과 같은 디렉토리에 있는 rss_list.xlsx를 기본값으로 사용
_BASE_DIR = Path(__file__).resolve().parent
DEFAULT_RSS_LIST_PATH = _BASE_DIR / "rss_list.xlsx"


def load_rss_list(path: str | Path | None = None) -> List[RssFeedConfig]:
    """
    rss_list.xlsx를 읽어서 RssFeedConfig 리스트로 반환한다.
    path를 지정하지 않으면 app/rss_config/rss_list.xlsx를 사용.
    """
    if path is None:
        path = DEFAULT_RSS_LIST_PATH

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"RSS 리스트 파일을 찾을 수 없습니다: {path}")

    df = pd.read_excel(path)

    # 컬럼 이름 정리 (혹시 공백/대소문자 섞여 있는 경우 대비)
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})

    required = {"category", "name", "ticker"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"rss_list.xlsx에 필요한 컬럼이 없습니다: {missing}")

    # ticker가 비어 있는 행은 제거
    df = df.dropna(subset=["ticker"])

    feeds: List[RssFeedConfig] = []
    for _, row in df.iterrows():
        feeds.append(
            RssFeedConfig(
                category=str(row["category"]).strip(),
                name=str(row["name"]).strip(),
                ticker=str(row["ticker"]).strip(),
            )
        )

    return feeds
