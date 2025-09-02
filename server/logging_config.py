import logging
import sys
from typing import Dict, Any


def setup_logging(service_name: str, debug: bool = False) -> None:
    """
    로깅 설정 초기화
    
    Args:
        service_name: 서비스 이름
        debug: 디버그 모드 여부
    """
    
    # 로그 레벨 설정
    log_level = logging.DEBUG if debug else logging.INFO
    
    # 로그 포맷 설정
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        f"[{service_name}] - %(message)s"
    )
    
    # 루트 로거 설정
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # FastAPI 및 Uvicorn 로거 설정
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(log_level)
    
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(log_level)
    
    # SQLAlchemy 로거 설정 (쿼리 로깅)
    if debug:
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        sqlalchemy_logger.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    로거 인스턴스 반환
    
    Args:
        name: 로거 이름
        
    Returns:
        Logger 인스턴스
    """
    return logging.getLogger(name)


