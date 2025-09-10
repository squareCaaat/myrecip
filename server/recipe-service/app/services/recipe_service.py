import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipe import Ingredient, Recipe
from app.models.schemas import (
    IngredientCreate,
    RecipeCreate,
    RecipeListResponse,
    RecipeResponse,
    RecipeUpdate,
    ShareLinkResponse,
)


class RecipeService:
    """레시피 관련 비즈니스 로직"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_recipe(
        self, recipe_data: RecipeCreate, user_id: str
    ) -> RecipeResponse:
        """레시피 생성"""
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="올바르지 않은 사용자 ID 형식입니다."
            )
        # ingredients 빈 배열인지 확인
        if not recipe_data.ingredients:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="재료 항목은 필수 입니다.",
            )

        # 새 레시피 생성
        new_recipe = Recipe(
            user_id=user_uuid,
            title=recipe_data.title,
            base_spirit=recipe_data.base_spirit,
            instructions=recipe_data.instructions,
            notes=recipe_data.notes,
        )

        self.db.add(new_recipe)
        await self.db.flush()  # recipe_id 생성을 위해 flush

        # 재료 추가
        for ingredient_data in recipe_data.ingredients:
            if ingredient_data.amount <= 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="재료 양은 0 이상이어야 합니다.",
                )
            ingredient = Ingredient(
                recipe_id=new_recipe.recipe_id,
                name=ingredient_data.name,
                amount=ingredient_data.amount,
                unit=ingredient_data.unit,
                color=ingredient_data.color or "#000000",
            )
            self.db.add(ingredient)

        await self.db.commit()
        await self.db.refresh(new_recipe)

        return await self._get_recipe_with_ingredients(new_recipe.recipe_id)

    async def get_recipes_by_user(
        self, user_id: str, page: int = 1, per_page: int = 10
    ) -> RecipeListResponse:
        """사용자별 레시피 목록 조회 (페이징)"""
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="올바르지 않은 사용자 ID 형식입니다."
            )

        # 전체 개수 조회
        total_stmt = select(func.count(Recipe.recipe_id)).where(
            Recipe.user_id == user_uuid
        )
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar()

        # 페이징 계산
        offset = (page - 1) * per_page

        # 레시피 목록 조회 (최신순)
        stmt = (
            select(Recipe)
            .where(Recipe.user_id == user_uuid)
            .order_by(desc(Recipe.created_at))
            .offset(offset)
            .limit(per_page)
        )

        result = await self.db.execute(stmt)
        recipes = result.scalars().all()

        # 각 레시피의 재료 정보도 포함
        recipe_responses = []
        for recipe in recipes:
            recipe_response = await self._get_recipe_with_ingredients(recipe.recipe_id)
            recipe_responses.append(recipe_response)

        return RecipeListResponse(
            recipes=recipe_responses,
            total=total,
            page=page,
            per_page=per_page,
            has_next=total > offset + per_page,
            has_prev=page > 1,
        )

    async def get_recipe_by_id(
        self, recipe_id: str, user_id: Optional[str] = None
    ) -> RecipeResponse:
        """레시피 상세 조회"""
        try:
            recipe_uuid = uuid.UUID(recipe_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="올바르지 않은 레시피 ID 형식입니다."
            )

        recipe = await self._get_recipe_with_ingredients(recipe_uuid)

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="레시피를 찾을 수 없습니다."
            )

        # 공개 레시피이거나 본인의 레시피인지 확인
        if user_id:
            user_uuid = uuid.UUID(user_id)
            if recipe.user_id == user_uuid or recipe.is_public:
                return recipe
        elif recipe.is_public:
            return recipe

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다."
        )

    async def update_recipe(
        self, recipe_id: str, update_data: RecipeUpdate, user_id: str
    ) -> RecipeResponse:
        """레시피 수정"""
        try:
            recipe_uuid = uuid.UUID(recipe_id)
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="올바르지 않은 ID 형식입니다."
            )

        # 레시피 조회 및 권한 확인
        stmt = select(Recipe).where(
            and_(Recipe.recipe_id == recipe_uuid, Recipe.user_id == user_uuid)
        )
        result = await self.db.execute(stmt)
        recipe = result.scalar_one_or_none()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="레시피를 찾을 수 없거나 수정 권한이 없습니다.",
            )

        # 레시피 정보 업데이트
        if update_data.title is not None:
            recipe.title = update_data.title
        if update_data.base_spirit is not None:
            recipe.base_spirit = update_data.base_spirit
        if update_data.instructions is not None:
            recipe.instructions = update_data.instructions
        if update_data.notes is not None:
            recipe.notes = update_data.notes

        # 재료 업데이트
        if update_data.ingredients is not None:
            # 기존 재료 삭제
            ingredients_stmt = select(Ingredient).where(
                Ingredient.recipe_id == recipe_uuid
            )
            ingredients_result = await self.db.execute(ingredients_stmt)
            existing_ingredients = ingredients_result.scalars().all()

            for ingredient in existing_ingredients:
                await self.db.delete(ingredient)

            # 새 재료 추가
            for ingredient_data in update_data.ingredients:
                new_ingredient = Ingredient(
                    recipe_id=recipe_uuid,
                    name=ingredient_data.name,
                    amount=ingredient_data.amount,
                    unit=ingredient_data.unit,
                    color=ingredient_data.color or "#000000",
                )
                self.db.add(new_ingredient)

        recipe.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(recipe)

        return await self._get_recipe_with_ingredients(recipe_uuid)

    async def delete_recipe(self, recipe_id: str, user_id: str) -> bool:
        """레시피 삭제"""
        try:
            recipe_uuid = uuid.UUID(recipe_id)
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="올바르지 않은 ID 형식입니다."
            )

        # 레시피 조회 및 권한 확인
        stmt = select(Recipe).where(
            and_(Recipe.recipe_id == recipe_uuid, Recipe.user_id == user_uuid)
        )
        result = await self.db.execute(stmt)
        recipe = result.scalar_one_or_none()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="레시피를 찾을 수 없거나 삭제 권한이 없습니다.",
            )

        await self.db.delete(recipe)
        await self.db.commit()

        return True

    async def create_share_link(
        self, recipe_id: str, user_id: str
    ) -> ShareLinkResponse:
        """공유 링크 생성"""
        try:
            recipe_uuid = uuid.UUID(recipe_id)
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="올바르지 않은 ID 형식입니다."
            )

        # 레시피 조회 및 권한 확인
        stmt = select(Recipe).where(
            and_(Recipe.recipe_id == recipe_uuid, Recipe.user_id == user_uuid)
        )
        result = await self.db.execute(stmt)
        recipe = result.scalar_one_or_none()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="레시피를 찾을 수 없거나 공유 권한이 없습니다.",
            )

        # 공유 ID가 없으면 생성
        if not recipe.share_id:
            recipe.share_id = uuid.uuid4()
            recipe.is_public = True
            await self.db.commit()

        return ShareLinkResponse(
            share_id=recipe.share_id, share_url=f"/shared/{recipe.share_id}"
        )

    async def get_shared_recipe(self, share_id: str) -> RecipeResponse:
        """공유된 레시피 조회"""
        try:
            share_uuid = uuid.UUID(share_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="올바르지 않은 공유 링크 형식입니다."
            )

        stmt = select(Recipe).where(
            and_(Recipe.share_id == share_uuid, Recipe.is_public == True)
        )
        result = await self.db.execute(stmt)
        recipe = result.scalar_one_or_none()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="공유된 레시피를 찾을 수 없습니다."
            )

        return await self._get_recipe_with_ingredients(recipe.recipe_id)

    async def _get_recipe_with_ingredients(
        self, recipe_id: uuid.UUID
    ) -> Optional[RecipeResponse]:
        """레시피와 재료 정보를 함께 조회하는 헬퍼 메소드"""
        stmt = select(Recipe).where(Recipe.recipe_id == recipe_id)
        result = await self.db.execute(stmt)
        recipe = result.scalar_one_or_none()

        if not recipe:
            return None

        # 재료 정보 조회
        ingredients_stmt = select(Ingredient).where(Ingredient.recipe_id == recipe_id)
        ingredients_result = await self.db.execute(ingredients_stmt)
        ingredients = ingredients_result.scalars().all()

        # RecipeResponse 객체 생성
        recipe_dict = {
            "recipe_id": recipe.recipe_id,
            "user_id": recipe.user_id,
            "title": recipe.title,
            "base_spirit": recipe.base_spirit,
            "instructions": recipe.instructions,
            "notes": recipe.notes,
            "photo_url": recipe.photo_url,
            "visual_image_url": recipe.visual_image_url,
            "share_id": recipe.share_id,
            "is_public": recipe.is_public,
            "created_at": recipe.created_at,
            "updated_at": recipe.updated_at,
            "ingredients": [
                {
                    "ingredient_id": ing.ingredient_id,
                    "recipe_id": ing.recipe_id,
                    "name": ing.name,
                    "amount": ing.amount,
                    "unit": ing.unit,
                    "color": ing.color,
                }
                for ing in ingredients
            ],
        }

        return RecipeResponse(**recipe_dict)
