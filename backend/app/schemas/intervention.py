"""
Intervention Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from uuid import UUID


class InterventionBase(BaseModel):
    """Base intervention schema"""
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., pattern="^(supplement|diet|exercise|sleep|stress|other)$")
    dosage: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    baseline_days: int = Field(default=14, ge=7, le=90)
    notes: Optional[str] = None


class InterventionCreate(InterventionBase):
    """Schema for creating an intervention"""
    pass


class InterventionUpdate(BaseModel):
    """Schema for updating an intervention"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, pattern="^(supplement|diet|exercise|sleep|stress|other)$")
    dosage: Optional[str] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|abandoned)$")
    notes: Optional[str] = None


class InterventionResponse(InterventionBase):
    """Schema for intervention response"""
    id: UUID
    user_id: UUID
    status: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
