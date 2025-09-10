import asyncio
import os
import uuid
from typing import Optional

import aiofiles
from fastapi import HTTPException, UploadFile, status
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.recipe import Ingredient, Recipe


class ImageService:
    """이미지 처리 관련 서비스"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_dir = settings.upload_dir
        self.max_file_size = settings.max_file_size
        self.allowed_extensions = settings.allowed_extensions

    async def upload_recipe_image(
        self, recipe_id: str, file: UploadFile, user_id: str
    ) -> dict:
        """레시피 이미지 업로드"""

        # 파일 유효성 검증
        self._validate_image_file(file)

        # 레시피 존재 및 권한 확인
        recipe_uuid = uuid.UUID(recipe_id)
        user_uuid = uuid.UUID(user_id)

        stmt = select(Recipe).where(
            Recipe.recipe_id == recipe_uuid, Recipe.user_id == user_uuid
        )
        result = await self.db.execute(stmt)
        recipe = result.scalar_one_or_none()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="레시피를 찾을 수 없거나 업로드 권한이 없습니다.",
            )

        # 파일 저장
        file_extension = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{recipe_id}_{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)

        try:
            # 비동기 파일 저장
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)

            # 이미지 최적화 (리사이징)
            await self._optimize_image(file_path)

            # 데이터베이스에 URL 저장
            photo_url = f"/static/{unique_filename}"
            recipe.photo_url = photo_url
            await self.db.commit()

            return {
                "message": "이미지가 성공적으로 업로드되었습니다.",
                "filename": unique_filename,
                "url": photo_url,
            }

        except Exception as e:
            # 실패 시 파일 삭제 (실패는 무시)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이미지 업로드 중 오류가 발생했습니다: {str(e)}",
            )

    async def generate_visual_image(self, recipe_id: str) -> str:
        """레시피 시각화 이미지 생성"""

        # 레시피와 재료 정보 조회
        recipe_uuid = uuid.UUID(recipe_id)

        stmt = select(Recipe).where(Recipe.recipe_id == recipe_uuid)
        result = await self.db.execute(stmt)
        recipe = result.scalar_one_or_none()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="레시피를 찾을 수 없습니다."
            )

        # 재료 정보 조회
        ingredients_stmt = select(Ingredient).where(Ingredient.recipe_id == recipe_uuid)
        ingredients_result = await self.db.execute(ingredients_stmt)
        ingredients = ingredients_result.scalars().all()

        if not ingredients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="재료 정보가 없어 시각화 이미지를 생성할 수 없습니다.",
            )

        # 시각화 이미지 생성
        image_path = await self._create_cocktail_visualization(recipe, ingredients)

        # 데이터베이스에 URL 저장
        visual_url = f"/static/{os.path.basename(image_path)}"
        recipe.visual_image_url = visual_url
        await self.db.commit()

        return visual_url

    def _validate_image_file(self, file: UploadFile):
        """이미지 파일 유효성 검증"""

        # 파일 확장자 검증
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="파일명이 없습니다."
            )

        file_extension = os.path.splitext(file.filename)[1].lower().lstrip(".")
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 파일 형식입니다. 허용된 확장자: {', '.join(self.allowed_extensions)}",
            )

        # 파일 크기 검증 (UploadFile은 size 속성이 없으므로 실제 읽어서 확인)
        # 실제 구현에서는 nginx 등에서 크기 제한을 하는 것이 좋습니다

    async def _optimize_image(self, file_path: str):
        """이미지 최적화 (리사이징)"""
        try:
            with Image.open(file_path) as img:
                # RGB 모드로 변환
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # 최대 크기 제한 (800x800)
                max_size = (800, 800)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # 품질 85%로 저장
                img.save(file_path, "JPEG", quality=85, optimize=True)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이미지 최적화 중 오류가 발생했습니다: {str(e)}",
            )

    async def _create_cocktail_visualization(
        self, recipe: Recipe, ingredients: list[Ingredient]
    ) -> str:
        """칵테일 시각화 이미지 생성"""

        # 이미지 크기 설정
        width, height = 400, 600
        glass_width = 150
        glass_height = 400
        glass_x = (width - glass_width) // 2
        glass_y = (height - glass_height) // 2

        # 이미지 생성
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)

        # 글래스 외곽선 그리기
        glass_coords = [
            glass_x,
            glass_y + glass_height,  # 하단 좌
            glass_x,
            glass_y + 50,  # 상단 좌 (약간 위)
            glass_x + glass_width,
            glass_y + 50,  # 상단 우
            glass_x + glass_width,
            glass_y + glass_height,  # 하단 우
        ]
        draw.polygon(glass_coords, outline="black", width=2)

        # 재료별 레이어 계산
        total_amount = sum(float(ing.amount) for ing in ingredients)
        if total_amount == 0:
            total_amount = 1  # 0으로 나누기 방지

        current_height = glass_y + glass_height - 10  # 하단에서 시작
        layer_height = (glass_height - 60) / len(ingredients)  # 각 레이어 높이

        # 재료별 색상 레이어 그리기
        for ingredient in ingredients:
            layer_ratio = float(ingredient.amount) / total_amount
            actual_layer_height = layer_height * layer_ratio * 2  # 비율에 따른 높이 조정

            # 색상 파싱 (기본값 사용)
            color = (
                ingredient.color
                if ingredient.color and ingredient.color != "#000000"
                else self._get_default_color(ingredient.name)
            )

            # 레이어 그리기
            layer_coords = [
                glass_x + 5,
                current_height,
                glass_x + 5,
                current_height - actual_layer_height,
                glass_x + glass_width - 5,
                current_height - actual_layer_height,
                glass_x + glass_width - 5,
                current_height,
            ]

            try:
                draw.polygon(layer_coords, fill=color)
            except:
                draw.polygon(layer_coords, fill="#87CEEB")  # 기본 파란색

            current_height -= actual_layer_height

        # 레시피 제목 추가
        try:
            # 기본 폰트 사용 (시스템에 따라 다를 수 있음)
            font_size = 20
            title_text = (
                recipe.title[:20] + "..." if len(recipe.title) > 20 else recipe.title
            )

            # 텍스트 크기 계산
            bbox = draw.textbbox((0, 0), title_text)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2

            draw.text((text_x, 30), title_text, fill="black")

        except Exception:
            # 폰트 문제가 있을 경우 기본 텍스트
            draw.text((width // 2 - 50, 30), recipe.title[:10], fill="black")

        # 재료 목록 추가
        ingredients_text = "\n".join(
            [f"• {ing.name}: {ing.amount}{ing.unit}" for ing in ingredients[:5]]
        )
        draw.text((20, height - 120), ingredients_text, fill="black")

        # 파일 저장
        filename = f"visual_{recipe.recipe_id}_{uuid.uuid4().hex}.png"
        file_path = os.path.join(self.upload_dir, filename)
        img.save(file_path, "PNG")

        return file_path

    def _get_default_color(self, ingredient_name: str) -> str:
        """재료명에 따른 기본 색상 반환"""
        color_map = {
            "위스키": "#D2691E",
            "보드카": "#F0F8FF",
            "진": "#E6E6FA",
            "럼": "#DEB887",
            "데킬라": "#F5DEB3",
            "레몬": "#FFFF00",
            "라임": "#00FF00",
            "오렌지": "#FFA500",
            "크랜베리": "#DC143C",
            "토닉": "#F0F8FF",
            "소다": "#F0F8FF",
            "콜라": "#2F4F4F",
            "그레나딘": "#FF69B4",
            "민트": "#98FB98",
        }

        ingredient_lower = ingredient_name.lower()
        for key, color in color_map.items():
            if key in ingredient_lower:
                return color

        # 기본 색상들
        default_colors = [
            "#87CEEB",
            "#DDA0DD",
            "#98FB98",
            "#F0E68C",
            "#FFB6C1",
            "#87CEFA",
        ]
        return default_colors[hash(ingredient_name) % len(default_colors)]
