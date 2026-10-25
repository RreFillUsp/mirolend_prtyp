from typing import Optional, List
from sqlalchemy import Column, String, Boolean, Integer, Float, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.core.database import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    national_id = Column(String(20), unique=True, nullable=True, index=True)
    date_of_birth = Column(Date, nullable=True)
    
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    
    employment_status = Column(
        Enum("employed", "self_employed", "business_owner", "unemployed", 
             name="employment_status"),
        nullable=True
    )
    employer = Column(String(255), nullable=True)
    monthly_income = Column(Float, nullable=True)
    
    credit_score = Column(Integer, default=500)
    
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    kyc_status = Column(
        Enum("pending", "submitted", "verified", "rejected", name="kyc_status"),
        default="pending"
    )
    
    # Relationships
    collateral_items = relationship("CollateralItem", back_populates="owner", lazy="selectin")
    loan_applications = relationship("LoanApplication", back_populates="borrower", lazy="selectin")
    loan_contracts = relationship("LoanContract", back_populates="borrower", lazy="selectin")
    repayments = relationship("Repayment", back_populates="borrower", lazy="selectin")
    kyc_documents = relationship("KYCDocument", back_populates="user", lazy="selectin")
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_eligible_for_loan(self) -> bool:
        return (
            self.is_verified 
            and self.is_active 
            and self.kyc_status == "verified"
            and self.credit_score >= 450
        )