import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class Recipe(Base):
    __tablename__ = "recipes"
    
    recipe_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # User Service와 연결
    title = Column(String(100), nullable=False)
    base_spirit = Column(String(50), nullable=False)
    instructions = Column(Text)
    notes = Column(Text)
    photo_url = Column(String(500))
    visual_image_url = Column(String(500))
    share_id = Column(UUID(as_uuid=True), unique=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Recipe(recipe_id='{self.recipe_id}', title='{self.title}', user_id='{self.user_id}')>"


class Ingredient(Base):
    __tablename__ = "ingredients"
    
    ingredient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.recipe_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    amount = Column(Numeric(6, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    color = Column(String(7), default="#000000")  # HEX 색상 코드
    
    # 관계 설정
    recipe = relationship("Recipe", back_populates="ingredients")

    def __repr__(self):
        return f"<Ingredient(name='{self.name}', amount={self.amount}, unit='{self.unit}')>"

