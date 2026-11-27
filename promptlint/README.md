# PromptLint: Enterprise Developer Toolkit for AI Prompt Engineering

**Lead Systems Architect:** Mullainathan (`mullainathan95@gmail.com`)  
**Organization:** Brix Softworks  
**Role:** Principal Systems Architect & Senior Software Engineer  
**Distribution:** PyPI (`promptlint`) | VS Code Extension | Model Context Protocol (MCP) Server  
**Repository Status:** Production / Fully Functional  

---

## Executive Summary

PromptLint is an open-source static analysis engine, automated linter, and Language Server Protocol (LSP) suite designed to evaluate, optimize, score, and secure generative AI prompts.

Built with Python 3.11+, PromptLint executes 25+ deterministic rule passes with sub-10ms latency across AST-extracted prompt strings, plain text templates, and dynamic Jinja/Handlebars interpolations. It identifies hardcoded security credentials, prompt injection vectors, ambiguous task definitions, hallucination triggers, token inefficiencies, and contradictory instructions.

The platform provides a native Model Context Protocol (MCP) server, enabling AI coding agents (Claude Code, Antigravity, Cursor) to self-audit their generated prompts prior to downstream invocation.

---

## Architecture Pipeline

```text
       [ Prompt Source ] (CLI, Stdin, Python AST, VS Code LSP, MCP)
                                   │
                                   ▼
                       [ Tokenizer & AST Parser ]
                                   │
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
     [ Static Rules ]      [ Security Audit ]     [ Metric Profiler ]
      - Structure           - Secret Detection     - Token Overhead
      - Ambiguity           - Prompt Injection     - Estimated Latency
      - Contradictions      - Data Exfiltration    - Compute Cost
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                                   ▼
                       [ Scoring Engine (0 - 100) ]
                                   │
             ┌─────────────────────┴─────────────────────┐
             ▼                                           ▼
  [ Deterministic Fixer ]                       [ Language Server / MCP ]
   - Redundancy Pruning                          - Real-time Diagnostics
   - Constraint Standardization                  - Claude / Cursor Tool Interface
```

---

## Technical Specifications

- **Language & Runtime:** Python 3.11+ with strict type annotations (`mypy` verified).
- **Inference & Execution Speed:** Sub-10ms deterministic rule engine; zero external network calls required for standard lint passes.
- **Protocols Supported:** Model Context Protocol (MCP) JSON-RPC, Language Server Protocol (LSP 3.17).
- **Rule Matrix:** 25+ production rules organized into Security (`SEC`), Structure (`STRUCT`), Clarity (`CLAR`), Ambiguity (`AMB`), Conflicts (`CONF`), and Efficiency (`EFF`).
- **Distribution:** Packaged as PyPI package (`promptlint`) and VS Code language extension.

---

## Rule Reference Matrix

| Rule ID | Category | Severity | Invariant Enforced |
| :--- | :--- | :--- | :--- |
| **SEC001** | Security | CRITICAL | Detects hardcoded API keys (AWS, OpenAI, GitHub, Stripe tokens). |
| **SEC002** | Security | ERROR | Detects prompt injection and jailbreak vector patterns. |
| **STRUCT001** | Structure | WARNING | Enforces explicit task objective and role declarations. |
| **STRUCT002** | Structure | WARNING | Enforces deterministic output schema declarations (JSON/Markdown). |
| **STRUCT005** | Structure | INFO | Detects ungrounded context variables lacking schema anchors. |
| **CLAR001** | Clarity | WARNING | Flags subjective quality qualifiers ("make it good", "be fast"). |
| **AMB004** | Ambiguity | WARNING | Detects hallucination-inducing open phrases ("feel free to guess"). |
| **CONF001** | Conflicts | WARNING | Identifies logically contradictory instructions in prompt bodies. |
| **EFF001** | Efficiency | WARNING | Flags repeated tokens and duplicate semantic directives. |
| **EFF004** | Efficiency | WARNING | Flags excessive negative constraint chains (>4 negative clauses). |

---

## Command Line Interface & Usage

### 1. Installation

```bash
pip install promptlint
```

### 2. Diagnostic Analysis & Scoring

```bash
# Evaluate quality score (0 to 100)
promptlint score prompt.txt

# Run full diagnostic analysis with categorized warnings
promptlint analyze prompt.txt

# Security-specific secret and injection audit
promptlint security prompt.txt
```

### 3. Automated Fixer & Diff Inspection

```bash
# Apply deterministic structural and token optimizations
promptlint fix prompt.txt --output fixed_prompt.txt

# Inspect diff between prompt revisions
promptlint diff v1_prompt.txt v2_prompt.txt
```

### 4. Integration via Model Context Protocol (MCP)

To connect autonomous LLM agents directly to PromptLint:

```json
{
  "mcpServers": {
    "promptlint": {
      "command": "promptlint",
      "args": ["mcp"]
    }
  }
}
```

---

## Authorship & Intellectual Property

- **Lead Systems Architect:** Mullainathan
- **Email:** mullainathan95@gmail.com
- **Organization:** Brix Softworks
- **License:** MIT License
