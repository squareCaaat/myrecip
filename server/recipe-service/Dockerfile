FROM python:3.11-slim

# 작업 디렉터리 설정
WORKDIR /app

# 필요한 시스템 패키지 설치 (PostgreSQL, 이미지 처리용)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 이미지 저장용 디렉터리 생성
RUN mkdir -p /app/uploads

# 포트 노출
EXPOSE 8002

# 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]

