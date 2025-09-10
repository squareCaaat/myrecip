import pytest
import uuid
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from app.services.user_service import UserService
from app.models.schemas import UserCreate, UserLogin, UserUpdate
from app.models.user import User


@pytest.mark.unit
@pytest.mark.auth
class TestUserService:
    """UserService 단위 테스트"""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, test_db_session, sample_user_data):
        """사용자 생성 성공 테스트"""
        # Given
        user_service = UserService(test_db_session)
        user_create = UserCreate(**sample_user_data)
        
        # When
        result = await user_service.create_user(user_create)
        
        # Then
        assert result.email == sample_user_data["email"]
        assert result.username == sample_user_data["username"]
        assert hasattr(result, "user_id")
        assert hasattr(result, "created_at")
        assert hasattr(result, "updated_at")
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, test_db_session, created_user, sample_user_data):
        """중복 이메일로 사용자 생성 실패 테스트"""
        # Given
        user_service = UserService(test_db_session)
        user_create = UserCreate(**sample_user_data)  # 같은 이메일 사용
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(user_create)
        
        assert exc_info.value.status_code == 400
        assert "이미 등록된 이메일입니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, test_db_session, created_user, sample_login_data):
        """사용자 인증 성공 테스트"""
        # Given
        user_service = UserService(test_db_session)
        login_data = UserLogin(**sample_login_data)
        
        # When
        with patch('app.utils.redis_client.redis_client.set_token', return_value=True):
            result = await user_service.authenticate_user(login_data)
        
        # Then
        assert result.access_token is not None
        assert result.token_type == "bearer"
        assert result.expires_in > 0
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_email(self, test_db_session, created_user):
        """잘못된 이메일로 인증 실패 테스트"""
        # Given
        user_service = UserService(test_db_session)
        login_data = UserLogin(email="wrong@example.com", password="password123")
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await user_service.authenticate_user(login_data)
        
        assert exc_info.value.status_code == 401
        assert "이메일 또는 비밀번호가 틀렸습니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, test_db_session, created_user, sample_user_data):
        """잘못된 비밀번호로 인증 실패 테스트"""
        # Given
        user_service = UserService(test_db_session)
        login_data = UserLogin(email=sample_user_data["email"], password="wrongpassword")
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await user_service.authenticate_user(login_data)
        
        assert exc_info.value.status_code == 401
        assert "이메일 또는 비밀번호가 틀렸습니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, test_db_session, created_user):
        """사용자 ID로 조회 성공 테스트"""
        # Given
        user_service = UserService(test_db_session)
        user_id = str(created_user.user_id)
        
        # When
        result = await user_service.get_user_by_id(user_id)
        
        # Then
        assert result.user_id == created_user.user_id
        assert result.email == created_user.email
        assert result.username == created_user.username
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, test_db_session):
        """존재하지 않는 사용자 ID로 조회 실패 테스트"""
        # Given
        user_service = UserService(test_db_session)
        non_existent_id = str(uuid.uuid4())
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await user_service.get_user_by_id(non_existent_id)
        
        assert exc_info.value.status_code == 404
        assert "사용자를 찾을 수 없습니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_invalid_uuid(self, test_db_session):
        """잘못된 UUID 형식으로 조회 실패 테스트"""
        # Given
        user_service = UserService(test_db_session)
        invalid_uuid = "invalid-uuid"
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await user_service.get_user_by_id(invalid_uuid)
        
        assert exc_info.value.status_code == 400
        assert "올바르지 않은 사용자 ID 형식입니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, test_db_session, created_user, sample_user_update_data):
        """사용자 정보 수정 성공 테스트"""
        # Given
        user_service = UserService(test_db_session)
        user_id = str(created_user.user_id)
        update_data = UserUpdate(**sample_user_update_data)
        
        # When
        result = await user_service.update_user(user_id, update_data)
        
        # Then
        assert result.user_id == created_user.user_id
        assert result.username == sample_user_update_data["username"]
        assert result.email == sample_user_update_data["email"]
    
    @pytest.mark.asyncio
    async def test_update_user_duplicate_email(self, test_db_session, created_user):
        """중복 이메일로 사용자 정보 수정 실패 테스트"""
        # Given
        user_service = UserService(test_db_session)
        
        # 다른 사용자 생성
        another_user_data = {
            "email": "another@example.com",
            "username": "anotheruser",
            "password": "password123"
        }
        another_user = await user_service.create_user(UserCreate(**another_user_data))
        
        # 기존 사용자의 이메일을 다른 사용자 이메일로 변경 시도
        user_id = str(created_user.user_id)
        update_data = UserUpdate(email="another@example.com")
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await user_service.update_user(user_id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "이미 등록된 이메일입니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_logout_user_success(self, test_db_session, created_user):
        """사용자 로그아웃 성공 테스트"""
        # Given
        user_service = UserService(test_db_session)
        user_id = str(created_user.user_id)
        test_token = "test.token.here"
        
        # When
        with patch('app.utils.redis_client.redis_client.delete_token', return_value=True), \
             patch('app.utils.redis_client.redis_client.blacklist_token', return_value=True), \
             patch('app.utils.auth.AuthUtils.verify_token', return_value={"exp": 9999999999}):
            result = await user_service.logout_user(user_id, test_token)
        
        # Then
        assert result is True


@pytest.mark.unit
class TestAuthUtils:
    """AuthUtils 단위 테스트"""
    
    def test_hash_password(self):
        """비밀번호 해싱 테스트"""
        from app.utils.auth import AuthUtils
        
        # Given
        password = "testpassword123"
        
        # When
        hashed = AuthUtils.hash_password(password)
        
        # Then
        assert hashed != password
        assert len(hashed) > 0
        assert AuthUtils.verify_password(password, hashed) is True
    
    def test_verify_password_success(self):
        """비밀번호 검증 성공 테스트"""
        from app.utils.auth import AuthUtils
        
        # Given
        password = "testpassword123"
        hashed = AuthUtils.hash_password(password)
        
        # When
        result = AuthUtils.verify_password(password, hashed)
        
        # Then
        assert result is True
    
    def test_verify_password_failure(self):
        """비밀번호 검증 실패 테스트"""
        from app.utils.auth import AuthUtils
        
        # Given
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = AuthUtils.hash_password(password)
        
        # When
        result = AuthUtils.verify_password(wrong_password, hashed)
        
        # Then
        assert result is False
    
    def test_create_access_token(self):
        """JWT 토큰 생성 테스트"""
        from app.utils.auth import AuthUtils
        
        # Given
        data = {"sub": "test-user-id"}
        
        # When
        token = AuthUtils.create_access_token(data)
        
        # Then
        assert token is not None
        assert len(token) > 0
        assert "." in token  # JWT 형식 확인
    
    def test_verify_token_success(self):
        """JWT 토큰 검증 성공 테스트"""
        from app.utils.auth import AuthUtils
        
        # Given
        data = {"sub": "test-user-id"}
        token = AuthUtils.create_access_token(data)
        
        # When
        payload = AuthUtils.verify_token(token)
        
        # Then
        assert payload is not None
        assert payload["sub"] == "test-user-id"
    
    def test_verify_token_invalid(self):
        """JWT 토큰 검증 실패 테스트"""
        from app.utils.auth import AuthUtils
        
        # Given
        invalid_token = "invalid.token.here"
        
        # When
        payload = AuthUtils.verify_token(invalid_token)
        
        # Then
        assert payload is None
    
    def test_get_user_id_from_token(self):
        """토큰에서 사용자 ID 추출 테스트"""
        from app.utils.auth import AuthUtils
        
        # Given
        user_id = "test-user-id"
        data = {"sub": user_id}
        token = AuthUtils.create_access_token(data)
        
        # When
        extracted_id = AuthUtils.get_user_id_from_token(token)
        
        # Then
        assert extracted_id == user_id

