from datetime import timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.models.schemas import UserCreate, UserLogin, UserResponse, UserUpdate, Token
from app.utils.auth import AuthUtils
from app.utils.redis_client import redis_client
from app.config import settings
import uuid


class UserService:
    """사용자 관련 비즈니스 로직"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """사용자 생성 (회원가입)"""
        
        # 이메일 중복 검사
        stmt = select(User).where(User.email == user_data.email)
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다."
            )
        
        # 비밀번호 해싱
        hashed_password = AuthUtils.hash_password(user_data.password)
        
        # 새 사용자 생성
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password
        )
        
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        
        return UserResponse.model_validate(new_user)
    
    async def authenticate_user(self, login_data: UserLogin) -> Token:
        """사용자 인증 (로그인)"""
        
        # 사용자 조회
        stmt = select(User).where(User.email == login_data.email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not AuthUtils.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 틀렸습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # JWT 토큰 생성
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = AuthUtils.create_access_token(
            data={"sub": str(user.user_id)},
            expires_delta=access_token_expires
        )
        
        # Redis에 토큰 저장
        await redis_client.set_token(
            str(user.user_id), 
            access_token, 
            settings.access_token_expire_minutes * 60
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """사용자 ID로 사용자 조회"""
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="올바르지 않은 사용자 ID 형식입니다."
            )
        
        stmt = select(User).where(User.user_id == user_uuid)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        return UserResponse.model_validate(user)
    
    async def update_user(self, user_id: str, update_data: UserUpdate) -> UserResponse:
        """사용자 정보 수정"""
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="올바르지 않은 사용자 ID 형식입니다."
            )
        
        stmt = select(User).where(User.user_id == user_uuid)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        # 이메일 변경 시 중복 검사
        if update_data.email and update_data.email != user.email:
            stmt = select(User).where(User.email == update_data.email)
            result = await self.db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 등록된 이메일입니다."
                )
            user.email = update_data.email
        
        # 사용자명 업데이트
        if update_data.username:
            user.username = update_data.username
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return UserResponse.model_validate(user)
    
    async def logout_user(self, user_id: str, token: str) -> bool:
        """사용자 로그아웃"""
        # Redis에서 토큰 삭제
        await redis_client.delete_token(user_id)
        
        # 토큰을 블랙리스트에 추가 (남은 유효시간 동안)
        payload = AuthUtils.verify_token(token)
        if payload and payload.get("exp"):
            import time
            remaining_time = payload["exp"] - int(time.time())
            if remaining_time > 0:
                await redis_client.blacklist_token(token, remaining_time)
        
        return True

