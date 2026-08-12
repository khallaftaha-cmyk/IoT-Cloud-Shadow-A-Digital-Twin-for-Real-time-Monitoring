from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from .. import database, models, schemas
from . import oauth2

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ── Rule Management ──────────────────────────────────────────────────────────

@router.post("/rules", status_code=status.HTTP_201_CREATED, response_model=schemas.AlertRuleOut)
def create_alert_rule(
    rule: schemas.AlertRuleIn,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    Create a new threshold alert rule for a device metric.
    """
    if rule.operator not in [">", "<", ">=", "<=", "=="]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operator. Must be one of: '>', '<', '>=', '<=', '=='"
        )

    new_rule = models.AlertRule(
        device_id=rule.device_id,
        metric=rule.metric,
        operator=rule.operator,
        threshold=rule.threshold,
        severity=rule.severity or "warning",
        is_active=True,
        created_by=current_user.id
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return new_rule


@router.get("/rules", response_model=List[schemas.AlertRuleOut])
def list_alert_rules(
    device_id: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    List active alert rules.
    """
    query = db.query(models.AlertRule)
    if device_id:
        query = query.filter(models.AlertRule.device_id == device_id)
    return query.all()


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert_rule(
    rule_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    Delete an alert rule by ID.
    """
    rule = db.query(models.AlertRule).filter(models.AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    db.delete(rule)
    db.commit()
    return None


# ── Triggered Alerts ──────────────────────────────────────────────────────────

@router.get("/", response_model=List[schemas.AlertOut])
def list_alerts(
    device_id: Optional[str] = None,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    limit: int = 50,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    Query triggered alerts with filters.
    """
    query = db.query(models.Alert)
    if device_id:
        query = query.filter(models.Alert.device_id == device_id)
    if severity:
        query = query.filter(models.Alert.severity == severity)
    if acknowledged is not None:
        query = query.filter(models.Alert.acknowledged == acknowledged)

    alerts = query.order_by(models.Alert.triggered_at.desc()).limit(limit).all()
    return alerts


@router.patch("/{alert_id}/acknowledge", response_model=schemas.AlertOut)
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    Acknowledge a triggered alert.
    """
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged = True
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert
