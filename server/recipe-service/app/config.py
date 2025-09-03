import os
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 데이터베이스 설정
    database_url: str = Field(default="postgresql://postgres:password@localhost:5432/test_db", env="DATABASE_URL")
    
    # Redis 설정
    redis_url: str = Field(default="redis://redis:6379", env="REDIS_URL")
    
    # JWT 설정
    secret_key: str = os.getenv("SECRET_KEY", None)
    algorithm: str = "HS256"
    
    # 애플리케이션 설정
    app_name: str = "My Cocktail Recipe Service"
    debug: bool = Field(default=False, env="DEBUG")
    
    # 파일 업로드 설정
    max_file_size: int = Field(default=5242880, env="MAX_FILE_SIZE")  # 5MB
    allowed_extensions: List[str] = Field(default=["jpg","jpeg","png","gif"], env="ALLOWED_EXTENSIONS")
    
    upload_dir: str = Field(default="/app/uploads", env="UPLOAD_DIR")
    
    # CORS 설정
    allowed_origins: list = ["*"]  # 프로덕션에서는 구체적인 도메인으로 변경
    
    class Config:
        env_file = ".env"


# 전역 설정 인스턴스
settings = Settings()


