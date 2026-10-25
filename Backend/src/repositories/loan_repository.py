from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from src.repositories.base import BaseRepository
from src.models.loan import LoanApplication, LoanContract, Repayment


class LoanApplicationRepository(BaseRepository[LoanApplication]):
    """Loan application repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(LoanApplication, session)
    
    async def get_by_user(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[LoanApplication]:
        """Get loan applications by user."""
        filters = {"user_id": user_id}
        if status:
            filters["status"] = status
        return await self.get_all(skip=skip, limit=limit, **filters)
    
    async def get_pending_approvals(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[LoanApplication]:
        """Get loan applications pending approval."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            status="pending",
        )
    
    async def update_status(
        self,
        application_id: UUID,
        status: str,
        approved_by: Optional[UUID] = None,
        notes: Optional[str] = None,
    ) -> Optional[LoanApplication]:
        """Update loan application status."""
        update_data = {"status": status}
        if approved_by:
            update_data["approved_by"] = approved_by
            update_data["approval_date"] = func.now()
        if notes:
            update_data["approval_notes"] = notes
        return await self.update(application_id, **update_data)


class LoanContractRepository(BaseRepository[LoanContract]):
    """Loan contract repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(LoanContract, session)
    
    async def get_by_user(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[LoanContract]:
        """Get contracts by user."""
        filters = {"user_id": user_id}
        if status:
            filters["status"] = status
        return await self.get_all(skip=skip, limit=limit, **filters)
    
    async def get_by_contract_number(
        self,
        contract_number: str,
    ) -> Optional[LoanContract]:
        """Get contract by number."""
        return await self.get_by_id(contract_number)  # Will need adjustment
    
    async def get_active_contracts(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[LoanContract]:
        """Get active contracts."""
        return await self.get_all(skip=skip, limit=limit, status="active")
    
    async def get_contracts_due_today(self) -> List[LoanContract]:
        """Get contracts with repayments due today."""
        # Custom query
        query = (
            select(LoanContract)
            .join(Repayment, LoanContract.id == Repayment.contract_id)
            .where(
                and_(
                    LoanContract.status == "active",
                    Repayment.status == "pending",
                    Repayment.due_date == date.today(),
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class RepaymentRepository(BaseRepository[Repayment]):
    """Repayment repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Repayment, session)
    
    async def get_by_contract(
        self,
        contract_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Repayment]:
        """Get repayments by contract."""
        filters = {"contract_id": contract_id}
        if status:
            filters["status"] = status
        return await self.get_all(skip=skip, limit=limit, **filters)
    
    async def get_overdue_repayments(self) -> List[Repayment]:
        """Get overdue repayments."""
        query = (
            select(Repayment)
            .where(
                and_(
                    Repayment.status == "pending",
                    Repayment.due_date < date.today(),
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def mark_as_paid(
        self,
        repayment_id: UUID,
        transaction_reference: str,
        payment_method: str,
    ) -> Optional[Repayment]:
        """Mark repayment as paid."""
        return await self.update(
            repayment_id,
            status="paid",
            paid_date=func.now(),
            transaction_reference=transaction_reference,
            payment_method=payment_method,
        )