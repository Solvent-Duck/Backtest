"""
Data import model
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class DataImport(Base):
    """Data import tracking model"""
    __tablename__ = "data_imports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255))
    file_size_mb = Column(Float)
    records_imported = Column(Integer)
    status = Column(String(20), index=True)  # pending, processing, completed, failed
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
