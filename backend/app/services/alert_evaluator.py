"""
Alert evaluation engine - runs in background to check alert rules
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..models import AlertRule, AlertEvent
from ..services.metrics_store import metrics_store
import logging

logger = logging.getLogger(__name__)

class AlertEvaluator:
    def __init__(self, db: Session):
        self.db = db
        self.last_alert_times = {}  # rule_id -> last_fired_at for cooldown
    
    def evaluate_all_rules(self):
        """Evaluate all enabled alert rules"""
        rules = self.db.query(AlertRule).filter(AlertRule.enabled == True).all()
        
        for rule in rules:
            try:
                self._evaluate_rule(rule)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.id}: {e}")
    
    def _evaluate_rule(self, rule: AlertRule):
        """Evaluate a single alert rule"""
        if rule.condition_type == "metric_threshold":
            self._evaluate_metric_threshold(rule)
        # Add other condition types here
    
    def _evaluate_metric_threshold(self, rule: AlertRule):
        """Evaluate metric threshold condition"""
        if not rule.metric_name or rule.threshold is None:
            return
        
        # Check cooldown
        rule_key = str(rule.id)
        if rule_key in self.last_alert_times:
            last_fired = self.last_alert_times[rule_key]
            if (datetime.utcnow() - last_fired).total_seconds() < rule.cooldown_seconds:
                return  # Still in cooldown
        
        # Query metric data
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=rule.window_seconds)
        
        try:
            data = metrics_store.query(
                workspace_id=str(rule.workspace_id),
                service=rule.service or "*",
                metric=rule.metric_name,
                start_time=start_time,
                end_time=end_time
            )
            
            if not data:
                return  # No data to evaluate
            
            # Aggregate data
            aggregated = metrics_store.aggregate(
                data,
                interval=rule.window_seconds,
                aggregation=rule.aggregation or "avg"
            )
            
            if not aggregated:
                return
            
            # Get latest value
            latest = aggregated[-1]
            value = latest[1]
            
            # Compare against threshold
            triggered = self._check_threshold(value, rule.threshold, rule.comparison)
            
            if triggered:
                # Create alert event
                self._fire_alert(rule, value)
                self.last_alert_times[rule_key] = datetime.utcnow()
        
        except Exception as e:
            logger.error(f"Error querying metrics for rule {rule.id}: {e}")
    
    def _check_threshold(self, value: float, threshold: float, comparison: str) -> bool:
        """Check if value meets threshold condition"""
        if comparison == "gt":
            return value > threshold
        elif comparison == "gte":
            return value >= threshold
        elif comparison == "lt":
            return value < threshold
        elif comparison == "lte":
            return value <= threshold
        elif comparison == "eq":
            return value == threshold
        return False
    
    def _fire_alert(self, rule: AlertRule, value: float):
        """Create a firing alert event"""
        message = f"{rule.name}: {rule.metric_name} is {value:.2f} (threshold: {rule.threshold})"
        
        alert_event = AlertEvent(
            workspace_id=rule.workspace_id,
            alert_rule_id=rule.id,
            state="firing",
            severity=rule.severity,
            message=message,
            details={
                "value": value,
                "threshold": rule.threshold,
                "comparison": rule.comparison,
                "metric_name": rule.metric_name,
                "service": rule.service
            },
            fired_at=datetime.utcnow()
        )
        
        self.db.add(alert_event)
        self.db.commit()
        
        logger.info(f"Alert fired: {message}")
