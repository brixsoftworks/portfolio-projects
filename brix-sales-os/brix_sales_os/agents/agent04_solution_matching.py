"""
brix_sales_os/agents/agent04_solution_matching.py
================================================
AGENT 04: SOLUTION MATCHING & OFFER RECOMMENDER
Matches qualified company needs to the verified 60 n8n workflow library.
Recommends Offer A (Digital Pack $297), Offer B (Turnkey Automation $750 + $150/mo),
or Offer C (Fractional AI Engineer $1,500/mo). Returns exact workflow IDs and
operational benefits without fabricated claims.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from brix_sales_os.agents.base import BaseAgent
from brix_sales_os.database.models import (
    Organization, ResearchReport, WorkflowRegistryItem, SolutionMatch, Deal
)

class SolutionMatchingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="AGENT_04_SOLUTION_MATCHING",
            name="Solution & Workflow Matcher"
        )

    def match_workflows_for_prospect(
        self,
        db: Session,
        industry: str,
        verified_obs: List[str],
        hypotheses: List[str]
    ) -> Dict[str, Any]:
        obs_strs = [str(x.get("observation", x) if isinstance(x, dict) else x) for x in verified_obs]
        hypo_strs = [str(y.get("hypothesis", y) if isinstance(y, dict) else y) for y in hypotheses]
        all_text = " ".join([industry] + obs_strs + hypo_strs).lower()
        
        # Match keywords to workflow tags
        matched_wfs = []
        all_wfs = db.query(WorkflowRegistryItem).all()
        
        for wf in all_wfs:
            score = 0
            # Tag match
            for t in (wf.tags or []):
                if t.lower() in all_text:
                    score += 2
            # Department match
            if "marketing" in all_text and wf.department == "Marketing & Content":
                score += 3
            if ("inquiry" in all_text or "form" in all_text or "lead" in all_text) and wf.department == "Sales & Growth":
                score += 3
            if ("support" in all_text or "faq" in all_text) and wf.department == "Customer Support":
                score += 3
            if ("invoice" in all_text or "billing" in all_text) and wf.department == "Finance & Legal":
                score += 3
            if ("developer" in all_text or "code" in all_text or "api" in all_text) and wf.department == "DevOps & Infrastructure":
                score += 3

            if score > 0:
                matched_wfs.append((wf, score))

        # Sort descending by match score
        matched_wfs.sort(key=lambda x: x[1], reverse=True)
        top_wfs = [item[0] for item in matched_wfs[:4]]
        
        # If no specific matches found, provide foundational sales/intake agents
        if not top_wfs:
            top_wfs = db.query(WorkflowRegistryItem).filter(
                WorkflowRegistryItem.id.in_(["WF-01", "WF-02", "WF-03", "WF-06"])
            ).all()

        wf_ids = [w.id for w in top_wfs]
        
        # Determine Offer recommendation
        # If agency/builder -> Offer A ($297 Complete Pack)
        # If enterprise/SaaS tech -> Offer C ($1,500/mo Retainer)
        # Otherwise -> Offer B ($750 setup + $150/mo Turnkey)
        if any(k in all_text for k in ["agency", "freelancer", "consultancy", "pack", "templates"]):
            offer = "OFFER_B" if "custom" in all_text else "OFFER_A"
        elif any(k in all_text for k in ["saas", "continuous", "complex", "developer", "retainer"]):
            offer = "OFFER_C"
        else:
            offer = "OFFER_B"

        if offer == "OFFER_A":
            setup_price = 297.0
            monthly_price = 0.0
            complexity = "Low (Instant Download & Import)"
            rationale = "Client operates as an agency/builder; instant access to all 60 workflows provides immediate reusable inventory."
            benefits = "Full 60-workflow library, immediate deployment capability, 0 cloud AI runtime costs when paired with local Ollama."
        elif offer == "OFFER_C":
            setup_price = 1500.0
            monthly_price = 1500.0
            complexity = "High (Custom Architecture & Integration)"
            rationale = "Client needs ongoing technical automation engineering, multi-step API synchronization, and LangChain/PostgreSQL development."
            benefits = "Dedicated senior automation architect, direct webhook error recovery, custom API adapters, weekly sprint improvements."
        else:
            setup_price = 750.0
            monthly_price = 150.0
            complexity = "Medium (Turnkey Configuration)"
            rationale = f"Client has specific intake/operational needs in {industry}. Direct deployment of targeted workflows ({', '.join(wf_ids[:2])})."
            benefits = "Turnkey deployment, zero maintenance overhead, automated notification routing, bi-directional CRM integration."

        return {
            "offer": offer,
            "workflow_ids": wf_ids,
            "setup_price": setup_price,
            "monthly_price": monthly_price,
            "complexity": complexity,
            "rationale": rationale,
            "benefits": benefits,
            "top_workflows": [
                {"id": w.id, "name": w.name, "dept": w.department, "complexity": w.complexity}
                for w in top_wfs
            ]
        }

    def run(self, db: Session, **kwargs) -> Dict[str, Any]:
        organization_id = kwargs.get("organization_id")
        if not organization_id:
            raise ValueError("organization_id required")

        org = db.query(Organization).filter_by(id=organization_id).first()
        if not org:
            raise ValueError(f"Organization {organization_id} not found")

        report = db.query(ResearchReport).filter_by(organization_id=org.id).order_by(ResearchReport.created_at.desc()).first()
        verified_obs = report.verified_observations if report else []
        hypotheses = report.hypotheses if report else []

        match_res = self.match_workflows_for_prospect(
            db=db,
            industry=org.industry or "",
            verified_obs=verified_obs,
            hypotheses=hypotheses
        )

        solution_match = SolutionMatch(
            organization_id=org.id,
            recommended_offer=match_res["offer"],
            matched_workflow_ids=match_res["workflow_ids"],
            implementation_complexity=match_res["complexity"],
            proposed_setup_price=match_res["setup_price"],
            proposed_monthly_price=match_res["monthly_price"],
            matching_rationale=match_res["rationale"]
        )
        db.add(solution_match)

        # Update deal matched offer and amount
        deal = db.query(Deal).filter_by(organization_id=org.id).first()
        if deal:
            deal.matched_offer = match_res["offer"]
            deal.amount = match_res["setup_price"]

        db.commit()
        db.refresh(solution_match)

        return {
            "items_processed": 1,
            "solution_match_id": solution_match.id,
            "recommended_offer": solution_match.recommended_offer,
            "matched_workflow_ids": solution_match.matched_workflow_ids,
            "setup_price": solution_match.proposed_setup_price,
            "monthly_price": solution_match.proposed_monthly_price,
            "benefits": match_res["benefits"]
        }

agent04_matching = SolutionMatchingAgent()
