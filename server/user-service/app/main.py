from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, async_engine
from app.routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # Startup
    print("User Service 시작됨")

    # 데이터베이스 테이블 생성
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("데이터베이스 테이블 생성 완료")
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")

    yield

    # Shutdown
    print("User Service 종료됨")

    # 데이터베이스 연결 종료
    await async_engine.dispose()


app = FastAPI(
    title="칵테일 저장소 User Service",
    description="사용자 인증 및 계정 관리 서비스",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "user-service",
        "version": "1.0.0",
        "database": "connected",
    }


# 루트 엔드포인트
@app.get("/")
async def root():
    """루트 경로"""
    return {
        "message": "칵테일 저장소 User Service",
        "docs": "/docs",
        "endpoints": {"auth": "/api/auth", "users": "/api/users"},
    }


# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

# 기존 on_event는 lifespan으로 마이그레이션됨

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
