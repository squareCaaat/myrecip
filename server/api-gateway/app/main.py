import logging
import time
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.middleware.auth import AuthMiddleware

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate Limiter 설정
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # Startup
    print("API Gateway 시작됨")
    yield
    # Shutdown
    print("API Gateway 종료됨")


app = FastAPI(
    title="칵테일 저장소 API Gateway",
    description="마이크로서비스 API 게이트웨이",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Rate Limiting 설정
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 인증 미들웨어 추가
auth_middleware = AuthMiddleware()
app.middleware("http")(auth_middleware)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 로깅 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # 요청 로깅
    logger.info(f"Request: {request.method} {request.url.path}")

    response = await call_next(request)

    # 응답 시간 계산
    process_time = time.time() - start_time

    # 응답 로깅
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")

    # 응답 헤더에 처리 시간 추가
    response.headers["X-Process-Time"] = str(process_time)

    return response


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
        "services": services_health,
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
            "recipe-service": f"{RECIPE_SERVICE_URL}/docs",
        },
    }


# 향상된 프록시 라우팅
@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("60/minute")
async def proxy_user_service(request: Request, path: str):
    """User Service로 요청 프록시 (Rate Limited)"""
    try:
        async with httpx.AsyncClient(timeout=settings.service_timeout) as client:
            # 요청 헤더 및 바디 전달
            headers = dict(request.headers)

            # Host 헤더 제거 (서비스 간 통신 시 충돌 방지)
            headers.pop("host", None)

            body = await request.body()

            # URL 구성
            service_path = request.url.path.replace("/api/", "/api/")
            url = f"{USER_SERVICE_URL}{service_path}"

            logger.info(f"Proxying to User Service: {url}")

            response = await client.request(
                method=request.method, url=url, headers=headers, content=body
            )

            # 응답 헤더 정리 (불필요한 헤더 제거)
            response_headers = dict(response.headers)
            response_headers.pop("content-encoding", None)
            response_headers.pop("content-length", None)

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type"),
            )

    except httpx.TimeoutException:
        logger.error(f"User Service timeout: {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="User Service 응답 시간 초과"
        )
    except httpx.ConnectError:
        logger.error(f"User Service connection error: {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User Service에 연결할 수 없습니다",
        )
    except Exception as e:
        logger.error(f"User Service proxy error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User Service 연결 오류: {str(e)}",
        )


@app.api_route("/api/recipes/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("100/minute")  # 레시피는 더 높은 한도
async def proxy_recipe_service(request: Request, path: str):
    """Recipe Service로 요청 프록시 (Rate Limited)"""
    try:
        async with httpx.AsyncClient(timeout=settings.service_timeout) as client:
            # 요청 헤더 및 바디 전달
            headers = dict(request.headers)

            # Host 헤더 제거
            headers.pop("host", None)

            body = await request.body()

            # URL 구성
            url = f"{RECIPE_SERVICE_URL}/api/recipes/{path}"

            logger.info(f"Proxying to Recipe Service: {url}")

            response = await client.request(
                method=request.method, url=url, headers=headers, content=body
            )

            # 응답 헤더 정리
            response_headers = dict(response.headers)
            response_headers.pop("content-encoding", None)
            response_headers.pop("content-length", None)

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type"),
            )

    except httpx.TimeoutException:
        logger.error(f"Recipe Service timeout: {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Recipe Service 응답 시간 초과",
        )
    except httpx.ConnectError:
        logger.error(f"Recipe Service connection error: {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recipe Service에 연결할 수 없습니다",
        )
    except Exception as e:
        logger.error(f"Recipe Service proxy error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recipe Service 연결 오류: {str(e)}",
        )


# 기존 on_event는 lifespan으로 마이그레이션됨

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
