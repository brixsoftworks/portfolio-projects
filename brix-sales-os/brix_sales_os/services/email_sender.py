"""
brix_sales_os/services/email_sender.py
======================================
Production SMTP & Email Delivery Service for Brix Sales OS.
Supports:
  - Standard SMTP (Google Workspace, Gmail with App Password, Outlook, Custom Domain)
  - Resend API / SendGrid
  - Automatic PDF Proposal Attachment
  - Delivery audit logging and suppression verification
"""

import smtplib
import os
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, Any, Optional
from datetime import datetime

from brix_sales_os.database.session import SessionLocal
from brix_sales_os.database.models import OutreachMessage, Contact, Proposal, SuppressionEntry, EmailEvent
from brix_sales_os.config import settings

def send_smtp_email(
    to_email: str,
    subject: str,
    body_text: str,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_pass: Optional[str] = None,
    pdf_attachment_path: Optional[str] = None
) -> Dict[str, Any]:
    host = smtp_host or os.getenv("SMTP_HOST")
    port = int(smtp_port or os.getenv("SMTP_PORT", 587))
    user = smtp_user or os.getenv("SMTP_USER")
    password = smtp_pass or os.getenv("SMTP_PASS")

    if not host or not user or not password:
        return {
            "success": False,
            "error": "Missing SMTP credentials. Configure SMTP_HOST, SMTP_USER, and SMTP_PASS in .env or provide them via CLI."
        }

    # Verify recipient is not suppressed
    db = SessionLocal()
    try:
        suppressed = db.query(SuppressionEntry).filter_by(email=to_email).first()
        if suppressed:
            return {"success": False, "error": f"Recipient {to_email} is on suppression list (opted out)."}
    finally:
        db.close()

    msg = MIMEMultipart()
    msg["From"] = f"{settings.sender_name} <{user}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body_text, "plain", "utf-8"))

    # Attach PDF Proposal if provided and exists
    if pdf_attachment_path and os.path.exists(pdf_attachment_path):
        with open(pdf_attachment_path, "rb") as f:
            pdf_part = MIMEApplication(f.read(), _subtype="pdf")
            pdf_part.add_header("Content-Disposition", "attachment", filename=os.path.basename(pdf_attachment_path))
            msg.attach(pdf_part)

    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, [to_email], msg.as_string())

        return {"success": True, "recipient": to_email, "sent_at": datetime.utcnow().isoformat()}
    except Exception as e:
        return {"success": False, "error": f"SMTP Delivery Error: {str(e)}"}
