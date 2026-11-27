# Graph Report - brix-sales-os  (2026-10-28)

## Corpus Check
- 41 files · ~33,235 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: .example 1, (none) 1, .css 1)

## Summary
- 373 nodes · 980 edges · 18 communities (12 shown, 6 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 96 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- models.py
- main.py
- agent02_website_intelligence.py
- mail_automator.py
- .__init__
- test_database.py
- app.js
- brix-sales-api
- pdf_service.py
- MailAutomator
- CampaignManagerAgent
- BRIX SALES OS — Operations & Runbook Guide
- BRIX SALES OS
- BRIX SALES OS — Architecture & Engineering Specification
- DemoGeneratorAgent
- OllamaClient
- Project Workspace: Simulated Growth Agency

## God Nodes (most connected - your core abstractions)
1. `Organization` - 33 edges
2. `BaseAgent` - 31 edges
3. `Contact` - 28 edges
4. `Deal` - 27 edges
5. `OutreachMessage` - 19 edges
6. `log_audit_event()` - 17 edges
7. `ResearchReport` - 17 edges
8. `Proposal` - 17 edges
9. `fetchJSON()` - 17 edges
10. `SuppressionEntry` - 16 edges

## Surprising Connections (you probably didn't know these)
- `1. System Overview` --references--> `BaseAgent`  [INFERRED]
  ARCHITECTURE.md → brix_sales_os/agents/base.py
- `2. Server-Side Request Forgery (SSRF) Defenses` --references--> `is_safe_external_url()`  [INFERRED]
  SECURITY.md → brix_sales_os/core/security.py
- `1. Feature Status Breakdown` --references--> `EmailEvent`  [INFERRED]
  STATUS.md → brix_sales_os/database/models.py
- `test_full_sales_lifecycle()` --uses--> `Proposal`  [INFERRED]
  tests/test_sales_lifecycle_simulation.py → brix_sales_os/database/models.py
- `test_organization_and_contact_creation()` --calls--> `Organization`  [EXTRACTED]
  tests/test_database.py → brix_sales_os/database/models.py

## Import Cycles
- None detected.

## Communities (18 total, 6 thin omitted)

### Community 0 - "models.py"
Cohesion: 0.08
Nodes (24): LeadDiscoveryAgent, LeadScoringAgent, OutreachCopywriterAgent, ProposalGeneratorAgent, SalesClosingAgent, ClientOnboardingAgent, BaseAgent, log_audit_event() (+16 more)

### Community 1 - "main.py"
Cohesion: 0.09
Nodes (34): ApprovalAction, check_mailer_replies(), configure_mailer(), create_proposal(), dispatch_approved_messages(), download_proposal_pdf(), EmergencyStopRequest, get_health() (+26 more)

### Community 2 - "agent02_website_intelligence.py"
Cohesion: 0.08
Nodes (12): WebsiteIntelligenceAgent, is_safe_external_url(), sanitize_external_text(), audit_single_workflow(), run_full_audit(), 1. Zero-Trust Input Sanitization & Prompt Injection Defenses, 2. Server-Side Request Forgery (SSRF) Defenses, 3. Client Credential Protection Policy (+4 more)

### Community 3 - "mail_automator.py"
Cohesion: 0.12
Nodes (11): Settings, OutreachMessage, Proposal, get_db(), send_smtp_email(), configure(), print_banner(), run_daemon() (+3 more)

### Community 4 - ".__init__"
Cohesion: 0.13
Nodes (3): SolutionMatchingAgent, MeetingBookingAgent, Meeting

### Community 5 - "test_database.py"
Cohesion: 0.15
Nodes (10): InboxManagerAgent, on_startup(), Conversation, IntegrationCredentialsMetadata, SuppressionEntry, WorkflowRegistryItem, init_db(), test_database_initialization() (+2 more)

### Community 6 - "app.js"
Cohesion: 0.32
Nodes (18): checkMailerReplies(), dispatchApprovedQueue(), fetchJSON(), loadAgents(), loadCampaignQueue(), loadDeals(), loadInbox(), loadLeads() (+10 more)

### Community 7 - "brix-sales-api"
Cohesion: 0.11
Nodes (17): build, container_name, environment, extra_hosts, healthcheck, ports, restart, volumes (+9 more)

### Community 10 - "CampaignManagerAgent"
Cohesion: 0.32
Nodes (5): CampaignManagerAgent, EmailEvent, 1. Feature Status Breakdown, 2. Test Verification Summary, Brix Sales OS — Operational Status Matrix

### Community 11 - "BRIX SALES OS — Operations & Runbook Guide"
Cohesion: 0.18
Nodes (10): 1. Daily Operator Workflow, 2. Service Management, 3. Backup and Disaster Recovery, 4. Troubleshooting Guide, BRIX SALES OS — Operations & Runbook Guide, Database Backup:, Generated Proposals & Workspace Backup:, Global Emergency Stop: (+2 more)

### Community 12 - "BRIX SALES OS"
Cohesion: 0.18
Nodes (10): 1. Requirements, 2. Installation & Running Locally, 3. Accessing the System,  Automated Test Suite, Autonomous Multi-Agent Client Acquisition, Outreach & Revenue Engine for Brix Softworks, BRIX SALES OS,  Quickstart,  Safety & Compliance (+2 more)

### Community 13 - "BRIX SALES OS — Architecture & Engineering Specification"
Cohesion: 0.29
Nodes (6): 1. System Overview, 2. Multi-Agent Data Flow, 3. Open-Source Evaluation & Integration Matrix, 4. Database Entity Relationships, 5. Operating Modes, BRIX SALES OS — Architecture & Engineering Specification

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseAgent` connect `models.py` to `agent02_website_intelligence.py`, `.__init__`, `test_database.py`, `CampaignManagerAgent`, `BRIX SALES OS — Architecture & Engineering Specification`, `DemoGeneratorAgent`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `Organization` (e.g. with `LeadDiscoveryAgent` and `WebsiteIntelligenceAgent`) actually correct?**
  _`Organization` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Should `models.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0803921568627451 - nodes in this community are weakly interconnected._
- **Why does `MailAutomator` connect `MailAutomator` to `models.py`, `mail_automator.py`, `test_database.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `BaseAgent` (e.g. with `1. System Overview` and `AgentRun`) actually correct?**
  _`BaseAgent` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09158186864014801 - nodes in this community are weakly interconnected._
- **Why does `Organization` connect `models.py` to `main.py`, `agent02_website_intelligence.py`, `mail_automator.py`, `.__init__`, `test_database.py`, `DemoGeneratorAgent`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._