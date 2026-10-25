from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.loan_repository import (
    LoanApplicationRepository,
    LoanContractRepository,
    RepaymentRepository,
)
from src.repositories.user_repository import UserRepository
from src.repositories.collateral_repository import CollateralRepository
from src.core.exceptions import (
    NotFoundException,
    ValidationException,
    LoanEligibilityException,
    CollateralException,
)
from src.schemas.loan import (
    LoanApplicationCreate,
    LoanApplicationUpdate,
    LoanApplicationResponse,
    LoanContractResponse,
    RepaymentResponse,
)
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class LoanService:
    """Loan management service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.application_repo = LoanApplicationRepository(db)
        self.contract_repo = LoanContractRepository(db)
        self.repayment_repo = RepaymentRepository(db)
        self.user_repo = UserRepository(db)
        self.collateral_repo = CollateralRepository(db)
    
    async def create_application(
        self,
        user_id: UUID,
        data: LoanApplicationCreate,
    ) -> LoanApplicationResponse:
        """Create a new loan application."""
        # Check user eligibility
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        if not user.is_eligible_for_loan:
            raise LoanEligibilityException(
                "User is not eligible for a loan",
                details={
                    "is_verified": user.is_verified,
                    "kyc_status": user.kyc_status,
                    "credit_score": user.credit_score,
                },
            )
        
        # Check if user has active loans
        active_contracts = await self.contract_repo.get_by_user(
            user_id,
            status="active",
        )
        if active_contracts:
            raise LoanEligibilityException(
                "User has active loans",
                details={"active_loans": len(active_contracts)},
            )
        
        # Validate collateral
        if data.collateral_id:
            collateral = await self.collateral_repo.get_by_id(
                UUID(data.collateral_id)
            )
            if not collateral:
                raise NotFoundException("Collateral", data.collateral_id)
            
            if collateral.user_id != user_id:
                raise ValidationException("Collateral does not belong to user")
            
            if collateral.is_encumbered:
                raise CollateralException("Collateral is already encumbered")
            
            if not collateral.is_verified:
                raise CollateralException("Collateral is not verified")
        
        # Calculate loan terms
        interest_rate = data.interest_rate or settings.DEFAULT_INTEREST_RATE
        monthly_installment = self._calculate_monthly_installment(
            data.amount,
            interest_rate,
            data.term_months,
        )
        total_repayment = monthly_installment * data.term_months
        
        # Create application
        application = await self.application_repo.create(
            user_id=user_id,
            collateral_id=data.collateral_id,
            amount=data.amount,
            interest_rate=interest_rate,
            term_months=data.term_months,
            monthly_installment=monthly_installment,
            total_repayment=total_repayment,
            purpose=data.purpose,
        )
        
        # Log audit
        logger.info(
            "Loan application created",
            application_id=str(application.id),
            user_id=str(user_id),
            amount=data.amount,
        )
        
        return LoanApplicationResponse.model_validate(application)
    
    async def approve_application(
        self,
        application_id: UUID,
        admin_id: UUID,
        notes: Optional[str] = None,
    ) -> LoanApplicationResponse:
        """Approve a loan application."""
        application = await self.application_repo.get_by_id(application_id)
        if not application:
            raise NotFoundException("Application", application_id)
        
        if application.status != "pending":
            raise ValidationException(
                f"Cannot approve application with status: {application.status}"
            )
        
        # Check if user is still eligible
        user = await self.user_repo.get_by_id(application.user_id)
        if not user.is_eligible_for_loan:
            raise LoanEligibilityException("User is no longer eligible for a loan")
        
        # Approve
        application = await self.application_repo.update_status(
            application_id,
            "approved",
            approved_by=admin_id,
            notes=notes,
        )
        
        # Create contract
        await self._create_contract(application)
        
        logger.info(
            "Loan application approved",
            application_id=str(application_id),
            admin_id=str(admin_id),
        )
        
        return LoanApplicationResponse.model_validate(application)
    
    async def reject_application(
        self,
        application_id: UUID,
        admin_id: UUID,
        notes: str,
    ) -> LoanApplicationResponse:
        """Reject a loan application."""
        application = await self.application_repo.update_status(
            application_id,
            "rejected",
            approved_by=admin_id,
            notes=notes,
        )
        if not application:
            raise NotFoundException("Application", application_id)
        
        logger.info(
            "Loan application rejected",
            application_id=str(application_id),
            admin_id=str(admin_id),
            reason=notes,
        )
        
        return LoanApplicationResponse.model_validate(application)
    
    async def get_application(
        self,
        application_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> LoanApplicationResponse:
        """Get loan application details."""
        application = await self.application_repo.get_by_id(application_id)
        if not application:
            raise NotFoundException("Application", application_id)
        
        # Check permissions
        if user_id and application.user_id != user_id:
            raise ValidationException("Cannot view other user's application")
        
        return LoanApplicationResponse.model_validate(application)
    
    async def list_applications(
        self,
        user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[LoanApplicationResponse]:
        """List loan applications."""
        if user_id:
            applications = await self.application_repo.get_by_user(
                user_id,
                status=status,
                skip=skip,
                limit=limit,
            )
        else:
            applications = await self.application_repo.get_all(
                skip=skip,
                limit=limit,
                status=status,
            )
        
        return [
            LoanApplicationResponse.model_validate(a)
            for a in applications
        ]
    
    async def get_contract(
        self,
        contract_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> LoanContractResponse:
        """Get loan contract details."""
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise NotFoundException("Contract", contract_id)
        
        if user_id and contract.user_id != user_id:
            raise ValidationException("Cannot view other user's contract")
        
        return LoanContractResponse.model_validate(contract)
    
    async def list_contracts(
        self,
        user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[LoanContractResponse]:
        """List loan contracts."""
        if user_id:
            contracts = await self.contract_repo.get_by_user(
                user_id,
                status=status,
                skip=skip,
                limit=limit,
            )
        else:
            contracts = await self.contract_repo.get_all(
                skip=skip,
                limit=limit,
                status=status,
            )
        
        return [
            LoanContractResponse.model_validate(c)
            for c in contracts
        ]
    
    async def list_repayments(
        self,
        contract_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> List[RepaymentResponse]:
        """List repayments for a contract."""
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise NotFoundException("Contract", contract_id)
        
        if user_id and contract.user_id != user_id:
            raise ValidationException("Cannot view other user's repayments")
        
        repayments = await self.repayment_repo.get_by_contract(contract_id)
        return [RepaymentResponse.model_validate(r) for r in repayments]
    
    async def _create_contract(self, application):
        """Create a loan contract from an application."""
        # Generate contract number
        contract_number = f"ML-{datetime.now().strftime('%Y%m')}-{application.id.hex[:8].upper()}"
        
        start_date = date.today()
        end_date = start_date + timedelta(days=application.term_months * 30)
        
        contract = await self.contract_repo.create(
            application_id=application.id,
            user_id=application.user_id,
            contract_number=contract_number,
            principal=application.amount,
            interest_total=application.total_repayment - application.amount,
            total_amount_due=application.total_repayment,
            start_date=start_date,
            end_date=end_date,
            status="active",
        )
        
        # Create repayment schedule
        await self._create_repayment_schedule(contract, application)
        
        return contract
    
    async def _create_repayment_schedule(self, contract, application):
        """Create a repayment schedule for a contract."""
        monthly_installment = application.monthly_installment
        due_date = contract.start_date
        
        for month in range(1, application.term_months + 1):
            due_date = due_date + timedelta(days=30)
            
            await self.repayment_repo.create(
                contract_id=contract.id,
                user_id=application.user_id,
                amount=monthly_installment,
                due_date=due_date,
            )
    
    def _calculate_monthly_installment(
        self,
        principal: float,
        annual_rate: float,
        term_months: int,
    ) -> float:
        """Calculate monthly installment using amortization formula."""
        monthly_rate = annual_rate / 100 / 12
        
        if monthly_rate == 0:
            return principal / term_months
        
        # M = P * (r * (1 + r)^n) / ((1 + r)^n - 1)
        numerator = monthly_rate * (1 + monthly_rate) ** term_months
        denominator = (1 + monthly_rate) ** term_months - 1
        return principal * (numerator / denominator)