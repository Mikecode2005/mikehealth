"""Authentication service."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.config import get_settings
from mikehealth.models.user import User, UserRole
from mikehealth.repositories.user import UserRepository
from mikehealth.schemas.user import Token, TokenPayload, UserCreate, UserLogin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication and authorization service."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.settings = get_settings()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(
        self,
        user_id: str,
        role: str,
        patient_id: Optional[str] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a JWT access token."""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.settings.access_token_expire_minutes
            )

        to_encode = {
            "sub": user_id,
            "role": role,
            "patient_id": patient_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }
        return jwt.encode(to_encode, self.settings.secret_key, algorithm=self.settings.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """Create a JWT refresh token."""
        expire = datetime.now(timezone.utc) + timedelta(days=self.settings.refresh_token_expire_days)
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }
        return jwt.encode(to_encode, self.settings.secret_key, algorithm=self.settings.algorithm)

    def decode_token(self, token: str) -> TokenPayload:
        """Decode and validate a JWT token."""
        payload = jwt.decode(
            token, self.settings.secret_key, algorithms=[self.settings.algorithm]
        )
        return TokenPayload(**payload)

    async def authenticate_user(self, login: UserLogin) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = await self.user_repo.get_by_email(login.email)
        if not user or not user.is_active:
            return None
        if not self.verify_password(login.password, user.hashed_password):
            return None
        return user

    async def register_user(self, user_create: UserCreate) -> User:
        """Register a new user."""
        # Check if email already exists
        existing = await self.user_repo.get_by_email(user_create.email)
        if existing:
            raise ValueError("Email already registered")

        # Create user
        user = User(
            id=str(uuid4()),
            email=user_create.email,
            hashed_password=self.get_password_hash(user_create.password),
            full_name=user_create.full_name,
            role=UserRole(user_create.role),
            patient_id=user_create.patient_id,
        )
        return await self.user_repo.create(user)

    async def create_tokens(self, user: User) -> Token:
        """Create access and refresh tokens for a user."""
        access_token = self.create_access_token(
            user_id=user.id,
            role=user.role.value,
            patient_id=user.patient_id,
        )
        refresh_token = self.create_refresh_token(user_id=user.id)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.settings.access_token_expire_minutes * 60,
        )

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Create new access token from refresh token."""
        try:
            payload = self.decode_token(refresh_token)
            if payload.type != "refresh":
                return None
            user = await self.user_repo.get_by_id(UUID(payload.sub))
            if not user or not user.is_active:
                return None
            return self.create_access_token(
                user_id=user.id,
                role=user.role.value,
                patient_id=user.patient_id,
            )
        except Exception:
            return None