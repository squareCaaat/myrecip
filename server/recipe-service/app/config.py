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
    
    # 애플리케이션 설정
    app_name: str = "My Cocktail Recipe Service"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # 파일 업로드 설정
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB
    allowed_extensions: list = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif").split(",")
    upload_dir: str = os.getenv("UPLOAD_DIR", "/app/uploads")
    
    # CORS 설정
    allowed_origins: list = ["*"]  # 프로덕션에서는 구체적인 도메인으로 변경
    
    class Config:
        env_file = ".env"


# 전역 설정 인스턴스
settings = Settings()


