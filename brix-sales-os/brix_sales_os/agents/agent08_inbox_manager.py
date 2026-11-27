"""
brix_sales_os/agents/agent08_inbox_manager.py
============================================
AGENT 08: INBOX & CONVERSATION MANAGER
Classifies incoming prospect replies, immediately suppresses opt-outs,
updates CRM deal stages, and drafts context-aware replies for human review.
Never binds the business to unapproved terms.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from brix_sales_os.agents.base import BaseAgent
from brix_sales_os.database.models import (
    Contact, Organization, Conversation, SuppressionEntry, Deal
)
from brix_sales_os.core.ollama_client import ollama_client
from brix_sales_os.core.audit import log_audit_event
from brix_sales_os.config import settings

class InboxManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="AGENT_08_INBOX_MANAGER",
            name="Inbox Triage & Conversation Specialist"
        )

    def classify_intent(self, text: str) -> str:
        clean = text.lower().strip()
        if any(w in clean for w in ["unsubscribe", "remove me", "stop emailing", "opt out", "do not contact"]):
            return "UNSUBSCRIBE"
        if any(w in clean for w in ["not interested", "no thanks", "pass", "not looking"]):
            return "NOT_INTERESTED"
        if any(w in clean for w in ["out of office", "on leave", "vacation", "auto-reply"]):
            return "OUT_OF_OFFICE"
        if any(w in clean for w in ["calendar", "call", "zoom", "meet", "schedule", "talk next week"]):
            return "MEETING_REQUEST"
        if any(w in clean for w in ["pricing", "cost", "how much", "rate", "quote", "budget"]):
            return "PRICING_INQUIRY"
        if any(w in clean for w in ["send details", "more info", "case study", "how does it work", "overview"]):
            return "REQUESTING_INFORMATION"
        if any(w in clean for w in ["yes", "interested", "tell me more", "sounds good", "love to see it"]):
            return "INTERESTED"
        return "UNCLEAR"

    def draft_reply_for_intent(self, intent: str, contact_name: str, org_name: str) -> str:
        first_name = contact_name.split()[0] if contact_name else "there"
        if intent == "MEETING_REQUEST":
            return f"""Hi {first_name},

Glad to connect. Here is our direct scheduling link: https://calendly.com/brix-automation/discovery-call

Feel free to pick any slot that fits your timezone, or let me know a couple of times that suit you.

Best,
Mullai Nathan
Brix Softworks"""

        elif intent == "PRICING_INQUIRY":
            return f"""Hi {first_name},

Thanks for asking. Our automation solutions typically fall into two options:
1. Turnkey Done-for-You deployment: Starts at $750 setup with an optional $150/mo maintenance retainer.
2. Complete 60-Agent Workflow Pack: $297 instant self-hosted license.

Happy to tailor the exact scope to {org_name}'s existing tools. Would a quick 10-minute walkthrough help?

Best,
Mullai Nathan
Brix Softworks"""

        elif intent == "REQUESTING_INFORMATION" or intent == "INTERESTED":
            return f"""Hi {first_name},

Thanks for following up. We build modular n8n workflows that connect your forms, CRM, and communication channels without recurring cloud API markup.

I can share a short interactive walkthrough customized for {org_name}. What is the main workflow bottleneck your team is looking to solve right now?

Best,
Mullai Nathan
Brix Softworks"""

        return ""

    def run(self, db: Session, **kwargs) -> Dict[str, Any]:
        contact_id = kwargs.get("contact_id")
        incoming_message = kwargs.get("incoming_message", "").strip()

        if not contact_id or not incoming_message:
            raise ValueError("contact_id and incoming_message required")

        contact = db.query(Contact).filter_by(id=contact_id).first()
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")

        org = contact.organization
        intent = self.classify_intent(incoming_message)

        # Handle Immediate Suppression on Unsubscribe
        if intent == "UNSUBSCRIBE":
            existing_sup = db.query(SuppressionEntry).filter_by(email=contact.email).first()
            if not existing_sup:
                sup = SuppressionEntry(
                    email=contact.email,
                    domain=org.domain if org else None,
                    reason="PROSPECT_UNSUBSCRIBE_REPLY"
                )
                db.add(sup)
                db.commit()

            log_audit_event(
                action="CONTACT_AUTO_SUPPRESSED",
                actor="INBOX_MANAGER",
                target_entity="contacts",
                target_id=contact.id,
                details={"email": contact.email, "reason": "Unsubscribe request received"}
            )

        # Update Deal Stage if positive intent
        deal = db.query(Deal).filter_by(organization_id=org.id).first() if org else None
        if deal:
            if intent in ("INTERESTED", "MEETING_REQUEST", "PRICING_INQUIRY"):
                deal.stage = "INTERESTED"
                deal.confidence = 0.75
            elif intent in ("NOT_INTERESTED", "UNSUBSCRIBE"):
                deal.stage = "LOST"
                deal.confidence = 0.0
            db.commit()

        # Draft proposed reply
        suggested_reply = self.draft_reply_for_intent(intent, contact.full_name, org.name if org else "")

        conv = Conversation(
            contact_id=contact.id,
            incoming_message=incoming_message,
            intent_classification=intent,
            ai_suggested_reply=suggested_reply,
            status="AWAITING_REVIEW"
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

        return {
            "items_processed": 1,
            "conversation_id": conv.id,
            "intent": intent,
            "suppressed": intent == "UNSUBSCRIBE",
            "suggested_reply": suggested_reply
        }

agent08_inbox = InboxManagerAgent()
