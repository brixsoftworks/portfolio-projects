"""
brix_sales_os/services/pdf_service.py
====================================
Generates professional, styled PDF proposals and Statements of Work (SOWs)
using reportlab.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.pdfgen import canvas

def generate_proposal_pdf(
    file_path: Path,
    client_name: str,
    company_name: str,
    proposal_title: str,
    client_problem: str,
    proposed_solution: str,
    selected_workflows: list,
    setup_price: float,
    monthly_retainer: float,
    timeline_weeks: int
) -> str:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a')
    )
    
    subhead_style = ParagraphStyle(
        'DocSubHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#475569')
    )

    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#0284c7'),
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1e293b')
    )

    story = []

    # Title Banner
    story.append(Paragraph("BRIX SOFTWORKS", ParagraphStyle('Brand', fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#0284c7'))))
    story.append(Paragraph(proposal_title, header_style))
    story.append(Paragraph(f"Prepared for: <strong>{company_name}</strong> &bull; Attention: {client_name}", subhead_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=14))

    # 1. Executive Summary & Problem
    story.append(Paragraph("1. Identified Challenge & Operational Opportunity", section_title))
    story.append(Paragraph(client_problem, body_style))
    story.append(Spacer(1, 10))

    # 2. Proposed Architecture & Solution
    story.append(Paragraph("2. Proposed Modular Automation Architecture", section_title))
    story.append(Paragraph(proposed_solution, body_style))
    story.append(Spacer(1, 10))

    # 3. Selected Workflows Table
    story.append(Paragraph("3. Target n8n Workflows Included", section_title))
    table_data = [["Workflow ID", "Scope & Deliverable", "Execution Engine"]]
    for wf in selected_workflows:
        table_data.append([wf, "Production n8n blueprint & webhooks", "Local GPU / Private Cloud"])
    
    t = Table(table_data, colWidths=[110, 260, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    # 4. Commercial Terms & Investment
    story.append(Paragraph("4. Investment & Implementation Schedule", section_title))
    pricing_data = [
        ["Deliverable", "Timeline", "Fee (USD)"],
        ["Initial Architecture, Configuration & Testing", f"{timeline_weeks} Weeks", f"${setup_price:,.2f} Fixed"],
        ["Ongoing Maintenance, Monitoring & Retainer", "Monthly (Optional)", f"${monthly_retainer:,.2f} / Month"]
    ]
    pt = Table(pricing_data, colWidths=[240, 140, 140])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(pt)
    story.append(Spacer(1, 14))

    # 5. Acceptance & Scope Terms
    story.append(Paragraph("5. Scope & Acceptance Terms", section_title))
    scope_text = (
        "&bull; <strong>Scope Exclusions:</strong> Custom non-API legacy software modification without documented webhooks.<br/>"
        "&bull; <strong>Acceptance Criteria:</strong> Tested end-to-end execution of all agreed workflows with audit logging.<br/>"
        "&bull; <strong>Data Privacy:</strong> 100% ownership of source code, configurations, and API credentials retained by client."
    )
    story.append(Paragraph(scope_text, body_style))
    story.append(Spacer(1, 18))

    # Signoff block
    signoff_data = [
        ["Accepted by Brix Softworks:", f"Accepted by {company_name}:"],
        ["\n\nMullai Nathan\nSenior Automation Architect", "\n\nAuthorized Signature / Name\nDate:"]
    ]
    st = Table(signoff_data, colWidths=[260, 260])
    st.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('LINEBELOW', (0,1), (0,1), 1, colors.HexColor('#94a3b8')),
        ('LINEBELOW', (1,1), (1,1), 1, colors.HexColor('#94a3b8')),
    ]))
    story.append(st)

    doc.build(story)
    return str(file_path)
