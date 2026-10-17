from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..database import Base

class Trace(Base):
    __tablename__ = "traces"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    trace_id = Column(String(32), unique=True, nullable=False)  # Hex trace ID
    root_service_id = Column(UUID(as_uuid=True), ForeignKey("services.id", ondelete="SET NULL"))
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)  # Calculated
    status = Column(String(20))    # ok, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
