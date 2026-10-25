from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from src.repositories.base import BaseRepository
from src.models.user import User


class UserRepository(BaseRepository[User]):
    """User repository with custom methods."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone."""
        query = select(User).where(User.phone == phone)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_national_id(self, national_id: str) -> Optional[User]:
        """Get user by national ID."""
        query = select(User).where(User.national_id == national_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_email_or_phone(
        self,
        email: str,
        phone: str,
    ) -> Optional[User]:
        """Get user by email or phone."""
        query = select(User).where(
            or_(User.email == email, User.phone == phone)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        """Get active users."""
        return await self.get_all(skip=skip, limit=limit, is_active=True)
    
    async def update_credit_score(
        self,
        user_id: UUID,
        new_score: int,
    ) -> Optional[User]:
        """Update user's credit score."""
        return await self.update(user_id, credit_score=new_score)
    
    async def update_kyc_status(
        self,
        user_id: UUID,
        status: str,
    ) -> Optional[User]:
        """Update KYC status."""
        return await self.update(user_id, kyc_status=status, is_verified=(status == "verified"))