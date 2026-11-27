#!/usr/bin/env python3
"""
send_campaign.py
================
CLI utility to dispatch approved outreach messages from Brix Sales OS
via standard SMTP (Gmail, Google Workspace, Outlook, SendGrid, etc.).
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from brix_sales_os.database.session import SessionLocal
from brix_sales_os.database.models import OutreachMessage, Contact, Organization, Proposal
from brix_sales_os.services.email_sender import send_smtp_email
from brix_sales_os.config import settings

def main():
    print("=" * 65)
    print("  BRIX SALES OS — OUTREACH EMAIL DISPATCHER")
    print("=" * 65)

    db = SessionLocal()
    approved_messages = db.query(OutreachMessage).filter(
        OutreachMessage.status.in_(["APPROVED", "PENDING_APPROVAL"])
    ).all()

    if not approved_messages:
        print("\nNo pending or approved messages found in the queue.")
        print("Run the AI pipeline in the dashboard (http://localhost:8000) to generate drafts.\n")
        db.close()
        return

    print(f"\nFound {len(approved_messages)} message(s) ready to send:\n")
    for idx, msg in enumerate(approved_messages, 1):
        contact = msg.contact
        org = contact.organization if contact else None
        print(f"[{idx}] Recipient: {contact.email if contact else 'N/A'} ({contact.full_name if contact else ''})")
        print(f"    Company:   {org.name if org else 'N/A'}")
        print(f"    Subject:   {msg.subject}")
        print(f"    Status:    {msg.status}")
        print("-" * 55)

    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not smtp_host or not smtp_user or not smtp_pass:
        print("\nSMTP credentials not found in environment.")
        print("Supported presets:")
        print("  1. Gmail / Google Workspace (smtp.gmail.com:587 with App Password)")
        print("  2. Outlook / Office 365 (smtp.office365.com:587)")
        print("  3. Custom Domain SMTP")
        
        choice = input("\nSelect preset [1=Gmail, 2=Outlook, 3=Custom, q=Quit]: ").strip()
        if choice == "1":
            smtp_host = "smtp.gmail.com"
            smtp_port = 587
        elif choice == "2":
            smtp_host = "smtp.office365.com"
            smtp_port = 587
        elif choice == "3":
            smtp_host = input("Enter SMTP Host (e.g. mail.yourdomain.com): ").strip()
            smtp_port = int(input("Enter SMTP Port [587]: ").strip() or 587)
        else:
            print("Aborted.")
            db.close()
            return

        smtp_user = input("Enter your Sender Email Address: ").strip()
        smtp_pass = input("Enter your Email Password or App Password: ").strip()

    confirm = input(f"\nReady to transmit {len(approved_messages)} email(s) via {smtp_host} as {smtp_user}? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Sending canceled.")
        db.close()
        return

    print("\nTransmitting messages...\n")
    sent_count = 0
    for msg in approved_messages:
        contact = msg.contact
        org = contact.organization if contact else None
        
        # Check if proposal PDF exists for this organization
        pdf_path = None
        if org:
            prop = db.query(Proposal).filter_by(organization_id=org.id).order_by(Proposal.created_at.desc()).first()
            if prop and prop.pdf_path and os.path.exists(prop.pdf_path):
                pdf_path = prop.pdf_path

        print(f"-> Sending to {contact.email} ({org.name if org else ''})...", end=" ")
        res = send_smtp_email(
            to_email=contact.email,
            subject=msg.subject,
            body_text=msg.body_text,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
            pdf_attachment_path=pdf_path
        )

        if res.get("success"):
            msg.status = "SENT"
            msg.sent_at = res.get("sent_at")
            db.commit()
            print("✓ SUCCESS" + (f" (attached {os.path.basename(pdf_path)})" if pdf_path else ""))
            sent_count += 1
        else:
            print(f"✕ FAILED ({res.get('error')})")

    db.close()
    print(f"\nFinished: {sent_count}/{len(approved_messages)} emails transmitted successfully.")

if __name__ == "__main__":
    main()
