from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.loan_repository import RepaymentRepository, LoanContractRepository
from src.repositories.user_repository import UserRepository
from src.core.exceptions import NotFoundException, ValidationException, PaymentException
from src.schemas.payment import PaymentCreate, PaymentResponse, PaymentInitiateResponse
from src.core.logging import get_logger
import secrets
from datetime import datetime, timedelta

logger = get_logger(__name__)


class PaymentService:
    """Payment processing service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repayment_repo = RepaymentRepository(db)
        self.contract_repo = LoanContractRepository(db)
        self.user_repo = UserRepository(db)
    
    async def initiate_payment(
        self,
        user_id: UUID,
        repayment_id: UUID,
        data: PaymentCreate,
    ) -> PaymentInitiateResponse:
        """Initiate a payment for a repayment."""
        # Get repayment
        repayment = await self.repayment_repo.get_by_id(repayment_id)
        if not repayment:
            raise NotFoundException("Repayment", repayment_id)
        
        if repayment.user_id != user_id:
            raise ValidationException("Cannot pay other user's repayment")
        
        if repayment.status == "paid":
            raise PaymentException("Repayment already paid")
        
        # Get contract
        contract = await self.contract_repo.get_by_id(repayment.contract_id)
        if contract.status != "active":
            raise PaymentException("Loan is not active")
        
        # Calculate amount
        amount = data.amount or repayment.amount
        
        # Check for late fee
        if repayment.due_date < datetime.now().date():
            late_fee = repayment.late_fee or 0
            amount += late_fee
        
        # Generate reference
        reference = f"PAY-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        
        # In production, integrate with payment gateway here
        # For now, return mock response
        return PaymentInitiateResponse(
            payment_url=f"https://payment.microlend.co.bw/pay/{reference}",
            reference=reference,
            amount=amount,
            expires_at=datetime.now() + timedelta(hours=24),
            instructions="Pay via mobile money or bank transfer",
        )
    
    async def process_payment_callback(
        self,
        reference: str,
        status: str,
        transaction_id: Optional[str] = None,
    ) -> PaymentResponse:
        """Process payment callback from gateway."""
        # In production, find repayment by reference
        # For now, we'll need to implement this properly
        
        # This is a placeholder
        raise NotImplementedError("Payment callback processing not implemented")
    
    async def mark_repayment_paid(
        self,
        repayment_id: UUID,
        transaction_reference: str,
        payment_method: str,
    ) -> PaymentResponse:
        """Mark a repayment as paid."""
        repayment = await self.repayment_repo.mark_as_paid(
            repayment_id,
            transaction_reference,
            payment_method,
        )
        if not repayment:
            raise NotFoundException("Repayment", repayment_id)
        
        # Check if contract is fully paid
        contract = await self.contract_repo.get_by_id(repayment.contract_id)
        remaining = await self._calculate_remaining_balance(contract.id)
        
        if remaining <= 0:
            await self.contract_repo.update(
                contract.id,
                status="completed",
            )
            logger.info(
                "Loan fully paid",
                contract_id=str(contract.id),
                user_id=str(contract.user_id),
            )
        
        logger.info(
            "Repayment marked as paid",
            repayment_id=str(repayment_id),
            transaction_reference=transaction_reference,
        )
        
        return PaymentResponse.model_validate(repayment)
    
    async def _calculate_remaining_balance(self, contract_id: UUID) -> float:
        """Calculate remaining balance on a contract."""
        repayments = await self.repayment_repo.get_by_contract(contract_id)
        total_paid = sum(r.amount for r in repayments if r.status == "paid")
        
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            return 0
        
        return contract.total_amount_due - total_paid