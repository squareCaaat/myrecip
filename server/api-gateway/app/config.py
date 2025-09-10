import os
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 서비스 URL 설정 (Docker 서비스 이름 사용)
    user_service_url: str = Field(default="http://user-service:8001", alias="USER_SERVICE_URL")
    recipe_service_url: str = Field(default="http://recipe-service:8002", alias="RECIPE_SERVICE_URL")
    
    # Redis 설정
    redis_url: str = Field(default="redis://redis:6379", alias="REDIS_URL")
    
    # JWT 설정
    secret_key: str = Field(default=None, alias="SECRET_KEY")
    algorithm: str = "HS256"
    
    # 애플리케이션 설정
    app_name: str = "My Cocktail API Gateway"
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Rate Limiting 설정
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    
    # CORS 설정
    allowed_origins: list = ["*"]  # 프로덕션에서는 구체적인 도메인으로 변경
    
    # 타임아웃 설정
    service_timeout: float = Field(default=30.0, alias="SERVICE_TIMEOUT")
    
    model_config = ConfigDict(env_file=".env")


# 전역 설정 인스턴스
settings = Settings()