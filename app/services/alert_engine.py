from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import datetime, timezone
import json

OPERATORS = {
    ">": lambda val, thresh: val > thresh,
    "<": lambda val, thresh: val < thresh,
    ">=": lambda val, thresh: val >= thresh,
    "<=": lambda val, thresh: val <= thresh,
    "==": lambda val, thresh: val == thresh,
}


def evaluate_telemetry(data: schemas.DataIn, db: Session) -> list[models.Alert]:
    """
    Evaluates incoming sensor reading against active AlertRules for the device.
    Creates and returns triggered Alert database records.
    """
    rules = db.query(models.AlertRule).filter(
        models.AlertRule.device_id == data.device_id,
        models.AlertRule.is_active == True
    ).all()

    triggered_alerts = []

    for rule in rules:
        metric_value = getattr(data, rule.metric, None)
        if metric_value is None:
            continue

        comp_fn = OPERATORS.get(rule.operator)
        if comp_fn and comp_fn(metric_value, rule.threshold):
            message = (
                f"[{rule.severity.upper()}] Device '{data.device_id}' {rule.metric} "
                f"is {metric_value} (threshold {rule.operator} {rule.threshold})"
            )
            alert = models.Alert(
                rule_id=rule.id,
                device_id=data.device_id,
                metric=rule.metric,
                value=float(metric_value),
                threshold=rule.threshold,
                severity=rule.severity,
                message=message,
                acknowledged=False,
                triggered_at=datetime.now(timezone.utc)
            )
            db.add(alert)
            triggered_alerts.append(alert)

    if triggered_alerts:
        db.commit()
        for alert in triggered_alerts:
            db.refresh(alert)

    return triggered_alerts
