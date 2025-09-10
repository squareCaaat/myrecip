import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# 사용자 기본 스키마
class UserBase(BaseModel):
    email: EmailStr
    username: str


# 사용자 생성 스키마 (회원가입용)
class UserCreate(UserBase):
    password: str


# 사용자 업데이트 스키마
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


# 사용자 로그인 스키마
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# 사용자 응답 스키마 (비밀번호 제외)
class UserResponse(UserBase):
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# JWT 토큰 스키마
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# 토큰 데이터 스키마
class TokenData(BaseModel):
    user_id: Optional[str] = None
