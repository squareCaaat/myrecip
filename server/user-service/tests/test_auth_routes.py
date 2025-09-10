import pytest
from fastapi import status
from unittest.mock import patch


@pytest.mark.integration
@pytest.mark.auth
class TestAuthRoutes:
    """인증 라우터 통합 테스트"""
    
    def test_register_success(self, test_client, sample_user_data):
        """회원가입 성공 테스트"""
        # Given
        register_data = sample_user_data.copy()
        
        # When
        response = test_client.post("/api/auth/register", json=register_data)
        
        # Then
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["email"] == register_data["email"]
        assert response_data["username"] == register_data["username"]
        assert "user_id" in response_data
        assert "password" not in response_data  # 비밀번호는 응답에 포함되지 않아야 함
    
    def test_register_duplicate_email(self, test_client, created_user_integration, sample_user_data):
        """중복 이메일 회원가입 실패 테스트"""
        # Given
        register_data = sample_user_data.copy()  # 이미 생성된 사용자와 같은 이메일
        
        # When
        response = test_client.post("/api/auth/register", json=register_data)
        
        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "이미 등록된 이메일입니다" in response_data["detail"]
    
    def test_register_invalid_email(self, test_client):
        """잘못된 이메일 형식 회원가입 실패 테스트"""
        # Given
        invalid_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "password123"
        }
        
        # When
        response = test_client.post("/api/auth/register", json=invalid_data)
        
        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_fields(self, test_client):
        """필수 필드 누락 회원가입 실패 테스트"""
        # Given
        incomplete_data = {
            "email": "test@example.com",
            # username과 password 누락
        }
        
        # When
        response = test_client.post("/api/auth/register", json=incomplete_data)
        
        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, test_client, created_user_integration, sample_login_data):
        """로그인 성공 테스트"""
        # Given
        login_data = sample_login_data.copy()
        
        # When
        with patch('app.utils.redis_client.redis_client.set_token', return_value=True):
            response = test_client.post("/api/auth/login", json=login_data)
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "access_token" in response_data
        assert response_data["token_type"] == "bearer"
        assert "expires_in" in response_data
        assert response_data["expires_in"] > 0
    
    def test_login_wrong_email(self, test_client, created_user_integration):
        """잘못된 이메일 로그인 실패 테스트"""
        # Given
        wrong_data = {
            "email": "wrong@example.com",
            "password": "password123"
        }
        
        # When
        response = test_client.post("/api/auth/login", json=wrong_data)
        
        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = response.json()
        assert "이메일 또는 비밀번호가 틀렸습니다" in response_data["detail"]
    
    def test_login_wrong_password(self, test_client, created_user_integration, sample_user_data):
        """잘못된 비밀번호 로그인 실패 테스트"""
        # Given
        wrong_data = {
            "email": sample_user_data["email"],
            "password": "wrongpassword"
        }
        
        # When
        response = test_client.post("/api/auth/login", json=wrong_data)
        
        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = response.json()
        assert "이메일 또는 비밀번호가 틀렸습니다" in response_data["detail"]
    
    def test_get_current_user_success(self, test_client, auth_headers_integration, created_user_integration):
        """현재 사용자 정보 조회 성공 테스트"""
        # When
        with patch('app.utils.redis_client.redis_client.get_token', return_value=auth_headers_integration["Authorization"].split(" ")[1]), \
             patch('app.utils.redis_client.redis_client.is_token_blacklisted', return_value=False):
            response = test_client.get("/api/auth/me", headers=auth_headers_integration)
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["email"] == created_user_integration["email"]
        assert response_data["username"] == created_user_integration["username"]
        assert response_data["user_id"] == created_user_integration["user_id"]
    
    def test_get_current_user_no_token(self, test_client):
        """토큰 없이 현재 사용자 정보 조회 실패 테스트"""
        # When
        response = test_client.get("/api/auth/me")
        
        # Then
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_get_current_user_invalid_token(self, test_client):
        """잘못된 토큰으로 현재 사용자 정보 조회 실패 테스트"""
        # Given
        invalid_headers = {"Authorization": "Bearer invalid.token.here"}
        
        # When
        response = test_client.get("/api/auth/me", headers=invalid_headers)
        
        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_validate_token_success(self, test_client, auth_headers_integration, created_user_integration):
        """토큰 유효성 검증 성공 테스트"""
        # When
        with patch('app.utils.redis_client.redis_client.get_token', return_value=auth_headers_integration["Authorization"].split(" ")[1]), \
             patch('app.utils.redis_client.redis_client.is_token_blacklisted', return_value=False):
            response = test_client.get("/api/auth/validate-token", headers=auth_headers_integration)
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["valid"] is True
        assert response_data["user_id"] == created_user_integration["user_id"]
        assert response_data["username"] == created_user_integration["username"]
    
    def test_validate_token_invalid(self, test_client):
        """잘못된 토큰 유효성 검증 실패 테스트"""
        # Given
        invalid_headers = {"Authorization": "Bearer invalid.token.here"}
        
        # When
        response = test_client.get("/api/auth/validate-token", headers=invalid_headers)
        
        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout_success(self, test_client, auth_headers_integration, created_user_integration):
        """로그아웃 성공 테스트"""
        # When
        with patch('app.utils.redis_client.redis_client.get_token', return_value=auth_headers_integration["Authorization"].split(" ")[1]), \
             patch('app.utils.redis_client.redis_client.is_token_blacklisted', return_value=False), \
             patch('app.utils.redis_client.redis_client.delete_token', return_value=True), \
             patch('app.utils.redis_client.redis_client.blacklist_token', return_value=True):
            response = test_client.post("/api/auth/logout", headers=auth_headers_integration)
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "성공적으로 로그아웃되었습니다" in response_data["message"]
    
    def test_logout_no_token(self, test_client):
        """토큰 없이 로그아웃 실패 테스트"""
        # When
        response = test_client.post("/api/auth/logout")
        
        # Then
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


@pytest.mark.integration
class TestUserRoutes:
    """사용자 관리 라우터 통합 테스트"""
    
    def test_get_my_profile_success(self, test_client, auth_headers_integration, created_user_integration):
        """내 프로필 조회 성공 테스트"""
        # When
        with patch('app.utils.redis_client.redis_client.get_token', return_value=auth_headers_integration["Authorization"].split(" ")[1]), \
             patch('app.utils.redis_client.redis_client.is_token_blacklisted', return_value=False):
            response = test_client.get("/api/users/me", headers=auth_headers_integration)
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["email"] == created_user_integration["email"]
        assert response_data["username"] == created_user_integration["username"]
        assert response_data["user_id"] == created_user_integration["user_id"]
    
    def test_update_my_profile_success(self, test_client, auth_headers_integration, created_user_integration, sample_user_update_data):
        """내 프로필 수정 성공 테스트"""
        # Given
        update_data = sample_user_update_data.copy()
        
        # When
        with patch('app.utils.redis_client.redis_client.get_token', return_value=auth_headers_integration["Authorization"].split(" ")[1]), \
             patch('app.utils.redis_client.redis_client.is_token_blacklisted', return_value=False):
            response = test_client.put("/api/users/me", json=update_data, headers=auth_headers_integration)
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["username"] == update_data["username"]
        assert response_data["email"] == update_data["email"]
        assert response_data["user_id"] == created_user_integration["user_id"]
    
    def test_update_my_profile_partial(self, test_client, auth_headers_integration, created_user_integration):
        """내 프로필 부분 수정 성공 테스트"""
        # Given
        partial_update = {"username": "new_username_only"}
        
        # When
        with patch('app.utils.redis_client.redis_client.get_token', return_value=auth_headers_integration["Authorization"].split(" ")[1]), \
             patch('app.utils.redis_client.redis_client.is_token_blacklisted', return_value=False):
            response = test_client.put("/api/users/me", json=partial_update, headers=auth_headers_integration)
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["username"] == partial_update["username"]
        assert response_data["email"] == created_user_integration["email"]  # 기존 이메일 유지
    
    def test_update_my_profile_no_token(self, test_client, sample_user_update_data):
        """토큰 없이 프로필 수정 실패 테스트"""
        # Given
        update_data = sample_user_update_data.copy()
        
        # When
        response = test_client.put("/api/users/me", json=update_data)
        
        # Then
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_delete_my_account_placeholder(self, test_client, auth_headers_integration):
        """회원 탈퇴 플레이스홀더 테스트"""
        # When
        with patch('app.utils.redis_client.redis_client.get_token', return_value=auth_headers_integration["Authorization"].split(" ")[1]), \
             patch('app.utils.redis_client.redis_client.is_token_blacklisted', return_value=False):
            response = test_client.delete("/api/users/me", headers=auth_headers_integration)
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "추후 구현 예정" in response_data["message"]

