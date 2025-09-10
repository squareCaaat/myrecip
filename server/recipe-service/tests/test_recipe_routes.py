import json
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, mock_open, patch

import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.recipe
class TestRecipeRoutes:
    """레시피 라우터 통합 테스트"""

    def test_get_my_recipes_success(self, test_client, auth_headers, created_recipe):
        """내 레시피 목록 조회 성공 테스트"""
        # When
        response = test_client.get("/api/recipes/", headers=auth_headers)

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "recipes" in response_data
        assert "total" in response_data
        assert "page" in response_data
        assert "per_page" in response_data
        assert response_data["total"] >= 1
        assert len(response_data["recipes"]) >= 1

    def test_get_my_recipes_pagination(self, test_client, auth_headers):
        """내 레시피 목록 페이징 테스트"""
        # When
        response = test_client.get(
            "/api/recipes/?page=1&per_page=5", headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["page"] == 1
        assert response_data["per_page"] == 5

    def test_get_my_recipes_no_auth(self, test_client):
        """인증 없이 레시피 목록 조회 실패 테스트"""
        # When
        response = test_client.get("/api/recipes/")

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_recipe_success(self, test_client, auth_headers, sample_recipe_data):
        """레시피 생성 성공 테스트"""
        # Given
        recipe_data = sample_recipe_data.copy()
        # Decimal을 float으로 변환 (JSON 직렬화용)
        for ingredient in recipe_data["ingredients"]:
            ingredient["amount"] = float(ingredient["amount"])

        # When
        response = test_client.post(
            "/api/recipes/", json=recipe_data, headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["title"] == recipe_data["title"]
        assert response_data["base_spirit"] == recipe_data["base_spirit"]
        assert len(response_data["ingredients"]) == len(recipe_data["ingredients"])

    def test_create_recipe_missing_fields(self, test_client, auth_headers):
        """필수 필드 누락 레시피 생성 실패 테스트"""
        # Given
        incomplete_data = {
            "title": "테스트 레시피",
            # base_spirit과 ingredients 누락
        }

        # When
        response = test_client.post(
            "/api/recipes/", json=incomplete_data, headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_recipe_no_auth(self, test_client, sample_recipe_data):
        """인증 없이 레시피 생성 실패 테스트"""
        # Given
        recipe_data = sample_recipe_data.copy()
        for ingredient in recipe_data["ingredients"]:
            ingredient["amount"] = float(ingredient["amount"])

        # When
        response = test_client.post("/api/recipes/", json=recipe_data)

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_recipe_success(self, test_client, auth_headers, created_recipe):
        """레시피 상세 조회 성공 테스트"""
        # Given
        recipe_id = str(created_recipe.recipe_id)

        # When
        response = test_client.get(f"/api/recipes/{recipe_id}", headers=auth_headers)

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["recipe_id"] == recipe_id
        assert response_data["title"] == created_recipe.title

    def test_get_recipe_not_found(self, test_client, auth_headers):
        """존재하지 않는 레시피 조회 실패 테스트"""
        # Given
        import uuid

        non_existent_id = str(uuid.uuid4())

        # When
        response = test_client.get(
            f"/api/recipes/{non_existent_id}", headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_recipe_invalid_id(self, test_client, auth_headers):
        """잘못된 ID 형식으로 레시피 조회 실패 테스트"""
        # Given
        invalid_id = "invalid-uuid"

        # When
        response = test_client.get(f"/api/recipes/{invalid_id}", headers=auth_headers)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_recipe_success(
        self, test_client, auth_headers, created_recipe, sample_recipe_update_data
    ):
        """레시피 수정 성공 테스트"""
        # Given
        recipe_id = str(created_recipe.recipe_id)
        update_data = sample_recipe_update_data.copy()
        # Decimal을 float으로 변환
        for ingredient in update_data["ingredients"]:
            ingredient["amount"] = float(ingredient["amount"])

        # When
        response = test_client.put(
            f"/api/recipes/{recipe_id}", json=update_data, headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["title"] == update_data["title"]
        assert response_data["base_spirit"] == update_data["base_spirit"]

    def test_update_recipe_partial(self, test_client, auth_headers, created_recipe):
        """레시피 부분 수정 성공 테스트"""
        # Given
        recipe_id = str(created_recipe.recipe_id)
        partial_update = {"title": "새로운 제목만 변경"}

        # When
        response = test_client.put(
            f"/api/recipes/{recipe_id}", json=partial_update, headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["title"] == partial_update["title"]
        assert response_data["base_spirit"] == created_recipe.base_spirit  # 기존 값 유지

    def test_delete_recipe_success(self, test_client, auth_headers, created_recipe):
        """레시피 삭제 성공 테스트"""
        # Given
        recipe_id = str(created_recipe.recipe_id)

        # When
        response = test_client.delete(f"/api/recipes/{recipe_id}", headers=auth_headers)

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "레시피가 삭제되었습니다" in response_data["message"]

    def test_delete_recipe_not_found(self, test_client, auth_headers):
        """존재하지 않는 레시피 삭제 실패 테스트"""
        # Given
        import uuid

        non_existent_id = str(uuid.uuid4())

        # When
        response = test_client.delete(
            f"/api/recipes/{non_existent_id}", headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_share_link_success(self, test_client, auth_headers, created_recipe):
        """공유 링크 생성 성공 테스트"""
        # Given
        recipe_id = str(created_recipe.recipe_id)

        # When
        response = test_client.post(
            f"/api/recipes/{recipe_id}/share", headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "share_id" in response_data
        assert "share_url" in response_data
        assert response_data["share_url"].startswith("/shared/")

    def test_create_share_link_not_found(self, test_client, auth_headers):
        """존재하지 않는 레시피 공유 링크 생성 실패 테스트"""
        # Given
        import uuid

        non_existent_id = str(uuid.uuid4())

        # When
        response = test_client.post(
            f"/api/recipes/{non_existent_id}/share", headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_shared_recipe_success(self, test_client, created_recipe, auth_headers):
        """공유된 레시피 조회 성공 테스트"""
        # Given
        recipe_id = str(created_recipe.recipe_id)

        # 먼저 공유 링크 생성
        share_response = test_client.post(
            f"/api/recipes/{recipe_id}/share", headers=auth_headers
        )
        share_data = share_response.json()
        share_id = share_data["share_id"]

        # When
        response = test_client.get(f"/api/recipes/shared/{share_id}")

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["recipe_id"] == recipe_id
        assert response_data["title"] == created_recipe.title

    def test_get_shared_recipe_not_found(self, test_client):
        """존재하지 않는 공유 레시피 조회 실패 테스트"""
        # Given
        import uuid

        non_existent_share_id = str(uuid.uuid4())

        # When
        response = test_client.get(f"/api/recipes/shared/{non_existent_share_id}")

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.image
class TestImageRoutes:
    """이미지 처리 라우터 통합 테스트"""

    @patch("app.services.image_service.os.remove")
    @patch("app.services.image_service.aiofiles.open")
    @patch("app.services.image_service.os.path.exists")
    def test_upload_recipe_image_success(
        self,
        mock_exists,
        mock_aiofiles_open,
        mock_remove,
        test_client,
        auth_headers,
        created_recipe,
    ):
        """레시피 이미지 업로드 성공 테스트"""
        # Given
        recipe_id = str(created_recipe.recipe_id)

        # Mock 설정
        # mock_exists.return_value = True
        # mock_file = mock_open()
        # mock_aiofiles_open.open.return_value.__aenter__.return_value = mock_file
        mock_file = AsyncMock()
        mock_file.write = AsyncMock()
        mock_file.read = AsyncMock(return_value=b"fake_image_data")

        # async context manager 모킹
        mock_content_manager = AsyncMock()
        mock_content_manager.__aenter__.return_value = mock_file
        mock_content_manager.__aexit__.return_value = None
        mock_aiofiles_open.return_value = mock_content_manager

        # 기타 파일 시스템 관련 모킹
        mock_exists.return_value = True
        mock_remove.return_value = None

        # 가짜 이미지 파일 데이터
        files = {"file": ("test_image.jpg", b"fake_image_data", "image/jpeg")}

        # When
        with patch("app.services.image_service.ImageService._optimize_image"):
            response = test_client.post(
                f"/api/recipes/{recipe_id}/image", files=files, headers=auth_headers
            )

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "message" in response_data
        assert "filename" in response_data
        assert "url" in response_data

        # Mock 호출 확인
        mock_aiofiles_open.assert_called_once()
        mock_file.write.assert_called_once_with(b"fake_image_data")

    @patch('app.services.image_service.os.remove')
    @patch('app.services.image_service.os.path.exists')
    @patch('app.services.image_service.aiofiles.open')
    def test_upload_recipe_image_not_found(self, test_client, auth_headers, mock_exists, mock_aiofiles_open, mock_remove):
        """존재하지 않는 레시피 이미지 업로드 실패 테스트"""
        # Given
        import uuid

        non_existent_id = str(uuid.uuid4())
        files = {"file": ("test_image.jpg", b"fake_image_data", "image/jpeg")}

        # When
        response = test_client.post(
            f"/api/recipes/{non_existent_id}/image", files=files, headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upload_recipe_image_no_auth(self, test_client, created_recipe):
        """인증 없이 이미지 업로드 실패 테스트"""
        # Given
        recipe_id = str(created_recipe.recipe_id)
        files = {"file": ("test_image.jpg", b"fake_image_data", "image/jpeg")}

        # When
        response = test_client.post(f"/api/recipes/{recipe_id}/image", files=files)

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("app.services.image_service.ImageService._create_cocktail_visualization")
    def test_get_visual_image_success(
        self, mock_visualization, test_client, created_recipe
    ):
        """시각화 이미지 생성 성공 테스트"""
        # Given
        recipe_id = str(created_recipe.recipe_id)
        mock_visualization.return_value = "/fake/path/to/image.png"

        # When
        response = test_client.get(f"/api/recipes/{recipe_id}/visual")

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "message" in response_data
        assert "visual_url" in response_data

    def test_get_visual_image_not_found(self, test_client):
        """존재하지 않는 레시피 시각화 이미지 생성 실패 테스트"""
        # Given
        import uuid

        non_existent_id = str(uuid.uuid4())

        # When
        response = test_client.get(f"/api/recipes/{non_existent_id}/visual")

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_visual_image_invalid_id(self, test_client):
        """잘못된 ID로 시각화 이미지 생성 실패 테스트"""
        # Given
        invalid_id = str(uuid.uuid4())

        # When
        response = test_client.get(f"/api/recipes/{invalid_id}/visual")

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
class TestRecipeValidation:
    """레시피 데이터 검증 테스트"""

    def test_create_recipe_empty_ingredients(self, test_client, auth_headers):
        """빈 재료 목록으로 레시피 생성 실패 테스트"""
        # Given
        recipe_data = {
            "title": "테스트 레시피",
            "base_spirit": "테스트 주류",
            "ingredients": [],  # 빈 재료 목록
        }

        # When
        response = test_client.post(
            "/api/recipes/", json=recipe_data, headers=auth_headers
        )

        # Then # 왜 201 뜸?????
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_recipe_invalid_amount(self, test_client, auth_headers):
        """잘못된 재료 양으로 레시피 생성 실패 테스트"""
        # Given
        recipe_data = {
            "title": "테스트 레시피",
            "base_spirit": "테스트 주류",
            "ingredients": [
                {
                    "name": "테스트 재료",
                    "amount": -10,  # 음수 양
                    "unit": "ml",
                    "color": "#000000",
                }
            ],
        }

        # When
        response = test_client.post(
            "/api/recipes/", json=recipe_data, headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
