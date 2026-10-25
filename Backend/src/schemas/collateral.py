from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


class CollateralType(str, Enum):
    PHONE = "phone"
    LAPTOP = "laptop"
    TABLET = "tablet"
    TV = "tv"
    CAMERA = "camera"
    GAMING_CONSOLE = "gaming_console"
    JEWELRY = "jewelry"
    VEHICLE = "vehicle"
    OTHER = "other"


class ItemCondition(str, Enum):
    NEW = "new"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class CollateralCreate(BaseModel):
    item_type: CollateralType
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    imei: Optional[str] = Field(None, pattern=r"^\d{15}$")
    estimated_value: float = Field(..., gt=0, le=500000)
    condition: ItemCondition = ItemCondition.GOOD
    description: Optional[str] = Field(None, max_length=500)
    images: List[str] = Field(default_factory=list)
    
    @field_validator("estimated_value")
    @classmethod
    def validate_value(cls, v: float) -> float:
        if v < 100:
            raise ValueError("Estimated value must be at least P100")
        return v


class CollateralUpdate(BaseModel):
    estimated_value: Optional[float] = Field(None, gt=0)
    condition: Optional[ItemCondition] = None
    description: Optional[str] = Field(None, max_length=500)
    images: Optional[List[str]] = None


class CollateralResponse(BaseModel):
    id: str
    user_id: str
    item_type: str
    brand: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    imei: Optional[str]
    estimated_value: float
    condition: str
    description: Optional[str]
    images: List[str]
    registry_reference: Optional[str]
    security_interest_registered: bool
    is_encumbered: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CollateralVerificationRequest(BaseModel):
    registry_reference: str
    verified: bool
    notes: Optional[str] = None