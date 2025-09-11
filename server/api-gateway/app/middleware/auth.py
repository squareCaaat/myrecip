import json
from typing import Optional

import httpx
import redis
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from app.config import settings


class AuthMiddleware:
    """JWT 인증 미들웨어"""

    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            settings.redis_url, decode_responses=True
        )
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm

        # 인증이 필요한 경로 패턴
        self.protected_paths = [
            "/api/auth/logout",
            "/api/auth/me",
            "/api/users/",
            "/api/recipes/",
        ]

        # 인증이 불필요한 경로 패턴
        self.public_paths = [
            "/api/auth/register",
            "/api/auth/login",
            "/api/recipes/shared/",
            "/health",
            "/docs",
            "/openapi.json",
        ]

    async def __call__(self, request: Request, call_next):
        """미들웨어 실행"""

        # 정적 파일 및 문서는 통과
        if request.url.path.startswith("/static") or request.url.path in [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]:
            return await call_next(request)

        # 공개 경로 확인
        if self._is_public_path(request.url.path):
            return await call_next(request)

        # 보호된 경로인지 확인
        if self._is_protected_path(request.url.path):
            # JWT 토큰 검증
            user_id = await self._verify_token(request)
            if not user_id:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "인증이 필요합니다."},
                )

            # 요청 헤더에 사용자 ID 추가
            request.headers.__dict__["_list"].append((b"x-user-id", user_id.encode()))

        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        """공개 경로인지 확인"""
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True
        return False

    def _is_protected_path(self, path: str) -> bool:
        """보호된 경로인지 확인"""
        for protected_path in self.protected_paths:
            if path.startswith(protected_path):
                return True
        return False

    async def _verify_token(self, request: Request) -> Optional[str]:
        """JWT 토큰 검증 및 사용자 ID 반환"""

        # Authorization 헤더에서 토큰 추출
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None

        token = authorization.split(" ")[1]

        try:
            # 토큰이 블랙리스트에 있는지 확인
            if self.redis_client.exists(f"blacklist_token:{token}"):
                return None

            # JWT 토큰 검증
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")

            if not user_id:
                return None

            # Redis에서 토큰 유효성 확인
            stored_token = self.redis_client.get(f"user_token:{user_id}")
            if stored_token != token:
                return None

            return user_id

        except JWTError:
            return None
        except Exception:
            return None


async def auth_middleware_factory():
    """인증 미들웨어 팩토리"""
    return AuthMiddleware()
