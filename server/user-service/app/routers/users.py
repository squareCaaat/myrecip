from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.schemas import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: UserResponse = Depends(get_current_user)):
    """
    내 프로필 정보 조회

    현재 로그인한 사용자의 상세 정보를 반환합니다.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    update_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    내 프로필 정보 수정

    - **username**: 변경할 사용자명 (선택)
    - **email**: 변경할 이메일 주소 (선택, 중복 불가)
    """
    user_service = UserService(db)
    return await user_service.update_user(str(current_user.user_id), update_data)


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_my_account(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    회원 탈퇴

    현재 사용자의 계정을 삭제합니다.
    """
    # TODO: 실제 계정 삭제 로직 구현 (연관된 레시피도 함께 처리)
    return {"message": "회원 탈퇴 기능은 추후 구현 예정입니다."}
