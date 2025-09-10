import pytest
import uuid
from unittest.mock import AsyncMock, patch, mock_open
from fastapi import HTTPException
from decimal import Decimal

from app.services.recipe_service import RecipeService
from app.models.schemas import RecipeCreate, RecipeUpdate
from app.models.recipe import Recipe, Ingredient


@pytest.mark.unit
@pytest.mark.recipe
class TestRecipeService:
    """RecipeService 단위 테스트"""
    
    @pytest.mark.asyncio
    async def test_create_recipe_success(self, test_db_session, sample_recipe_data, test_user_id):
        """레시피 생성 성공 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        recipe_create = RecipeCreate(**sample_recipe_data)
        
        # When
        result = await recipe_service.create_recipe(recipe_create, test_user_id)
        
        # Then
        assert result.title == sample_recipe_data["title"]
        assert result.base_spirit == sample_recipe_data["base_spirit"]
        assert result.user_id == uuid.UUID(test_user_id)
        assert len(result.ingredients) == len(sample_recipe_data["ingredients"])
        
        # 재료 확인
        for i, ingredient in enumerate(result.ingredients):
            expected = sample_recipe_data["ingredients"][i]
            assert ingredient.name == expected["name"]
            assert ingredient.amount == expected["amount"]
            assert ingredient.unit == expected["unit"]
            assert ingredient.color == expected["color"]
    
    @pytest.mark.asyncio
    async def test_create_recipe_invalid_user_id(self, test_db_session, sample_recipe_data):
        """잘못된 사용자 ID로 레시피 생성 실패 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        recipe_create = RecipeCreate(**sample_recipe_data)
        invalid_user_id = "invalid-uuid"
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await recipe_service.create_recipe(recipe_create, invalid_user_id)
        
        assert exc_info.value.status_code == 400
        assert "올바르지 않은 사용자 ID 형식입니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_user_success(self, test_db_session, created_recipe, test_user_id):
        """사용자별 레시피 목록 조회 성공 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        
        # When
        result = await recipe_service.get_recipes_by_user(test_user_id, page=1, per_page=10)
        
        # Then
        assert result.total >= 1
        assert result.page == 1
        assert result.per_page == 10
        assert len(result.recipes) >= 1
        assert result.recipes[0].user_id == uuid.UUID(test_user_id)
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_user_pagination(self, test_db_session, test_user_id):
        """사용자별 레시피 목록 페이징 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        
        # 여러 레시피 생성
        for i in range(5):
            recipe_data = {
                "title": f"테스트 레시피 {i}",
                "base_spirit": "테스트 주류",
                "ingredients": [
                    {
                        "name": "테스트 재료",
                        "amount": Decimal("50.00"),
                        "unit": "ml",
                        "color": "#000000"
                    }
                ]
            }
            recipe_create = RecipeCreate(**recipe_data)
            await recipe_service.create_recipe(recipe_create, test_user_id)
        
        # When
        result = await recipe_service.get_recipes_by_user(test_user_id, page=1, per_page=3)
        
        # Then
        assert result.total >= 5
        assert len(result.recipes) == 3
        assert result.has_next is True
        assert result.has_prev is False
    
    @pytest.mark.asyncio
    async def test_get_recipe_by_id_success(self, test_db_session, created_recipe, test_user_id):
        """레시피 ID로 조회 성공 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        recipe_id = str(created_recipe.recipe_id)
        
        # When
        result = await recipe_service.get_recipe_by_id(recipe_id, test_user_id)
        
        # Then
        assert result.recipe_id == created_recipe.recipe_id
        assert result.title == created_recipe.title
        assert result.user_id == created_recipe.user_id
    
    @pytest.mark.asyncio
    async def test_get_recipe_by_id_not_found(self, test_db_session, test_user_id):
        """존재하지 않는 레시피 ID로 조회 실패 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        non_existent_id = str(uuid.uuid4())
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await recipe_service.get_recipe_by_id(non_existent_id, test_user_id)
        
        assert exc_info.value.status_code == 404
        assert "레시피를 찾을 수 없습니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_recipe_by_id_no_permission(self, test_db_session, created_recipe):
        """권한 없는 사용자의 레시피 조회 실패 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        recipe_id = str(created_recipe.recipe_id)
        other_user_id = str(uuid.uuid4())
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await recipe_service.get_recipe_by_id(recipe_id, other_user_id)
        
        assert exc_info.value.status_code == 403
        assert "접근 권한이 없습니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_recipe_success(self, test_db_session, created_recipe, test_user_id, sample_recipe_update_data):
        """레시피 수정 성공 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        recipe_id = str(created_recipe.recipe_id)
        update_data = RecipeUpdate(**sample_recipe_update_data)
        
        # When
        result = await recipe_service.update_recipe(recipe_id, update_data, test_user_id)
        
        # Then
        assert result.recipe_id == created_recipe.recipe_id
        assert result.title == sample_recipe_update_data["title"]
        assert result.base_spirit == sample_recipe_update_data["base_spirit"]
        assert len(result.ingredients) == len(sample_recipe_update_data["ingredients"])
    
    @pytest.mark.asyncio
    async def test_update_recipe_not_found(self, test_db_session, test_user_id, sample_recipe_update_data):
        """존재하지 않는 레시피 수정 실패 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        non_existent_id = str(uuid.uuid4())
        update_data = RecipeUpdate(**sample_recipe_update_data)
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await recipe_service.update_recipe(non_existent_id, update_data, test_user_id)
        
        assert exc_info.value.status_code == 404
        assert "레시피를 찾을 수 없거나 수정 권한이 없습니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_delete_recipe_success(self, test_db_session, created_recipe, test_user_id):
        """레시피 삭제 성공 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        recipe_id = str(created_recipe.recipe_id)
        
        # When
        result = await recipe_service.delete_recipe(recipe_id, test_user_id)
        
        # Then
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_recipe_not_found(self, test_db_session, test_user_id):
        """존재하지 않는 레시피 삭제 실패 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        non_existent_id = str(uuid.uuid4())
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await recipe_service.delete_recipe(non_existent_id, test_user_id)
        
        assert exc_info.value.status_code == 404
        assert "레시피를 찾을 수 없거나 삭제 권한이 없습니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_create_share_link_success(self, test_db_session, created_recipe, test_user_id):
        """공유 링크 생성 성공 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        recipe_id = str(created_recipe.recipe_id)
        
        # When
        result = await recipe_service.create_share_link(recipe_id, test_user_id)
        
        # Then
        assert result.share_id is not None
        assert result.share_url == f"/shared/{result.share_id}"
    
    @pytest.mark.asyncio
    async def test_create_share_link_not_found(self, test_db_session, test_user_id):
        """존재하지 않는 레시피 공유 링크 생성 실패 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        non_existent_id = str(uuid.uuid4())
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await recipe_service.create_share_link(non_existent_id, test_user_id)
        
        assert exc_info.value.status_code == 404
        assert "레시피를 찾을 수 없거나 공유 권한이 없습니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_shared_recipe_success(self, test_db_session, created_recipe, test_user_id):
        """공유된 레시피 조회 성공 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        recipe_id = str(created_recipe.recipe_id)
        
        # 먼저 공유 링크 생성
        share_result = await recipe_service.create_share_link(recipe_id, test_user_id)
        share_id = str(share_result.share_id)
        
        # When
        result = await recipe_service.get_shared_recipe(share_id)
        
        # Then
        assert result.recipe_id == created_recipe.recipe_id
        assert result.title == created_recipe.title
        assert result.is_public is True
    
    @pytest.mark.asyncio
    async def test_get_shared_recipe_not_found(self, test_db_session):
        """존재하지 않는 공유 레시피 조회 실패 테스트"""
        # Given
        recipe_service = RecipeService(test_db_session)
        non_existent_share_id = str(uuid.uuid4())
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await recipe_service.get_shared_recipe(non_existent_share_id)
        
        assert exc_info.value.status_code == 404
        assert "공유된 레시피를 찾을 수 없습니다" in str(exc_info.value.detail)


@pytest.mark.unit
@pytest.mark.image
class TestImageService:
    """ImageService 단위 테스트"""
    
    @pytest.mark.asyncio
    async def test_validate_image_file_success(self, test_db_session, mock_image_file):
        """이미지 파일 검증 성공 테스트"""
        from app.services.image_service import ImageService
        
        # Given
        image_service = ImageService(test_db_session)
        
        # When & Then (예외 발생하지 않아야 함)
        image_service._validate_image_file(mock_image_file)
    
    @pytest.mark.asyncio
    async def test_validate_image_file_no_filename(self, test_db_session):
        """파일명 없는 이미지 파일 검증 실패 테스트"""
        from app.services.image_service import ImageService
        from fastapi import UploadFile
        from io import BytesIO
        
        # Given
        image_service = ImageService(test_db_session)
        file_without_name = UploadFile(filename=None, file=BytesIO(b"test"))
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            image_service._validate_image_file(file_without_name)
        
        assert exc_info.value.status_code == 400
        assert "파일명이 없습니다" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_validate_image_file_invalid_extension(self, test_db_session):
        """잘못된 확장자 이미지 파일 검증 실패 테스트"""
        from app.services.image_service import ImageService
        from fastapi import UploadFile
        from io import BytesIO
        
        # Given
        image_service = ImageService(test_db_session)
        invalid_file = UploadFile(filename="test.txt", file=BytesIO(b"test"))
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            image_service._validate_image_file(invalid_file)
        
        assert exc_info.value.status_code == 400
        assert "지원하지 않는 파일 형식입니다" in str(exc_info.value.detail)
    
    def test_get_default_color(self, test_db_session):
        """재료별 기본 색상 반환 테스트"""
        from app.services.image_service import ImageService
        
        # Given
        image_service = ImageService(test_db_session)
        
        # When & Then
        assert image_service._get_default_color("위스키") == "#D2691E"
        assert image_service._get_default_color("보드카") == "#F0F8FF"
        assert image_service._get_default_color("진") == "#E6E6FA"
        assert image_service._get_default_color("알 수 없는 재료")  # 기본 색상 반환







