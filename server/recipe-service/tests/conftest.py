import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 테스트 환경 설정
TEST_DATABASE_URL = "postgresql://testuser:password@localhost:5433/cocktail_db_test"
TEST_ASYNC_DATABASE_URL = TEST_DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# 테스트용 환경 변수 설정
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SECRET_KEY"] = "test-secret-key"

import asyncio
import uuid
from decimal import Decimal

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
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
        transaction = await session.begin()  # Nested transaction
        try:
            yield session
        finally:
            try:
                if transaction.is_active:
                    await transaction.rollback()
            except Exception:
                pass


@pytest.fixture
def test_client(test_db_session):
    """테스트용 FastAPI 클라이언트"""
    with TestClient(app) as client:
        yield client


# 테스트 데이터 픽스처
@pytest.fixture
def test_user_id():
    """테스트용 사용자 ID"""
    return str(uuid.uuid4())


@pytest.fixture
def sample_recipe_data():
    """테스트용 레시피 데이터"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "title": f"모히또_{unique_id}",
        "base_spirit": "럼",
        "instructions": "민트잎을 으깨고 럼과 라임을 넣어 섞는다",
        "notes": "민트는 너무 세게 으깨지 말 것",
        "ingredients": [
            {
                "name": "화이트 럼",
                "amount": Decimal("50.00"),
                "unit": "ml",
                "color": "#F5DEB3",
            },
            {
                "name": "라임 주스",
                "amount": Decimal("20.00"),
                "unit": "ml",
                "color": "#00FF00",
            },
            {
                "name": "민트잎",
                "amount": Decimal("10.00"),
                "unit": "잎",
                "color": "#98FB98",
            },
        ],
    }


@pytest.fixture
def sample_recipe_update_data():
    """테스트용 레시피 업데이트 데이터"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "title": f"업데이트된 모히또_{unique_id}",
        "base_spirit": "다크 럼",
        "instructions": "업데이트된 제작 방법",
        "notes": "업데이트된 팁",
        "ingredients": [
            {
                "name": "다크 럼",
                "amount": Decimal("60.00"),
                "unit": "ml",
                "color": "#8B4513",
            },
            {
                "name": "라임 주스",
                "amount": Decimal("25.00"),
                "unit": "ml",
                "color": "#00FF00",
            },
        ],
    }


@pytest_asyncio.fixture
async def created_recipe(test_db_session, sample_recipe_data, test_user_id):
    """테스트용 생성된 레시피"""
    from app.models.schemas import RecipeCreate
    from app.services.recipe_service import RecipeService

    recipe_service = RecipeService(test_db_session)
    recipe_create = RecipeCreate(**sample_recipe_data)
    recipe = await recipe_service.create_recipe(recipe_create, test_user_id)
    await test_db_session.commit()
    return recipe


@pytest.fixture
def auth_headers(test_user_id):
    """테스트용 인증 헤더 (X-User-ID 헤더 사용)"""
    return {"X-User-ID": test_user_id}


@pytest.fixture
def mock_image_file():
    """테스트용 모킹 이미지 파일"""
    from io import BytesIO

    from fastapi import UploadFile

    # 가짜 이미지 데이터
    image_data = b"fake_image_data_for_testing"
    image_file = BytesIO(image_data)

    upload_file = UploadFile(
        filename="test_image.jpg",
        file=image_file,
        size=len(image_data),
        headers={"content-type": "image/jpeg"},
    )

    return upload_file


# pytest 설정
def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line("markers", "unit: 단위 테스트")
    config.addinivalue_line("markers", "integration: 통합 테스트")
    config.addinivalue_line("markers", "recipe: 레시피 관련 테스트")
    config.addinivalue_line("markers", "image: 이미지 처리 테스트")
    config.addinivalue_line("markers", "slow: 느린 테스트")
