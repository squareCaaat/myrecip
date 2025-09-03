from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.schemas import UserCreate, UserLogin, UserResponse, Token
from app.services.user_service import UserService
from app.dependencies.auth import get_current_user, security


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 회원가입
    
    - **email**: 이메일 주소 (중복 불가)
    - **username**: 사용자명
    - **password**: 비밀번호 (최소 8자)
    """
    user_service = UserService(db)
    return await user_service.create_user(user_data)


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 로그인
    
    - **email**: 등록된 이메일 주소
    - **password**: 비밀번호
    
    성공 시 JWT 액세스 토큰을 반환합니다.
    """
    user_service = UserService(db)
    return await user_service.authenticate_user(login_data)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 로그아웃
    
    현재 사용자의 토큰을 무효화합니다.
    """
    user_service = UserService(db)
    token = credentials.credentials
    
    success = await user_service.logout_user(str(current_user.user_id), token)
    
    if success:
        return {"message": "성공적으로 로그아웃되었습니다."}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그아웃 처리 중 오류가 발생했습니다."
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    현재 로그인한 사용자 정보 조회
    
    JWT 토큰이 필요합니다.
    """
    return current_user


@router.get("/validate-token", response_model=dict)
async def validate_token(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    토큰 유효성 검증
    
    JWT 토큰의 유효성을 확인합니다.
    """
    return {
        "valid": True,
        "user_id": str(current_user.user_id),
        "username": current_user.username
    }

