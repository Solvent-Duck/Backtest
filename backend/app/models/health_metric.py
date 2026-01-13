"""
Health metric model (TimescaleDB hypertable)
"""
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.dialects.postgresql import TIMESTAMP
import uuid

from app.core.database import Base


class HealthMetric(Base):
    """Health metric model - will be converted to TimescaleDB hypertable"""
    __tablename__ = "health_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    date = Column(Date, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    source_device = Column(String(100))
    metadata = Column(JSONB)
    
    # Composite primary key for TimescaleDB
    __table_args__ = (
        Index("idx_health_metrics_user_type", "user_id", "metric_type"),
        Index("idx_health_metrics_timestamp", "timestamp"),
    )
