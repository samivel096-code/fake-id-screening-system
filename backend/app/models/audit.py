import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from app.models.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), index=True, nullable=False)
    user_name = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False)
    document_id = Column(String(36), index=True, nullable=True)
    result = Column(String(100), nullable=True)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
