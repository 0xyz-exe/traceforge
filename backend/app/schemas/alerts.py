from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid

# Alert Rules
class AlertRuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    service: Optional[str] = None
    condition_type: str = Field(pattern="^(metric_threshold|error_rate|missing_telemetry)$")
    metric_name: Optional[str] = None
    threshold: Optional[float] = None
    comparison: Optional[str] = Field(None, pattern="^(gt|lt|gte|lte|eq)$")
    aggregation: Optional[str] = Field(None, pattern="^(avg|sum|min|max|count|p50|p95|p99)$")
    window_seconds: int = Field(300, ge=60, le=3600)
    severity: str = Field(pattern="^(warning|critical)$")
    cooldown_seconds: int = Field(300, ge=60, le=7200)

class AlertRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    threshold: Optional[float] = None
    window_seconds: Optional[int] = Field(None, ge=60, le=3600)
    cooldown_seconds: Optional[int] = Field(None, ge=60, le=7200)

class AlertRuleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    service: Optional[str]
    condition_type: str
    metric_name: Optional[str]
    threshold: Optional[float]
    comparison: Optional[str]
    aggregation: Optional[str]
    window_seconds: int
    severity: str
    enabled: bool
    cooldown_seconds: int
    created_at: datetime

class AlertRulesListResponse(BaseModel):
    rules: List[AlertRuleResponse]
    total: int

# Alert Events
class AlertEventResponse(BaseModel):
    id: str
    alert_rule_id: str
    rule_name: str
    state: str
    severity: str
    message: str
    details: dict
    fired_at: datetime
    resolved_at: Optional[datetime]

class AlertEventsListResponse(BaseModel):
    events: List[AlertEventResponse]
    total: int
    limit: int

# Incidents
class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    severity: str = Field(pattern="^(warning|critical)$")
    alert_event_id: Optional[str] = None

class IncidentUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(open|acknowledged|resolved)$")
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None

class IncidentTimelineEntry(BaseModel):
    id: str
    event_type: str
    message: str
    created_by: Optional[str]
    created_at: datetime

class IncidentResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    severity: str
    status: str
    assigned_to: Optional[str]
    created_by: Optional[str]
    started_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    metadata: dict
    timeline: List[IncidentTimelineEntry]

class IncidentsListResponse(BaseModel):
    incidents: List[IncidentResponse]
    total: int
    limit: int
