from sqlalchemy import Column, String, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, INET
import uuid
from src.core.database import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    details = Column(JSON, default=dict)