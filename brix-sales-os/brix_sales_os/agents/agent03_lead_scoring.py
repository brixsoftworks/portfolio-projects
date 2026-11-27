"""
brix_sales_os/agents/agent03_lead_scoring.py
===========================================
AGENT 03: AI LEAD SCORING ENGINE
Scores prospects on a 0-100 scale using configurable criteria:
  - Industry fit (25 pts)
  - Evidence of automation opportunity (25 pts)
  - Company size fit (15 pts)
  - Relevant buying signal (15 pts)
  - Contact quality (10 pts)
  - Geographic & service fit (10 pts)
Categorizes into HIGH (80-100), MEDIUM (60-79), LOW (<60) with stored rationale.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from brix_sales_os.agents.base import BaseAgent
from brix_sales_os.database.models import Organization, Contact, ResearchReport, LeadScore, Deal

class LeadScoringAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="AGENT_03_LEAD_SCORING",
            name="AI Lead Qualification & Scoring Engine"
        )
        # Default Weights
        self.weights = {
            "industry_fit": 25,
            "evidence_opportunity": 25,
            "company_size": 15,
            "buying_signal": 15,
            "contact_quality": 10,
            "geo_service_fit": 10,
        }

    def score_organization(self, org: Organization, contact: Optional[Contact], report: Optional[ResearchReport]) -> Dict[str, Any]:
        # 1. Industry fit (max 25)
        high_priority_industries = [
            "digital marketing", "marketing agency", "web development", "software",
            "saas", "e-commerce", "recruitment", "real estate", "consulting"
        ]
        org_ind = (org.industry or "").lower()
        if any(h in org_ind for h in high_priority_industries):
            industry_score = 25
        elif org.industry:
            industry_score = 15
        else:
            industry_score = 10  # Never zero solely for missing info

        # 2. Evidence of automation opportunity (max 25)
        obs_count = len(report.verified_observations) if report else 0
        hypo_count = len(report.hypotheses) if report else 0
        if obs_count >= 2 or hypo_count >= 2:
            evidence_score = 25
        elif obs_count > 0 or hypo_count > 0:
            evidence_score = 18
        else:
            evidence_score = 12

        # 3. Company size fit (max 15)
        size = (org.employee_count or "").lower()
        if any(s in size for s in ["10-50", "11-50", "20-100", "small", "mid"]):
            size_score = 15
        elif any(s in size for s in ["1-10", "solo", "seed"]):
            size_score = 12
        else:
            size_score = 10

        # 4. Relevant buying signal (max 15)
        # Check if research observed forms, active growth, or inbound inquiries
        has_signals = False
        if report:
            for obs in (report.verified_observations or []):
                obs_str = str(obs.get("observation", obs) if isinstance(obs, dict) else obs).lower()
                if any(k in obs_str for k in ["form", "booking", "chat", "hiring", "lead"]):
                    has_signals = True
                    break
        buying_signal_score = 15 if has_signals else 10

        # 5. Contact quality (max 10)
        if contact and contact.email:
            if contact.is_decision_maker and contact.full_name:
                contact_score = 10
            else:
                contact_score = 8
        else:
            contact_score = 4

        # 6. Geographic & service fit (max 10)
        country = (org.country or "").lower()
        tier_one_countries = ["united states", "usa", "us", "united kingdom", "uk", "australia", "canada", "germany", "switzerland"]
        if any(c in country for c in tier_one_countries):
            geo_score = 10
        elif org.country:
            geo_score = 7
        else:
            geo_score = 5

        total = industry_score + evidence_score + size_score + buying_signal_score + contact_score + geo_score
        total = min(100, max(0, total))

        if total >= 80:
            priority = "HIGH"
        elif total >= 60:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        rationale = (
            f"Score {total}/100 ({priority}). Industry match: {industry_score}/25. "
            f"Opportunity evidence: {evidence_score}/25. Company size fit: {size_score}/15. "
            f"Buying signals: {buying_signal_score}/15. Contact completeness: {contact_score}/10. "
            f"Geographic target fit: {geo_score}/10."
        )

        return {
            "total_score": total,
            "priority": priority,
            "industry_fit": industry_score,
            "evidence": evidence_score,
            "company_size": size_score,
            "buying_signal": buying_signal_score,
            "contact_quality": contact_score,
            "geo_service_fit": geo_score,
            "rationale": rationale
        }

    def run(self, db: Session, **kwargs) -> Dict[str, Any]:
        organization_id = kwargs.get("organization_id")
        if not organization_id:
            raise ValueError("organization_id required")

        org = db.query(Organization).filter_by(id=organization_id).first()
        if not org:
            raise ValueError(f"Organization {organization_id} not found")

        contact = db.query(Contact).filter_by(organization_id=org.id).first()
        report = db.query(ResearchReport).filter_by(organization_id=org.id).order_by(ResearchReport.created_at.desc()).first()

        scores = self.score_organization(org, contact, report)

        lead_score = LeadScore(
            organization_id=org.id,
            total_score=scores["total_score"],
            priority_level=scores["priority"],
            industry_fit_score=scores["industry_fit"],
            evidence_score=scores["evidence"],
            company_size_score=scores["company_size"],
            buying_signal_score=scores["buying_signal"],
            contact_quality_score=scores["contact_quality"],
            geo_service_fit_score=scores["geo_service_fit"],
            scoring_rationale=scores["rationale"]
        )
        db.add(lead_score)

        # Update Deal stage and confidence if high
        deal = db.query(Deal).filter_by(organization_id=org.id).first()
        if deal:
            if scores["priority"] in ("HIGH", "MEDIUM"):
                deal.stage = "QUALIFIED"
                deal.confidence = scores["total_score"] / 100.0

        db.commit()
        db.refresh(lead_score)

        return {
            "items_processed": 1,
            "score_id": lead_score.id,
            "total_score": lead_score.total_score,
            "priority": lead_score.priority_level,
            "rationale": lead_score.scoring_rationale
        }

agent03_scoring = LeadScoringAgent()
