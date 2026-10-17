from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.sql import func
import uuid
from ..database import Base, GUID, JSONType

class AlertEvent(Base):
    __tablename__ = "alert_events"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    alert_rule_id = Column(GUID(), ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False)
    state = Column(String(20), nullable=False)  # firing, resolved
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSONType)  # value, threshold, metric details
    fired_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_alert_events_workspace_time', 'workspace_id', 'fired_at'),
        Index('idx_alert_events_rule', 'alert_rule_id'),
        Index('idx_alert_events_state', 'state'),
    )
