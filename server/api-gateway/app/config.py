import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 서비스 URL 설정 (Docker 서비스 이름 사용)
    user_service_url: str = Field(default="http://user-service:8001", env="USER_SERVICE_URL")
    recipe_service_url: str = Field(default="http://recipe-service:8002", env="RECIPE_SERVICE_URL")
    
    # Redis 설정
    redis_url: str = Field(default="redis://redis:6379", env="REDIS_URL")
    
    # JWT 설정
    secret_key: str = Field(default=None, env="SECRET_KEY")
    algorithm: str = "HS256"
    
    # 애플리케이션 설정
    app_name: str = "My Cocktail API Gateway"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Rate Limiting 설정
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # CORS 설정
    allowed_origins: list = ["*"]  # 프로덕션에서는 구체적인 도메인으로 변경
    
    # 타임아웃 설정
    service_timeout: float = Field(default=30.0, env="SERVICE_TIMEOUT")
    
    class Config:
        env_file = ".env"


# 전역 설정 인스턴스
settings = Settings()