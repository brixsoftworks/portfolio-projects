# BRIX SALES OS
## Autonomous Multi-Agent Client Acquisition, Outreach & Revenue Engine for Brix Softworks

**Brix Sales OS** is a self-hosted, open-source-first sales operating system designed to acquire paying international clients for Brix Softworks' AI automation workflows and engineering services.

It orchestrates **12 modular autonomous agents** backed by local GPU inference (NVIDIA RTX 5060 + Ollama `qwen2.5-coder:7b`) to discover prospects, research publicly accessible websites, qualify leads, recommend exact n8n workflow blueprints from our 60-agent library, draft high-integrity personalized outreach, enforce human-in-the-loop review, manage meeting discovery, export PDF proposals, and provision client onboarding workspaces.

---

## 🚀 Quickstart

### 1. Requirements
- Python 3.10+
- Local Ollama running with `qwen2.5-coder:7b` (port `11434`)
- Node.js (for n8n workflows if running locally)

### 2. Installation & Running Locally

```bash
cd /home/mullainathan/brix-sales-os

# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database schema & seed the 60 audited workflows
python3 -c "from brix_sales_os.database.session import init_db; init_db()"

# 3. Launch the API & Web Command Center
python3 -m uvicorn brix_sales_os.api.main:app --host 0.0.0.0 --port 8000
```

### 3. Accessing the System
- **Sales Command Center Dashboard**: [http://localhost:8000/dashboard](http://localhost:8000/dashboard) or [http://localhost:8000/](http://localhost:8000/)
- **Interactive REST API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Workflow Capability Registry**: [http://localhost:8000/api/workflows](http://localhost:8000/api/workflows)

---

## 📦 The 3 Commercial Offers

| Offer | Product / Service | Pricing | Target Audience |
| :--- | :--- | :--- | :--- |
| **OFFER A** | **n8n Agency OS Complete Pack** | **$297** Instant Download | Freelancers, marketing agencies, automation builders |
| **OFFER B** | **Done-For-You AI Automation** | **$750** Setup + **$150/mo** | Local businesses, clinics, real estate, dental offices |
| **OFFER C** | **Fractional AI Automation Engineer** | **$1,500 – $2,500** / Month | Growth SaaS, tech startups, e-commerce brands |

---

## 🤖 The 12 Autonomous Agents

1. **Agent 01 — Lead Discovery**: Discovers and deduplicates prospects, records data provenance, checks suppression entries.
2. **Agent 02 — Website Intelligence**: Safely scrapes public pages with SSRF defenses; strictly separates verified observations from hypotheses using Ollama.
3. **Agent 03 — AI Lead Scoring**: Configurable 6-factor scoring (0–100) assigning High (80-100), Medium (60-79), and Low (<60) priority.
4. **Agent 04 — Solution Matching**: Semantic tag matching against the 60 n8n workflow registry; returns recommended offer, setup price, and real operational benefits.
5. **Agent 05 — Demo Generator**: Generates lightweight interactive HTML walkthroughs with synthetic execution traces; enforces a compute budget to prevent waste.
6. **Agent 06 — Outreach Copywriter**: Drafts ethical cold emails with verified observations, clear opt-out language, and zero fake familiarity or invented urgency.
7. **Agent 07 — Campaign Gatekeeper**: Enforces human approval (`PENDING_APPROVAL` queue), daily sending limits, and suppression list checks.
8. **Agent 08 — Inbox Manager**: Classifies replies (Interested, Info, Pricing, Unsubscribe), auto-suppresses opt-outs, and drafts context-aware replies for review.
9. **Agent 09 — Meeting Booking**: Coordinates discovery calls across international time zones (US/UK/EU/Australia) and prepares technical discovery questions.
10. **Agent 10 — Proposal Generator**: Compiles professional Statements of Work (SOWs) and renders publication-grade PDFs via ReportLab.
11. **Agent 11 — Closing Assistant**: Handles sales objections, generates checkout invoices, and verifies payment webhooks with strict idempotency.
12. **Agent 12 — Client Onboarding**: Sets up client workspace folders, implementation checklists, and secure credential transfer protocols (never plain email).

---

## 🛡️ Safety & Compliance

- **Human-in-the-Loop Gatekeeping**: Outbound emails and proposals start in `PENDING_APPROVAL` / `DRAFT` status and cannot be sent without human confirmation.
- **Global Emergency Stop**: Instant kill-switch halting all external actions at `POST /api/emergency-stop` or via the dashboard topbar button.
- **SSRF & Injection Defenses**: Target URLs are validated against loopback, private subnets (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), and AWS/GCP metadata services (169.254.169.254).
- **Zero Fabrication Policy**: Research agents are forbidden from inventing response times, lost leads, or unverified operational flaws.

---

## 🧪 Automated Test Suite

Run the complete automated test suite (unit + integration + full simulated sales lifecycle):

```bash
PYTHONPATH=/home/mullainathan/brix-sales-os pytest tests/ -v
```
