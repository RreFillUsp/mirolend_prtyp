from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date, datetime
from enum import Enum


class EmploymentStatus(str, Enum):
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    BUSINESS_OWNER = "business_owner"
    UNEMPLOYED = "unemployed"


class KYCSchema(BaseModel):
    kyc_status: str = "pending"
    national_id: Optional[str] = Field(None, pattern=r"^[A-Z]{2}\d{6}$")
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    
    employment_status: Optional[EmploymentStatus] = None
    employer: Optional[str] = None
    monthly_income: Optional[float] = Field(None, gt=0)


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+267\d{8}$")
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: str
    email: EmailStr
    phone: str
    first_name: str
    last_name: str
    national_id: Optional[str]
    date_of_birth: Optional[date]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    employment_status: Optional[str]
    employer: Optional[str]
    monthly_income: Optional[float]
    credit_score: int
    is_verified: bool
    is_active: bool
    kyc_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    items: List[UserProfileResponse]
    total: int
    page: int
    size: int
    pages: int