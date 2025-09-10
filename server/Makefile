# 칵테일 저장소 백엔드 개발 도구

.PHONY: help install test test-unit test-integration coverage lint format fix clean docker-build docker-up docker-down logs

# 기본 설정
PYTHON := python
PIP := pip
PYTEST := pytest
SERVICES := user-service recipe-service api-gateway
TEST_SERVICES := user-service recipe-service

# 도움말
help:
	@echo "칵테일 저장소 백엔드 개발 도구"
	@echo ""
	@echo "설치 및 설정:"
	@echo "  install          모든 의존성 설치"
	@echo "  install-dev      개발용 의존성 설치"
	@echo ""
	@echo "테스트:"
	@echo "  test             모든 테스트 실행"
	@echo "  test-unit        단위 테스트만 실행"
	@echo "  test-integration 통합 테스트만 실행"
	@echo "  test-user        User Service 테스트"
	@echo "  test-recipe      Recipe Service 테스트"
	@echo "  coverage         테스트 커버리지 측정"
	@echo ""
	@echo "코드 품질:"
	@echo "  lint             코드 린팅 검사"
	@echo "  format           코드 포맷팅 검사"
	@echo "  fix              코드 자동 수정"
	@echo "  quality          전체 코드 품질 검사"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build     Docker 이미지 빌드"
	@echo "  docker-up        Docker Compose 실행"
	@echo "  docker-down      Docker Compose 중지"
	@echo "  docker-test      Docker 환경에서 테스트"
	@echo "  logs             Docker 로그 확인"
	@echo ""
	@echo "정리:"
	@echo "  clean            임시 파일 정리"
	@echo "  clean-test       테스트 관련 파일 정리"
	@echo "  clean-cache      Python 캐시 정리"

# 의존성 설치
install:
	@echo "기본 의존성 설치 중..."
	@for service in $(SERVICES); do \
		echo "Installing $$service dependencies..."; \
		if [ -d "$$service" ] && [ -f "$$service/requirements.txt" ]; then \
			cd $$service && $(PIP) install -r requirements.txt && cd ..; \
		else \
			echo "Warning: $$service directory or requirements.txt not found"; \
		fi; \
	done

install-dev:
	@echo "개발용 의존성 설치 중..."
	@for service in $(SERVICES); do \
		echo "Installing $$service dependencies..."; \
		if [ -d "$$service" ] && [ -f "$$service/requirements.txt" ]; then \
			cd $$service && $(PIP) install -r requirements.txt && cd ..; \
		else \
			echo "Warning: $$service directory or requirements.txt not found"; \
		fi; \
	done
	@if [ -f "requirements-test.txt" ]; then \
		$(PIP) install -r requirements-test.txt; \
	else \
		echo "Warning: requirements-test.txt not found"; \
	fi

# 테스트
test:
	@echo "모든 테스트 실행 중..."
	$(PYTHON) scripts/run_tests.py --service all --type all

test-unit:
	@echo "단위 테스트 실행 중..."
	$(PYTHON) scripts/run_tests.py --service all --type unit

test-integration:
	@echo "통합 테스트 실행 중..."
	$(PYTHON) scripts/run_tests.py --service all --type integration

test-user:
	@echo "User Service 테스트 실행 중..."
	$(PYTHON) scripts/run_tests.py --service user-service

test-recipe:
	@echo "Recipe Service 테스트 실행 중..."
	$(PYTHON) scripts/run_tests.py --service recipe-service

coverage:
	@echo "테스트 커버리지 측정 중..."
	$(PYTHON) scripts/run_tests.py --service all
	@echo "커버리지 리포트는 htmlcov/ 디렉터리에서 확인하세요"

# 코드 품질
lint:
	@echo "코드 린팅 검사 중..."
	$(PYTHON) scripts/code_quality.py --no-test

format:
	@echo "코드 포맷팅 검사 중..."
	$(PYTHON) scripts/code_quality.py --no-test
	@echo "💡 자동 수정이 필요하면 'make fix' 명령을 사용하세요"

fix:
	@echo "코드 자동 수정 중..."
	$(PYTHON) scripts/code_quality.py --fix --no-test

quality:
	@echo "전체 코드 품질 검사 중..."
	$(PYTHON) scripts/code_quality.py

# Docker
docker-build:
	@echo "Docker 이미지 빌드 중..."
	docker-compose build --no-cache

docker-up:
	@echo "Docker Compose 실행 중..."
	docker-compose up -d

docker-down:
	@echo "Docker Compose 중지 중..."
	docker-compose down

docker-test:
	@echo "Docker 환경에서 테스트 실행 중..."
	docker-compose up -d postgres redis
	@sleep 10
	@echo "테스트 데이터베이스 준비 완료"
	$(PYTHON) scripts/run_tests.py --service all
	docker-compose down

# Docker Test
test-docker:
	@echo "Docker 환경에서 테스트 실행"
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
	docker-compose -f docker-compose.test.yml down

test-user-service-docker:
	@echo "User Service 테스트"
	docker-compose -f docker-compose.test.yml up --build user-service-test --abort-on-container-exit

test-recipe-service-docker:
	@echo "Recipe Service 테스트"
	docker-compose -f docker-compose.test.yml up --build recipe-service-test --abort-on-container-exit

test-integration-docker:
	@echo "통합 테스트 실행"
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
	docker-compose -f docker-compose.test.yml down

test-unit-docker:
	@echo "단위 테스트 (로컬)"
	@if [ -d "user-service" ]; then \
		echo "User Service 단위 테스트 실행..."; \
		cd user-service && python -m pytest tests/ -m unit -v; \
	else \
		echo "Warning: user-service 디렉터리를 찾을 수 없습니다."; \
	fi
	@if [ -d "recipe-service" ]; then \
		echo "Recipe Service 단위 테스트 실행..."; \
		cd recipe-service && python -m pytest tests/ -m unit -v; \
	else \
		echo "Warning: recipe-service 디렉터리를 찾을 수 없습니다."; \
	fi

logs:
	@echo "Docker 로그 확인 중..."
	docker-compose logs -f

logs-api:
	@echo "API Gateway 로그 확인 중..."
	docker-compose logs -f api-gateway

logs-user:
	@echo "User Service 로그 확인 중..."
	docker-compose logs -f user-service

logs-recipe:
	@echo "Recipe Service 로그 확인 중..."
	docker-compose logs -f recipe-service

# 개발 서버 실행
dev-user:
	@echo "User Service 개발 서버 실행 중..."
	@if [ -d "user-service" ]; then \
		cd user-service && uvicorn app.main:app --reload --port 8001; \
	else \
		echo "Error: user-service 디렉터리를 찾을 수 없습니다."; \
	fi

dev-recipe:
	@echo "Recipe Service 개발 서버 실행 중..."
	@if [ -d "recipe-service" ]; then \
		cd recipe-service && uvicorn app.main:app --reload --port 8002; \
	else \
		echo "Error: recipe-service 디렉터리를 찾을 수 없습니다."; \
	fi

dev-gateway:
	@echo "API Gateway 개발 서버 실행 중..."
	@if [ -d "api-gateway" ]; then \
		cd api-gateway && uvicorn app.main:app --reload --port 8000; \
	else \
		echo "Error: api-gateway 디렉터리를 찾을 수 없습니다."; \
	fi

# 정리
clean:
	@echo "임시 파일 정리 중..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/
	rm -rf dist/

clean-test:
	@echo "테스트 관련 파일 정리 중..."
	find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "coverage.xml" -type f -delete 2>/dev/null || true
	find . -name ".coverage" -type f -delete 2>/dev/null || true
	find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

clean-cache:
	@echo "Python 캐시 정리 중..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean-all: clean clean-test clean-cache
	@echo "모든 임시 파일 정리 완료"

# CI/CD 시뮬레이션
ci:
	@echo "CI/CD 파이프라인 시뮬레이션 중..."
	@echo "1/4 코드 품질 검사..."
	$(PYTHON) scripts/code_quality.py --no-test
	@echo "2/4 단위 테스트..."
	$(PYTHON) scripts/run_tests.py --service all --type unit
	@echo "3/4 통합 테스트..."
	$(PYTHON) scripts/run_tests.py --service all --type integration
	@echo "4/4 커버리지 측정..."
	$(PYTHON) scripts/run_tests.py --service all
	@echo "CI/CD 파이프라인 시뮬레이션 완료!"

# 개발 환경 초기화
init:
	@echo "개발 환경 초기화 중..."
	make install-dev
	make docker-up
	@sleep 15
	@echo "서비스 준비 대기 중..."
	make test
	@echo "개발 환경 초기화 완료!"

# 빠른 검사 (개발 중 자주 사용)
check:
	@echo "빠른 코드 검사 중..."
	$(PYTHON) scripts/code_quality.py --no-test
	$(PYTHON) scripts/run_tests.py --service all --type unit --quiet
	@echo "빠른 검사 완료!"