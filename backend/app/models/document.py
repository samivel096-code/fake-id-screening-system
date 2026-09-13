import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.models.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    normalized_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=False)
    document_type = Column(String(100), nullable=False)
    uploaded_by_user_id = Column(String(50), index=True, nullable=True)
    status = Column(String(50), default="UPLOADED")  # UPLOADED, PROCESSED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
