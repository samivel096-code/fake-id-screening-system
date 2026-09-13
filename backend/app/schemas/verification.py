from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class VerificationRunRequest(BaseModel):
    document_id: str
    document_type: str
    template_id: Optional[str] = None
    allow_demo_authoritative_provider: bool = False

class DataComparisonRow(BaseModel):
    field: str
    extracted_value: str
    reference_or_qr_value: str
    result: str  # MATCH, PARTIAL MATCH, MISMATCH, NOT FOUND, NOT AVAILABLE
    details: Optional[str] = None

class FlaggedIssue(BaseModel):
    id: str
    type: str  # TEMPLATE_MISMATCH, QR_MISMATCH, INTEGRITY_ANOMALY, MISSING_FIELD, QUALITY_WARNING
    severity: str  # HIGH, MEDIUM, LOW
    title: str
    description: str
    region: Optional[Dict[str, float]] = None  # {x, y, w, h} normalized 0-1 or pixel coords

class ScoreBreakdown(BaseModel):
    template_match: float
    ocr_consistency: float
    qr_consistency: float
    required_fields: float
    image_quality: float
    integrity_screening: float
    authorized_verification: str  # "VERIFIED", "NOT AVAILABLE", "FAILED"
    
    # Nested template breakdown
    template_details: Optional[Dict[str, float]] = None

class VerificationResponse(BaseModel):
    id: str
    document_id: str
    document_type: str
    template_id: Optional[str]
    template_name: Optional[str]
    
    officer_id: Optional[str]
    officer_name: Optional[str]
    
    status: str  # "VERIFIED", "LIKELY AUTHENTIC", "SUSPICIOUS / LIKELY ALTERED", "UNABLE TO VERIFY"
    screening_score: float
    
    breakdown: ScoreBreakdown
    validation_notes: List[str]
    recommendation: str
    legal_disclaimer: str
    
    flagged_issues: List[FlaggedIssue]
    data_comparison: List[DataComparisonRow]
    extracted_fields: Dict[str, Any]
    
    qr_analysis: Dict[str, Any]
    image_quality: Dict[str, Any]
    integrity_screening: Dict[str, Any]
    
    normalized_image_url: Optional[str]
    overlay_image_url: Optional[str]
    sample_image_url: Optional[str]
    
    text_boxes: List[Dict[str, Any]] = []
    qr_box: Optional[Dict[str, Any]] = None
    
    manual_review_needed: bool
    officer_review_decision: Optional[str]
    officer_notes: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: datetime

class OfficerReviewRequest(BaseModel):
    decision: str  # "APPROVED", "FLAGGED", "OVERRIDDEN"
    notes: str
    new_status: Optional[str] = None
