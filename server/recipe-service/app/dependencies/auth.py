from fastapi import Header, HTTPException, status
from typing import Optional
import uuid


async def get_current_user_id(
    x_user_id: Optional[str] = Header(None, description="API Gateway에서 전달된 사용자 ID")
) -> str:
    """
    API Gateway에서 전달받은 사용자 ID를 반환
    API Gateway가 JWT 토큰을 검증하고 X-User-ID 헤더로 사용자 ID를 전달
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다. API Gateway를 통해 요청해주세요."
        )
    
    try:
        # UUID 형식 검증
        uuid.UUID(x_user_id)
        return x_user_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바르지 않은 사용자 ID 형식입니다."
        )


async def get_current_user_id_optional(
    x_user_id: Optional[str] = Header(None, description="API Gateway에서 전달된 사용자 ID")
) -> Optional[str]:
    """
    선택적 사용자 ID 반환 (공개 레시피 조회 등에 사용)
    """
    if not x_user_id:
        return None
    
    try:
        # UUID 형식 검증
        uuid.UUID(x_user_id)
        return x_user_id
    except ValueError:
        return None

