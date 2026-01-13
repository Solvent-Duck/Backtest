"""
Health metric schemas.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class HealthMetricResponse(BaseModel):
    """Schema for health metric response."""
    id: UUID
    user_id: UUID
    metric_type: str
    value: float
    unit: Optional[str]
    date: date
    timestamp: datetime
    source_device: Optional[str]
    
    class Config:
        from_attributes = True


class DailyMetricAggregate(BaseModel):
    """Schema for daily metric aggregates."""
    day: date
    metric_type: str
    avg_value: float
    stddev_value: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    sample_size: int
