import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 서비스 URL 설정 (Docker 서비스 이름 사용)
    user_service_url: str = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
    recipe_service_url: str = os.getenv("RECIPE_SERVICE_URL", "http://recipe-service:8002")
    
    # Redis 설정
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # JWT 설정
    secret_key: str = os.getenv("SECRET_KEY", None)
    algorithm: str = "HS256"
    
    # 애플리케이션 설정
    app_name: str = "My Cocktail API Gateway"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Rate Limiting 설정
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # CORS 설정
    allowed_origins: list = ["*"]  # 프로덕션에서는 구체적인 도메인으로 변경
    
    # 타임아웃 설정
    service_timeout: float = float(os.getenv("SERVICE_TIMEOUT", "30.0"))
    
    class Config:
        env_file = ".env"


# 전역 설정 인스턴스
settings = Settings()