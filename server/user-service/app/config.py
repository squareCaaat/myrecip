import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 데이터베이스 설정
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/test_db")
    
    # Redis 설정
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # JWT 설정
    secret_key: str = os.getenv("SECRET_KEY", None)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # 애플리케이션 설정
    app_name: str = "My Cocktail User Service"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS 설정
    allowed_origins: list = ["*"]  # 프로덕션에서는 구체적인 도메인으로 변경
    
    class Config:
        env_file = ".env"


# 전역 설정 인스턴스
settings = Settings()


