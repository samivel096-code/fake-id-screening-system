from pydantic import BaseModel
from typing import List, Dict, Any

class StatCard(BaseModel):
    title: str
    count: int
    change: Optional[str] = None
    color: str

class ChartPoint(BaseModel):
    label: str
    value: float

class DashboardStatistics(BaseModel):
    total_documents: int
    processing: int
    verified: int
    likely_authentic: int
    suspicious: int
    unable_to_verify: int
    needs_review: int
    
    daily_processing: List[Dict[str, Any]]
    status_distribution: List[Dict[str, Any]]
    document_type_distribution: List[Dict[str, Any]]
    qr_verification_stats: Dict[str, Any]
    recent_verifications: List[Dict[str, Any]]
