"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.api.deps import get_auth_service
from mikehealth.schemas.user import UserCreate, UserLogin, Token, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, auth_service=Depends(get_auth_service)):
    """Register a new user."""
    try:
        user = await auth_service.register_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, auth_service=Depends(get_auth_service)):
    """Login and get access/refresh tokens."""
    user = await auth_service.authenticate_user(credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await auth_service.create_tokens(user)


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, auth_service=Depends(get_auth_service)):
    """Get new access token using refresh token."""
    access_token = await auth_service.refresh_access_token(refresh_token)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserRead)
async def get_current_user_info(current_user=Depends(get_auth_service.get_current_user)):
    """Get current user info."""
    return current_user