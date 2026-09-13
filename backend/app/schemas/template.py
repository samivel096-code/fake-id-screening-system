from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class TemplateField(BaseModel):
    name: str
    label: str
    required: bool = True
    data_type: str = "string"  # string, date, number, id
    pattern: Optional[str] = None
    expected_region: Optional[Dict[str, float]] = None  # relative [x, y, w, h] in 0.0-1.0

class TemplateProfile(BaseModel):
    document_type: str
    aspect_ratio: float
    expected_width: int
    expected_height: int
    required_sections: List[str]
    expected_fields: List[TemplateField]
    has_qr_code: bool = True
    expected_qr_region: Optional[Dict[str, float]] = None
    expected_symbols: List[Dict[str, Any]] = []
    expected_photo_region: Optional[Dict[str, float]] = None
    typography_characteristics: Dict[str, Any] = {}
    background_characteristics: Dict[str, Any] = {}
    issuing_org: Optional[str] = None
    version: str = "v1.0"

class TemplateCreate(BaseModel):
    document_type: str
    template_name: str
    version: str = "v1.0"
    issuing_org: Optional[str] = None
    is_default: bool = False
    profile: TemplateProfile

class TemplateResponse(BaseModel):
    id: str
    document_type: str
    template_name: str
    version: str
    issuing_org: Optional[str]
    status: str
    is_default: bool
    aspect_ratio: Optional[float]
    expected_width: Optional[int]
    expected_height: Optional[int]
    sample_image_path: Optional[str]
    profile: Dict[str, Any]
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
