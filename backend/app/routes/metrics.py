from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from ..database import get_db
from ..schemas.telemetry import MetricQueryResponse, MetricDataPoint
from ..dependencies import get_workspace_from_user
from ..services.metrics_store import metrics_store

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/query", response_model=MetricQueryResponse)
def query_metrics(
    service: str = Query(...),
    metric: str = Query(...),
    aggregation: str = Query(..., regex="^(sum|avg|min|max|count|p50|p95|p99)$"),
    start: datetime = Query(...),
    end: datetime = Query(...),
    interval: int = Query(60, ge=1, le=3600),
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    # Query raw data points
    data_points = metrics_store.query(
        workspace_id=str(workspace_id),
        service=service,
        metric=metric,
        start=start,
        end=end
    )
    
    # Aggregate
    aggregated = metrics_store.aggregate(data_points, aggregation, interval)
    
    # Format response
    response_points = [
        MetricDataPoint(timestamp=ts, value=val)
        for ts, val in aggregated
    ]
    
    return MetricQueryResponse(
        metric=metric,
        aggregation=aggregation,
        data_points=response_points,
        unit=None  # Future: extract from metric name
    )
