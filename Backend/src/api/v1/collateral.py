from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.security import get_current_user, get_current_admin_user
from src.services.collateral_service import CollateralService
from src.schemas.collateral import (
    CollateralCreate,
    CollateralUpdate,
    CollateralResponse,
    CollateralVerificationRequest,
)
from src.models.user import User
from uuid import UUID

router = APIRouter(prefix="/collateral", tags=["Collateral"])


@router.post(
    "/",
    response_model=CollateralResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add collateral item",
)
async def create_collateral(
    data: CollateralCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new collateral item."""
    service = CollateralService(db)
    return await service.create_collateral(current_user.id, data)


@router.get(
    "/",
    response_model=List[CollateralResponse],
    summary="List user's collateral",
)
async def list_collateral(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's collateral items."""
    service = CollateralService(db)
    return await service.list_collateral(
        current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/available",
    response_model=List[CollateralResponse],
    summary="Get available collateral for loans",
)
async def get_available_collateral(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get collateral items available for new loans."""
    service = CollateralService(db)
    return await service.get_available_collateral(current_user.id)


@router.get(
    "/{collateral_id}",
    response_model=CollateralResponse,
    summary="Get collateral details",
)
async def get_collateral(
    collateral_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get collateral details."""
    service = CollateralService(db)
    return await service.get_collateral(
        UUID(collateral_id),
        user_id=current_user.id,
    )


@router.put(
    "/{collateral_id}",
    response_model=CollateralResponse,
    summary="Update collateral",
)
async def update_collateral(
    collateral_id: str,
    data: CollateralUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update collateral details."""
    service = CollateralService(db)
    return await service.update_collateral(
        UUID(collateral_id),
        current_user.id,
        data,
    )


@router.delete(
    "/{collateral_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete collateral",
)
async def delete_collateral(
    collateral_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete collateral item."""
    service = CollateralService(db)
    await service.delete_collateral(UUID(collateral_id), current_user.id)
    return None


@router.put(
    "/{collateral_id}/verify",
    response_model=CollateralResponse,
    summary="Verify collateral (admin only)",
)
async def verify_collateral(
    collateral_id: str,
    data: CollateralVerificationRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify collateral and register security interest (admin only)."""
    service = CollateralService(db)
    return await service.verify_collateral(
        UUID(collateral_id),
        current_user.id,
        data,
    )