"""
brix_sales_os/agents/agent05_demo_generator.py
=============================================
AGENT 05: PERSONALIZED DEMO GENERATOR
Generates lightweight proof-of-value demos (interactive HTML dashboards,
workflow pipeline diagrams, and synthetic execution traces) for qualified leads.
Uses a compute budget and caching to avoid wasteful processing.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from brix_sales_os.agents.base import BaseAgent
from brix_sales_os.database.models import (
    Organization, SolutionMatch, Demo, LeadScore
)

class DemoGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="AGENT_05_DEMO_GENERATOR",
            name="Personalized Proof-of-Value Demo Generator"
        )

    def render_interactive_demo_html(
        self,
        company_name: str,
        industry: str,
        matched_wfs: list,
        synthetic_payload: dict
    ) -> str:
        wf_list_html = "".join([
            f"<li style='margin-bottom:8px;'><strong>{wf}</strong> — Ingests lead payload &bull; Normalizes schema &bull; Dispatches CRM sync</li>"
            for wf in matched_wfs
        ])

        return f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 28px; border-radius: 12px; border: 1px solid #334155; max-width: 720px; margin: 0 auto;">
  <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid #1e293b; padding-bottom: 14px; margin-bottom: 20px;">
    <h3 style="margin:0; font-size: 20px; color: #38bdf8;"> Brix AI Automation Proof-of-Concept</h3>
    <span style="background: rgba(34, 197, 94, 0.2); color: #4ade80; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;">Active Mock Pipeline</span>
  </div>
  <p style="color: #94a3b8; font-size: 14px; line-height: 1.5;">
    Custom workflow simulation tailored for <strong>{company_name}</strong> ({industry}). 
    Demonstrates how incoming requests are captured, routed through local AI nodes, and synchronized without manual intervention.
  </p>
  <div style="background: #1e293b; border-radius: 8px; padding: 16px; margin: 18px 0;">
    <h4 style="margin: 0 0 10px 0; font-size: 14px; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.05em;">Activated Workflows</h4>
    <ul style="margin:0; padding-left: 20px; font-size: 13px; color: #e2e8f0;">
      {wf_list_html}
    </ul>
  </div>
  <div style="background: #020617; border-radius: 8px; padding: 14px; font-family: monospace; font-size: 12px; color: #22c55e;">
    <div style="color: #64748b; margin-bottom: 6px;">// Sample Normalized Inbound Payload</div>
    <pre style="margin:0; overflow-x: auto;">{synthetic_payload}</pre>
  </div>
  <div style="margin-top: 20px; text-align: right;">
    <span style="font-size: 12px; color: #64748b;">Engine: Brix Sales OS &bull; Local GPU Verified</span>
  </div>
</div>
"""

    def run(self, db: Session, **kwargs) -> Dict[str, Any]:
        organization_id = kwargs.get("organization_id")
        if not organization_id:
            raise ValueError("organization_id required")

        org = db.query(Organization).filter_by(id=organization_id).first()
        if not org:
            raise ValueError(f"Organization {organization_id} not found")

        # Check existing demo cache
        existing = db.query(Demo).filter_by(organization_id=org.id).first()
        if existing and not kwargs.get("force_refresh"):
            return {
                "items_processed": 1,
                "cached": True,
                "demo_id": existing.id,
                "demo_title": existing.title
            }

        # Check priority: don't spend compute on low priority unless forced
        score = db.query(LeadScore).filter_by(organization_id=org.id).order_by(LeadScore.created_at.desc()).first()
        if score and score.priority_level == "LOW" and not kwargs.get("force_refresh"):
            return {
                "items_processed": 0,
                "skipped": True,
                "reason": "Lead priority is LOW; demo generation budget preserved."
            }

        solution_match = db.query(SolutionMatch).filter_by(organization_id=org.id).order_by(SolutionMatch.created_at.desc()).first()
        matched_wfs = solution_match.matched_workflow_ids if solution_match else ["WF-01", "WF-02"]

        synthetic_payload = {
            "source": f"inbound_{org.domain}",
            "prospect_intent": "Schedule discovery call for AI automation",
            "extracted_need": f"Automated intake & lead qualification in {org.industry}",
            "assigned_workflow": matched_wfs[0],
            "execution_status": "SUCCESS",
            "latency_ms": 18
        }

        demo_html = self.render_interactive_demo_html(
            company_name=org.name,
            industry=org.industry or "Commercial Services",
            matched_wfs=matched_wfs,
            synthetic_payload=synthetic_payload
        )

        demo = Demo(
            organization_id=org.id,
            solution_match_id=solution_match.id if solution_match else None,
            demo_type="SAMPLE_DASHBOARD",
            title=f"AI Automation Interactive Walkthrough — {org.name}",
            content_html=demo_html,
            synthetic_data=synthetic_payload
        )
        db.add(demo)
        db.commit()
        db.refresh(demo)

        return {
            "items_processed": 1,
            "demo_id": demo.id,
            "title": demo.title,
            "matched_workflows": matched_wfs
        }

agent05_demo = DemoGeneratorAgent()
