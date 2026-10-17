from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from ..database import get_db
from ..models import Service
from ..schemas.base import ServiceCreate, ServiceResponse, ServiceListResponse
from ..dependencies import get_workspace_from_user

router = APIRouter(prefix="/services", tags=["services"])

def _compute_health_status(last_telemetry_at: datetime | None) -> str:
    if not last_telemetry_at:
        return "unknown"
    age = datetime.utcnow() - last_telemetry_at.replace(tzinfo=None)
    if age < timedelta(minutes=5):
        return "healthy"
    elif age < timedelta(hours=1):
        return "stale"
    else:
        return "down"

@router.get("", response_model=ServiceListResponse)
def list_services(
    environment: str | None = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    query = db.query(Service).filter(Service.workspace_id == workspace_id)
    
    if environment:
        query = query.filter(Service.environment == environment)
    
    total = query.count()
    services = query.order_by(Service.created_at.desc()).limit(limit).offset(offset).all()
    
    # Add health status
    service_responses = []
    for svc in services:
        svc_dict = {
            "id": svc.id,
            "name": svc.name,
            "environment": svc.environment,
            "version": svc.version,
            "last_telemetry_at": svc.last_telemetry_at,
            "health_status": _compute_health_status(svc.last_telemetry_at),
            "created_at": svc.created_at
        }
        service_responses.append(ServiceResponse(**svc_dict))
    
    return ServiceListResponse(
        services=service_responses,
        total=total,
        limit=limit,
        offset=offset
    )

@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    service_data: ServiceCreate,
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    # Check for duplicate
    existing = db.query(Service).filter(
        Service.workspace_id == workspace_id,
        Service.name == service_data.name,
        Service.environment == service_data.environment
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service already exists for this environment"
        )
    
    service = Service(
        workspace_id=workspace_id,
        name=service_data.name,
        environment=service_data.environment,
        version=service_data.version
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    return ServiceResponse(
        **{
            "id": service.id,
            "name": service.name,
            "environment": service.environment,
            "version": service.version,
            "last_telemetry_at": service.last_telemetry_at,
            "health_status": _compute_health_status(service.last_telemetry_at),
            "created_at": service.created_at
        }
    )

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: uuid.UUID,
    workspace_id: uuid.UUID = Depends(get_workspace_from_user),
    db: Session = Depends(get_db)
):
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.workspace_id == workspace_id
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return ServiceResponse(
        **{
            "id": service.id,
            "name": service.name,
            "environment": service.environment,
            "version": service.version,
            "last_telemetry_at": service.last_telemetry_at,
            "health_status": _compute_health_status(service.last_telemetry_at),
            "created_at": service.created_at
        }
    )
