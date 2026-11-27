#!/usr/bin/env python3
"""
mail_automator_cli.py
=====================
Command Line Interface to configure and run the Autonomous Mail Automator.
Features:
  - Configure Email & App Key (Google / Outlook / Custom SMTP)
  - Verify SMTP & IMAP connection
  - Send initial cold emails with attached PDF proposals
  - Run the Autonomous Follow-Up & Reply Monitor Daemon
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from brix_sales_os.services.mail_automator import mail_automator, CONFIG_FILE
from brix_sales_os.database.session import SessionLocal
from brix_sales_os.database.models import OutreachMessage, Proposal

def print_banner():
    print("=" * 65)
    print("      BRIX SALES OS — AUTONOMOUS MAIL AUTOMATOR")
    print("=" * 65)

def configure():
    print_banner()
    print("\n[CONFIGURE EMAIL CREDENTIALS]")
    print("Enter your sender email and App Password (or App Key).\n")
    print("Options:")
    print("  1. Gmail / Google Workspace (smtp.gmail.com / imap.gmail.com)")
    print("  2. Microsoft Outlook / Office 365")
    print("  3. Custom SMTP / IMAP Server")
    
    choice = input("\nSelect provider [1=Gmail, 2=Outlook, 3=Custom]: ").strip()
    provider = "gmail"
    if choice == "2":
        provider = "outlook"
    elif choice == "3":
        provider = "custom"

    email_addr = input("Enter your email address: ").strip()
    app_key = input("Enter your App Password / App Key: ").strip()

    mail_automator.save_credentials(email_addr, app_key, provider)
    print(f"\n[OK] Credentials saved to {CONFIG_FILE} and environment!")
    print("Running automated connection test...")
    test_conn()

def test_conn():
    print("\n[TESTING SMTP & IMAP CONNECTION]")
    res = mail_automator.test_connection()
    if res["success"]:
        print(f"[OK] ALL SYSTEMS VERIFIED for {res['email']}")
        print(f"  SMTP (Outbound): {res['smtp_status']}")
        print(f"  IMAP (Inbound):  {res['imap_status']}")
    else:
        print("[X] CONNECTION FAILED")
        print(f"  SMTP: {res.get('smtp_status')}")
        print(f"  IMAP: {res.get('imap_status')}")
        print("\nTroubleshooting tips:")
        print("  - For Gmail: Ensure 2-Step Verification is ON and generate an App Password")
        print("    at: https://myaccount.google.com/apppasswords")
        print("  - For Gmail: Ensure IMAP is enabled in Gmail Settings -> Forwarding and POP/IMAP")

def send_approved():
    print_banner()
    db = SessionLocal()
    approved = db.query(OutreachMessage).filter_by(status="APPROVED").all()
    if not approved:
        # Also check pending approval
        pending = db.query(OutreachMessage).filter_by(status="PENDING_APPROVAL").all()
        if pending:
            print(f"Found {len(pending)} pending messages. Auto-approving for dispatch...")
            for p in pending:
                p.status = "APPROVED"
            db.commit()
            approved = pending
        else:
            print("\nNo messages waiting in queue. Ingest leads first via the dashboard.")
            db.close()
            return

    print(f"\nReady to transmit {len(approved)} message(s):\n")
    for msg in approved:
        contact = msg.contact
        org = contact.organization if contact else None
        print(f"- To: {contact.email} ({org.name if org else ''}) | Subject: {msg.subject}")

    confirm = input("\nProceed with sending? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        db.close()
        return

    sent = 0
    for msg in approved:
        contact = msg.contact
        org = contact.organization if contact else None
        pdf_path = None
        if org:
            prop = db.query(Proposal).filter_by(organization_id=org.id).order_by(Proposal.created_at.desc()).first()
            if prop and prop.pdf_path and os.path.exists(prop.pdf_path):
                pdf_path = prop.pdf_path

        print(f"\nSending to {contact.email}...", end=" ")
        try:
            res = mail_automator.send_single_email(
                to_email=contact.email,
                subject=msg.subject,
                body_text=msg.body_text,
                pdf_path=pdf_path
            )
            msg.status = "SENT"
            msg.sent_at = res["sent_at"]
            db.commit()
            print("[OK] SENT" + (f" (attached {os.path.basename(pdf_path)})" if pdf_path else ""))
            sent += 1
            time.sleep(3)  # Anti-spam jitter delay
        except Exception as e:
            print(f"[X] FAILED: {e}")

    db.close()
    print(f"\nCompleted: {sent} emails delivered successfully.")

def run_daemon():
    print_banner()
    print("\n[AUTONOMOUS FOLLOW-UP & INBOX MONITOR DAEMON ACTIVE]")
    print(f"Sender Account: {mail_automator.email_address or 'Not configured'}")
    print("Checking inbox every 60 seconds. Press CTRL+C to stop.\n")

    while True:
        db = SessionLocal()
        try:
            # 1. Check for incoming replies
            replies = mail_automator.check_inbox_for_replies(db)
            if replies:
                for r in replies:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}]  INCOMING REPLY DETECTED from {r['contact_email']} (Intent: {r['intent']})")
                    print(f"    Suggested AI Reply staged in dashboard.")

            # 2. Process automated follow-ups (if no reply after 3 days)
            follow_ups = mail_automator.process_automated_follow_ups(db)
            if follow_ups:
                for f in follow_ups:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}]  Sent automated follow-up to {f['recipient']}: '{f['subject']}'")

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Daemon cycle warning: {e}")
        finally:
            db.close()

        time.sleep(60)

if __name__ == "__main__":
    import json
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
                mail_automator.email_address = cfg.get("email_address")
                mail_automator.app_password = cfg.get("app_password")
                mail_automator.smtp_host = cfg.get("smtp_host", "smtp.gmail.com")
                mail_automator.imap_host = cfg.get("imap_host", "imap.gmail.com")
        except Exception:
            pass

    args = sys.argv[1:] if len(sys.argv) > 1 else ["help"]
    cmd = args[0].lower()

    if cmd == "configure":
        configure()
    elif cmd == "test":
        test_conn()
    elif cmd in ("send", "send-now"):
        send_approved()
    elif cmd == "daemon":
        run_daemon()
    else:
        print_banner()
        print("\nCommands:")
        print("  python3 mail_automator_cli.py configure   -> Enter email & App Password")
        print("  python3 mail_automator_cli.py test        -> Test SMTP & IMAP connection")
        print("  python3 mail_automator_cli.py send-now    -> Dispatch approved cold emails")
        print("  python3 mail_automator_cli.py daemon      -> Start 24/7 auto reply & follow-up daemon")
