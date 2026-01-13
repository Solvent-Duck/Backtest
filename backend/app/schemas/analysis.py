"""
Analysis result Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class AnalysisResultResponse(BaseModel):
    """Schema for analysis result response"""
    id: UUID
    intervention_id: UUID
    metric_type: str
    baseline_avg: Optional[float]
    baseline_stddev: Optional[float]
    intervention_avg: Optional[float]
    intervention_stddev: Optional[float]
    percent_change: Optional[float]
    p_value: Optional[float]
    is_significant: Optional[bool]
    sample_size_baseline: Optional[int]
    sample_size_intervention: Optional[int]
    generated_insight: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class InterventionAnalysisResponse(BaseModel):
    """Schema for complete intervention analysis"""
    intervention_id: UUID
    results: list[AnalysisResultResponse]
    summary: dict
