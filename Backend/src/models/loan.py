from typing import Optional, List
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.core.database import BaseModel


class LoanApplication(BaseModel):
    __tablename__ = "loan_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    collateral_id = Column(UUID(as_uuid=True), ForeignKey("collateral_items.id"), nullable=True)
    
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    term_months = Column(Integer, nullable=False)
    monthly_installment = Column(Float, nullable=True)
    total_repayment = Column(Float, nullable=True)
    
    purpose = Column(String(500), nullable=True)
    
    status = Column(
        Enum("draft", "pending", "under_review", "approved", "rejected", 
             "disbursed", "completed", "defaulted", name="loan_status"),
        default="pending"
    )
    
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    approval_notes = Column(String(500), nullable=True)
    
    disbursement_date = Column(DateTime, nullable=True)
    disbursement_method = Column(String(50), nullable=True)
    disbursement_reference = Column(String(100), nullable=True)
    
    # Relationships
    borrower = relationship("User", foreign_keys=[user_id], back_populates="loan_applications")
    collateral = relationship("CollateralItem", back_populates="loan_applications")
    contract = relationship("LoanContract", back_populates="application", uselist=False)
    reviewer = relationship("User", foreign_keys=[approved_by])
    
    @property
    def is_approved(self) -> bool:
        return self.status in ["approved", "disbursed", "completed"]


class LoanContract(BaseModel):
    __tablename__ = "loan_contracts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("loan_applications.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    contract_number = Column(String(50), unique=True, nullable=False, index=True)
    
    principal = Column(Float, nullable=False)
    interest_total = Column(Float, nullable=False)
    fees_total = Column(Float, default=0)
    total_amount_due = Column(Float, nullable=False)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    status = Column(
        Enum("active", "completed", "defaulted", "written_off", name="contract_status"),
        default="active"
    )
    
    signed_by_customer = Column(Boolean, default=False)
    signed_by_lender = Column(Boolean, default=False)
    signed_at = Column(DateTime, nullable=True)
    esignature_url = Column(String(500), nullable=True)
    
    # Relationships
    borrower = relationship("User", back_populates="loan_contracts")
    application = relationship("LoanApplication", back_populates="contract")
    repayments = relationship("Repayment", back_populates="contract")
    
    @property
    def remaining_balance(self) -> float:
        total_paid = sum(r.amount for r in self.repayments if r.status == "paid")
        return self.total_amount_due - total_paid


class Repayment(BaseModel):
    __tablename__ = "repayments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("loan_contracts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date, nullable=True)
    
    status = Column(
        Enum("pending", "paid", "overdue", "partial", name="repayment_status"),
        default="pending"
    )
    
    payment_method = Column(
        Enum("mobile_money", "bank_transfer", "cash", "card", name="payment_method"),
        nullable=True
    )
    transaction_reference = Column(String(100), nullable=True, index=True)
    
    late_fee = Column(Float, default=0)
    penalty_interest = Column(Float, default=0)
    
    # Relationships
    contract = relationship("LoanContract", back_populates="repayments")
    borrower = relationship("User", back_populates="repayments")