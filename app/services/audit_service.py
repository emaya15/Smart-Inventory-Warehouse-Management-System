from sqlalchemy.orm import Session
from typing import Any, Optional
from app.models.audit_log import AuditLog

def log_audit(db: Session, user_id: Optional[int], action: str, entity_type: str, entity_id: Any, old_value: Optional[dict] = None, new_value: Optional[dict] = None):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        old_value=old_value,
        new_value=new_value
    )
    db.add(audit)
