from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.collateral_repository import CollateralRepository
from src.repositories.user_repository import UserRepository
from src.core.exceptions import NotFoundException, ValidationException, CollateralException
from src.schemas.collateral import (
    CollateralCreate,
    CollateralUpdate,
    CollateralResponse,
    CollateralVerificationRequest,
)
from src.core.logging import get_logger

logger = get_logger(__name__)


class CollateralService:
    """Collateral management service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.collateral_repo = CollateralRepository(db)
        self.user_repo = UserRepository(db)
    
    async def create_collateral(
        self,
        user_id: UUID,
        data: CollateralCreate,
    ) -> CollateralResponse:
        """Create a new collateral item."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        # Check if serial number or IMEI already exists
        if data.serial_number:
            existing = await self.collateral_repo.get_by_serial_number(
                data.serial_number
            )
            if existing:
                raise CollateralException("Serial number already registered")
        
        if data.imei:
            existing = await self.collateral_repo.get_by_imei(data.imei)
            if existing:
                raise CollateralException("IMEI already registered")
        
        # Create collateral
        collateral = await self.collateral_repo.create(
            user_id=user_id,
            **data.dict(),
        )
        
        logger.info(
            "Collateral created",
            collateral_id=str(collateral.id),
            user_id=str(user_id),
            item_type=data.item_type,
        )
        
        return CollateralResponse.model_validate(collateral)
    
    async def get_collateral(
        self,
        collateral_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> CollateralResponse:
        """Get collateral details."""
        collateral = await self.collateral_repo.get_by_id(collateral_id)
        if not collateral:
            raise NotFoundException("Collateral", collateral_id)
        
        if user_id and collateral.user_id != user_id:
            raise ValidationException("Cannot view other user's collateral")
        
        return CollateralResponse.model_validate(collateral)
    
    async def list_collateral(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CollateralResponse]:
        """List user's collateral items."""
        items = await self.collateral_repo.get_by_user(
            user_id,
            skip=skip,
            limit=limit,
        )
        return [CollateralResponse.model_validate(i) for i in items]
    
    async def update_collateral(
        self,
        collateral_id: UUID,
        user_id: UUID,
        data: CollateralUpdate,
    ) -> CollateralResponse:
        """Update collateral details."""
        collateral = await self.collateral_repo.get_by_id(collateral_id)
        if not collateral:
            raise NotFoundException("Collateral", collateral_id)
        
        if collateral.user_id != user_id:
            raise ValidationException("Cannot update other user's collateral")
        
        if collateral.is_encumbered:
            raise CollateralException("Cannot update encumbered collateral")
        
        updated = await self.collateral_repo.update(
            collateral_id,
            **data.dict(exclude_unset=True),
        )
        
        logger.info(
            "Collateral updated",
            collateral_id=str(collateral_id),
            user_id=str(user_id),
        )
        
        return CollateralResponse.model_validate(updated)
    
    async def delete_collateral(
        self,
        collateral_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Delete collateral item."""
        collateral = await self.collateral_repo.get_by_id(collateral_id)
        if not collateral:
            raise NotFoundException("Collateral", collateral_id)
        
        if collateral.user_id != user_id:
            raise ValidationException("Cannot delete other user's collateral")
        
        if collateral.is_encumbered:
            raise CollateralException("Cannot delete encumbered collateral")
        
        deleted = await self.collateral_repo.delete(collateral_id)
        
        logger.info(
            "Collateral deleted",
            collateral_id=str(collateral_id),
            user_id=str(user_id),
        )
        
        return deleted
    
    async def verify_collateral(
        self,
        collateral_id: UUID,
        admin_id: UUID,
        data: CollateralVerificationRequest,
    ) -> CollateralResponse:
        """Verify collateral (admin only)."""
        collateral = await self.collateral_repo.get_by_id(collateral_id)
        if not collateral:
            raise NotFoundException("Collateral", collateral_id)
        
        if data.verified:
            # Register security interest
            collateral = await self.collateral_repo.register_security_interest(
                collateral_id,
                data.registry_reference,
            )
            await self.collateral_repo.update(
                collateral_id,
                is_verified=True,
            )
        else:
            collateral = await self.collateral_repo.update(
                collateral_id,
                is_verified=False,
            )
        
        logger.info(
            "Collateral verified" if data.verified else "Collateral verification failed",
            collateral_id=str(collateral_id),
            admin_id=str(admin_id),
            notes=data.notes,
        )
        
        return CollateralResponse.model_validate(collateral)
    
    async def get_available_collateral(
        self,
        user_id: UUID,
    ) -> List[CollateralResponse]:
        """Get available collateral for loans."""
        items = await self.collateral_repo.get_available_for_loan(user_id)
        return [CollateralResponse.model_validate(i) for i in items]