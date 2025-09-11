# 🧪 칵테일 저장소 API 테스트 가이드

## 1. 회원가입 및 로그인

### 회원가입
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "cocktail_lover",
    "password": "password123"
  }'
```

### 로그인
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**응답 예시:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

## 2. 레시피 관리

### 새 레시피 생성
```bash
curl -X POST "http://localhost:8000/api/recipes/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "모히또",
    "base_spirit": "럼",
    "instructions": "민트잎을 으깨고 럼과 라임을 넣어 섞는다",
    "notes": "민트는 너무 세게 으깨지 말 것",
    "ingredients": [
      {
        "name": "화이트 럼",
        "amount": 50,
        "unit": "ml",
        "color": "#F5DEB3"
      },
      {
        "name": "라임 주스",
        "amount": 20,
        "unit": "ml", 
        "color": "#00FF00"
      },
      {
        "name": "민트잎",
        "amount": 10,
        "unit": "잎",
        "color": "#98FB98"
      }
    ]
  }'
```

### 내 레시피 목록 조회
```bash
curl -X GET "http://localhost:8000/api/recipes/?page=1&per_page=5" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 레시피 상세 조회
```bash
curl -X GET "http://localhost:8000/api/recipes/{recipe_id}" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 3. 이미지 관리

### 레시피 이미지 업로드
```bash
curl -X POST "http://localhost:8000/api/recipes/{recipe_id}/image" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@cocktail_photo.jpg"
```

### 시각화 이미지 생성
```bash
curl -X GET "http://localhost:8000/api/recipes/{recipe_id}/visual" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 4. 레시피 공유

### 공유 링크 생성
```bash
curl -X POST "http://localhost:8000/api/recipes/{recipe_id}/share" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**응답 예시:**
```json
{
  "share_id": "550e8400-e29b-41d4-a716-446655440000",
  "share_url": "/shared/550e8400-e29b-41d4-a716-446655440000"
}
```

### 공유된 레시피 조회 (인증 불필요)
```bash
curl -X GET "http://localhost:8000/api/recipes/shared/{share_id}"
```

## 5. 사용자 정보 관리

### 내 정보 조회
```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 내 정보 수정
```bash
curl -X PUT "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_username"
  }'
```

### 로그아웃
```bash
curl -X POST "http://localhost:8000/api/auth/logout" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 6. 시스템 상태 확인

### 헬스체크
```bash
curl -X GET "http://localhost:8000/health"
```

**응답 예시:**
```json
{
  "status": "healthy",
  "service": "api-gateway", 
  "version": "1.0.0",
  "services": {
    "user-service": {
      "status": "healthy",
      "service": "user-service"
    },
    "recipe-service": {
      "status": "healthy", 
      "service": "recipe-service"
    }
  }
}
```

## ⚡ 고급 기능

### Rate Limiting 테스트
API Gateway는 다음과 같은 Rate Limit이 적용됩니다:
- User Service: 60 requests/minute
- Recipe Service: 100 requests/minute

### 로깅 확인
```bash
docker-compose logs api-gateway -f
```

### 성능 모니터링
모든 응답에 `X-Process-Time` 헤더가 포함되어 처리 시간을 확인할 수 있습니다.

## 🛠️ 오류 해결

### 인증 오류 (401)
- JWT 토큰이 만료되었거나 유효하지 않음
- Redis에서 토큰이 삭제되었거나 블랙리스트에 추가됨

### 권한 오류 (403)  
- 다른 사용자의 레시피에 접근 시도
- 비공개 레시피에 권한 없이 접근

### Rate Limit 오류 (429)
- 요청 제한 초과, 잠시 후 재시도

### 서비스 연결 오류 (503/504)
- 마이크로서비스가 다운되었거나 응답 지연
- `docker-compose ps`로 서비스 상태 확인

