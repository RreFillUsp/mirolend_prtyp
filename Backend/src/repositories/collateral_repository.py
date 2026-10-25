from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.repositories.base import BaseRepository
from src.models.collateral import CollateralItem


class CollateralRepository(BaseRepository[CollateralItem]):
    """Collateral repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(CollateralItem, session)
    
    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CollateralItem]:
        """Get collateral items by user."""
        return await self.get_all(skip=skip, limit=limit, user_id=user_id)
    
    async def get_by_serial_number(
        self,
        serial_number: str,
    ) -> Optional[CollateralItem]:
        """Get collateral by serial number."""
        query = select(CollateralItem).where(
            CollateralItem.serial_number == serial_number
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_imei(
        self,
        imei: str,
    ) -> Optional[CollateralItem]:
        """Get collateral by IMEI."""
        query = select(CollateralItem).where(CollateralItem.imei == imei)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_available_for_loan(
        self,
        user_id: UUID,
    ) -> List[CollateralItem]:
        """Get collateral items available for a new loan."""
        query = (
            select(CollateralItem)
            .where(
                and_(
                    CollateralItem.user_id == user_id,
                    CollateralItem.is_encumbered == False,
                    CollateralItem.is_verified == True,
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def register_security_interest(
        self,
        collateral_id: UUID,
        registry_reference: str,
    ) -> Optional[CollateralItem]:
        """Register security interest with collateral registry."""
        return await self.update(
            collateral_id,
            registry_reference=registry_reference,
            security_interest_registered=True,
            registration_date=func.now(),
            is_encumbered=True,
        )
    
    async def release_security_interest(
        self,
        collateral_id: UUID,
    ) -> Optional[CollateralItem]:
        """Release security interest from collateral."""
        return await self.update(
            collateral_id,
            registry_reference=None,
            security_interest_registered=False,
            registration_date=None,
            is_encumbered=False,
        )