from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.security import get_current_user, get_current_admin_user
from src.services.user_service import UserService
from src.schemas.user import UserProfileResponse, UserListResponse, UserUpdate
from src.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get the current user's profile."""
    return current_user


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update current user profile",
)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    service = UserService(db)
    return await service.update_profile(current_user.id, user_data)


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List users (admin only)",
)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    kyc_status: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List all users with pagination (admin only)."""
    service = UserService(db)
    return await service.list_users(
        skip=skip,
        limit=limit,
        is_active=is_active,
        kyc_status=kyc_status,
    )


@router.get(
    "/{user_id}",
    response_model=UserProfileResponse,
    summary="Get user by ID (admin only)",
)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user by ID (admin only)."""
    service = UserService(db)
    return await service.get_profile(UUID(user_id))


@router.put(
    "/{user_id}/verify",
    response_model=UserProfileResponse,
    summary="Verify user (admin only)",
)
async def verify_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify a user (admin only)."""
    service = UserService(db)
    return await service.verify_user(UUID(user_id))


@router.put(
    "/{user_id}/deactivate",
    response_model=UserProfileResponse,
    summary="Deactivate user (admin only)",
)
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a user (admin only)."""
    service = UserService(db)
    return await service.deactivate_user(UUID(user_id))


@router.put(
    "/{user_id}/credit-score",
    response_model=UserProfileResponse,
    summary="Update credit score (admin only)",
)
async def update_credit_score(
    user_id: str,
    score: int = Query(..., ge=300, le=850),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a user's credit score (admin only)."""
    service = UserService(db)
    return await service.update_credit_score(UUID(user_id), score)