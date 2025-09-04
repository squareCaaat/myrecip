# 나만의 칵테일 저장소 백엔드

## 아키텍처 개요

마이크로서비스 아키텍처(MSA)로 구성된 칵테일 레시피 관리 시스템입니다.

```plain text
클라이언트 → API Gateway → User Service / Recipe Service
                    ↓
                PostgreSQL + Redis
```

## 서비스 구성

### 1. User Service (Port: 8001)
- **책임**: 사용자 인증 및 계정 관리
- **주요 기능**: 회원가입, 로그인, 사용자 정보 관리
- **API 엔드포인트**: `/api/auth/register`, `/api/auth/login`, `/api/users/me`

### 2. Recipe Service (Port: 8002)
- **책임**: 칵테일 레시피 CRUD 및 이미지 처리
- **주요 기능**: 레시피 생성/조회/수정/삭제, 이미지 생성, 공유 링크 생성
- **API 엔드포인트**: `/api/recipes`, `/api/recipes/{id}`, `/api/recipes/{id}/share`

### 3. API Gateway (Port: 8000)
- **책임**: 요청 라우팅, 인증, CORS 처리
- **주요 기능**: 서비스 프록시, JWT 검증, Rate Limiting

## 기술 스택

- **백엔드**: FastAPI + Python 3.11
- **데이터베이스**: PostgreSQL 15
- **캐시**: Redis 7
- **컨테이너**: Docker + Docker Compose
- **인증**: JWT + bcrypt

## 로컬 개발 환경 실행

```bash
# 1. 전체 환경 실행
docker-compose up -d

# 2. 개별 서비스 실행 (개발용)
cd user-service && uvicorn app.main:app --reload --port 8001
cd recipe-service && uvicorn app.main:app --reload --port 8002
cd api-gateway && uvicorn app.main:app --reload --port 8000
```

## API 문서

각 서비스의 API 문서는 다음 URL에서 확인할 수 있습니다:

- API Gateway: http://localhost:8000/docs
- User Service: http://localhost:8001/docs
- Recipe Service: http://localhost:8002/docs

## 구현된 핵심 기능들
- **레시피 CRUD**: 생성, 조회, 수정, 삭제, 페이징 처리
- **이미지 처리 시스템**: 파일 업로드 + Pillow 기반 시각화 이미지 자동 생성  
- **레시피 공유**: UUID 기반 공유 링크 시스템
- **API Gateway**: JWT 인증, Rate Limiting (60-100 req/min), 로깅 미들웨어
- **서비스 간 통신**: 사용자 정보 자동 전파 (X-User-ID 헤더)
- **MSA**: User Service + Recipe Service + API Gateway

### API 테스트
상세한 테스트 가이드는 [test_api.md](./test_api.md)를 참조하세요.

#### 기본 사용 플로우:
```bash
# 1. 회원가입
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "password123"}'

# 2. 로그인  
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# 3. 레시피 생성
curl -X POST "http://localhost:8000/api/recipes/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "모히또",
    "base_spirit": "럼", 
    "ingredients": [
      {"name": "화이트 럼", "amount": 50, "unit": "ml", "color": "#F5DEB3"},
      {"name": "라임 주스", "amount": 20, "unit": "ml", "color": "#00FF00"}
    ]
  }'

# 4. 시각화 이미지 생성
curl -X GET "http://localhost:8000/api/recipes/{recipe_id}/visual"

# 5. 공유 링크 생성
curl -X POST "http://localhost:8000/api/recipes/{recipe_id}/share" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 환경 설정

환경 변수는 docker-compose.yml에 이미 설정되어 있습니다:

```yaml
environment:
  - DATABASE_URL=${DATABASE_URL}
  - REDIS_URL=redis://redis:6379  
  - SECRET_KEY=${SECRET_KEY}
  - ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## 성능 및 모니터링

- **Rate Limiting**: User Service (60/min), Recipe Service (100/min)
- **로깅**: 모든 요청/응답 시간 추적 (`X-Process-Time` 헤더)
- **헬스체크**: 모든 서비스 상태 실시간 모니터링
- **오류 처리**: 타임아웃, 연결 오류별 적절한 HTTP 상태 코드

