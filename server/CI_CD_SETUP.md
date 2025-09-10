# 🤖 CI/CD 설정 가이드

## 📋 개요

칵테일 저장소 백엔드 프로젝트의 CI/CD 파이프라인 설정 방법을 안내합니다.

## 🔐 GitHub Secrets 설정

GitHub Actions를 위해 다음 시크릿들을 설정해야 합니다:

### Repository Settings > Secrets and variables > Actions에서 추가:

#### Docker Hub 배포용 (선택사항)
- `DOCKER_USERNAME`: Docker Hub 사용자명
- `DOCKER_PASSWORD`: Docker Hub 액세스 토큰

#### 알림용 (선택사항)
- `SLACK_WEBHOOK_URL`: Slack 웹훅 URL (배포 알림용)
- `DISCORD_WEBHOOK_URL`: Discord 웹훅 URL

### Docker Hub 토큰 생성 방법:
1. Docker Hub에 로그인
2. Account Settings > Security > New Access Token
3. 토큰 생성 후 `DOCKER_PASSWORD`에 설정

## 🚀 GitHub Actions 워크플로우 구성

### 트리거 조건
- `main` 브랜치 푸시: 전체 파이프라인 실행 (배포 포함)
- `develop` 브랜치 푸시: 테스트 및 빌드만 실행
- Pull Request: 코드 품질 검사 및 테스트만 실행
- 수동 실행: `workflow_dispatch` 이벤트

### 파이프라인 단계

#### 1. 코드 품질 검사 (code-quality)
```yaml
- Black 포맷팅 검사
- isort import 정렬 검사
- Flake8 린팅 검사
```

#### 2. 테스트 실행 (test)
```yaml
- PostgreSQL 15 + Redis 7 서비스 실행
- Python 3.11 환경 설정
- 의존성 설치
- User Service 테스트 (커버리지 포함)
- Recipe Service 테스트 (커버리지 포함)
- 커버리지 리포트 업로드 (Codecov)
```

#### 3. Docker 빌드 및 테스트 (build)
```yaml
- Docker Buildx 설정
- 이미지 빌드 (cache 없이)
- 헬스체크 테스트
- 아티팩트 저장
```

#### 4. 보안 스캔 (security-scan, main 브랜치만)
```yaml
- pip-audit로 의존성 보안 스캔
- CodeQL 정적 분석
```

#### 5. 배포 (deploy, main 브랜치만)
```yaml
- Docker Hub에 이미지 푸시
- 버전 태깅 (latest + git SHA)
```

## 🔧 로컬 개발 환경

### 필수 도구 설치
```bash
# Python 의존성
pip install -r requirements-test.txt

# Docker & Docker Compose
# https://docs.docker.com/get-docker/
```

### 개발용 명령어
```bash
# 전체 환경 초기화
make init

# 코드 품질 검사
make quality

# 테스트 실행
make test

# 개발 서버 실행
make dev-user    # User Service
make dev-recipe  # Recipe Service  
make dev-gateway # API Gateway

# Docker 환경 실행
make docker-up
make docker-down
```

## 📊 테스트 커버리지

### 목표
- 단위 테스트 커버리지: 80% 이상
- 통합 테스트: 주요 API 엔드포인트 전체

### 커버리지 리포트
- CI에서 자동으로 Codecov에 업로드
- 로컬에서는 `htmlcov/` 디렉터리에 HTML 리포트 생성

## 🐳 Docker 이미지

### 이미지 태깅 전략
- `latest`: 최신 main 브랜치 버전
- `{git-sha}`: 특정 커밋 버전
- `v{version}`: 릴리즈 버전 (향후 추가)

### 이미지 구성
```
cocktail-user-service:latest
cocktail-recipe-service:latest  
cocktail-api-gateway:latest
```

## 🔍 코드 품질 기준

### Black (포맷팅)
- 라인 길이: 88자
- Python 3.11 타겟
- 자동 포맷팅 적용

### isort (import 정렬)
- Black 호환 프로필
- 멀티라인 출력: mode 3
- 알파벳 순 정렬

### Flake8 (린팅)
- 기본 오류: E9,F63,F7,F82
- 복잡도 제한: 10
- 라인 길이: 88자

## 🚨 실패 처리

### 코드 품질 실패
```bash
# 로컬에서 자동 수정
make fix

# 수동 확인
make format
make lint
```

### 테스트 실패
```bash
# 특정 서비스 테스트
make test-user
make test-recipe

# 상세 로그와 함께 실행
python scripts/run_tests.py --service user-service -v
```

### Docker 빌드 실패
```bash
# 로컬에서 빌드 테스트
make docker-build

# 개별 서비스 빌드
docker build -t test-user-service ./user-service
docker build -t test-recipe-service ./recipe-service
docker build -t test-api-gateway ./api-gateway
```

## 📈 성능 최적화

### CI 최적화
- Python pip 캐시 활용
- Docker layer 캐시 활용
- 병렬 테스트 실행
- 단계별 의존성 최적화

### 로컬 개발 최적화
- Make 명령어로 간편한 실행
- 빠른 검사를 위한 `make check`
- 서비스별 개별 테스트

## 🔄 브랜치 전략

### 권장 Git Flow
```
main     ← 프로덕션 코드 (자동 배포)
develop  ← 개발 브랜치 (테스트만)
feature/* ← 기능 개발 브랜치
hotfix/*  ← 긴급 수정 브랜치
```

### PR 체크리스트
- [ ] 코드 품질 검사 통과
- [ ] 모든 테스트 통과
- [ ] 커버리지 80% 이상 유지
- [ ] 보안 스캔 통과
- [ ] 문서 업데이트 (필요시)

## 📞 문제 해결

### 자주 발생하는 문제

#### 1. PostgreSQL 연결 실패
```bash
# Docker로 PostgreSQL 실행
docker-compose up -d postgres

# 연결 테스트
psql -h localhost -U postgres -d cocktail_db_test
```

#### 2. Redis 연결 실패
```bash
# Docker로 Redis 실행
docker-compose up -d redis

# 연결 테스트
redis-cli ping
```

#### 3. 의존성 충돌
```bash
# 가상환경 재생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

pip install -r requirements-test.txt
```

#### 4. 테스트 격리 문제
```bash
# 테스트 데이터베이스 초기화
python scripts/reset_test_db.py

# 또는 개별 테스트 실행
pytest tests/test_specific.py -v
```

## 📚 추가 리소스

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Docker 공식 문서](https://docs.docker.com/)
- [FastAPI 테스팅 가이드](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest 문서](https://docs.pytest.org/)
- [Black 코드 포맷터](https://black.readthedocs.io/)

---

**💡 Tip**: CI/CD 파이프라인이 실패할 경우, 로컬에서 `make ci` 명령으로 동일한 검사를 실행해볼 수 있습니다.







