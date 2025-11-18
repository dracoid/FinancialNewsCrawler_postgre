# scripts/run_all.py
import logging

from app.logging_config import setup_logging
from pipeline.ingest import run_ingest
from scripts import run_export_and_send as export_and_send


logger = logging.getLogger(__name__)


def main():
    setup_logging()
    logger.info("===== FinancialNewsCrawler: run_all start =====")

    # 1) RSS → DB 저장
    try:
        logger.info("Step 1/2: ingest (RSS -> DB) 시작")
        run_ingest()
        logger.info("Step 1/2: ingest 완료")
    except Exception as e:
        logger.exception("ingest 실행 중 예외 발생: %s", e)
        # 여기서 바로 return 하면 export/send는 생략
        return

    # 2) DB → 텍스트 요약 + 엑셀 → 텔레그램
    try:
        logger.info("Step 2/2: export_and_send (DB -> Telegram) 시작")
        export_and_send.main()
        logger.info("Step 2/2: export_and_send 완료")
    except Exception as e:
        logger.exception("export_and_send 실행 중 예외 발생: %s", e)

    logger.info("===== FinancialNewsCrawler: run_all finished =====")


if __name__ == "__main__":
    main()