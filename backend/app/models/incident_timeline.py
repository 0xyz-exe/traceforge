from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
import uuid
from ..database import Base, GUID

class IncidentTimeline(Base):
    __tablename__ = "incident_timeline"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    incident_id = Column(GUID(), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False)  # created, acknowledged, updated, resolved, comment
    message = Column(Text, nullable=False)
    created_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
