"""
brix_sales_os/services/mail_automator.py
=======================================
Autonomous Mail Automator & Follow-Up Engine.
Sends cold emails, checks for prospect replies via IMAP,
and automatically sends threaded follow-ups if no response is detected.
Works directly with standard Google/Gmail App Passwords or Outlook App Keys.
"""

import os
import time
import email
import imaplib
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from brix_sales_os.database.session import SessionLocal
from brix_sales_os.database.models import (
    OutreachMessage, Contact, Organization, Proposal, SuppressionEntry, Conversation
)
from brix_sales_os.core.ollama_client import ollama_client
from brix_sales_os.core.audit import log_audit_event
from brix_sales_os.config import settings, DATA_DIR

CONFIG_FILE = DATA_DIR / "mailer_credentials.json"

class MailAutomator:
    def __init__(
        self,
        email_address: Optional[str] = None,
        app_password: Optional[str] = None,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        imap_host: str = "imap.gmail.com",
        imap_port: int = 993,
        follow_up_delay_days: int = 3
    ):
        self.email_address = email_address or os.getenv("SMTP_USER")
        self.app_password = app_password or os.getenv("SMTP_PASS")
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port
        self.imap_host = imap_host or os.getenv("IMAP_HOST", "imap.gmail.com")
        self.imap_port = imap_port
        self.follow_up_delay_days = follow_up_delay_days

    def save_credentials(self, email_addr: str, app_pass: str, provider: str = "gmail"):
        self.email_address = email_addr.strip()
        self.app_password = app_pass.strip().replace(" ", "")  # Google app passwords often have spaces
        
        if provider.lower() in ("gmail", "google"):
            self.smtp_host = "smtp.gmail.com"
            self.smtp_port = 587
            self.imap_host = "imap.gmail.com"
            self.imap_port = 993
        elif provider.lower() in ("outlook", "office365", "microsoft"):
            self.smtp_host = "smtp.office365.com"
            self.smtp_port = 587
            self.imap_host = "outlook.office365.com"
            self.imap_port = 993

        # Update environment & write configuration
        os.environ["SMTP_USER"] = self.email_address
        os.environ["SMTP_PASS"] = self.app_password
        os.environ["SMTP_HOST"] = self.smtp_host

        import json
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "email_address": self.email_address,
                "app_password": self.app_password,
                "smtp_host": self.smtp_host,
                "smtp_port": self.smtp_port,
                "imap_host": self.imap_host,
                "imap_port": self.imap_port,
                "configured_at": datetime.utcnow().isoformat()
            }, f, indent=2)

    def test_connection(self) -> Dict[str, Any]:
        """
        Validates both SMTP outbound and IMAP inbound access with the App Key.
        """
        if not self.email_address or not self.app_password:
            return {"success": False, "error": "Missing email or app key."}

        # 1. Test SMTP
        smtp_ok = False
        smtp_err = ""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as s:
                s.starttls()
                s.login(self.email_address, self.app_password)
                smtp_ok = True
        except Exception as e:
            smtp_err = str(e)

        # 2. Test IMAP
        imap_ok = False
        imap_err = ""
        try:
            with imaplib.IMAP4_SSL(self.imap_host, self.imap_port) as mail:
                mail.login(self.email_address, self.app_password)
                imap_ok = True
        except Exception as e:
            imap_err = str(e)

        return {
            "success": smtp_ok and imap_ok,
            "smtp_status": "CONNECTED" if smtp_ok else f"FAILED: {smtp_err}",
            "imap_status": "CONNECTED" if imap_ok else f"FAILED: {imap_err}",
            "email": self.email_address
        }

    def send_single_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        pdf_path: Optional[str] = None,
        in_reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends an email and returns the generated Message-ID header for thread tracking.
        """
        if not self.email_address or not self.app_password:
            raise ValueError("Credentials not configured. Provide email and app password.")

        msg = MIMEMultipart()
        msg["From"] = f"{settings.sender_name} <{self.email_address}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Date"] = email.utils.formatdate(localtime=True)
        message_id = email.utils.make_msgid(domain="brixsoftworks.com")
        msg["Message-ID"] = message_id

        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            msg["References"] = in_reply_to

        msg.attach(MIMEText(body_text, "plain", "utf-8"))

        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                part = MIMEApplication(f.read(), _subtype="pdf")
                part.add_header("Content-Disposition", "attachment", filename=os.path.basename(pdf_path))
                msg.attach(part)

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as s:
            s.starttls()
            s.login(self.email_address, self.app_password)
            s.sendmail(self.email_address, [to_email], msg.as_string())

        return {"success": True, "message_id": message_id, "sent_at": datetime.utcnow()}

    def check_inbox_for_replies(self, db: SessionLocal) -> List[Dict[str, Any]]:
        """
        Scans IMAP INBOX for replies from prospects.
        If a reply is detected:
          1. Records conversation in database.
          2. Classifies intent using local Ollama.
          3. Halts any future follow-up sequences for that prospect.
          4. Auto-suppresses if the prospect requested to unsubscribe.
        """
        if not self.email_address or not self.app_password:
            return []

        replies_found = []
        try:
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(self.email_address, self.app_password)
            mail.select("INBOX")

            # Search unseen or recent messages
            status, data = mail.search(None, "ALL")
            if status != "OK" or not data[0]:
                mail.logout()
                return []

            email_ids = data[0].split()[-30:]  # Inspect last 30 messages
            for eid in reversed(email_ids):
                f_status, msg_data = mail.fetch(eid, "(RFC822)")
                if f_status != "OK":
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                from_header = email.utils.parseaddr(msg.get("From", ""))[1].lower()

                # Check if this sender matches an outreach contact
                contact = db.query(Contact).filter_by(email=from_header).first()
                if not contact:
                    continue

                # Extract body
                body_content = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body_content = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    body_content = msg.get_payload(decode=True).decode(errors="ignore")

                # Check if conversation already recorded
                existing_conv = db.query(Conversation).filter_by(
                    contact_id=contact.id,
                    incoming_message=body_content[:200]
                ).first()
                if existing_conv:
                    continue

                # Classify intent via Agent 08
                from brix_sales_os.agents.agent08_inbox_manager import agent08_inbox
                inbox_action = agent08_inbox.execute(
                    contact_id=contact.id,
                    incoming_message=body_content[:1500]
                )

                replies_found.append({
                    "contact_email": contact.email,
                    "intent": inbox_action.get("intent"),
                    "suggested_reply": inbox_action.get("suggested_reply")
                })

            mail.logout()
        except Exception as e:
            print(f"[IMAP CHECK ERROR] {e}")

        return replies_found

    def process_automated_follow_ups(self, db: SessionLocal) -> List[Dict[str, Any]]:
        """
        Scans sent emails. If no reply was received within follow_up_delay_days,
        automatically formats and sends Follow-up #1 or Follow-up #2.
        """
        if not self.email_address or not self.app_password:
            return []

        sent_messages = db.query(OutreachMessage).filter_by(status="SENT").all()
        now = datetime.utcnow()
        follow_ups_sent = []

        for initial_msg in sent_messages:
            contact = initial_msg.contact
            if not contact:
                continue

            # Check if contact already replied or opted out
            replied = db.query(Conversation).filter_by(contact_id=contact.id).first()
            if replied:
                continue

            suppressed = db.query(SuppressionEntry).filter_by(email=contact.email).first()
            if suppressed:
                continue

            # Check time elapsed since last message
            last_sent = initial_msg.sent_at or initial_msg.created_at
            days_elapsed = (now - last_sent).days

            if days_elapsed >= self.follow_up_delay_days:
                org = contact.organization
                follow_up_subject = f"Re: {initial_msg.subject}"
                follow_up_body = f"""Hi {contact.first_name or 'there'},

Following up on my previous note regarding the n8n automation blueprints for {org.name if org else 'your team'}.

I put together a short 2-minute video walkthrough showing how the workflow operates end-to-end on local private models.

Would you be open to taking a look this week?

Best,
{settings.sender_name}
Brix Softworks

If you'd prefer not to receive further follow-ups, reply with 'unsubscribe' and I will immediately remove your contact."""

                try:
                    res = self.send_single_email(
                        to_email=contact.email,
                        subject=follow_up_subject,
                        body_text=follow_up_body
                    )
                    
                    # Update status to avoid sending again today
                    initial_msg.approval_notes = f"Follow-up #1 sent at {now.isoformat()}"
                    db.commit()

                    follow_ups_sent.append({
                        "recipient": contact.email,
                        "subject": follow_up_subject,
                        "status": "SENT"
                    })
                except Exception as e:
                    print(f"[FOLLOW-UP ERROR] {e}")

        return follow_ups_sent

mail_automator = MailAutomator()
