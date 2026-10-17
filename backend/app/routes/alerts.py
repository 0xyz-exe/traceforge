from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from ..database import get_db
from ..models import AlertRule
from ..schemas.alerts import AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse, AlertRulesListResponse
from ..dependencies import get_workspace_from_user

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
