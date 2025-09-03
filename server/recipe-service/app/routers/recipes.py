from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_db
from app.models.schemas import (
    RecipeCreate, RecipeUpdate, RecipeResponse, RecipeListResponse, ShareLinkResponse
)
import uuid


router = APIRouter()


@router.get("/", response_model=RecipeListResponse)
async def get_my_recipes(
    page: int = Query(1, ge=1, description="페이지 번호"),
    per_page: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    db: AsyncSession = Depends(get_db)
    # current_user: UserResponse = Depends(get_current_user_from_gateway)  # API Gateway에서 전달받음
):
    """
    내 레시피 목록 조회
    
    - **page**: 페이지 번호 (기본값: 1)
    - **per_page**: 페이지당 항목 수 (기본값: 10, 최대: 100)
    
    페이징된 레시피 목록을 반환합니다.
    """
    # TODO: 실제 레시피 조회 로직 구현
    return RecipeListResponse(
        recipes=[],
        total=0,
        page=page,
        per_page=per_page,
        has_next=False,
        has_prev=False
    )


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_data: RecipeCreate,
    db: AsyncSession = Depends(get_db)
    # current_user: UserResponse = Depends(get_current_user_from_gateway)
):
    """
    새 레시피 생성
    
    - **title**: 칵테일 이름 (필수)
    - **base_spirit**: 베이스 주류 (필수)
    - **instructions**: 제작 과정 (선택)
    - **notes**: 개인 팁 (선택)
    - **ingredients**: 재료 목록 (필수)
    """
    # TODO: 실제 레시피 생성 로직 구현
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="레시피 생성 기능은 구현 중입니다."
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: str,
    db: AsyncSession = Depends(get_db)
    # current_user: Optional[UserResponse] = Depends(get_current_user_optional_from_gateway)
):
    """
    레시피 상세 조회
    
    - **recipe_id**: 레시피 ID
    
    공개 레시피이거나 본인의 레시피인 경우 조회 가능합니다.
    """
    try:
        recipe_uuid = uuid.UUID(recipe_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바르지 않은 레시피 ID 형식입니다."
        )
    
    # TODO: 실제 레시피 조회 로직 구현
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="레시피를 찾을 수 없습니다."
    )


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: str,
    update_data: RecipeUpdate,
    db: AsyncSession = Depends(get_db)
    # current_user: UserResponse = Depends(get_current_user_from_gateway)
):
    """
    레시피 수정
    
    - **recipe_id**: 레시피 ID
    
    본인의 레시피만 수정 가능합니다.
    """
    try:
        recipe_uuid = uuid.UUID(recipe_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바르지 않은 레시피 ID 형식입니다."
        )
    
    # TODO: 실제 레시피 수정 로직 구현
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="레시피 수정 기능은 구현 중입니다."
    )


@router.delete("/{recipe_id}", status_code=status.HTTP_200_OK)
async def delete_recipe(
    recipe_id: str,
    db: AsyncSession = Depends(get_db)
    # current_user: UserResponse = Depends(get_current_user_from_gateway)
):
    """
    레시피 삭제
    
    - **recipe_id**: 레시피 ID
    
    본인의 레시피만 삭제 가능합니다.
    """
    try:
        recipe_uuid = uuid.UUID(recipe_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바르지 않은 레시피 ID 형식입니다."
        )
    
    # TODO: 실제 레시피 삭제 로직 구현
    return {"message": "레시피가 삭제되었습니다."}


@router.post("/{recipe_id}/share", response_model=ShareLinkResponse)
async def create_share_link(
    recipe_id: str,
    db: AsyncSession = Depends(get_db)
    # current_user: UserResponse = Depends(get_current_user_from_gateway)
):
    """
    레시피 공유 링크 생성
    
    - **recipe_id**: 레시피 ID
    
    본인의 레시피에 대한 공유 링크를 생성합니다.
    """
    try:
        recipe_uuid = uuid.UUID(recipe_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바르지 않은 레시피 ID 형식입니다."
        )
    
    # TODO: 실제 공유 링크 생성 로직 구현
    share_uuid = uuid.uuid4()
    return ShareLinkResponse(
        share_id=share_uuid,
        share_url=f"/shared/{share_uuid}"
    )


@router.post("/{recipe_id}/image", status_code=status.HTTP_200_OK)
async def upload_recipe_image(
    recipe_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
    # current_user: UserResponse = Depends(get_current_user_from_gateway)
):
    """
    레시피 이미지 업로드
    
    - **recipe_id**: 레시피 ID
    - **file**: 업로드할 이미지 파일 (jpg, jpeg, png, gif)
    
    본인의 레시피에만 이미지를 업로드할 수 있습니다.
    """
    try:
        recipe_uuid = uuid.UUID(recipe_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바르지 않은 레시피 ID 형식입니다."
        )
    
    # TODO: 실제 이미지 업로드 로직 구현
    return {"message": "이미지가 업로드되었습니다.", "filename": file.filename}


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
    try:
        recipe_uuid = uuid.UUID(recipe_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바르지 않은 레시피 ID 형식입니다."
        )
    
    # TODO: 실제 시각화 이미지 생성 로직 구현
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="시각화 이미지 생성 기능은 구현 중입니다."
    )


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
    try:
        share_uuid = uuid.UUID(share_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바르지 않은 공유 링크 형식입니다."
        )
    
    # TODO: 실제 공유 레시피 조회 로직 구현
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="공유된 레시피를 찾을 수 없습니다."
    )

