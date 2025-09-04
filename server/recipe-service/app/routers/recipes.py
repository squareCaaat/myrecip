from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_db
from app.models.schemas import (
    RecipeCreate, RecipeUpdate, RecipeResponse, RecipeListResponse, ShareLinkResponse
)
from app.services.recipe_service import RecipeService
from app.dependencies.auth import get_current_user_id, get_current_user_id_optional
import uuid


router = APIRouter()


@router.get("/", response_model=RecipeListResponse)
async def get_my_recipes(
    page: int = Query(1, ge=1, description="페이지 번호"),
    per_page: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    내 레시피 목록 조회
    
    - **page**: 페이지 번호 (기본값: 1)
    - **per_page**: 페이지당 항목 수 (기본값: 10, 최대: 100)
    
    페이징된 레시피 목록을 반환합니다.
    """
    recipe_service = RecipeService(db)
    return await recipe_service.get_recipes_by_user(current_user_id, page, per_page)


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_data: RecipeCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    새 레시피 생성
    
    - **title**: 칵테일 이름 (필수)
    - **base_spirit**: 베이스 주류 (필수)
    - **instructions**: 제작 과정 (선택)
    - **notes**: 개인 팁 (선택)
    - **ingredients**: 재료 목록 (필수)
    """
    recipe_service = RecipeService(db)
    return await recipe_service.create_recipe(recipe_data, current_user_id)


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: str,
    current_user_id: Optional[str] = Depends(get_current_user_id_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    레시피 상세 조회
    
    - **recipe_id**: 레시피 ID
    
    공개 레시피이거나 본인의 레시피인 경우 조회 가능합니다.
    """
    recipe_service = RecipeService(db)
    return await recipe_service.get_recipe_by_id(recipe_id, current_user_id)


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: str,
    update_data: RecipeUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    레시피 수정
    
    - **recipe_id**: 레시피 ID
    
    본인의 레시피만 수정 가능합니다.
    """
    recipe_service = RecipeService(db)
    return await recipe_service.update_recipe(recipe_id, update_data, current_user_id)


@router.delete("/{recipe_id}", status_code=status.HTTP_200_OK)
async def delete_recipe(
    recipe_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    레시피 삭제
    
    - **recipe_id**: 레시피 ID
    
    본인의 레시피만 삭제 가능합니다.
    """
    recipe_service = RecipeService(db)
    await recipe_service.delete_recipe(recipe_id, current_user_id)
    return {"message": "레시피가 삭제되었습니다."}


@router.post("/{recipe_id}/share", response_model=ShareLinkResponse)
async def create_share_link(
    recipe_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    레시피 공유 링크 생성
    
    - **recipe_id**: 레시피 ID
    
    본인의 레시피에 대한 공유 링크를 생성합니다.
    """
    recipe_service = RecipeService(db)
    return await recipe_service.create_share_link(recipe_id, current_user_id)


@router.post("/{recipe_id}/image", status_code=status.HTTP_200_OK)
async def upload_recipe_image(
    recipe_id: str,
    file: UploadFile = File(..., description="업로드할 이미지 파일"),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    레시피 이미지 업로드
    
    - **recipe_id**: 레시피 ID
    - **file**: 업로드할 이미지 파일 (jpg, jpeg, png, gif)
    
    본인의 레시피에만 이미지를 업로드할 수 있습니다.
    """
    from app.services.image_service import ImageService
    
    image_service = ImageService(db)
    return await image_service.upload_recipe_image(recipe_id, file, current_user_id)


@router.get("/{recipe_id}/visual")
async def get_visual_image(
    recipe_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    시각화 이미지 생성 및 반환
    
    - **recipe_id**: 레시피 ID
    
    레시피의 재료 비율을 기반으로 시각화 이미지를 생성합니다.
    """
    from app.services.image_service import ImageService
    
    image_service = ImageService(db)
    visual_url = await image_service.generate_visual_image(recipe_id)
    
    return {
        "message": "시각화 이미지가 생성되었습니다.",
        "visual_url": visual_url
    }


# 공유 레시피 조회 (인증 불필요)
@router.get("/shared/{share_id}", response_model=RecipeResponse)
async def get_shared_recipe(
    share_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    공유된 레시피 조회
    
    - **share_id**: 공유 링크 ID
    
    공유 링크를 통해 레시피를 조회합니다. 인증이 필요하지 않습니다.
    """
    recipe_service = RecipeService(db)
    return await recipe_service.get_shared_recipe(share_id)

