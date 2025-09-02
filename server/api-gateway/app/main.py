from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
from app.config import settings

# 로컬 임포트는 나중에 추가
# from .routes import proxy

app = FastAPI(
    title="칵테일 저장소 API Gateway",
    description="마이크로서비스 API 게이트웨이",
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

# 서비스 URL 설정
USER_SERVICE_URL = settings.user_service_url
RECIPE_SERVICE_URL = settings.recipe_service_url

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    services_health = {}
    
    # User Service 헬스체크
    try:
        print(f"User Service URL: {USER_SERVICE_URL}")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{USER_SERVICE_URL}/health", timeout=5.0)
            services_health["user-service"] = response.json()
    except Exception as e:
        services_health["user-service"] = {"status": "unhealthy", "error": str(e)}
    
    # Recipe Service 헬스체크
    try:
        print(f"Recipe Service URL: {RECIPE_SERVICE_URL}")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RECIPE_SERVICE_URL}/health", timeout=5.0)
            services_health["recipe-service"] = response.json()
    except Exception as e:
        services_health["recipe-service"] = {"status": "unhealthy", "error": str(e)}
    
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0",
        "services": services_health
    }

# 루트 엔드포인트
@app.get("/")
async def root():
    """루트 경로"""
    return {
        "message": "칵테일 저장소 API Gateway",
        "docs": "/docs",
        "services": {
            "user-service": f"{USER_SERVICE_URL}/docs",
            "recipe-service": f"{RECIPE_SERVICE_URL}/docs"
        }
    }

# 기본 프록시 라우팅 (나중에 개선)
@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_user_service(request: Request, path: str):
    """User Service로 요청 프록시"""
    try:
        async with httpx.AsyncClient() as client:
            # 요청 헤더 및 바디 전달
            headers = dict(request.headers)
            body = await request.body()
            
            # User Service로 요청 전달
            url = f"{USER_SERVICE_URL}/api/{request.url.path.split('/')[-2]}/{path}"
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                timeout=30.0
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User Service 연결 오류: {str(e)}")

@app.api_route("/api/recipes/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_recipe_service(request: Request, path: str):
    """Recipe Service로 요청 프록시"""
    try:
        async with httpx.AsyncClient() as client:
            # 요청 헤더 및 바디 전달
            headers = dict(request.headers)
            body = await request.body()
            
            # Recipe Service로 요청 전달
            url = f"{RECIPE_SERVICE_URL}/api/recipes/{path}"
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                timeout=30.0
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recipe Service 연결 오류: {str(e)}")

# 애플리케이션 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("API Gateway 시작됨")

# 애플리케이션 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    print("API Gateway 종료됨")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

