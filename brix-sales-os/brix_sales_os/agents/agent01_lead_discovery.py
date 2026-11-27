"""
brix_sales_os/agents/agent01_lead_discovery.py
=============================================
AGENT 01: LEAD DISCOVERY & PROVENANCE TRACKER
Ingests qualified international B2B prospects from permitted sources,
enforces domain/email deduplication, checks suppression lists,
records data provenance, and initializes deal pipelines.
"""

import urllib.parse
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from brix_sales_os.agents.base import BaseAgent
from brix_sales_os.database.models import (
    Organization, Contact, LeadSource, Deal, SuppressionEntry
)
from brix_sales_os.core.audit import log_audit_event

class LeadDiscoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="AGENT_01_LEAD_DISCOVERY",
            name="Lead Discovery & Provenance Engine"
        )

    def normalize_domain(self, website_url: str) -> str:
        if not website_url.startswith(("http://", "https://")):
            website_url = "https://" + website_url
        parsed = urllib.parse.urlparse(website_url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain

    def run(self, db: Session, **kwargs) -> Dict[str, Any]:
        prospects_data: List[Dict[str, Any]] = kwargs.get("prospects", [])
        source_name = kwargs.get("source_name", "Public B2B Lead Source")
        source_type = kwargs.get("source_type", "DIRECTORY")
        commercial_permission = kwargs.get("commercial_permission", "PUBLIC_VERIFIED_FAIR_USE")

        # Record Lead Source
        source = db.query(LeadSource).filter_by(name=source_name).first()
        if not source:
            source = LeadSource(
                name=source_name,
                source_type=source_type,
                commercial_permission=commercial_permission
            )
            db.add(source)
            db.commit()
            db.refresh(source)

        ingested = []
        skipped_duplicates = 0
        skipped_suppressed = 0

        for p in prospects_data:
            website = p.get("website", "").strip()
            company_name = p.get("company_name", "").strip()
            contact_email = p.get("contact_email", "").strip().lower()
            contact_name = p.get("contact_name", "Decision Maker").strip()
            role = p.get("contact_role", "Executive / Founder").strip()
            industry = p.get("industry", "Digital Services").strip()
            country = p.get("country", "United States").strip()
            employee_count = p.get("employee_count", "10-50")
            initial_budget = float(p.get("budget", 750.0))

            if not website or not company_name:
                continue

            domain = self.normalize_domain(website)

            # Check Suppression
            if contact_email:
                suppressed = db.query(SuppressionEntry).filter(
                    (SuppressionEntry.email == contact_email) | (SuppressionEntry.domain == domain)
                ).first()
                if suppressed:
                    skipped_suppressed += 1
                    continue

            # Deduplicate by domain
            org = db.query(Organization).filter_by(domain=domain).first()
            if not org:
                org = Organization(
                    name=company_name,
                    domain=domain,
                    website=website,
                    industry=industry,
                    country=country,
                    employee_count=employee_count
                )
                db.add(org)
                db.commit()
                db.refresh(org)
            else:
                skipped_duplicates += 1

            # Deduplicate or create Contact
            contact = None
            if contact_email:
                contact = db.query(Contact).filter_by(email=contact_email).first()
                if not contact:
                    names = contact_name.split(" ", 1)
                    first_name = names[0]
                    last_name = names[1] if len(names) > 1 else ""
                    contact = Contact(
                        organization_id=org.id,
                        first_name=first_name,
                        last_name=last_name,
                        full_name=contact_name,
                        email=contact_email,
                        role=role,
                        consent_status="LEGITIMATE_INTEREST_B2B"
                    )
                    db.add(contact)
                    db.commit()
                    db.refresh(contact)

            # Ensure initial deal exists
            deal = db.query(Deal).filter_by(organization_id=org.id).first()
            if not deal:
                deal = Deal(
                    organization_id=org.id,
                    title=f"AI Automation Intake — {org.name}",
                    stage="NEW_LEAD",
                    amount=initial_budget,
                    matched_offer="OFFER_B"
                )
                db.add(deal)
                db.commit()

            ingested.append({
                "organization_id": org.id,
                "company_name": org.name,
                "domain": org.domain,
                "contact_id": contact.id if contact else None,
                "contact_email": contact.email if contact else None,
                "country": org.country,
                "industry": org.industry
            })

        return {
            "items_processed": len(ingested),
            "ingested_leads": ingested,
            "skipped_duplicates": skipped_duplicates,
            "skipped_suppressed": skipped_suppressed
        }

agent01_discovery = LeadDiscoveryAgent()
