"""
Analysis result model.
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class AnalysisResult(Base):
    """Analysis result model."""
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intervention_id = Column(UUID(as_uuid=True), ForeignKey("interventions.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)
    baseline_avg = Column(Float)
    baseline_stddev = Column(Float)
    intervention_avg = Column(Float)
    intervention_stddev = Column(Float)
    percent_change = Column(Float)
    p_value = Column(Float)
    is_significant = Column(Boolean)
    sample_size_baseline = Column(Integer)
    sample_size_intervention = Column(Integer)
    generated_insight = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    intervention = relationship("Intervention", back_populates="analysis_results")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint("intervention_id", "metric_type", name="uq_intervention_metric"),
    )
