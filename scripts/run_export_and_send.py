# scripts/run_export_and_send.py
from datetime import date
import logging
from typing import List, Dict, Any, Dict as TypingDict

from app.logging_config import setup_logging
from db.repository import (
    fetch_articles_for_date,
    fetch_latest_articles_for_ticker,
)
from pipeline.export_daily import export_for_date
from telegram.sender import send_file, send_message
from rss_config.loader import load_rss_list

logger = logging.getLogger(__name__)


def format_ticker_summary(
    ticker: str,
    display_name: str,
    rows: List[Dict[str, Any]],
    max_items: int = 3,
) -> str:
    """
    한 종목에 대한 뉴스 요약 메시지 포맷팅.
    예전 스타일:
    📢 [Fermi America LLC 뉴스 요약]

    🔹 [YYYY-MM-DD HH:MM] 제목
    URL
    """
    if not rows:
        return ""

    header_name = display_name or ticker
    lines: List[str] = [f"📢 [{header_name} 뉴스 요약]"]

    # 최신 뉴스가 위로 오도록 정렬
    rows_sorted = sorted(
        rows,
        key=lambda r: r.get("published_dt"),
        reverse=True,
    )

    for r in rows_sorted[:max_items]:
        dt = r.get("published_dt")
        title = (r.get("title") or "").strip()
        link = (r.get("link") or "").strip()

        dt_str = dt.strftime("%Y-%m-%d %H:%M") if dt else "알 수 없음"

        lines.append(f"🔹 [{dt_str}] {title}\n{link}")

    return "\n\n".join(lines)


def main():
    setup_logging()
    target_date = date.today()
    logger.info("run_export_and_send: target_date=%s", target_date)

    # 1) 오늘자 기사 전체 조회 (엑셀 + "오늘 뉴스 있는 티커" 용)
    todays_rows = fetch_articles_for_date(target_date)
    logger.info("fetch_articles_for_date(%s): %d rows", target_date, len(todays_rows))

    # 오늘자 전체가 하나도 없어도 => fallback 로직 때문에 바로 리턴하지 않는다.

    # 2) 오늘자 기사들을 티커별로 그룹핑
    today_groups: TypingDict[str, List[Dict[str, Any]]] = {}
    for r in todays_rows:
        t = (r.get("ticker") or "").upper()
        today_groups.setdefault(t, []).append(r)

    # 3) rss_list.xlsx 기준으로 관심 티커들 순서대로 처리
    feeds = load_rss_list()  # ticker, name, category 등 포함
    summary_sent = 0

    for feed in feeds:
        ticker = feed.ticker.upper()
        display_name = feed.name

        # (1) 우선 오늘 뉴스가 있는지 확인
        rows_for_ticker = today_groups.get(ticker, [])

        # (2) 오늘 뉴스가 0개면 => DB 전체에서 가장 최근 N개 가져오기
        if not rows_for_ticker:
            rows_for_ticker = fetch_latest_articles_for_ticker(ticker, limit=3)

        # (3) DB 전체에도 하나도 없으면 => 아직 해당 티커는 기사 없음, 스킵
        if not rows_for_ticker:
            logger.info(
                "run_export_and_send: ticker=%s 은(는) DB에 기사 레코드가 없어 스킵",
                ticker,
            )
            continue

        summary = format_ticker_summary(ticker, display_name, rows_for_ticker, max_items=3)
        if summary:
            send_message(summary)
            summary_sent += 1

    if summary_sent == 0:
        # 정말로 아무 티커에도 뉴스가 없을 때만 안내 메시지
        msg = f"[FinancialNewsCrawler] {target_date.isoformat()} 기준 전송할 뉴스 요약이 없습니다."
        send_message(msg)

    # 4) 엑셀 파일 생성 (여전히 '오늘자 기사' 기준)
    file_path, row_count = export_for_date(target_date)
    if not file_path or row_count == 0:
        # 오늘자 기사만 기준이므로, 없을 수 있음
        logger.info(
            "export_for_date(%s): 오늘 날짜 기준으로는 엑셀로 내보낼 뉴스가 없습니다.",
            target_date,
        )
        return

    logger.info(
        "run_export_and_send: excel_path=%s (exists=%s)",
        file_path,
        file_path.exists(),
    )

    # 5) 엑셀 파일 텔레그램 전송
    caption = f"[FinancialNewsCrawler] {target_date.isoformat()} 뉴스 {row_count}건(오늘 기준)을 첨부합니다."
    send_file(file_path, caption=caption)


if __name__ == "__main__":
    main()