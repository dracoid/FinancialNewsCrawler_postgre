# scripts/test_telegram.py
from app.logging_config import setup_logging  # 네가 만든 로깅 함수 이름에 맞게
from telegram.sender import send_message


def main():
    setup_logging()
    send_message("[FinancialNewsCrawler] 텔레그램 전송 테스트 메시지입니다.")


if __name__ == "__main__":
    main()