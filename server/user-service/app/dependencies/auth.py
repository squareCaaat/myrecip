from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas import UserResponse
from app.services.user_service import UserService
from app.utils.auth import AuthUtils
from app.utils.redis_client import redis_client

# HTTP Bearer 토큰 스키마
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """현재 로그인한 사용자 정보 반환"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 올바르지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # 토큰이 블랙리스트에 있는지 확인
    if await redis_client.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="만료된 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWT 토큰 검증
    user_id = AuthUtils.get_user_id_from_token(token)
    if user_id is None:
        raise credentials_exception

    # Redis에서 토큰 확인
    stored_token = await redis_client.get_token(user_id)
    if stored_token != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 세션입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 사용자 정보 조회
    user_service = UserService(db)
    try:
        user = await user_service.get_user_by_id(user_id)
        return user
    except HTTPException:
        raise credentials_exception


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserResponse]:
    """선택적 인증 (토큰이 있으면 사용자 정보 반환, 없으면 None)"""

    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
