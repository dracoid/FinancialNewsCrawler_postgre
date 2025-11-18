# scripts/run_export_and_send.py
from datetime import date
import logging

from pipeline.export_daily import export_for_date
from telegram.sender import send_file, send_message

logger = logging.getLogger(__name__)


def main():
    target_date = date.today()
    logger.info("run_export_and_send: target_date=%s", target_date)

    excel_path = export_for_date(target_date)

    if not excel_path:
        msg = f"[FinancialNewsCrawler] {target_date.isoformat()} 기준 뉴스가 없습니다."
        logger.info(msg)
        send_message(msg)
        return

    caption = f"[FinancialNewsCrawler] {target_date.isoformat()} 뉴스 요약 파일입니다."
    send_file(excel_path, caption=caption)


if __name__ == "__main__":
    main()
