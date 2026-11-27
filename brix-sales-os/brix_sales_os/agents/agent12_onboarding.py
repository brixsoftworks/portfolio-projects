"""
brix_sales_os/agents/agent12_onboarding.py
=========================================
AGENT 12: CLIENT ONBOARDING & WORKSPACE PROVISIONER
Initiates project workspaces upon confirmed payment, creates security-compliant
credential collection forms (never plain email), generates implementation checklists,
and maps verified n8n workflows to deployment tasks.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from brix_sales_os.agents.base import BaseAgent
from brix_sales_os.database.models import (
    Organization, Deal, Project, SolutionMatch
)
from brix_sales_os.config import DATA_DIR

CLIENTS_DIR = DATA_DIR / "clients"
CLIENTS_DIR.mkdir(parents=True, exist_ok=True)

class ClientOnboardingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="AGENT_12_ONBOARDING",
            name="Client Onboarding & Project Workspace Provisioner"
        )

    def run(self, db: Session, **kwargs) -> Dict[str, Any]:
        organization_id = kwargs.get("organization_id")
        deal_id = kwargs.get("deal_id")

        if not organization_id:
            raise ValueError("organization_id required")

        org = db.query(Organization).filter_by(id=organization_id).first()
        if not org:
            raise ValueError(f"Organization {organization_id} not found")

        deal = db.query(Deal).filter_by(id=deal_id).first() if deal_id else db.query(Deal).filter_by(organization_id=org.id).first()
        solution = db.query(SolutionMatch).filter_by(organization_id=org.id).order_by(SolutionMatch.created_at.desc()).first()
        matched_wfs = solution.matched_workflow_ids if solution else ["WF-01", "WF-02"]

        # Create isolated client workspace folder
        safe_domain = org.domain.replace(".", "_")
        workspace_path = CLIENTS_DIR / safe_domain
        workspace_path.mkdir(parents=True, exist_ok=True)

        # Build secure onboarding instructions & checklist
        checklist = [
            {"task": "Schedule technical kickoff call", "status": "PENDING"},
            {
                "task": "Issue secure Bitwarden / 1Password credential vault share for API keys",
                "status": "PENDING",
                "security_note": "NEVER send credentials via unencrypted email"
            },
            {"task": f"Import workflows ({', '.join(matched_wfs)}) into client n8n instance", "status": "PENDING"},
            {"task": "Configure webhook endpoints & database connections", "status": "PENDING"},
            {"task": "Run end-to-end sandbox testing with mock payloads", "status": "PENDING"},
            {"task": "Client acceptance signoff & production switchover", "status": "PENDING"}
        ]

        # Write workspace README
        readme_file = workspace_path / "PROJECT_BRIEF.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(f"""# Project Workspace: {org.name}
- **Domain:** {org.domain}
- **Industry:** {org.industry}
- **Matched Solution:** {solution.recommended_offer if solution else 'OFFER_B'}
- **Workflows:** {', '.join(matched_wfs)}
- **Provisioned At:** {workspace_path}

## Secure Credential Protocol:
Credentials must be transferred via an encrypted password manager link (1Password/Bitwarden).
Never request or accept plaintext API keys or passwords over ordinary email.
""")

        project = Project(
            organization_id=org.id,
            deal_id=deal.id if deal else None,
            project_name=f"Automation Deployment — {org.name}",
            status="ONBOARDING",
            checklist=checklist,
            workspace_path=str(workspace_path)
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        return {
            "items_processed": 1,
            "project_id": project.id,
            "workspace_path": project.workspace_path,
            "checklist_items": len(checklist),
            "status": project.status
        }

agent12_onboarding = ClientOnboardingAgent()
