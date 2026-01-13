"""
Intervention model.
"""
from sqlalchemy import Column, String, Integer, Date, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Intervention(Base):
    """Intervention model."""
    __tablename__ = "interventions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # supplement, diet, exercise, sleep, stress, other
    dosage = Column(Text)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, index=True)
    baseline_days = Column(Integer, default=14)
    status = Column(String(20), default="active")  # active, completed, abandoned
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    analysis_results = relationship("AnalysisResult", back_populates="intervention", cascade="all, delete-orphan")
