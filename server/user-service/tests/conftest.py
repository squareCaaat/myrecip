import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 테스트 환경 설정
TEST_DATABASE_URL = "postgresql://postgres:password123!@localhost:5432/cocktail_db_test"
TEST_ASYNC_DATABASE_URL = TEST_DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)
TEST_REDIS_URL = "redis://localhost:6379/1"  # 테스트용 DB 1번 사용

# 테스트용 환경 변수 설정
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["REDIS_URL"] = TEST_REDIS_URL
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

import asyncio
import uuid

import pytest
import pytest_asyncio
import redis
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """이벤트 루프 설정"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """테스트용 데이터베이스 엔진"""
    engine = create_async_engine(TEST_ASYNC_DATABASE_URL, echo=False)

    # 테스트 데이터베이스 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 테스트 완료 후 테이블 삭제
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_engine):
    """테스트용 데이터베이스 세션"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
def test_redis():
    """테스트용 Redis 클라이언트"""
    client = redis.Redis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield client
    # 테스트 완료 후 Redis 데이터 삭제
    client.flushdb()


@pytest.fixture
def test_client(test_db_session):
    """테스트용 FastAPI 클라이언트"""
    with TestClient(app) as client:
        yield client


# 테스트 데이터 픽스처
@pytest.fixture
def sample_user_data():
    """테스트용 사용자 데이터"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "password123",
    }


@pytest.fixture
def sample_login_data(sample_user_data):
    """테스트용 로그인 데이터"""
    return {
        "email": sample_user_data["email"],
        "password": sample_user_data["password"],
    }


@pytest.fixture
def sample_user_update_data():
    """테스트용 사용자 업데이트 데이터"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"updated_user_{unique_id}",
        "email": f"updated_{unique_id}@example.com",
    }


@pytest_asyncio.fixture
async def created_user(test_db_session, sample_user_data):
    """테스트용 생성된 사용자"""
    from app.models.schemas import UserCreate
    from app.services.user_service import UserService

    user_service = UserService(test_db_session)
    user_create = UserCreate(**sample_user_data)
    user = await user_service.create_user(user_create)
    await test_db_session.commit()
    return user


# 통합 테스트용
@pytest.fixture
def created_user_integration(test_client, sample_user_data):
    """테스트용 생성된 사용자"""
    response = test_client.post("/api/auth/register", json=sample_user_data)
    assert response.status_code == 201
    return response.json()


@pytest_asyncio.fixture
async def authenticated_user_token(test_client, created_user, sample_login_data):
    """테스트용 인증된 사용자 토큰"""
    response = test_client.post("/api/auth/login", json=sample_login_data)
    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]


# 통합 테스트용
@pytest.fixture
def authenticated_user_token_integration(
    test_client, created_user_integration, sample_login_data
):
    """테스트용 인증된 사용자 토큰"""
    response = test_client.post("/api/auth/login", json=sample_login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(authenticated_user_token):
    """테스트용 인증 헤더"""
    return {"Authorization": f"Bearer {authenticated_user_token}"}


@pytest.fixture
def auth_headers_integration(authenticated_user_token_integration):
    """테스트용 인증 헤더"""
    return {"Authorization": f"Bearer {authenticated_user_token_integration}"}


# pytest 설정
def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line("markers", "unit: 단위 테스트")
    config.addinivalue_line("markers", "integration: 통합 테스트")
    config.addinivalue_line("markers", "auth: 인증 관련 테스트")
    config.addinivalue_line("markers", "slow: 느린 테스트")


# 테스트 간 데이터 정리
@pytest.fixture(autouse=True)
async def cleanup_test_data(test_engine):
    """테스트 간 데이터 정리"""
    yield
    # 테스트 완료 후 테스트 데이터 정리
    async with test_engine.begin() as conn:
        await conn.execute(
            text("DELETE FROM users WHERE email LIKE 'test_%@example.com'")
        )
