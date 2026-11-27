# Brix Sales OS: Autonomous Multi-Agent Revenue & Client Acquisition Engine

**Lead Systems Architect:** Mullainathan (`mullainathan95@gmail.com`)  
**Organization:** Brix Softworks  
**Role:** Principal Systems Architect & Senior Software Engineer  
**Repository Status:** Production / Fully Functional  

---

## Executive Summary

Brix Sales OS is an enterprise-grade, self-hosted autonomous sales operating system designed to automate end-to-end client acquisition for AI engineering and workflow automation contracts. 

The system orchestrates **12 decoupled autonomous agents** powered by local GPU inference (NVIDIA RTX 5060 + Ollama `qwen2.5-coder:7b`) and deterministic business logic. It handles automated prospect discovery, deep website intelligence extraction, multi-factor lead scoring, semantic solution matching against a 60-workflow enterprise blueprint library, high-integrity personalized copywriting, human-in-the-loop authorization gates, meeting discovery coordination, programmatic PDF Statement of Work (SOW) compilation, and client onboarding workspace provisioning.

All data processing, scraping, and inference pipelines run on air-gapped or self-hosted infrastructure, guaranteeing zero data leakage of client or prospect intelligence.

---

## System Architecture

```
                                [ Ingestion & Discovery ]
                                           │
                             [ Agent 01: Lead Discovery ]
                                           │
                           [ Agent 02: Website Intelligence ]
                            (SSRF Defenses + Local Ollama)
                                           │
                             [ Agent 03: Lead Scoring ]
                               (6-Factor Quantitative)
                                           │
                           [ Agent 04: Solution Matching ]
                            (Vector / Tag Semantic Match)
                                           │
                            [ Agent 05: Demo Generator ]
                            (Interactive HTML Sandboxes)
                                           │
                           [ Agent 06: Ethical Outreach ]
                            (Verified Fact Attribution)
                                           │
                          [ Agent 07: Campaign Gatekeeper ]
                          (Human-in-the-Loop Review Queue)
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
         [ Agent 08: Inbox Manager ]                [ Agent 09: Meeting Booking ]
         (NLP Intent Classification)                (Cross-Timezone Discovery)
                     │                                           │
                     └─────────────────────┬─────────────────────┘
                                           │
                           [ Agent 10: Proposal Generator ]
                            (ReportLab Publication SOWs)
                                           │
                           [ Agent 11: Closing Assistant ]
                            (Objection Matrix + Checkout)
                                           │
                          [ Agent 12: Client Onboarding ]
                          (Workspace Setup + Key Vaults)
```

---

## The 12 Autonomous Agents

1. **Agent 01 - Lead Discovery**: Ingests, deduplicates, and validates prospective organization records with strict provenance tracking and suppression list cross-referencing.
2. **Agent 02 - Website Intelligence**: High-concurrency asynchronous scraping engine with strict SSRF defenses; extracts tech stacks and operational signals using local LLM inference.
3. **Agent 03 - AI Lead Scoring**: Multi-factor scoring algorithm (0 to 100) evaluating company size, technical readiness, automation deficit, and outbound budget fit.
4. **Agent 04 - Solution Matching**: Semantic matching engine mapping client operational profiles directly to audited n8n automation blueprints from our 60-workflow repository.
5. **Agent 05 - Demo Generator**: Programmatically generates lightweight, interactive HTML walkthroughs with synthetic execution traces under strict compute limits.
6. **Agent 06 - Outreach Copywriter**: Formulates high-conversion, non-spam cold correspondence strictly grounded in verified facts, omitting fabricated familiarity.
7. **Agent 07 - Campaign Gatekeeper**: Enforces strict Human-in-the-Loop (HITL) approval, daily rate-limiting, and opt-out suppression before external dispatch.
8. **Agent 08 - Inbox Manager**: Real-time webhook listener classifying inbound email sentiment (Interested, Information, Pricing, Unsubscribe) and auto-drafting contextual replies.
9. **Agent 09 - Meeting Booking**: Schedules technical discovery sessions across global time zones (US, UK, EU, APAC) and generates bespoke discovery agendas.
10. **Agent 10 - Proposal Generator**: Dynamic document rendering engine compiling formal Statements of Work (SOW) and publication-grade PDF proposals via ReportLab.
11. **Agent 11 - Closing Assistant**: Automated objection-handling engine with integrated payment link generation and idempotent Stripe/Razorpay webhook validation.
12. **Agent 12 - Client Onboarding**: Provisions secure private repositories, implementation milestone boards, and encrypted credential transfer vaults.

---

## Technical Specifications & Stack

- **Runtime & Framework:** Python 3.10+, FastAPI (Asynchronous ASGI), Uvicorn.
- **Local Inference Engine:** Ollama with `qwen2.5-coder:7b` (quantized 4-bit / 8-bit), running locally on NVIDIA RTX 5060 (8GB VRAM) via CUDA 13.x acceleration.
- **Persistence & ORM:** SQLite / PostgreSQL via SQLAlchemy with asynchronous connection pooling.
- **Document Generation:** ReportLab PDF Engine with custom enterprise typography and vector layout matrices.
- **Security & Network:** SSRF-safe HTTP client with IP blocklisting (private subnets, cloud metadata endpoints), header sanitization, and rate-limiting middleware.

---

## Commercial Offerings Matrix

| Offer Tier | Solution Name | Commercial Scope | Target Market |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **Workflow Blueprint Pack** | Instant delivery of audited n8n production pipelines | Automation engineers, digital agencies |
| **Tier 2** | **Done-For-You AI Automation** | Turnkey workflow implementation, testing, and deployment | SMEs, medical clinics, logistics operators |
| **Tier 3** | **Fractional AI Systems Architect** | Dedicated architectural leadership, SLA-backed retainers | High-growth SaaS, fintech, enterprise teams |

---

## Enterprise Safety & Security Standards

- **Human-in-the-Loop Authorization**: Every generated outreach email, proposal, and client document begins in `PENDING_APPROVAL` status; dispatch without authenticated operator consent is physically blocked at the database constraint level.
- **Global Emergency Stop**: Instant kill-switch endpoint (`POST /api/emergency-stop`) halting all outbound network I/O, scheduled tasks, and agent executions within sub-10ms.
- **SSRF Defenses**: Outbound scrapers validate all target DNS resolutions against loopback (`127.0.0.0/8`), private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), and cloud instance metadata addresses (`169.254.169.254`).
- **Zero Hallucination Policy**: Generative prompts mandate hard boundary conditions; agents cannot infer or invent revenue, team sizes, or operational metrics without cited web provenance.

---

## Deployment & Verification

### 1. Environment Setup

```bash
# Clone and enter workspace
cd brix-sales-os

# Create and activate isolated environment
python3 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install -r requirements.txt
```

### 2. Database Initialization

```bash
# Initialize schema and seed 60 workflow blueprints
python3 -c "from brix_sales_os.database.session import init_db; init_db()"
```

### 3. Launching Command Center

```bash
# Start asynchronous API and dashboard
python3 -m uvicorn brix_sales_os.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

- **Executive Dashboard:** `http://localhost:8000/dashboard`
- **Swagger Documentation:** `http://localhost:8000/docs`
- **Workflow Registry:** `http://localhost:8000/api/workflows`

### 4. Automated Test Suite Execution

```bash
# Run complete unit, integration, and simulation test suite
PYTHONPATH=. pytest tests/ -v --tb=short
```

---

## Authorship & Intellectual Property

- **Lead Systems Architect:** Mullainathan
- **Email:** mullainathan95@gmail.com
- **Organization:** Brix Softworks
- **License:** Proprietary - All rights reserved by Mullainathan
