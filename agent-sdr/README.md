# AgentSDR: Autonomous Multi-Channel Outbound & CRM Operating System

**Lead Systems Architect:** Mullainathan (`mullainathan95@gmail.com`)  
**Organization:** Brix Softworks  
**Role:** Principal Systems Architect & Senior Software Engineer  
**Stack:** Next.js 16, React 19, TypeScript, PostgreSQL 16+, Prisma ORM  
**Repository Status:** Production / Fully Functional  

---

## Executive Summary

AgentSDR is an enterprise-grade autonomous outbound sales operating system and intelligent CRM designed to consolidate multi-channel prospect engagement (Email, LinkedIn, WhatsApp) into a single self-hosted workspace.

The platform eliminates the need for fragmented third-party enrichment, sequencing, and dialer tools by uniting verified lead intelligence, personalized cross-channel sequencing, and real-time LLM-driven reply classification into a single PostgreSQL persistence layer. Incoming replies across all channels are ingested into a unified queue where autonomous agents parse intent, extract objections, draft contextual responses, and stage them for single-click human authorization.

All customer data, lead records, call recordings, and API keys remain strictly contained within self-hosted infrastructure.

---

## Architecture Blueprint

```text
                                [ Lead Sources & Enrichment ]
                                (Apollo, Hunter, Lusha, CSV)
                                             │
                                             ▼
                             [ Central Lead Record & Identity ]
                               (PostgreSQL 16 + Row-Level Security)
                                             │
                       ┌─────────────────────┼─────────────────────┐
                       ▼                     ▼                     ▼
              [ Email Sequencer ]    [ LinkedIn Engine ]   [ WhatsApp Voice/Chat ]
               - Google Workspace     - Connection Notes    - Twilio / Unipile
               - Sending Windows      - Safe Daily Limits   - Audio Call Recording
                       │                     │                     │
                       └─────────────────────┼─────────────────────┘
                                             │
                                             ▼
                               [ Unified Inbound Event Bus ]
                                             │
                                             ▼
                             [ Real-Time NLP Intent Classifier ]
                              - Interested / Demo Requested
                              - Objection / Out of Office
                              - Unsubscribe (Auto-Suppression)
                                             │
                                             ▼
                              [ Contextual Response Drafter ]
                                             │
                                             ▼
                            [ Human-in-the-Loop Approval Queue ]
                               (Single-Click Operator Dispatch)
```

---

## Technical Specifications

- **Frontend & Fullstack Runtime:** Next.js 16 (App Router), React 19, Tailwind CSS.
- **Database & Persistence:** PostgreSQL 16+ via Prisma ORM with connection pooling.
- **Channel Integrations:** Google Workspace SMTP/IMAP, LinkedIn Webhook Bridge, WhatsApp Business API.
- **AI Classification Engine:** Multi-provider LLM connector (OpenRouter, Gemini, Claude) with structured JSON intent outputs.
- **Safety & Compliance Invariants:** Hard daily sending thresholds, human-in-the-loop draft review, automatic unsubscribe suppression, and zero simulated/falsified engagement events.

---

## Authorship & Intellectual Property

- **Lead Systems Architect:** Mullainathan
- **Email:** mullainathan95@gmail.com
- **Organization:** Brix Softworks
- **License:** Proprietary - All rights reserved by Mullainathan
