import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, Text, DateTime, Integer
from app.models.database import Base

class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), index=True, nullable=False)
    document_type = Column(String(100), index=True, nullable=False)
    template_id = Column(String(36), nullable=True)
    
    officer_id = Column(String(50), index=True, nullable=True)
    officer_name = Column(String(255), nullable=True)
    
    status = Column(String(50), nullable=False, index=True)
    # Statuses: "VERIFIED", "LIKELY AUTHENTIC", "SUSPICIOUS / LIKELY ALTERED", "UNABLE TO VERIFY"
    
    screening_score = Column(Float, default=0.0)
    template_match_score = Column(Float, default=0.0)
    ocr_consistency_score = Column(Float, default=0.0)
    qr_consistency_score = Column(Float, default=0.0)
    required_fields_score = Column(Float, default=0.0)
    image_quality_score = Column(Float, default=0.0)
    integrity_score = Column(Float, default=0.0)
    
    authorized_verification_status = Column(String(50), default="NOT AVAILABLE")
    # "VERIFIED", "NOT AVAILABLE", "FAILED"
    authorized_provider_name = Column(String(100), nullable=True)
    
    breakdown_json = Column(Text, nullable=True)
    validation_notes_json = Column(Text, nullable=True)
    flagged_issues_json = Column(Text, nullable=True)
    data_comparison_json = Column(Text, nullable=True)
    extracted_fields_json = Column(Text, nullable=True)
    qr_data_json = Column(Text, nullable=True)
    text_boxes_json = Column(Text, nullable=True)
    qr_box_json = Column(Text, nullable=True)
    overlay_image_path = Column(String(500), nullable=True)
    
    manual_review_needed = Column(Boolean, default=False)
    officer_review_decision = Column(String(50), nullable=True)  # APPROVED, FLAGGED, OVERRIDDEN
    officer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
