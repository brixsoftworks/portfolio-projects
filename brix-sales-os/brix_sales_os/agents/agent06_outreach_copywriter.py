"""
brix_sales_os/agents/agent06_outreach_copywriter.py
==================================================
AGENT 06: OUTREACH COPYWRITER
Integrates `01_cold_outreach__outbound_prospector.json` core logic.
Drafts personalized, high-integrity cold emails with no fake familiarity,
no false urgency, verified observations, accurate sender ID, and clear opt-out.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from brix_sales_os.agents.base import BaseAgent
from brix_sales_os.database.models import (
    Organization, Contact, ResearchReport, SolutionMatch, OutreachMessage, Campaign
)
from brix_sales_os.core.ollama_client import ollama_client
from brix_sales_os.config import settings

class OutreachCopywriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="AGENT_06_OUTREACH_COPYWRITER",
            name="Ethical B2B Outreach Copywriter"
        )

    def run(self, db: Session, **kwargs) -> Dict[str, Any]:
        organization_id = kwargs.get("organization_id")
        campaign_id = kwargs.get("campaign_id")
        if not organization_id:
            raise ValueError("organization_id required")

        org = db.query(Organization).filter_by(id=organization_id).first()
        if not org:
            raise ValueError(f"Organization {organization_id} not found")

        contact = db.query(Contact).filter_by(organization_id=org.id).first()
        if not contact or not contact.email:
            raise ValueError(f"No valid contact or email found for {org.name}")

        report = db.query(ResearchReport).filter_by(organization_id=org.id).order_by(ResearchReport.created_at.desc()).first()
        solution = db.query(SolutionMatch).filter_by(organization_id=org.id).order_by(SolutionMatch.created_at.desc()).first()

        verified_obs = report.verified_observations if report and report.verified_observations else [f"active services in {org.industry}"]
        matched_wfs = solution.matched_workflow_ids if solution else ["WF-01", "WF-02"]
        first_obs = verified_obs[0] if verified_obs else f"your work in {org.industry}"
        primary_obs = str(first_obs.get("observation", first_obs) if isinstance(first_obs, dict) else first_obs)

        # Ensure campaign exists
        if not campaign_id:
            campaign = db.query(Campaign).first()
            if not campaign:
                campaign = Campaign(
                    name="Default International AI Outreach",
                    target_niche=org.industry or "Technology",
                    target_offer=solution.recommended_offer if solution else "OFFER_B",
                    status="DRAFT_ONLY"
                )
                db.add(campaign)
                db.commit()
                db.refresh(campaign)
            campaign_id = campaign.id

        system_prompt = (
            "You are a professional B2B outreach copywriter for Brix Softworks. "
            "Write a concise, honest, and personalized cold outreach email. "
            "STRICT RULES: "
            "1. NO fake familiarity (e.g. 'I hope this email finds you well' or pretending you know them). "
            "2. NO fabricated research or invented case studies. "
            "3. NO false urgency ('only 2 spots left'). "
            "4. NO misleading subject lines. "
            "5. NO generic mass-mail buzzwords. "
            "Format the email with: "
            "Subject: Quick automation idea for [Company] "
            "Salutation: Hi [First Name], "
            "Body: 2-3 short sentences citing a verified observation and suggesting an automation workflow. "
            "Call to action: A low-pressure invitation for a 2-minute walkthrough. "
            "Signoff: "
            "Best,\n"
            "Mullai Nathan\n"
            "Brix Softworks\n\n"
            "Include opt-out at the bottom: 'If you would rather not hear from me, please reply with unsubscribe and I will immediately remove you.'"
        )

        user_prompt = f"""
Prospect Name: {contact.first_name or contact.full_name}
Prospect Company: {org.name}
Industry: {org.industry}
Verified Observation: {primary_obs}
Recommended Solution / Workflows: {', '.join(matched_wfs)}
"""

        draft_body = ollama_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            timeout_seconds=45
        )

        subject = f"Quick automation idea for {org.name}"

        # Clean fallback if LLM is verbose
        if not draft_body or len(draft_body) < 30:
            draft_body = f"""Hi {contact.first_name or 'there'},

I noticed {primary_obs} on {org.website}.

I build AI automation workflows for businesses and put together a small example of how an automated intake and lead qualification system ({', '.join(matched_wfs[:2])}) could assist your team.

Would you be open to a 2-minute demonstration?

Best,
Mullai Nathan
Brix Softworks

If you would rather not hear from me, reply with unsubscribe and I will immediately remove you."""

        msg = OutreachMessage(
            campaign_id=campaign_id,
            contact_id=contact.id,
            subject=subject,
            body_text=draft_body.strip(),
            status="PENDING_APPROVAL"  # Never auto-send without explicit approval
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)

        return {
            "items_processed": 1,
            "message_id": msg.id,
            "contact_email": contact.email,
            "subject": msg.subject,
            "status": msg.status,
            "preview": msg.body_text[:120] + "..."
        }

agent06_copywriter = OutreachCopywriterAgent()
