"""
brix_sales_os/agents/agent09_meeting_booking.py
==============================================
AGENT 09: MEETING BOOKING & DISCOVERY PREPARER
Coordinates discovery calls across international time zones (US/UK/EU/Australia),
prepares tailored pre-call technical briefing notes and discovery questions,
and advances deal stages upon confirmed booking.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from brix_sales_os.agents.base import BaseAgent
from brix_sales_os.database.models import (
    Contact, Organization, Meeting, Deal, ResearchReport
)

class MeetingBookingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="AGENT_09_MEETING_BOOKING",
            name="Meeting Booking & Discovery Specialist"
        )

    def generate_discovery_questions(self, industry: str, hypotheses: List[str]) -> List[str]:
        return [
            f"How is your team currently handling incoming leads and project inquiries?",
            f"Which CRM or database is your single source of truth for client data?",
            f"Where are manual handoffs slowing down your operations in {industry}?",
            f"Are there data privacy constraints (e.g. HIPAA, GDPR) requiring local or private AI inference?"
        ]

    def run(self, db: Session, **kwargs) -> Dict[str, Any]:
        contact_id = kwargs.get("contact_id")
        scheduled_time_str = kwargs.get("scheduled_time")
        timezone = kwargs.get("timezone", "America/New_York")
        booking_url = kwargs.get("booking_url", "https://calendly.com/brix-automation/discovery-call")

        if not contact_id:
            raise ValueError("contact_id required")

        contact = db.query(Contact).filter_by(id=contact_id).first()
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")

        org = contact.organization
        report = db.query(ResearchReport).filter_by(organization_id=org.id).order_by(ResearchReport.created_at.desc()).first() if org else None
        hypotheses = report.hypotheses if report else []

        scheduled_time = (
            datetime.fromisoformat(scheduled_time_str)
            if scheduled_time_str
            else datetime.utcnow() + timedelta(days=2, hours=4)
        )

        discovery_qs = self.generate_discovery_questions(org.industry or "General Business", hypotheses)
        notes = (
            f"Pre-Call Briefing for {org.name} ({contact.full_name}):\n"
            f"- Industry: {org.industry}\n"
            f"- Observed signals: {len(report.verified_observations) if report else 0} verified observations\n"
            f"- Discovery Focus Questions:\n" + "\n".join([f"  * {q}" for q in discovery_qs])
        )

        meeting = Meeting(
            contact_id=contact.id,
            scheduled_time=scheduled_time,
            timezone=timezone,
            calendar_provider="CALENDLY",
            booking_url=booking_url,
            status="CONFIRMED",
            notes=notes
        )
        db.add(meeting)

        # Advance deal to MEETING
        if org:
            deal = db.query(Deal).filter_by(organization_id=org.id).first()
            if deal:
                deal.stage = "MEETING"
                deal.confidence = 0.80

        db.commit()
        db.refresh(meeting)

        return {
            "items_processed": 1,
            "meeting_id": meeting.id,
            "scheduled_time": meeting.scheduled_time.isoformat(),
            "timezone": timezone,
            "discovery_questions": discovery_qs
        }

agent09_meeting = MeetingBookingAgent()
