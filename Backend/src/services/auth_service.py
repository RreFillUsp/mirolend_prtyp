from typing import Optional, Tuple
from uuid import UUID
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.core.exceptions import (
    UnauthorizedException,
    ConflictException,
    ValidationException,
    NotFoundException,
)
from src.repositories.user_repository import UserRepository
from src.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from src.schemas.user import UserUpdate
from src.core.config import settings
import secrets


class AuthService:
    """Authentication service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register(self, user_data: UserRegister) -> TokenResponse:
        """Register a new user."""
        # Check if user exists
        existing = await self.user_repo.get_by_email_or_phone(
            user_data.email,
            user_data.phone,
        )
        if existing:
            raise ConflictException("User already exists")
        
        # Check if national ID is already registered
        if user_data.national_id:
            existing_nid = await self.user_repo.get_by_national_id(
                user_data.national_id
            )
            if existing_nid:
                raise ConflictException("National ID already registered")
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        user = await self.user_repo.create(
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            national_id=user_data.national_id,
        )
        
        return await self._generate_token_response(user)
    
    async def login(self, credentials: UserLogin) -> TokenResponse:
        """Login user."""
        user = await self.user_repo.get_by_email(credentials.email)
        
        if not user:
            raise UnauthorizedException("Invalid credentials")
        
        if not verify_password(credentials.password, user.password_hash):
            raise UnauthorizedException("Invalid credentials")
        
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")
        
        return await self._generate_token_response(user)
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token."""
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise UnauthorizedException("Invalid token")
            
            user = await self.user_repo.get_by_id(UUID(user_id))
            if not user:
                raise UnauthorizedException("User not found")
            
            if not user.is_active:
                raise UnauthorizedException("Account is deactivated")
            
            return await self._generate_token_response(user)
            
        except Exception as e:
            raise UnauthorizedException("Invalid refresh token")
    
    async def request_password_reset(self, email: str):
        """Request password reset."""
        user = await self.user_repo.get_by_email(email)
        if user:
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            # In production, store this token in Redis with TTL
            # and send email with reset link
            # For now, just log
            print(f"Password reset token for {email}: {reset_token}")
        
        # Always return success to prevent email enumeration
        return True
    
    async def confirm_password_reset(
        self,
        token: str,
        new_password: str,
    ) -> TokenResponse:
        """Confirm password reset."""
        # In production, validate token from Redis
        # For now, we'll skip validation and just update
        
        # This is a placeholder - in production, you'd decode the token
        # and find the user ID
        raise NotImplementedError("Password reset confirmation not implemented")
    
    async def update_profile(
        self,
        user_id: UUID,
        user_data: UserUpdate,
    ) -> UserResponse:
        """Update user profile."""
        user = await self.user_repo.update(user_id, **user_data.dict(exclude_unset=True))
        if not user:
            raise NotFoundException("User", user_id)
        return UserResponse.model_validate(user)
    
    async def _generate_token_response(self, user) -> TokenResponse:
        """Generate token response."""
        access_token = create_access_token(
            {"sub": str(user.id), "email": user.email}
        )
        refresh_token = create_refresh_token(
            {"sub": str(user.id)}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )