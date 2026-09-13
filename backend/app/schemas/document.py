from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class QualityCheckDetail(BaseModel):
    name: str
    status: str  # PASS, FAIL, WARN
    score: float
    threshold: float
    description: str

class QualityAnalysisResponse(BaseModel):
    acceptable: bool
    summary: str
    blur_score: float
    brightness: float
    contrast: float
    width: int
    height: int
    aspect_ratio: float
    reasons: List[str]
    checks: Dict[str, Any]

class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    file_path: str
    normalized_path: Optional[str]
    thumbnail_path: Optional[str]
    file_type: str
    document_type: str
    uploaded_by_user_id: Optional[str]
    status: str
    created_at: datetime
    quality: Optional[QualityAnalysisResponse] = None

    class Config:
        from_attributes = True
