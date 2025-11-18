# scripts/run_all.py
from pipeline.ingest import run_ingest
from scripts.run_export_and_send import main as run_export_and_send
from app.logging_config import setup_logging
import logging

logger = logging.getLogger(__name__)


def main():
    setup_logging()
    logger.info("=== run_all: start ===")

    run_ingest()
    run_export_and_send()

    logger.info("=== run_all: finished ===")


if __name__ == "__main__":
    main()
