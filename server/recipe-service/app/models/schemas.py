from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
import uuid


# 재료 기본 스키마
class IngredientBase(BaseModel):
    name: str
    amount: Decimal
    unit: str
    color: Optional[str] = "#000000"


# 재료 생성 스키마
class IngredientCreate(IngredientBase):
    pass


# 재료 응답 스키마
class IngredientResponse(IngredientBase):
    ingredient_id: uuid.UUID
    recipe_id: uuid.UUID
    
    class Config:
        from_attributes = True


# 레시피 기본 스키마
class RecipeBase(BaseModel):
    title: str
    base_spirit: str
    instructions: Optional[str] = None
    notes: Optional[str] = None


# 레시피 생성 스키마
class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate]


# 레시피 업데이트 스키마
class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    base_spirit: Optional[str] = None
    instructions: Optional[str] = None
    notes: Optional[str] = None
    ingredients: Optional[List[IngredientCreate]] = None


# 레시피 응답 스키마
class RecipeResponse(RecipeBase):
    recipe_id: uuid.UUID
    user_id: uuid.UUID
    photo_url: Optional[str] = None
    visual_image_url: Optional[str] = None
    share_id: Optional[uuid.UUID] = None
    is_public: bool
    created_at: datetime
    updated_at: datetime
    ingredients: List[IngredientResponse] = []
    
    class Config:
        from_attributes = True


# 레시피 목록 응답 스키마 (페이징용)
class RecipeListResponse(BaseModel):
    recipes: List[RecipeResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


# 공유 링크 생성 응답 스키마
class ShareLinkResponse(BaseModel):
    share_id: uuid.UUID
    share_url: str

