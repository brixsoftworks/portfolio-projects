"""
brix_sales_os/core/audit.py
==========================
Central audit logging utility.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from brix_sales_os.database.session import SessionLocal
from brix_sales_os.database.models import AuditLog

def log_audit_event(
    action: str,
    actor: str = "SYSTEM",
    target_entity: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: str = "127.0.0.1"
):
    db = SessionLocal()
    try:
        entry = AuditLog(
            action=action,
            actor=actor,
            target_entity=target_entity,
            target_id=target_id,
            details_json=details or {},
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[AUDIT ERROR] Failed to write audit log: {e}")
    finally:
        db.close()
