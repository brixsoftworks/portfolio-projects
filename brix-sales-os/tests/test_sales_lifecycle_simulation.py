"""
tests/test_sales_lifecycle_simulation.py
========================================
Comprehensive End-to-End Simulation Test:
Executes the full 12-agent autonomous sales lifecycle from lead ingestion
to research, scoring, matching, drafting, approval, reply triage,
meeting booking, proposal PDF generation, idempotent payment closing,
and client onboarding workspace creation.
"""

import os
from pathlib import Path
from brix_sales_os.database.session import SessionLocal, init_db
from brix_sales_os.database.models import (
    Organization, Contact, Deal, Proposal, Invoice, Payment, Project
)
from brix_sales_os.agents import (
    agent01_discovery, agent02_intelligence, agent03_scoring, agent04_matching,
    agent05_demo, agent06_copywriter, agent07_campaign, agent08_inbox,
    agent09_meeting, agent10_proposal, agent11_closing, agent12_onboarding
)

def test_full_sales_lifecycle():
    init_db()
    db = SessionLocal()

    test_domain = "simulated_growth_agency.com"
    # Clean previous run if present
    old_org = db.query(Organization).filter_by(domain=test_domain).first()
    if old_org:
        for inv in db.query(Invoice).filter_by(organization_id=old_org.id).all():
            db.query(Payment).filter_by(invoice_id=inv.id).delete()
            db.delete(inv)
        db.query(Project).filter_by(organization_id=old_org.id).delete()
        db.query(Proposal).filter_by(organization_id=old_org.id).delete()
        db.query(Deal).filter_by(organization_id=old_org.id).delete()
        db.query(Contact).filter_by(organization_id=old_org.id).delete()
        db.delete(old_org)
        db.commit()

    # 1. Lead Discovery (Agent 01)
    prospects = [{
        "company_name": "Simulated Growth Agency",
        "website": f"https://{test_domain}",
        "industry": "Digital Marketing Agency",
        "country": "United States",
        "employee_count": "20-50",
        "contact_name": "David Miller",
        "contact_role": "Managing Director",
        "contact_email": "david@simulated_growth_agency.com",
        "budget": 750
    }]
    disc_res = agent01_discovery.execute(prospects=prospects, source_name="Simulation Suite")
    assert disc_res["items_processed"] == 1
    org_id = disc_res["ingested_leads"][0]["organization_id"]
    contact_id = disc_res["ingested_leads"][0]["contact_id"]

    # 2. Website Intelligence (Agent 02)
    research_res = agent02_intelligence.execute(organization_id=org_id)
    assert research_res["items_processed"] == 1
    assert len(research_res["verified_observations"]) > 0
    assert len(research_res["hypotheses"]) > 0

    # 3. AI Lead Scoring (Agent 03)
    score_res = agent03_scoring.execute(organization_id=org_id)
    assert score_res["items_processed"] == 1
    assert score_res["total_score"] >= 60, f"Expected high/medium score, got {score_res['total_score']}"

    # 4. Solution Matching (Agent 04)
    match_res = agent04_matching.execute(organization_id=org_id)
    assert match_res["items_processed"] == 1
    assert len(match_res["matched_workflow_ids"]) > 0
    assert match_res["setup_price"] > 0

    # 5. Personalized Demo Generator (Agent 05)
    demo_res = agent05_demo.execute(organization_id=org_id)
    assert demo_res["items_processed"] == 1
    assert "demo_id" in demo_res

    # 6. Outreach Copywriter (Agent 06)
    copy_res = agent06_copywriter.execute(organization_id=org_id)
    assert copy_res["items_processed"] == 1
    msg_id = copy_res["message_id"]
    assert copy_res["status"] == "PENDING_APPROVAL"

    # 7. Outreach Campaign Gatekeeper (Agent 07)
    # Approve message
    app_res = agent07_campaign.execute(action="APPROVE", message_id=msg_id)
    assert app_res["status"] == "APPROVED"
    # Dispatch queue
    disp_res = agent07_campaign.execute(action="DISPATCH")
    assert disp_res["dispatched_count"] >= 1

    # 8. Inbox & Conversation Manager (Agent 08)
    # Simulate inbound positive reply from prospect
    inbox_res = agent08_inbox.execute(
        contact_id=contact_id,
        incoming_message="Hi Mullai, this looks very relevant to our intake forms. How much is the setup?"
    )
    assert inbox_res["intent"] == "PRICING_INQUIRY"
    assert len(inbox_res["suggested_reply"]) > 20

    # 9. Meeting Booking (Agent 09)
    meet_res = agent09_meeting.execute(
        contact_id=contact_id,
        timezone="America/New_York"
    )
    assert meet_res["items_processed"] == 1
    assert len(meet_res["discovery_questions"]) >= 3

    # 10. Proposal Generator (Agent 10)
    prop_res = agent10_proposal.execute(organization_id=org_id)
    assert prop_res["items_processed"] == 1
    pdf_path = prop_res["pdf_path"]
    assert Path(pdf_path).exists()
    assert Path(pdf_path).stat().st_size > 1000

    # 11. Sales Closing Assistant (Agent 11)
    # Issue invoice & process verified payment webhook
    inv_res = agent11_closing.execute(
        action="ISSUE_INVOICE",
        organization_id=org_id,
        amount_usd=750.0
    )
    invoice_number = inv_res["invoice_number"]

    import time
    test_idemp = f"idemp_{int(time.time() * 1000)}"

    # Process Payment Webhook
    pay_res = agent11_closing.execute(
        action="PROCESS_PAYMENT",
        invoice_number=invoice_number,
        amount_usd=750.0,
        transaction_id=f"tx_{test_idemp}",
        idempotency_key=test_idemp
    )
    assert pay_res["success"] is True
    assert pay_res["deal_stage"] == "WON"

    # Test idempotency (repeat same webhook)
    dup_res = agent11_closing.execute(
        action="PROCESS_PAYMENT",
        invoice_number=invoice_number,
        amount_usd=750.0,
        transaction_id=f"tx_{test_idemp}",
        idempotency_key=test_idemp
    )
    assert dup_res["idempotent_duplicate"] is True

    # 12. Client Onboarding (Agent 12)
    onboard_res = agent12_onboarding.execute(organization_id=org_id)
    assert onboard_res["items_processed"] == 1
    assert Path(onboard_res["workspace_path"]).exists()
    assert Path(onboard_res["workspace_path"] + "/PROJECT_BRIEF.md").exists()

    db.close()
