# app/logging_config.py
import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """프로젝트 공통 로깅 설정."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
