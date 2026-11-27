"""
brix_sales_os/agents/agent10_proposal_generator.py
=================================================
AGENT 10: PROPOSAL GENERATOR & SOW COMPILER
Generates comprehensive technical proposals and Statements of Work (SOWs)
referencing exact n8n workflow IDs, timelines, pricing, and scope boundaries.
Exports cleanly rendered PDFs and keeps them in DRAFT mode awaiting human approval.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from brix_sales_os.agents.base import BaseAgent
from brix_sales_os.database.models import (
    Organization, Contact, Deal, SolutionMatch, ResearchReport, Proposal
)
from brix_sales_os.services.pdf_service import generate_proposal_pdf
from brix_sales_os.config import settings, DATA_DIR

PROPOSALS_DIR = DATA_DIR / "proposals"
PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)

class ProposalGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="AGENT_10_PROPOSAL_GENERATOR",
            name="Technical Proposal & SOW Architect"
        )

    def run(self, db: Session, **kwargs) -> Dict[str, Any]:
        organization_id = kwargs.get("organization_id")
        if not organization_id:
            raise ValueError("organization_id required")

        org = db.query(Organization).filter_by(id=organization_id).first()
        if not org:
            raise ValueError(f"Organization {organization_id} not found")

        contact = db.query(Contact).filter_by(organization_id=org.id).first()
        deal = db.query(Deal).filter_by(organization_id=org.id).first()
        if not deal:
            deal = Deal(
                organization_id=org.id,
                title=f"AI Automation Project — {org.name}",
                stage="PROPOSAL",
                amount=750.0
            )
            db.add(deal)
            db.commit()
            db.refresh(deal)

        solution = db.query(SolutionMatch).filter_by(organization_id=org.id).order_by(SolutionMatch.created_at.desc()).first()
        report = db.query(ResearchReport).filter_by(organization_id=org.id).order_by(ResearchReport.created_at.desc()).first()

        selected_wfs = solution.matched_workflow_ids if solution else ["WF-01", "WF-02"]
        setup_price = solution.proposed_setup_price if solution else 750.0
        monthly_retainer = solution.proposed_monthly_price if solution else 150.0

        client_problem = (
            f"{org.name} currently operates in the {org.industry} sector with manual touchpoints "
            f"across lead intake, customer communication, and internal CRM/notification routing. "
            f"Observed signals indicate opportunities to eliminate manual data entry and decrease response latency."
        )

        proposed_solution = (
            f"Brix Softworks will deploy a dedicated n8n automation pipeline tailored to {org.name}. "
            f"The architecture includes automated webhook triggers, payload normalization, error retry logic, "
            f"and direct integration with existing CRM/database storage. Solution includes: {', '.join(selected_wfs)}."
        )

        proposal_id = f"prop_{org.domain.replace('.', '_')}"
        pdf_path = PROPOSALS_DIR / f"{proposal_id}.pdf"

        # Generate actual PDF file
        generate_proposal_pdf(
            file_path=pdf_path,
            client_name=contact.full_name if contact else "Executive Team",
            company_name=org.name,
            proposal_title=f"AI Automation Statement of Work — {org.name}",
            client_problem=client_problem,
            proposed_solution=proposed_solution,
            selected_workflows=selected_wfs,
            setup_price=setup_price,
            monthly_retainer=monthly_retainer,
            timeline_weeks=2
        )

        proposal = Proposal(
            deal_id=deal.id,
            organization_id=org.id,
            client_problem=client_problem,
            proposed_solution=proposed_solution,
            selected_workflow_ids=selected_wfs,
            timeline_weeks=2,
            setup_price_usd=setup_price,
            monthly_retainer_usd=monthly_retainer,
            pdf_path=str(pdf_path),
            status="DRAFT"  # Requires human approval before sending
        )
        db.add(proposal)

        deal.stage = "PROPOSAL"
        deal.amount = setup_price
        deal.confidence = 0.85
        db.commit()
        db.refresh(proposal)

        return {
            "items_processed": 1,
            "proposal_id": proposal.id,
            "deal_id": deal.id,
            "pdf_path": proposal.pdf_path,
            "setup_price": setup_price,
            "monthly_retainer": monthly_retainer,
            "status": proposal.status
        }

agent10_proposal = ProposalGeneratorAgent()
