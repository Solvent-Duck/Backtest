"""
Data import schemas.
"""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class DataImportResponse(BaseModel):
    """Schema for data import response."""
    id: UUID
    user_id: UUID
    filename: Optional[str]
    file_size_mb: Optional[float]
    records_imported: Optional[int]
    status: str
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DataImportStatus(BaseModel):
    """Schema for data import status."""
    import_id: UUID
    status: str
    progress: Optional[float] = None  # 0-100
    records_imported: Optional[int] = None
    error_message: Optional[str] = None
