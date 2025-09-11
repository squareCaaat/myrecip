from datetime import datetime, timedelta
from typing import Optional

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from passlib.hash import bcrypt

from app.config import settings

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthUtils:
    """인증 관련 유틸리티 클래스"""

    @staticmethod
    def hash_password(password: str) -> str:
        """비밀번호 해싱"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """JWT 액세스 토큰 생성"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """JWT 토큰 검증 및 페이로드 반환"""
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            return payload
        except InvalidTokenError:
            return None

    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[str]:
        """토큰에서 사용자 ID 추출"""
        payload = AuthUtils.verify_token(token)
        if payload:
            return payload.get("sub")
        return None
