from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.user_repository import UserRepository
from src.core.exceptions import NotFoundException, ValidationException
from src.schemas.user import UserProfileResponse, UserListResponse
from src.schemas.auth import UserUpdate
from src.models.user import User


class UserService:
    """User management service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repo.get_by_id(user_id)
    
    async def get_profile(self, user_id: UUID) -> UserProfileResponse:
        """Get user profile."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return UserProfileResponse.model_validate(user)
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        kyc_status: Optional[str] = None,
    ) -> UserListResponse:
        """List users with pagination."""
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
        if kyc_status:
            filters["kyc_status"] = kyc_status
        
        users = await self.user_repo.get_all(skip=skip, limit=limit, **filters)
        total = await self.user_repo.get_count(**filters)
        
        return UserListResponse(
            items=[UserProfileResponse.model_validate(u) for u in users],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 1,
        )
    
    async def update_profile(
        self,
        user_id: UUID,
        user_data: UserUpdate,
    ) -> UserProfileResponse:
        """Update user profile."""
        # Check if phone is already taken by another user
        if user_data.phone:
            existing = await self.user_repo.get_by_phone(user_data.phone)
            if existing and existing.id != user_id:
                raise ValidationException("Phone number already in use")
        
        user = await self.user_repo.update(
            user_id,
            **user_data.dict(exclude_unset=True)
        )
        if not user:
            raise NotFoundException("User", user_id)
        
        return UserProfileResponse.model_validate(user)
    
    async def deactivate_user(self, user_id: UUID):
        """Deactivate a user."""
        user = await self.user_repo.update(user_id, is_active=False)
        if not user:
            raise NotFoundException("User", user_id)
        return UserProfileResponse.model_validate(user)
    
    async def verify_user(self, user_id: UUID):
        """Verify a user."""
        user = await self.user_repo.update(user_id, is_verified=True)
        if not user:
            raise NotFoundException("User", user_id)
        return UserProfileResponse.model_validate(user)
    
    async def update_credit_score(
        self,
        user_id: UUID,
        score: int,
    ) -> UserProfileResponse:
        """Update user's credit score."""
        if not 300 <= score <= 850:
            raise ValidationException("Credit score must be between 300 and 850")
        
        user = await self.user_repo.update_credit_score(user_id, score)
        if not user:
            raise NotFoundException("User", user_id)
        
        return UserProfileResponse.model_validate(user)