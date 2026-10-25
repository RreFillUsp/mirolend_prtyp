from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class PaymentMethod(str, Enum):
    MOBILE_MONEY = "mobile_money"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    CASH = "cash"


class PaymentCreate(BaseModel):
    repayment_id: str
    payment_method: PaymentMethod
    amount: Optional[float] = None  # If None, pay full amount
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class PaymentResponse(BaseModel):
    id: str
    repayment_id: str
    amount: float
    payment_method: str
    transaction_reference: Optional[str]
    status: str
    paid_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentInitiateResponse(BaseModel):
    payment_url: Optional[str]
    reference: str
    amount: float
    expires_at: datetime
    instructions: Optional[str]


class PaymentCallback(BaseModel):
    reference: str
    status: str
    amount: float
    transaction_id: Optional[str]
    metadata: Optional[dict] = None