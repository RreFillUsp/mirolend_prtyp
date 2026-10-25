from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.security import get_current_user, get_current_admin_user
from src.services.loan_service import LoanService
from src.schemas.loan import (
    LoanApplicationCreate,
    LoanApplicationUpdate,
    LoanApplicationResponse,
    LoanContractResponse,
    RepaymentResponse,
)
from src.models.user import User
from uuid import UUID

router = APIRouter(prefix="/loans", tags=["Loans"])


# Applications
@router.post(
    "/applications",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a loan application",
)
async def create_application(
    data: LoanApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new loan application."""
    service = LoanService(db)
    return await service.create_application(current_user.id, data)


@router.get(
    "/applications",
    response_model=List[LoanApplicationResponse],
    summary="List loan applications",
)
async def list_applications(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's loan applications."""
    service = LoanService(db)
    return await service.list_applications(
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/applications/{application_id}",
    response_model=LoanApplicationResponse,
    summary="Get loan application details",
)
async def get_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get loan application details."""
    service = LoanService(db)
    return await service.get_application(
        UUID(application_id),
        user_id=current_user.id,
    )


@router.put(
    "/applications/{application_id}/approve",
    response_model=LoanApplicationResponse,
    summary="Approve loan application (admin only)",
)
async def approve_application(
    application_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a loan application (admin only)."""
    service = LoanService(db)
    return await service.approve_application(
        UUID(application_id),
        current_user.id,
        notes,
    )


@router.put(
    "/applications/{application_id}/reject",
    response_model=LoanApplicationResponse,
    summary="Reject loan application (admin only)",
)
async def reject_application(
    application_id: str,
    notes: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject a loan application (admin only)."""
    service = LoanService(db)
    return await service.reject_application(
        UUID(application_id),
        current_user.id,
        notes,
    )


# Contracts
@router.get(
    "/contracts",
    response_model=List[LoanContractResponse],
    summary="List loan contracts",
)
async def list_contracts(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's loan contracts."""
    service = LoanService(db)
    return await service.list_contracts(
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/contracts/{contract_id}",
    response_model=LoanContractResponse,
    summary="Get loan contract details",
)
async def get_contract(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get loan contract details."""
    service = LoanService(db)
    return await service.get_contract(
        UUID(contract_id),
        user_id=current_user.id,
    )


# Repayments
@router.get(
    "/contracts/{contract_id}/repayments",
    response_model=List[RepaymentResponse],
    summary="List repayments for a contract",
)
async def list_repayments(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List repayments for a contract."""
    service = LoanService(db)
    return await service.list_repayments(
        UUID(contract_id),
        user_id=current_user.id,
    )