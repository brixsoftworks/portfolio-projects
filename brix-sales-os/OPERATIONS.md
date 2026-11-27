# BRIX SALES OS — Operations & Runbook Guide

## 1. Daily Operator Workflow

The operator's daily routine takes less than 15 minutes using the Web Command Center ([http://localhost:8000/dashboard](http://localhost:8000/dashboard)):

1. **Step 1: Check Telemetry Overview**
   - Verify that the status pill displays `ASSISTED_PRODUCTION` and that the Emergency Stop is green/idle.
   - Review the **Review Queue** counter.
2. **Step 2: Ingest & Discover Prospects**
   - Click **"Discover Leads"** to run Agent 01 across target niches (US digital marketing agencies, SaaS, web dev).
   - In the **Lead Explorer**, select a newly ingested lead and click **"⚡ Run AI Pipeline"**.
   - Agent 02 visits the site, Agent 03 scores the opportunity, Agent 04 matches suitable n8n workflows, and Agent 06 drafts a personalized cold email.
3. **Step 3: Review Outbound Drafts**
   - Go to **Campaign Review**.
   - Review each generated email:
     - Check that the verified observation is factually accurate.
     - Click **"✓ Approve"** to queue the message, or **"✕ Reject"** to discard.
   - Click **"🚀 Dispatch All Approved"** to safely release the approved queue.
4. **Step 4: Check Unified Inbox**
   - Review incoming responses.
   - Any prospect who replies with "unsubscribe" is **automatically suppressed** from all future communication.
   - For positive replies ("Interested", "Pricing Inquiry"), review the AI-suggested response and confirm.
5. **Step 5: Generate SOW Proposal & Close**
   - When a lead requests a formal quote, click **"Generate Proposal"** on the deal.
   - Agent 10 compiles a styled PDF proposal with selected n8n workflow IDs, timeline, and setup fee.
   - Download the PDF from the dashboard, review, and issue the approved checkout link.
6. **Step 6: Confirm Payment & Onboarding**
   - Upon receipt of a verified Stripe webhook, Agent 11 marks the deal `WON`.
   - Agent 12 automatically provisions a dedicated client workspace directory under `data/clients/{domain}` with the implementation checklist and secure vault instructions.

---

## 2. Service Management

### Start the Service:
```bash
cd /home/mullainathan/brix-sales-os
PYTHONPATH=/home/mullainathan/brix-sales-os python3 -m uvicorn brix_sales_os.api.main:app --host 0.0.0.0 --port 8000
```

### Stop the Service:
Press `CTRL+C` in the running terminal, or:
```bash
pkill -f "uvicorn brix_sales_os.api.main:app"
```

### Global Emergency Stop:
If you need to halt all outbound outreach immediately:
- Click **"🛑 Emergency Stop"** in the top navigation bar of the dashboard.
- Or execute:
  ```bash
  curl -X POST http://localhost:8000/api/emergency-stop \
    -H "Content-Type: application/json" \
    -d '{"active": true}'
  ```

---

## 3. Backup and Disaster Recovery

### Database Backup:
```bash
# SQLite (Standard)
cp /home/mullainathan/brix-sales-os/data/brix_sales.db \
   /home/mullainathan/brix-sales-os/data/brix_sales_backup_$(date +%Y%m%d).db

# PostgreSQL (if configured)
pg_dump -U postgres brix_sales > brix_sales_backup.sql
```

### Generated Proposals & Workspace Backup:
All proposal PDFs and client workspaces reside in `/home/mullainathan/brix-sales-os/data/`:
```bash
tar -czvf brix_sales_data_backup_$(date +%Y%m%d).tar.gz /home/mullainathan/brix-sales-os/data/
```

---

## 4. Troubleshooting Guide

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| **Ollama connection failed (`ollama_connected: false`)** | Local Ollama daemon not running on port 11434. | Start Ollama: `ollama serve`. Verify: `curl http://localhost:11434/api/tags`. |
| **Inference latency high (> 10s)** | Ollama model unloaded from GPU VRAM. | Warm up model: `ollama run qwen2.5-coder:7b "hi"`. Model will stay resident on the RTX 5060. |
| **Lead scoring returned low for all leads** | Incomplete website content or missing industry tag. | Add industry tags manually or provide a valid website URL with active landing page copy. |
| **Duplicate lead rejected** | Domain or contact email already exists in database. | System enforces normalized domain deduplication to prevent spamming prospects twice. |
| **Message blocked from sending** | Recipient is on the suppression list. | Check `suppression_entries` table. Do not override opt-outs. |
