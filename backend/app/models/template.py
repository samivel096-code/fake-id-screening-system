import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Text
from app.models.database import Base

class DocumentTemplate(Base):
    __tablename__ = "document_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_type = Column(String(100), index=True, nullable=False)
    template_name = Column(String(255), nullable=False)
    version = Column(String(50), default="v1.0")
    issuing_org = Column(String(255), nullable=True)
    status = Column(String(20), default="ACTIVE")  # ACTIVE, INACTIVE
    is_default = Column(Boolean, default=False)
    
    aspect_ratio = Column(Float, nullable=True)
    expected_width = Column(Integer, nullable=True)
    expected_height = Column(Integer, nullable=True)
    
    sample_image_path = Column(String(500), nullable=True)
    template_profile_json = Column(Text, nullable=False)  # full JSON profile
    
    created_by = Column(String(100), default="ADMIN")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
