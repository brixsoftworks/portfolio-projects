"""
brix_sales_os/config.py
======================
Central configuration for Brix Sales OS.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    # App Information
    app_name: str = "Brix Sales OS"
    app_version: str = "1.0.0"
    company_name: str = "Brix Softworks"
    sender_name: str = "Mullai Nathan"
    sender_title: str = "Senior Automation & AI Architect"
    sender_email: str = os.getenv("SENDER_EMAIL", "mullai@brixsoftworks.com")
    
    # Environment & Mode
    # MODES: "SIMULATION", "ASSISTED_PRODUCTION", "CONTROLLED_AUTOMATION"
    operating_mode: str = os.getenv("OPERATING_MODE", "ASSISTED_PRODUCTION")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Global Emergency Kill-Switch
    emergency_stop: bool = os.getenv("EMERGENCY_STOP", "false").lower() == "true"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'brix_sales.db'}")
    
    # AI Inference (Ollama on local NVIDIA RTX 5060 GPU)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    primary_model: str = os.getenv("PRIMARY_MODEL", "qwen2.5-coder:7b")
    fallback_model: str = os.getenv("FALLBACK_MODEL", "llama3.2:3b")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
    
    # Pricing Catalog Defaults
    offer_a_price_usd: int = 297       # n8n Agency OS Complete Pack (60 Agents)
    offer_b_setup_usd: int = 750       # Turnkey Done-For-You Workflow
    offer_b_monthly_usd: int = 150     # Turnkey Maintenance Retainer
    offer_c_monthly_usd: int = 1500    # Fractional Automation Engineer Retainer
    
    # Campaign & Outreach Constraints
    max_daily_outreach: int = int(os.getenv("MAX_DAILY_OUTREACH", "50"))
    require_human_approval_for_emails: bool = os.getenv("REQUIRE_EMAIL_APPROVAL", "true").lower() == "true"
    require_human_approval_for_proposals: bool = os.getenv("REQUIRE_PROPOSAL_APPROVAL", "true").lower() == "true"
    
    # Integrated Services
    agentsdr_url: str = os.getenv("AGENTSDR_URL", "http://localhost:3000")
    agency_portal_url: str = os.getenv("AGENCY_PORTAL_URL", "http://localhost:3850/sales")
    
settings = Settings()
