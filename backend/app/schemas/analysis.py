from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.analysis import AnalysisStatus


class AnalysisCreate(BaseModel):
    repository_id: int


class AnalysisMetrics(BaseModel):
    maintainability_score: float
    reliability_score: float
    scalability_score: float
    security_score: float
    overall_score: float


class AnalysisResponse(BaseModel):
    id: int
    repository_id: int
    status: AnalysisStatus
    maintainability_score: Optional[float]
    reliability_score: Optional[float]
    scalability_score: Optional[float]
    security_score: Optional[float]
    overall_score: Optional[float]
    code_metrics: Optional[Dict[str, Any]]
    architecture_patterns: Optional[Dict[str, Any]]
    dependencies: Optional[Dict[str, Any]]
    issues: Optional[List[Dict[str, Any]]]
    suggestions: Optional[str]
    detailed_report: Optional[Dict[str, Any]]
    analysis_duration: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
