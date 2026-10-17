from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from ..database import Base

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    service = Column(String(255))  # NULL = all services
    condition_type = Column(String(50), nullable=False)  # metric_threshold, error_rate, missing_telemetry
    metric_name = Column(String(255))  # For metric_threshold
    threshold = Column(Float)
    comparison = Column(String(10))  # gt, lt, gte, lte, eq
    aggregation = Column(String(50))  # avg, sum, p50, p95, p99
    window_seconds = Column(Integer, default=300)  # Evaluation window
    severity = Column(String(20), nullable=False)  # warning, critical
    enabled = Column(Boolean, default=True)
    cooldown_seconds = Column(Integer, default=300)  # Min time between alerts
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
