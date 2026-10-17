from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from ..database import get_db
from ..models import AlertRule, AlertEvent, Incident, IncidentTimeline, User
from ..schemas.alerts import (
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse, AlertRulesListResponse,
    AlertEventResponse, AlertEventsListResponse,
    IncidentCreate, IncidentUpdate, IncidentResponse, IncidentsListResponse, IncidentTimelineEntry
)
from ..dependencies import get_workspace_from_user, get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/rules", response_model=AlertRulesListResponse)
def list_alert_rules(
    enabled: bool | None = None,
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    query = db.query(AlertRule).filter(AlertRule.workspace_id == workspace_id)
    
    if enabled is not None:
        query = query.filter(AlertRule.enabled == enabled)
    
    rules = query.order_by(AlertRule.created_at.desc()).all()
    
    return AlertRulesListResponse(
        rules=[
            AlertRuleResponse(
                id=str(rule.id),
                name=rule.name,
                description=rule.description,
                service=rule.service,
                condition_type=rule.condition_type,
                metric_name=rule.metric_name,
                threshold=rule.threshold,
                comparison=rule.comparison,
                aggregation=rule.aggregation,
                window_seconds=rule.window_seconds,
                severity=rule.severity,
                enabled=rule.enabled,
                cooldown_seconds=rule.cooldown_seconds,
                created_at=rule.created_at
            )
            for rule in rules
        ],
        total=len(rules)
    )

@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
def create_alert_rule(
    data: AlertRuleCreate,
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    # Validate condition-specific fields
    if data.condition_type == "metric_threshold":
        if not data.metric_name or data.threshold is None or not data.comparison or not data.aggregation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="metric_threshold requires metric_name, threshold, comparison, and aggregation"
            )
    
    rule = AlertRule(
        workspace_id=workspace_id,
        name=data.name,
        description=data.description,
        service=data.service,
        condition_type=data.condition_type,
        metric_name=data.metric_name,
        threshold=data.threshold,
        comparison=data.comparison,
        aggregation=data.aggregation,
        window_seconds=data.window_seconds,
        severity=data.severity,
        enabled=True,
        cooldown_seconds=data.cooldown_seconds
    )
    
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return AlertRuleResponse(
        id=str(rule.id),
        name=rule.name,
        description=rule.description,
        service=rule.service,
        condition_type=rule.condition_type,
        metric_name=rule.metric_name,
        threshold=rule.threshold,
        comparison=rule.comparison,
        aggregation=rule.aggregation,
        window_seconds=rule.window_seconds,
        severity=rule.severity,
        enabled=rule.enabled,
        cooldown_seconds=rule.cooldown_seconds,
        created_at=rule.created_at
    )

@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
def get_alert_rule(
    rule_id: uuid.UUID,
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.workspace_id == workspace_id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    return AlertRuleResponse(
        id=str(rule.id),
        name=rule.name,
        description=rule.description,
        service=rule.service,
        condition_type=rule.condition_type,
        metric_name=rule.metric_name,
        threshold=rule.threshold,
        comparison=rule.comparison,
        aggregation=rule.aggregation,
        window_seconds=rule.window_seconds,
        severity=rule.severity,
        enabled=rule.enabled,
        cooldown_seconds=rule.cooldown_seconds,
        created_at=rule.created_at
    )

@router.patch("/rules/{rule_id}", response_model=AlertRuleResponse)
def update_alert_rule(
    rule_id: uuid.UUID,
    data: AlertRuleUpdate,
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.workspace_id == workspace_id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    if data.name is not None:
        rule.name = data.name
    if data.description is not None:
        rule.description = data.description
    if data.enabled is not None:
        rule.enabled = data.enabled
    if data.threshold is not None:
        rule.threshold = data.threshold
    if data.window_seconds is not None:
        rule.window_seconds = data.window_seconds
    if data.cooldown_seconds is not None:
        rule.cooldown_seconds = data.cooldown_seconds
    
    rule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rule)
    
    return AlertRuleResponse(
        id=str(rule.id),
        name=rule.name,
        description=rule.description,
        service=rule.service,
        condition_type=rule.condition_type,
        metric_name=rule.metric_name,
        threshold=rule.threshold,
        comparison=rule.comparison,
        aggregation=rule.aggregation,
        window_seconds=rule.window_seconds,
        severity=rule.severity,
        enabled=rule.enabled,
        cooldown_seconds=rule.cooldown_seconds,
        created_at=rule.created_at
    )

@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert_rule(
    rule_id: uuid.UUID,
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.workspace_id == workspace_id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    db.delete(rule)
    db.commit()
    
    return None

# Alert Events
@router.get("/events", response_model=AlertEventsListResponse)
def list_alert_events(
    state: str | None = Query(None, pattern="^(firing|resolved)$"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    query = db.query(AlertEvent).filter(AlertEvent.workspace_id == workspace_id)
    
    if state:
        query = query.filter(AlertEvent.state == state)
    
    total = query.count()
    events = query.order_by(AlertEvent.fired_at.desc()).limit(limit).offset(offset).all()
    
    event_responses = []
    for event in events:
        rule = db.query(AlertRule).filter(AlertRule.id == event.alert_rule_id).first()
        rule_name = rule.name if rule else "Unknown"
        
        event_responses.append(AlertEventResponse(
            id=str(event.id),
            alert_rule_id=str(event.alert_rule_id),
            rule_name=rule_name,
            state=event.state,
            severity=event.severity,
            message=event.message,
            details=event.details or {},
            fired_at=event.fired_at,
            resolved_at=event.resolved_at
        ))
    
    return AlertEventsListResponse(
        events=event_responses,
        total=total,
        limit=limit
    )

# Incidents
@router.get("/incidents", response_model=IncidentsListResponse)
def list_incidents(
    status_filter: str | None = Query(None, alias="status", pattern="^(open|acknowledged|resolved)$"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    query = db.query(Incident).filter(Incident.workspace_id == workspace_id)
    
    if status_filter:
        query = query.filter(Incident.status == status_filter)
    
    total = query.count()
    incidents = query.order_by(Incident.started_at.desc()).limit(limit).offset(offset).all()
    
    incident_responses = []
    for incident in incidents:
        # Get timeline
        timeline_entries = db.query(IncidentTimeline).filter(
            IncidentTimeline.incident_id == incident.id
        ).order_by(IncidentTimeline.created_at).all()
        
        timeline = [
            IncidentTimelineEntry(
                id=str(entry.id),
                event_type=entry.event_type,
                message=entry.message,
                created_by=str(entry.created_by) if entry.created_by else None,
                created_at=entry.created_at
            )
            for entry in timeline_entries
        ]
        
        incident_responses.append(IncidentResponse(
            id=str(incident.id),
            title=incident.title,
            description=incident.description,
            severity=incident.severity,
            status=incident.status,
            assigned_to=str(incident.assigned_to) if incident.assigned_to else None,
            created_by=str(incident.created_by) if incident.created_by else None,
            started_at=incident.started_at,
            acknowledged_at=incident.acknowledged_at,
            resolved_at=incident.resolved_at,
            resolution_notes=incident.resolution_notes,
            metadata=incident.metadata or {},
            timeline=timeline
        ))
    
    return IncidentsListResponse(
        incidents=incident_responses,
        total=total,
        limit=limit
    )

@router.post("/incidents", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    data: IncidentCreate,
    current_user = Depends(get_current_user),
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    incident = Incident(
        workspace_id=workspace_id,
        title=data.title,
        description=data.description,
        severity=data.severity,
        status="open",
        created_by=current_user.id,
        started_at=datetime.utcnow(),
        metadata={"alert_event_id": data.alert_event_id} if data.alert_event_id else {}
    )
    
    db.add(incident)
    db.flush()
    
    # Add timeline entry
    timeline_entry = IncidentTimeline(
        incident_id=incident.id,
        event_type="created",
        message=f"Incident created: {data.title}",
        created_by=current_user.id
    )
    db.add(timeline_entry)
    db.commit()
    db.refresh(incident)
    
    return IncidentResponse(
        id=str(incident.id),
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
        assigned_to=None,
        created_by=str(current_user.id),
        started_at=incident.started_at,
        acknowledged_at=None,
        resolved_at=None,
        resolution_notes=None,
        metadata=incident.metadata or {},
        timeline=[
            IncidentTimelineEntry(
                id=str(timeline_entry.id),
                event_type=timeline_entry.event_type,
                message=timeline_entry.message,
                created_by=str(current_user.id),
                created_at=timeline_entry.created_at
            )
        ]
    )

@router.patch("/incidents/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: uuid.UUID,
    data: IncidentUpdate,
    current_user = Depends(get_current_user),
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.workspace_id == workspace_id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Track changes for timeline
    timeline_messages = []
    
    if data.status and data.status != incident.status:
        old_status = incident.status
        incident.status = data.status
        timeline_messages.append(f"Status changed from {old_status} to {data.status}")
        
        if data.status == "acknowledged":
            incident.acknowledged_at = datetime.utcnow()
        elif data.status == "resolved":
            incident.resolved_at = datetime.utcnow()
    
    if data.assigned_to:
        incident.assigned_to = uuid.UUID(data.assigned_to)
        timeline_messages.append(f"Assigned to user {data.assigned_to}")
    
    if data.resolution_notes:
        incident.resolution_notes = data.resolution_notes
        timeline_messages.append("Resolution notes added")
    
    incident.updated_at = datetime.utcnow()
    
    # Add timeline entries
    for msg in timeline_messages:
        entry = IncidentTimeline(
            incident_id=incident.id,
            event_type="updated",
            message=msg,
            created_by=current_user.id
        )
        db.add(entry)
    
    db.commit()
    db.refresh(incident)
    
    # Get full timeline
    timeline_entries = db.query(IncidentTimeline).filter(
        IncidentTimeline.incident_id == incident.id
    ).order_by(IncidentTimeline.created_at).all()
    
    timeline = [
        IncidentTimelineEntry(
            id=str(entry.id),
            event_type=entry.event_type,
            message=entry.message,
            created_by=str(entry.created_by) if entry.created_by else None,
            created_at=entry.created_at
        )
        for entry in timeline_entries
    ]
    
    return IncidentResponse(
        id=str(incident.id),
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
        assigned_to=str(incident.assigned_to) if incident.assigned_to else None,
        created_by=str(incident.created_by) if incident.created_by else None,
        started_at=incident.started_at,
        acknowledged_at=incident.acknowledged_at,
        resolved_at=incident.resolved_at,
        resolution_notes=incident.resolution_notes,
        metadata=incident.metadata or {},
        timeline=timeline
    )
