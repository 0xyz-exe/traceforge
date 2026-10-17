from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func
import uuid
from ..database import Base, GUID, JSONType

class Span(Base):
    __tablename__ = "spans"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    trace_id = Column(String(32), nullable=False)
    span_id = Column(String(16), nullable=False)
    parent_span_id = Column(String(16))  # NULL for root span
    service_id = Column(GUID(), ForeignKey("services.id", ondelete="SET NULL"))
    operation_name = Column(String(255), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)
    status = Column(String(20))  # ok, error
    attributes = Column(JSONType)
    events = Column(JSONType)  # Array of span events
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('trace_id', 'span_id', name='uq_span_trace_span'),
        Index('idx_spans_trace', 'trace_id'),
        Index('idx_spans_parent', 'parent_span_id'),
        Index('idx_spans_workspace_time', 'workspace_id', 'start_time'),
        Index('idx_spans_service', 'service_id'),
    )
