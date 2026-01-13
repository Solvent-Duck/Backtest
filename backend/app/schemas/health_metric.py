"""
Health metric Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class HealthMetricResponse(BaseModel):
    """Schema for health metric response"""
    id: UUID
    metric_type: str
    value: float
    unit: Optional[str]
    date: str
    timestamp: datetime
    source_device: Optional[str]
    
    class Config:
        from_attributes = True


class DailyMetricResponse(BaseModel):
    """Schema for daily aggregated metric"""
    day: str
    metric_type: str
    avg_value: float
    stddev_value: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    sample_size: int
