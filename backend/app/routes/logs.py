from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
import uuid
from ..database import get_db
from ..models import Service, LogEntry as LogEntryModel
from ..schemas.telemetry import LogsSearchResponse, LogEntryResponse
from ..dependencies import get_workspace_from_user

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("", response_model=LogsSearchResponse)
def search_logs(
    service: str | None = None,
    severity: str | None = None,
    start: datetime = Query(...),
    end: datetime = Query(...),
    search: str | None = None,
    trace_id: str | None = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    # Build query
    query = db.query(LogEntryModel).filter(
        LogEntryModel.workspace_id == workspace_id,
        LogEntryModel.timestamp >= start,
        LogEntryModel.timestamp <= end
    )
    
    if service:
        # Find service
        svc = db.query(Service).filter(
            Service.workspace_id == workspace_id,
            Service.name == service
        ).first()
        if svc:
            query = query.filter(LogEntryModel.service_id == svc.id)
    
    if severity:
        query = query.filter(LogEntryModel.severity == severity)
    
    if trace_id:
        query = query.filter(LogEntryModel.trace_id == trace_id)
    
    if search:
        query = query.filter(LogEntryModel.message.ilike(f"%{search}%"))
    
    total = query.count()
    logs = query.order_by(LogEntryModel.timestamp.desc()).limit(limit).offset(offset).all()
    
    # Build response
    log_responses = []
    for log in logs:
        service_name = "unknown"
        if log.service_id:
            svc = db.query(Service).filter(Service.id == log.service_id).first()
            if svc:
                service_name = svc.name
        
        log_responses.append(LogEntryResponse(
            id=str(log.id),
            timestamp=log.timestamp,
            severity=log.severity,
            service=service_name,
            message=log.message,
            trace_id=log.trace_id,
            span_id=log.span_id,
            attributes=log.attributes or {}
        ))
    
    return LogsSearchResponse(
        logs=log_responses,
        total=total,
        limit=limit,
        offset=offset
    )
