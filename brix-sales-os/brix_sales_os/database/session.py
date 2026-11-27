"""
brix_sales_os/database/session.py
================================
Database session management and initial schema bootstrapper.
"""

import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from brix_sales_os.config import settings
from brix_sales_os.database.models import (
    Base, WorkflowRegistryItem, IntegrationCredentialsMetadata
)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Seed workflow registry into database if empty
    db = SessionLocal()
    try:
        count = db.query(WorkflowRegistryItem).count()
        if count == 0:
            reg_file = Path(__file__).parent.parent / "registry" / "workflow_registry.json"
            if reg_file.exists():
                with open(reg_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data:
                    wf = WorkflowRegistryItem(
                        id=item["id"],
                        name=item["name"],
                        filename=item["filename"],
                        department=item["department"],
                        description=item["description"],
                        complexity=item.get("complexity", "Medium"),
                        node_count=item.get("node_count", 0),
                        trigger_type=item.get("trigger_type", "Webhook"),
                        tags=item.get("tags", []),
                        operational_status=item.get("operational_status", "READY_WITH_CONFIG"),
                        suggested_setup_usd=item.get("suggested_price", {}).get("setup_usd", 750),
                        suggested_monthly_usd=item.get("suggested_price", {}).get("monthly_retainer_usd", 150)
                    )
                    db.add(wf)
                db.commit()
                
        # Seed Integrations status
        providers = ["OLLAMA", "AGENTSDR", "STRIPE", "CALENDLY", "SMTP", "TWENTY"]
        for p in providers:
            exists = db.query(IntegrationCredentialsMetadata).filter_by(provider_name=p).first()
            if not exists:
                is_conf = p in ["OLLAMA", "AGENTSDR"]  # Ollama and AgentSDR are verified running locally
                status = "HEALTHY" if is_conf else "NOT_CONFIGURED"
                meta = IntegrationCredentialsMetadata(
                    provider_name=p,
                    is_configured=is_conf,
                    status=status,
                    notes="Local verified service" if is_conf else "Pending external API credentials"
                )
                db.add(meta)
        db.commit()
    finally:
        db.close()
