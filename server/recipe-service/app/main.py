from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# 로컬 임포트는 나중에 추가
# from .routers import recipes, images
# from .database import engine, Base

app = FastAPI(
    title="칵테일 저장소 Recipe Service",
    description="칵테일 레시피 관리 및 이미지 처리 서비스",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (업로드된 이미지)
uploads_dir = "/app/uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

app.mount("/static", StaticFiles(directory=uploads_dir), name="static")

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "recipe-service",
        "version": "1.0.0"
    }

# 루트 엔드포인트
@app.get("/")
async def root():
    """루트 경로"""
    return {
        "message": "칵테일 저장소 Recipe Service",
        "docs": "/docs"
    }

# 라우터 등록 (나중에 활성화)
# app.include_router(recipes.router, prefix="/api/recipes", tags=["Recipes"])
# app.include_router(images.router, prefix="/api/images", tags=["Images"])

# 애플리케이션 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("Recipe Service 시작됨")
    # 나중에 데이터베이스 테이블 생성 로직 추가
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

# 애플리케이션 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    print("Recipe Service 종료됨")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )

