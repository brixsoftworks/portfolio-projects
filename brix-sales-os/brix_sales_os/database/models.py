"""
brix_sales_os/database/models.py
===============================
Complete relational data models for Brix Sales OS.
Implements Section 6 database requirements.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def gen_uuid() -> str:
    return str(uuid.uuid4())

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), unique=True, index=True, nullable=False)
    website = Column(String(512), nullable=False)
    industry = Column(String(100), index=True)
    country = Column(String(100), default="United States", index=True)
    city = Column(String(100))
    employee_count = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contacts = relationship("Contact", back_populates="organization", cascade="all, delete-orphan")
    research_reports = relationship("ResearchReport", back_populates="organization", cascade="all, delete-orphan")
    lead_scores = relationship("LeadScore", back_populates="organization", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="organization", cascade="all, delete-orphan")
    proposals = relationship("Proposal", back_populates="organization", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(150))
    linkedin_url = Column(String(512))
    phone = Column(String(50))
    is_decision_maker = Column(Boolean, default=True)
    consent_status = Column(String(50), default="LEGITIMATE_INTEREST_B2B")
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="contacts")
    messages = relationship("OutreachMessage", back_populates="contact")
    conversations = relationship("Conversation", back_populates="contact")


class LeadSource(Base):
    __tablename__ = "lead_sources"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(150), nullable=False)  # e.g., "Public B2B Directory", "Inbound Sales Form", "Discord Job Radar"
    source_type = Column(String(50), nullable=False)  # "DIRECTORY", "JOB_BOARD", "INBOUND_FORM", "PARTNER"
    commercial_permission = Column(String(100), default="PUBLIC_VERIFIED_FAIR_USE")
    url = Column(String(512))
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    target_url = Column(String(512), nullable=False)
    verified_observations = Column(JSON, default=list)  # Direct facts observed
    hypotheses = Column(JSON, default=list)  # Inferred automation opportunities
    tech_stack_detected = Column(JSON, default=list)
    raw_markdown = Column(Text)
    model_used = Column(String(100), default="qwen2.5-coder:7b")
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="research_reports")


class LeadScore(Base):
    __tablename__ = "lead_scores"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    total_score = Column(Integer, nullable=False)  # 0 to 100
    priority_level = Column(String(20), nullable=False)  # HIGH (80-100), MEDIUM (60-79), LOW (<60)
    industry_fit_score = Column(Integer, default=0)
    evidence_score = Column(Integer, default=0)
    company_size_score = Column(Integer, default=0)
    buying_signal_score = Column(Integer, default=0)
    contact_quality_score = Column(Integer, default=0)
    geo_service_fit_score = Column(Integer, default=0)
    scoring_rationale = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="lead_scores")


class WorkflowRegistryItem(Base):
    __tablename__ = "workflow_registry"

    id = Column(String(50), primary_key=True)  # e.g., "WF-01"
    name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    complexity = Column(String(20), default="Medium")
    node_count = Column(Integer, default=0)
    trigger_type = Column(String(50), default="Webhook")
    tags = Column(JSON, default=list)
    operational_status = Column(String(50), default="READY_WITH_CONFIG")
    suggested_setup_usd = Column(Integer, default=750)
    suggested_monthly_usd = Column(Integer, default=150)


class SolutionMatch(Base):
    __tablename__ = "solution_matches"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    recommended_offer = Column(String(50), nullable=False)  # "OFFER_A", "OFFER_B", "OFFER_C"
    matched_workflow_ids = Column(JSON, default=list)  # ["WF-01", "WF-02"]
    implementation_complexity = Column(String(50))
    proposed_setup_price = Column(Float, default=750.0)
    proposed_monthly_price = Column(Float, default=150.0)
    matching_rationale = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Demo(Base):
    __tablename__ = "demos"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    solution_match_id = Column(String(36), ForeignKey("solution_matches.id"))
    demo_type = Column(String(50))  # "WORKFLOW_DIAGRAM", "SAMPLE_DASHBOARD", "PDF_BRIEF"
    title = Column(String(255))
    content_html = Column(Text)
    synthetic_data = Column(JSON, default=dict)
    cached_asset_url = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    target_niche = Column(String(100))
    target_offer = Column(String(50), default="OFFER_B")
    status = Column(String(50), default="DRAFT_ONLY")  # "DRAFT_ONLY", "PENDING_APPROVAL", "ACTIVE", "PAUSED"
    daily_limit = Column(Integer, default=25)
    sent_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("OutreachMessage", back_populates="campaign")


class OutreachMessage(Base):
    __tablename__ = "outreach_messages"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"))
    contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=False)
    subject = Column(String(255), nullable=False)
    body_text = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING_APPROVAL")  # "PENDING_APPROVAL", "APPROVED", "REJECTED", "SENT", "DELIVERED", "FAILED"
    approval_notes = Column(Text)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="messages")
    contact = relationship("Contact", back_populates="messages")


class SuppressionEntry(Base):
    __tablename__ = "suppression_entries"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    domain = Column(String(255), index=True)
    reason = Column(String(100), default="UNSUBSCRIBED")  # "UNSUBSCRIBED", "BOUNCED", "COMPLAINT", "MANUAL"
    created_at = Column(DateTime, default=datetime.utcnow)


class EmailEvent(Base):
    __tablename__ = "email_events"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    message_id = Column(String(36), ForeignKey("outreach_messages.id"))
    event_type = Column(String(50))  # "SENT", "OPENED", "CLICKED", "BOUNCED", "REPLIED"
    details_json = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=False)
    incoming_message = Column(Text, nullable=False)
    intent_classification = Column(String(50))  # "INTERESTED", "INFO_REQUEST", "PRICING", "MEETING", "NOT_INTERESTED", "UNSUBSCRIBE"
    ai_suggested_reply = Column(Text)
    status = Column(String(50), default="AWAITING_REVIEW")  # "AWAITING_REVIEW", "REPLIED", "SUPPRESSED"
    received_at = Column(DateTime, default=datetime.utcnow)

    contact = relationship("Contact", back_populates="conversations")


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    timezone = Column(String(50), default="UTC")
    calendar_provider = Column(String(50), default="CALENDLY")
    booking_url = Column(String(512))
    status = Column(String(50), default="CONFIRMED")  # "CONFIRMED", "CANCELLED", "COMPLETED"
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Deal(Base):
    __tablename__ = "deals"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    title = Column(String(255), nullable=False)
    stage = Column(String(50), default="NEW_LEAD")
    # STAGES: "NEW_LEAD", "QUALIFIED", "CONTACT_APPROVED", "CONTACTED", "INTERESTED", "MEETING", "PROPOSAL", "NEGOTIATION", "WON", "LOST"
    amount = Column(Float, default=0.0)
    matched_offer = Column(String(50), default="OFFER_B")
    confidence = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="deals")
    proposals = relationship("Proposal", back_populates="deal")


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    deal_id = Column(String(36), ForeignKey("deals.id"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    client_problem = Column(Text)
    proposed_solution = Column(Text)
    selected_workflow_ids = Column(JSON, default=list)
    timeline_weeks = Column(Integer, default=2)
    setup_price_usd = Column(Float, default=750.0)
    monthly_retainer_usd = Column(Float, default=150.0)
    pdf_path = Column(String(512))
    status = Column(String(50), default="DRAFT")  # "DRAFT", "APPROVED", "DISPATCHED", "ACCEPTED", "REJECTED"
    created_at = Column(DateTime, default=datetime.utcnow)

    deal = relationship("Deal", back_populates="proposals")
    organization = relationship("Organization", back_populates="proposals")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    proposal_id = Column(String(36), ForeignKey("proposals.id"))
    terms_summary = Column(Text)
    signed_by_client = Column(Boolean, default=False)
    signed_at = Column(DateTime)
    status = Column(String(50), default="PENDING_SIGNATURE")  # "PENDING_SIGNATURE", "EXECUTED", "TERMINATED"
    created_at = Column(DateTime, default=datetime.utcnow)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    amount_usd = Column(Float, nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), default="ISSUED")  # "ISSUED", "PAID", "VOID", "OVERDUE"
    payment_link = Column(String(512))
    issued_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)

    organization = relationship("Organization")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    amount_usd = Column(Float, nullable=False)
    payment_provider = Column(String(50), default="STRIPE")  # "STRIPE", "LEMONSQUEEZY", "BANK_WIRE"
    transaction_id = Column(String(255), unique=True)
    status = Column(String(50), default="SUCCEEDED")  # "SUCCEEDED", "FAILED", "REFUNDED"
    idempotency_key = Column(String(255), unique=True)
    verified_at = Column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    deal_id = Column(String(36), ForeignKey("deals.id"))
    project_name = Column(String(255), nullable=False)
    status = Column(String(50), default="ONBOARDING")  # "ONBOARDING", "IN_PROGRESS", "DEPLOYED", "MAINTENANCE"
    checklist = Column(JSON, default=list)
    workspace_path = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="projects")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    agent_id = Column(String(50), nullable=False)  # e.g., "AGENT_01_DISCOVERY"
    trigger_type = Column(String(50), default="MANUAL")
    status = Column(String(50), default="COMPLETED")  # "RUNNING", "COMPLETED", "FAILED"
    items_processed = Column(Integer, default=0)
    errors = Column(JSON, default=list)
    duration_ms = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    action = Column(String(100), nullable=False)
    actor = Column(String(100), default="SYSTEM")
    target_entity = Column(String(100))
    target_id = Column(String(100))
    details_json = Column(JSON, default=dict)
    ip_address = Column(String(50), default="127.0.0.1")
    timestamp = Column(DateTime, default=datetime.utcnow)


class IntegrationCredentialsMetadata(Base):
    __tablename__ = "integration_credentials_metadata"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    provider_name = Column(String(100), unique=True, nullable=False)  # "OLLAMA", "STRIPE", "CALENDLY", "SMTP", "TWENTY"
    is_configured = Column(Boolean, default=False)
    status = Column(String(50), default="NOT_CONFIGURED")  # "HEALTHY", "DEGRADED", "ERROR", "NOT_CONFIGURED"
    last_verified = Column(DateTime)
    notes = Column(Text)
