from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from ..database import get_db
from ..models import Service, Trace, Span
from ..schemas.telemetry import TraceResponse, SpanResponse, TracesListResponse
from ..dependencies import get_workspace_from_user

router = APIRouter(prefix="/traces", tags=["traces"])

@router.get("", response_model=TracesListResponse)
def list_traces(
    service: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    min_duration_ms: int | None = None,
    start: datetime = Query(...),
    end: datetime = Query(...),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    # Build query
    query = db.query(Trace).filter(
        Trace.workspace_id == workspace_id,
        Trace.start_time >= start,
        Trace.start_time <= end
    )
    
    if service:
        svc = db.query(Service).filter(
            Service.workspace_id == workspace_id,
            Service.name == service
        ).first()
        if svc:
            query = query.filter(Trace.root_service_id == svc.id)
    
    if status_filter:
        query = query.filter(Trace.status == status_filter)
    
    if min_duration_ms:
        query = query.filter(Trace.duration_ms >= min_duration_ms)
    
    total = query.count()
    traces = query.order_by(Trace.start_time.desc()).limit(limit).offset(offset).all()
    
    # Build response
    trace_list = []
    for trace in traces:
        root_service = "unknown"
        if trace.root_service_id:
            svc = db.query(Service).filter(Service.id == trace.root_service_id).first()
            if svc:
                root_service = svc.name
        
        span_count = db.query(Span).filter(Span.trace_id == trace.trace_id).count()
        
        trace_list.append({
            "trace_id": trace.trace_id,
            "root_service": root_service,
            "start_time": trace.start_time.isoformat(),
            "duration_ms": trace.duration_ms,
            "status": trace.status,
            "span_count": span_count
        })
    
    return TracesListResponse(
        traces=trace_list,
        total=total,
        limit=limit
    )

@router.get("/{trace_id}", response_model=TraceResponse)
def get_trace(
    trace_id: str,
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    # Find trace
    trace = db.query(Trace).filter(
        Trace.trace_id == trace_id,
        Trace.workspace_id == workspace_id
    ).first()
    
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found"
        )
    
    # Get all spans
    spans = db.query(Span).filter(Span.trace_id == trace_id).all()
    
    # Build span responses
    span_responses = []
    for span in spans:
        service_name = "unknown"
        if span.service_id:
            svc = db.query(Service).filter(Service.id == span.service_id).first()
            if svc:
                service_name = svc.name
        
        span_responses.append(SpanResponse(
            span_id=span.span_id,
            parent_span_id=span.parent_span_id,
            service=service_name,
            operation_name=span.operation_name,
            start_time=span.start_time,
            end_time=span.end_time,
            duration_ms=span.duration_ms,
            status=span.status,
            attributes=span.attributes or {},
            events=span.events or []
        ))
    
    # Get root service
    root_service = "unknown"
    if trace.root_service_id:
        svc = db.query(Service).filter(Service.id == trace.root_service_id).first()
        if svc:
            root_service = svc.name
    
    return TraceResponse(
        trace_id=trace.trace_id,
        root_service=root_service,
        start_time=trace.start_time,
        duration_ms=trace.duration_ms,
        status=trace.status,
        spans=span_responses
    )
