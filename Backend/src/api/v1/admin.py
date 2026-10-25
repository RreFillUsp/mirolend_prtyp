from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.security import get_current_admin_user
from src.services.loan_service import LoanService
from src.services.user_service import UserService
from src.schemas.loan import LoanApplicationResponse, LoanContractResponse
from src.schemas.user import UserProfileResponse, UserListResponse
from src.models.user import User
from uuid import UUID

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/applications/pending",
    response_model=List[LoanApplicationResponse],
    summary="Get pending loan applications",
)
async def get_pending_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all pending loan applications (admin only)."""
    service = LoanService(db)
    return await service.list_applications(
        status="pending",
        skip=skip,
        limit=limit,
    )


@router.get(
    "/contracts/active",
    response_model=List[LoanContractResponse],
    summary="Get active loan contracts",
)
async def get_active_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all active loan contracts (admin only)."""
    service = LoanService(db)
    return await service.list_contracts(
        status="active",
        skip=skip,
        limit=limit,
    )


@router.get(
    "/users/unverified",
    response_model=UserListResponse,
    summary="Get unverified users",
)
async def get_unverified_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get users pending verification (admin only)."""
    service = UserService(db)
    return await service.list_users(
        skip=skip,
        limit=limit,
        kyc_status="pending",
    )


@router.get(
    "/dashboard/stats",
    summary="Get admin dashboard statistics",
)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get admin dashboard statistics (admin only)."""
    # Implementation needed
    return {
        "total_users": 0,
        "pending_applications": 0,
        "active_loans": 0,
        "total_disbursed": 0,
        "revenue": 0,
        "default_rate": 0,
    }