from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from enum import Enum


class LoanApplicationCreate(BaseModel):
    collateral_id: Optional[str] = None
    amount: float = Field(..., gt=0)
    term_months: int = Field(..., ge=1, le=12)
    purpose: Optional[str] = Field(None, max_length=500)
    interest_rate: Optional[float] = None
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v < 100:
            raise ValueError("Minimum loan amount is P100")
        if v > 50000:
            raise ValueError("Maximum loan amount is P50,000")
        return v


class LoanApplicationUpdate(BaseModel):
    status: Optional[str] = None
    approval_notes: Optional[str] = None


class LoanApplicationResponse(BaseModel):
    id: str
    user_id: str
    collateral_id: Optional[str]
    amount: float
    interest_rate: float
    term_months: int
    monthly_installment: Optional[float]
    total_repayment: Optional[float]
    purpose: Optional[str]
    status: str
    approval_date: Optional[datetime]
    disbursement_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoanContractResponse(BaseModel):
    id: str
    contract_number: str
    principal: float
    interest_total: float
    fees_total: float
    total_amount_due: float
    start_date: date
    end_date: date
    status: str
    signed_by_customer: bool
    signed_at: Optional[datetime]
    remaining_balance: Optional[float]
    
    class Config:
        from_attributes = True


class RepaymentResponse(BaseModel):
    id: str
    contract_id: str
    amount: float
    due_date: date
    paid_date: Optional[date]
    status: str
    payment_method: Optional[str]
    transaction_reference: Optional[str]
    late_fee: float
    
    class Config:
        from_attributes = True