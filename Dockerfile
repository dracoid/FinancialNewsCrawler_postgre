# Python 3.10 슬림 이미지 사용
FROM python:3.10-slim

# 시스템 패키지(시간대, PostgreSQL 클라이언트 등) 약간 설치(필수는 아님)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tzdata \
        libpq5 && \
    rm -rf /var/lib/apt/lists/*

# 작업 디렉터리
WORKDIR /app

# 파이썬 출력 버퍼링 끄기
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# requirements 먼저 복사 후 설치(캐시 활용)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 나머지 소스 전체 복사
COPY . /app

# 기본 실행 명령: 전체 파이프라인 한 번 실행
CMD ["python", "-m", "scripts.run_all"]