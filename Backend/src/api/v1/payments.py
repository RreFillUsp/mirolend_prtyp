from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.security import get_current_user
from src.services.payment_service import PaymentService
from src.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentInitiateResponse,
    PaymentCallback,
)
from src.models.user import User
from uuid import UUID

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/initiate",
    response_model=PaymentInitiateResponse,
    summary="Initiate a payment",
)
async def initiate_payment(
    repayment_id: str = Body(...),
    payment_method: str = Body(...),
    amount: Optional[float] = Body(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initiate a payment for a repayment."""
    service = PaymentService(db)
    payment_data = PaymentCreate(
        repayment_id=repayment_id,
        payment_method=payment_method,
        amount=amount,
    )
    return await service.initiate_payment(
        current_user.id,
        UUID(repayment_id),
        payment_data,
    )


@router.post(
    "/callback",
    response_model=PaymentResponse,
    summary="Payment callback from gateway",
)
async def payment_callback(
    callback_data: PaymentCallback,
    db: AsyncSession = Depends(get_db),
):
    """Handle payment callback from payment gateway."""
    service = PaymentService(db)
    return await service.process_payment_callback(
        callback_data.reference,
        callback_data.status,
        callback_data.transaction_id,
    )


@router.get(
    "/repayments/{repayment_id}",
    response_model=PaymentResponse,
    summary="Get repayment details",
)
async def get_repayment(
    repayment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get repayment details."""
    # Implementation needed
    pass