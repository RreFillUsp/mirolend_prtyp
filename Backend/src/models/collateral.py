from typing import Optional, List
from sqlalchemy import Column, String, Float, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.core.database import BaseModel


class CollateralItem(BaseModel):
    __tablename__ = "collateral_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    item_type = Column(
        Enum("phone", "laptop", "tablet", "tv", "camera", "gaming_console",
             "jewelry", "vehicle", "other", name="collateral_type"),
        nullable=False
    )
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True, index=True)
    imei = Column(String(50), nullable=True, index=True)
    
    estimated_value = Column(Float, nullable=False)
    condition = Column(
        Enum("new", "excellent", "good", "fair", "poor", name="item_condition"),
        default="good"
    )
    description = Column(String(500), nullable=True)
    
    images = Column(JSON, default=list)  # Array of image URLs
    
    # Collateral Registry (Movable Property Act)
    registry_reference = Column(String(100), nullable=True, index=True)
    security_interest_registered = Column(Boolean, default=False)
    registration_date = Column(DateTime, nullable=True)
    
    is_encumbered = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    owner = relationship("User", back_populates="collateral_items")
    loan_applications = relationship("LoanApplication", back_populates="collateral")
    
    @property
    def display_name(self) -> str:
        if self.brand and self.model:
            return f"{self.brand} {self.model}"
        return f"{self.item_type}"