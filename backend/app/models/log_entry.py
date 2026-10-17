from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.sql import func
import uuid
from ..database import Base, GUID, JSONType

class LogEntry(Base):
    __tablename__ = "log_entries"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(GUID(), ForeignKey("services.id", ondelete="SET NULL"))
    timestamp = Column(DateTime(timezone=True), nullable=False)
    severity = Column(String(20), nullable=False)  # DEBUG, INFO, WARN, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    trace_id = Column(String(32))  # Hex trace ID for correlation
    span_id = Column(String(16))   # Hex span ID
    attributes = Column(JSONType)     # Flexible structured data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_logs_workspace_time', 'workspace_id', 'timestamp'),
        Index('idx_logs_service', 'service_id'),
        Index('idx_logs_severity', 'severity'),
        Index('idx_logs_trace', 'trace_id'),
        Index('idx_logs_attributes', 'attributes'),
    )
