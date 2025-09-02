# 나만의 칵테일 저장소 백엔드

## 아키텍처 개요

마이크로서비스 아키텍처(MSA)로 구성된 칵테일 레시피 관리 시스템입니다.

```
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


