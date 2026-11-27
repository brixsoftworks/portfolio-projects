"""
brix_sales_os/api/main.py
========================
FastAPI Application for Brix Sales OS.
Exposes modular REST endpoints for all 12 agents, pipelines, and frontend telemetry.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from brix_sales_os.config import settings
from brix_sales_os.database.session import get_db, init_db
from brix_sales_os.database.models import (
    Organization, Contact, LeadScore, ResearchReport, SolutionMatch, Demo,
    Campaign, OutreachMessage, SuppressionEntry, Conversation, Meeting, Deal,
    Proposal, Invoice, Payment, Project, AgentRun, WorkflowRegistryItem,
    IntegrationCredentialsMetadata, AuditLog
)
from brix_sales_os.agents import (
    agent01_discovery, agent02_intelligence, agent03_scoring, agent04_matching,
    agent05_demo, agent06_copywriter, agent07_campaign, agent08_inbox,
    agent09_meeting, agent10_proposal, agent11_closing, agent12_onboarding,
    ALL_AGENTS
)
from brix_sales_os.core.emergency import is_emergency_stop_active, set_emergency_stop
from brix_sales_os.core.audit import log_audit_event

app = FastAPI(
    title="Brix Sales OS API",
    description="Autonomous AI Client Acquisition, Outreach, Sales & Revenue Engine",
    version=settings.app_version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# ─── Telemetry & Emergency Stop ──────────────────────────────────────────

@app.get("/api/health")
def get_health(db: Session = Depends(get_db)):
    ollama_ok = False
    try:
        import urllib.request
        urllib.request.urlopen(f"{settings.ollama_base_url}/api/tags", timeout=3)
        ollama_ok = True
    except Exception:
        pass

    return {
        "status": "HEALTHY",
        "app": settings.app_name,
        "version": settings.app_version,
        "mode": settings.operating_mode,
        "emergency_stop": is_emergency_stop_active(),
        "ollama_connected": ollama_ok,
        "primary_model": settings.primary_model,
        "database": "CONNECTED"
    }

@app.get("/api/telemetry")
def get_telemetry(db: Session = Depends(get_db)):
    prospects_count = db.query(Organization).count()
    qualified_count = db.query(LeadScore).filter(LeadScore.priority_level.in_(["HIGH", "MEDIUM"])).count()
    drafts_pending = db.query(OutreachMessage).filter_by(status="PENDING_APPROVAL").count()
    messages_sent = db.query(OutreachMessage).filter_by(status="SENT").count()
    conversations_count = db.query(Conversation).count()
    meetings_count = db.query(Meeting).filter_by(status="CONFIRMED").count()
    proposals_count = db.query(Proposal).count()
    deals_won = db.query(Deal).filter_by(stage="WON").count()
    
    # Calculate revenue and pipeline
    verified_revenue = db.query(func.sum(Payment.amount_usd)).scalar() or 0.0
    pipeline_value = db.query(func.sum(Deal.amount)).filter(Deal.stage != "LOST").scalar() or 0.0

    return {
        "prospects_discovered": prospects_count,
        "qualified_leads": qualified_count,
        "drafts_awaiting_approval": drafts_pending,
        "messages_sent": messages_sent,
        "conversations": conversations_count,
        "meetings_booked": meetings_count,
        "proposals_issued": proposals_count,
        "deals_won": deals_won,
        "verified_revenue_usd": round(verified_revenue, 2),
        "pipeline_value_usd": round(pipeline_value, 2),
        "emergency_stop": is_emergency_stop_active(),
        "operating_mode": settings.operating_mode
    }

class EmergencyStopRequest(BaseModel):
    active: bool

@app.post("/api/emergency-stop")
def toggle_emergency_stop(req: EmergencyStopRequest):
    set_emergency_stop(req.active)
    log_audit_event(
        action="EMERGENCY_STOP_TOGGLED",
        actor="USER",
        details={"active": req.active}
    )
    return {"emergency_stop": req.active}

class ModeRequest(BaseModel):
    mode: str

@app.post("/api/mode")
def update_mode(req: ModeRequest):
    if req.mode not in ("SIMULATION", "ASSISTED_PRODUCTION", "CONTROLLED_AUTOMATION"):
        raise HTTPException(status_code=400, detail="Invalid operating mode")
    settings.operating_mode = req.mode
    log_audit_event(
        action="OPERATING_MODE_CHANGED",
        actor="USER",
        details={"mode": req.mode}
    )
    return {"operating_mode": settings.operating_mode}

# ─── Agents Control Center ───────────────────────────────────────────────

@app.get("/api/agents")
def list_agents(db: Session = Depends(get_db)):
    result = []
    for agent in ALL_AGENTS:
        last_run = db.query(AgentRun).filter_by(agent_id=agent.agent_id).order_by(AgentRun.started_at.desc()).first()
        total_runs = db.query(AgentRun).filter_by(agent_id=agent.agent_id).count()
        failed_runs = db.query(AgentRun).filter_by(agent_id=agent.agent_id, status="FAILED").count()
        success_rate = ((total_runs - failed_runs) / total_runs * 100) if total_runs > 0 else 100.0

        result.append({
            "agent_id": agent.agent_id,
            "name": agent.name,
            "status": "READY" if not last_run or last_run.status != "RUNNING" else "RUNNING",
            "last_executed": last_run.started_at.isoformat() if last_run else None,
            "duration_ms": last_run.duration_ms if last_run else 0,
            "total_runs": total_runs,
            "success_rate": round(success_rate, 1),
            "last_status": last_run.status if last_run else "IDLE"
        })
    return result

# ─── Lead Explorer & Pipelines ───────────────────────────────────────────

@app.get("/api/leads")
def get_leads(
    priority: Optional[str] = None,
    industry: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Organization)
    if industry:
        query = query.filter(Organization.industry.ilike(f"%{industry}%"))

    orgs = query.all()
    leads = []
    for org in orgs:
        score = db.query(LeadScore).filter_by(organization_id=org.id).order_by(LeadScore.created_at.desc()).first()
        if priority and score and score.priority_level != priority:
            continue
        contact = db.query(Contact).filter_by(organization_id=org.id).first()
        deal = db.query(Deal).filter_by(organization_id=org.id).first()
        solution = db.query(SolutionMatch).filter_by(organization_id=org.id).order_by(SolutionMatch.created_at.desc()).first()
        demo = db.query(Demo).filter_by(organization_id=org.id).first()

        leads.append({
            "id": org.id,
            "company_name": org.name,
            "domain": org.domain,
            "website": org.website,
            "industry": org.industry,
            "country": org.country,
            "employee_count": org.employee_count,
            "contact_name": contact.full_name if contact else "N/A",
            "contact_email": contact.email if contact else "N/A",
            "contact_role": contact.role if contact else "N/A",
            "lead_score": score.total_score if score else None,
            "priority": score.priority_level if score else "UNSCORED",
            "recommended_offer": solution.recommended_offer if solution else None,
            "matched_workflows": solution.matched_workflow_ids if solution else [],
            "deal_stage": deal.stage if deal else "NEW_LEAD",
            "deal_amount": deal.amount if deal else 0.0,
            "has_demo": demo is not None
        })
    return leads

class LeadDiscoveryPayload(BaseModel):
    prospects: Optional[List[Dict[str, Any]]] = None
    source_name: Optional[str] = "Manual Ingestion"

@app.post("/api/leads/discover")
def trigger_lead_discovery(payload: LeadDiscoveryPayload, db: Session = Depends(get_db)):
    prospects = payload.prospects
    if not prospects:
        # High quality default starter prospects matching priority target niches
        prospects = [
            {
                "company_name": "Apex Growth Agency",
                "website": "https://apexgrowthagency.com",
                "industry": "Digital Marketing Agency",
                "country": "United States",
                "employee_count": "15-50",
                "contact_name": "Marcus Vance",
                "contact_role": "Managing Director",
                "contact_email": "marcus@apexgrowthagency.com",
                "budget": 750
            },
            {
                "company_name": "CloudScale Systems",
                "website": "https://cloudscalesystems.io",
                "industry": "B2B SaaS / DevOps",
                "country": "United Kingdom",
                "employee_count": "20-80",
                "contact_name": "Eleanor Brooks",
                "contact_role": "VP of Engineering",
                "contact_email": "eleanor@cloudscalesystems.io",
                "budget": 1500
            },
            {
                "company_name": "Lumina Creative Studio",
                "website": "https://luminacreative.co",
                "industry": "Web Development Agency",
                "country": "Australia",
                "employee_count": "10-30",
                "contact_name": "Liam Davies",
                "contact_role": "Founder & Creative Lead",
                "contact_email": "liam@luminacreative.co",
                "budget": 297
            }
        ]
    res = agent01_discovery.execute(prospects=prospects, source_name=payload.source_name)
    return res

@app.post("/api/leads/{id}/process-full-pipeline")
def process_lead_end_to_end(id: str, db: Session = Depends(get_db)):
    """
    Executes Agent 02 -> Agent 03 -> Agent 04 -> Agent 05 -> Agent 06 sequentially for a lead.
    """
    r2 = agent02_intelligence.execute(organization_id=id)
    r3 = agent03_scoring.execute(organization_id=id)
    r4 = agent04_matching.execute(organization_id=id)
    r5 = agent05_demo.execute(organization_id=id)
    r6 = agent06_copywriter.execute(organization_id=id)

    return {
        "success": True,
        "organization_id": id,
        "research": r2,
        "scoring": r3,
        "solution": r4,
        "demo": r5,
        "outreach_draft": r6
    }

# ─── Campaigns & Review Queue ────────────────────────────────────────────

@app.get("/api/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).all()
    res = []
    for c in campaigns:
        pending = db.query(OutreachMessage).filter_by(campaign_id=c.id, status="PENDING_APPROVAL").count()
        approved = db.query(OutreachMessage).filter_by(campaign_id=c.id, status="APPROVED").count()
        sent = db.query(OutreachMessage).filter_by(campaign_id=c.id, status="SENT").count()
        res.append({
            "id": c.id,
            "name": c.name,
            "target_niche": c.target_niche,
            "target_offer": c.target_offer,
            "status": c.status,
            "daily_limit": c.daily_limit,
            "pending_approval": pending,
            "approved_ready": approved,
            "sent_count": sent
        })
    return res

@app.get("/api/campaigns/review-queue")
def get_review_queue(db: Session = Depends(get_db)):
    messages = db.query(OutreachMessage).filter_by(status="PENDING_APPROVAL").all()
    queue = []
    for m in messages:
        contact = m.contact
        org = contact.organization if contact else None
        queue.append({
            "message_id": m.id,
            "campaign_id": m.campaign_id,
            "contact_name": contact.full_name if contact else "N/A",
            "contact_email": contact.email if contact else "N/A",
            "company_name": org.name if org else "N/A",
            "industry": org.industry if org else "N/A",
            "subject": m.subject,
            "body_text": m.body_text,
            "created_at": m.created_at.isoformat()
        })
    return queue

class ApprovalAction(BaseModel):
    message_id: str
    approved: bool
    notes: Optional[str] = None

@app.post("/api/campaigns/review")
def review_message(action: ApprovalAction, db: Session = Depends(get_db)):
    if action.approved:
        return agent07_campaign.execute(action="APPROVE", message_id=action.message_id)
    else:
        return agent07_campaign.execute(action="REJECT", message_id=action.message_id, reason=action.notes or "Rejected")

@app.post("/api/campaigns/dispatch")
def dispatch_approved_messages():
    return agent07_campaign.execute(action="DISPATCH")

# ─── Inbox & Conversations ───────────────────────────────────────────────

@app.get("/api/inbox")
def list_conversations(db: Session = Depends(get_db)):
    convs = db.query(Conversation).order_by(Conversation.received_at.desc()).all()
    res = []
    for c in convs:
        contact = c.contact
        org = contact.organization if contact else None
        res.append({
            "conversation_id": c.id,
            "contact_name": contact.full_name if contact else "N/A",
            "contact_email": contact.email if contact else "N/A",
            "company_name": org.name if org else "N/A",
            "incoming_message": c.incoming_message,
            "intent": c.intent_classification,
            "suggested_reply": c.ai_suggested_reply,
            "status": c.status,
            "received_at": c.received_at.isoformat()
        })
    return res

class SimulateReplyPayload(BaseModel):
    contact_id: str
    incoming_message: str

@app.post("/api/inbox/simulate-reply")
def simulate_incoming_reply(payload: SimulateReplyPayload):
    return agent08_inbox.execute(
        contact_id=payload.contact_id,
        incoming_message=payload.incoming_message
    )

# ─── Deals Pipeline & Proposals ──────────────────────────────────────────

@app.get("/api/deals")
def list_deals(db: Session = Depends(get_db)):
    deals = db.query(Deal).all()
    res = []
    for d in deals:
        org = d.organization
        res.append({
            "deal_id": d.id,
            "title": d.title,
            "company_name": org.name if org else "N/A",
            "domain": org.domain if org else "N/A",
            "stage": d.stage,
            "amount": d.amount,
            "matched_offer": d.matched_offer,
            "confidence": d.confidence,
            "updated_at": d.updated_at.isoformat()
        })
    return res

@app.post("/api/proposals/generate")
def create_proposal(org_id: str = Query(...)):
    return agent10_proposal.execute(organization_id=org_id)

@app.get("/api/proposals/{id}/pdf")
def download_proposal_pdf(id: str, db: Session = Depends(get_db)):
    prop = db.query(Proposal).filter_by(id=id).first()
    if not prop or not prop.pdf_path or not os.path.exists(prop.pdf_path):
        raise HTTPException(status_code=404, detail="Proposal PDF not found on disk")
    return FileResponse(prop.pdf_path, media_type="application/pdf", filename=os.path.basename(prop.pdf_path))

# ─── Closing & Onboarding ────────────────────────────────────────────────

class PaymentWebhookPayload(BaseModel):
    invoice_number: str
    amount_usd: float
    transaction_id: str
    idempotency_key: str
    provider: Optional[str] = "STRIPE"

@app.post("/api/closing/webhook")
def process_payment_webhook(payload: PaymentWebhookPayload):
    return agent11_closing.execute(
        action="PROCESS_PAYMENT",
        invoice_number=payload.invoice_number,
        amount_usd=payload.amount_usd,
        transaction_id=payload.transaction_id,
        idempotency_key=payload.idempotency_key,
        provider=payload.provider
    )

@app.post("/api/onboarding/start")
def start_onboarding(org_id: str = Query(...)):
    return agent12_onboarding.execute(organization_id=org_id)

# ─── Workflows Registry ──────────────────────────────────────────────────

@app.get("/api/workflows")
def list_workflows(
    department: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(WorkflowRegistryItem)
    if department:
        query = query.filter_by(department=department)
    items = query.all()
    if tag:
        items = [i for i in items if tag.lower() in [t.lower() for t in (i.tags or [])]]
    return items

# ─── Mail Automator Endpoints ──────────────────────────────────────────

from brix_sales_os.services.mail_automator import mail_automator

class MailerConfigPayload(BaseModel):
    email_address: str
    app_password: str
    provider: Optional[str] = "gmail"

@app.post("/api/mailer/configure")
def configure_mailer(payload: MailerConfigPayload):
    mail_automator.save_credentials(
        email_addr=payload.email_address,
        app_pass=payload.app_password,
        provider=payload.provider or "gmail"
    )
    test_result = mail_automator.test_connection()
    return test_result

@app.get("/api/mailer/status")
def get_mailer_status():
    if not mail_automator.email_address or not mail_automator.app_password:
        return {"configured": False, "status": "NOT_CONFIGURED"}
    return mail_automator.test_connection()

@app.post("/api/mailer/check-replies")
def check_mailer_replies(db: Session = Depends(get_db)):
    replies = mail_automator.check_inbox_for_replies(db)
    return {"replies_detected": len(replies), "details": replies}

# Mount Frontend Static Files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/dashboard", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

@app.get("/")
def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))
