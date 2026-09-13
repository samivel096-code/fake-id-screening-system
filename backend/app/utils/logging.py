import json
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_audit(db: Session, user_id: str, action: str, document_id: str = None, result: str = None, details: dict = None, user_name: str = None):
    try:
        log = AuditLog(
            user_id=user_id,
            user_name=user_name,
            action=action,
            document_id=document_id,
            result=result,
            details_json=json.dumps(details) if details else None
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Failed to log audit event: {e}")
