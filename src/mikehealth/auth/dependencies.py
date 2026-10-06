"""FastAPI authentication dependencies."""
from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.auth.jwt import decode_token
from mikehealth.database import get_db
from mikehealth.models.user import User, UserRole
from mikehealth.repositories.user import UserRepository
from mikehealth.schemas.user import TokenPayload


async def get_current_user(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not authorization:
        raise credentials_exception

    if not authorization.startswith("Bearer "):
        raise credentials_exception

    token = authorization.split(" ")[1]

    try:
        payload = decode_token(token)
        if payload.type != "access":
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(UUID(payload.sub))

    if not user or not user.is_active:
        raise credentials_exception

    return user


async def get_optional_user(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    session: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Get current user if token is provided and valid, otherwise None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.split(" ")[1]

    try:
        payload = decode_token(token)
        if payload.type != "access":
            return None
    except ValueError:
        return None

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(UUID(payload.sub))

    if not user or not user.is_active:
        return None

    return user


def require_role(*allowed_roles: UserRole):
    """Dependency factory for role-based access control."""
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.role.value} not authorized for this action",
            )
        return user
    return role_checker