from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from ..database import get_db
from ..models import Service
from ..schemas.telemetry import MetricsIngest, IngestResponse, MetricQueryResponse, MetricDataPoint
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
        Service.environment == "production"  # Default for now
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
