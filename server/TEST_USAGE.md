# 테스트 실행 가이드

## 📋 **개요**

`./server` 디렉터리에서 Makefile과 run_tests.py 스크립트를 사용하여 효율적으로 테스트를 실행할 수 있습니다.

## 🚀 **사용법**

### **기본 전제조건**

1. `./server` 디렉터리에서 명령어 실행
2. PostgreSQL과 Redis가 실행 중 (Docker Compose 권장)
3. Python 가상환경 활성화

```bash
# 서버 디렉터리로 이동
cd server

# 가상환경 활성화 (Windows)
activate-venv.bat

# 또는 (Linux/Mac)
source venv/bin/activate
```

### **Makefile 명령어**

#### **📦 의존성 설치**
```bash
# 기본 의존성 설치
make install

# 개발용 의존성 설치 (테스트 도구 포함)
make install-dev
```

#### **🧪 테스트 실행**
```bash
# 모든 테스트 실행
make test

# 단위 테스트만 실행
make test-unit

# 통합 테스트만 실행
make test-integration

# 특정 서비스 테스트
make test-user          # User Service만
make test-recipe        # Recipe Service만

# 커버리지 측정
make coverage
```

#### **🔍 코드 품질 검사**
```bash
# 코드 린팅 검사
make lint

# 코드 포맷팅 검사
make format

# 코드 자동 수정
make fix

# 전체 코드 품질 검사
make quality
```

#### **🐳 Docker 명령어**
```bash
# Docker 환경 구축
make docker-build
make docker-up

# Docker 환경에서 테스트
make docker-test

# 개별 서비스 Docker 테스트
make test-user-service-docker
make test-recipe-service-docker

# Docker 로그 확인
make logs
make logs-user
make logs-recipe
```

#### **⚡ 개발 서버 실행**
```bash
# User Service 개발 서버 (포트 8001)
make dev-user

# Recipe Service 개발 서버 (포트 8002)
make dev-recipe

# API Gateway 개발 서버 (포트 8000)
make dev-gateway
```

#### **🧹 정리**
```bash
# 임시 파일 정리
make clean

# 테스트 관련 파일 정리
make clean-test

# Python 캐시 정리
make clean-cache

# 모든 임시 파일 정리
make clean-all
```

### **run_tests.py 스크립트 직접 사용**

#### **기본 사용법**
```bash
# Python 스크립트 직접 실행
python scripts/run_tests.py --help

# 모든 서비스, 모든 테스트 타입
python scripts/run_tests.py

# 특정 서비스만
python scripts/run_tests.py --service user-service
python scripts/run_tests.py --service recipe-service

# 특정 테스트 타입만
python scripts/run_tests.py --type unit
python scripts/run_tests.py --type integration

# 조합 사용
python scripts/run_tests.py --service user-service --type unit
```

#### **고급 옵션**
```bash
# 커버리지 측정 비활성화
python scripts/run_tests.py --no-coverage

# 간단한 출력
python scripts/run_tests.py --quiet

# 의존성 검사 스킵 (빠른 실행)
python scripts/run_tests.py --skip-deps

# Docker 환경에서 실행
python scripts/run_tests.py --docker
```

## 🎯 **추천 워크플로우**

### **개발 중 빠른 검사**
```bash
# 1. 코드 품질 + 단위 테스트 (빠름)
make check

# 2. 또는 수동으로
make lint
python scripts/run_tests.py --type unit --quiet
```

### **커밋 전 전체 검사**
```bash
# CI/CD 파이프라인 시뮬레이션
make ci
```

### **개발 환경 초기 설정**
```bash
# 모든 의존성 설치 + Docker 실행 + 테스트
make init
```

## 🛠️ **수정된 주요 기능**

### **경로 자동 감지**
- `run_tests.py`가 자동으로 `server` 디렉터리를 찾아 이동
- 서비스 디렉터리 존재 여부 자동 확인
- 상대 경로 문제 해결

### **환경별 대응**
- Windows/Linux/Mac 경로 구분자 자동 처리
- PYTHONPATH 올바른 설정
- OS별 명령어 호환성 개선

### **에러 처리 강화**
- 디렉터리 없을 때 명확한 오류 메시지
- 의존성 누락 시 설치 가이드 제공
- 데이터베이스 연결 실패 시 Docker 가이드

### **향상된 출력**
- 현재 작업 디렉터리 표시
- PYTHONPATH 설정 내용 표시
- 각 단계별 상세한 상태 메시지

## 🚨 **문제 해결**

### **"모듈을 찾을 수 없습니다" 오류**
```bash
# 1. 올바른 디렉터리에서 실행 확인
pwd  # server 디렉터리여야 함

# 2. PYTHONPATH 확인
python scripts/run_tests.py --skip-deps
```

### **"데이터베이스 연결 실패" 오류**
```bash
# PostgreSQL 및 Redis 실행
docker-compose up -d postgres redis

# 연결 테스트
python scripts/run_tests.py
```

### **"requirements.txt not found" 경고**
```bash
# 의존성 파일 확인
ls user-service/requirements.txt
ls recipe-service/requirements.txt
ls requirements-test.txt

# 누락된 파일 생성 또는 복원
```
