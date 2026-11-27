"""
tests/test_proposal_pdf.py
==========================
Unit tests for ReportLab proposal PDF generation.
"""

from pathlib import Path
from brix_sales_os.services.pdf_service import generate_proposal_pdf

def test_pdf_rendering(tmp_path):
    pdf_out = tmp_path / "test_proposal.pdf"
    res_path = generate_proposal_pdf(
        file_path=pdf_out,
        client_name="Alex CTO",
        company_name="FlowPulse Labs",
        proposal_title="AI Automation Statement of Work — FlowPulse Labs",
        client_problem="Manual lead intake and qualification causing delayed response times.",
        proposed_solution="Deployment of modular n8n lead intake, scoring, and CRM synchronization workflows.",
        selected_workflows=["WF-01", "WF-02", "WF-03"],
        setup_price=750.0,
        monthly_retainer=150.0,
        timeline_weeks=2
    )
    assert Path(res_path).exists()
    assert Path(res_path).stat().st_size > 1000, "PDF file must be non-empty and formatted"
