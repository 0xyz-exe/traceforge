from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from ..database import get_db
from ..models import Service, LogEntry, Trace, Span
from ..schemas.telemetry import (
    MetricsIngest, IngestResponse, LogsIngest, TracesIngest
)
from ..dependencies import get_workspace_from_api_key
from ..services.metrics_store import metrics_store

router = APIRouter(prefix="/ingest", tags=["ingestion"])

@router.post("/metrics", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_metrics(
    data: MetricsIngest,
    workspace_id: uuid.UUID = Depends(get_workspace_from_api_key),
    db: Session = Depends(get_db)
):
    # Find or create service
    service = db.query(Service).filter(
        Service.workspace_id == workspace_id,
        Service.name == data.service,
        Service.environment == "production"
    ).first()
    
    if not service:
        service = Service(
            workspace_id=workspace_id,
            name=data.service,
            environment="production"
        )
        db.add(service)
        db.commit()
    
    # Update last telemetry timestamp
    service.last_telemetry_at = datetime.utcnow()
    db.commit()
    
    # Ingest metrics
    accepted = 0
    rejected = 0
    
    for metric in data.metrics:
        success = metrics_store.ingest(
            workspace_id=str(workspace_id),
            service=data.service,
            metric=metric.name,
            value=metric.value,
            timestamp=metric.timestamp,
            labels=metric.labels
        )
        if success:
            accepted += 1
        else:
            rejected += 1
    
    return IngestResponse(accepted=accepted, rejected=rejected)

@router.post("/logs", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_logs(
    data: LogsIngest,
    workspace_id: uuid.UUID = Depends(get_workspace_from_api_key),
    db: Session = Depends(get_db)
):
    # Find or create service
    service = db.query(Service).filter(
        Service.workspace_id == workspace_id,
        Service.name == data.service,
        Service.environment == "production"
    ).first()
    
    if not service:
        service = Service(
            workspace_id=workspace_id,
            name=data.service,
            environment="production"
        )
        db.add(service)
        db.flush()
    
    # Update last telemetry timestamp
    service.last_telemetry_at = datetime.utcnow()
    
    # Ingest logs
    accepted = 0
    rejected = 0
    
    for log in data.logs:
        try:
            log_entry = LogEntry(
                workspace_id=workspace_id,
                service_id=service.id,
                timestamp=log.timestamp,
                severity=log.severity,
                message=log.message[:10000],  # Truncate
                trace_id=log.trace_id,
                span_id=log.span_id,
                attributes=log.attributes
            )
            db.add(log_entry)
            accepted += 1
        except Exception:
            rejected += 1
    
    db.commit()
    return IngestResponse(accepted=accepted, rejected=rejected)

@router.post("/traces", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_traces(
    data: TracesIngest,
    workspace_id: uuid.UUID = Depends(get_workspace_from_api_key),
    db: Session = Depends(get_db)
):
    # Find or create service
    service = db.query(Service).filter(
        Service.workspace_id == workspace_id,
        Service.name == data.service,
        Service.environment == "production"
    ).first()
    
    if not service:
        service = Service(
            workspace_id=workspace_id,
            name=data.service,
            environment="production"
        )
        db.add(service)
        db.flush()
    
    # Update last telemetry timestamp
    service.last_telemetry_at = datetime.utcnow()
    
    # Ingest traces
    accepted = 0
    rejected = 0
    
    for trace_data in data.traces:
        try:
            # Find earliest and latest span times
            start_times = [s.start_time for s in trace_data.spans]
            end_times = [s.end_time for s in trace_data.spans if s.end_time]
            
            start_time = min(start_times)
            end_time = max(end_times) if end_times else None
            duration_ms = None
            if end_time:
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Determine status (error if any span has error)
            statuses = [s.status for s in trace_data.spans]
            trace_status = "error" if "error" in statuses else "ok"
            
            # Create trace
            trace = Trace(
                workspace_id=workspace_id,
                trace_id=trace_data.trace_id,
                root_service_id=service.id,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                status=trace_status
            )
            db.add(trace)
            db.flush()
            
            # Create spans
            for span_data in trace_data.spans:
                span_duration_ms = None
                if span_data.end_time:
                    span_duration_ms = int((span_data.end_time - span_data.start_time).total_seconds() * 1000)
                
                span = Span(
                    workspace_id=workspace_id,
                    trace_id=trace_data.trace_id,
                    span_id=span_data.span_id,
                    parent_span_id=span_data.parent_span_id,
                    service_id=service.id,
                    operation_name=span_data.operation_name,
                    start_time=span_data.start_time,
                    end_time=span_data.end_time,
                    duration_ms=span_duration_ms,
                    status=span_data.status,
                    attributes=span_data.attributes,
                    events=span_data.events
                )
                db.add(span)
            
            accepted += 1
        except Exception:
            rejected += 1
    
    db.commit()
    return IngestResponse(accepted=accepted, rejected=rejected)
