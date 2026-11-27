"""
brix_sales_os/agents/base.py
===========================
Base Agent abstraction providing execution tracking, error trapping,
timing metrics, and audit logging into `agent_runs`.
"""

import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from brix_sales_os.database.session import SessionLocal
from brix_sales_os.database.models import AgentRun
from brix_sales_os.core.audit import log_audit_event
from brix_sales_os.core.emergency import enforce_not_stopped

class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name

    def execute(self, **kwargs) -> Dict[str, Any]:
        enforce_not_stopped(f"Agent {self.name} run")
        start_time = time.time()
        started_at = datetime.utcnow()
        db = SessionLocal()
        run_record = AgentRun(
            agent_id=self.agent_id,
            trigger_type=kwargs.get("trigger_type", "MANUAL"),
            status="RUNNING",
            started_at=started_at
        )
        db.add(run_record)
        db.commit()
        db.refresh(run_record)
        
        errors = []
        items_count = 0
        result_data = {}
        
        try:
            result_data = self.run(db=db, **kwargs)
            items_count = result_data.get("items_processed", 1)
            run_record.status = "COMPLETED"
        except Exception as e:
            errors.append(str(e))
            run_record.status = "FAILED"
            run_record.errors = errors
            log_audit_event(
                action=f"{self.agent_id}_FAILED",
                actor="SYSTEM",
                target_entity="agent_runs",
                target_id=run_record.id,
                details={"error": str(e)}
            )
            raise e
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            run_record.duration_ms = duration_ms
            run_record.completed_at = datetime.utcnow()
            run_record.items_processed = items_count
            db.commit()
            
            log_audit_event(
                action=f"{self.agent_id}_COMPLETED" if not errors else f"{self.agent_id}_FAILED",
                actor="SYSTEM",
                target_entity="agent_runs",
                target_id=run_record.id,
                details={"duration_ms": duration_ms, "items_processed": items_count}
            )
            db.close()
            
        result_data["run_id"] = run_record.id
        result_data["duration_ms"] = duration_ms
        return result_data

    @abstractmethod
    def run(self, db, **kwargs) -> Dict[str, Any]:
        pass
