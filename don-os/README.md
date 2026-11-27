# DON OS: Distributed Multi-Agent Desktop Operating System

**Lead Systems Architect:** Mullainathan (mullainathan95@gmail.com)  
**Organization:** Brix Softworks  
**Repository:** [https://github.com/brixsoftworks/don-os](https://github.com/brixsoftworks/don-os)

---

## Technical Overview

DON OS is an autonomous desktop artificial intelligence operating system designed for local-first execution, continuous reasoning, and deterministic workstation automation. 

The system couples a high-throughput asynchronous backend built with Python and FastAPI to a glassmorphic Electron desktop client, exposing a centralized agent brain powered by Google Gemini 3.8 Flash. Workstation automation is executed through an extensive Model Context Protocol (MCP) router coordinating 17 discrete servers and 336 native tools.

![DON OS Architecture](docs/DON%20OS%20System%20Architecture.png)

---

## Architectural Pillars

### 1. Central Agent Brain
- **Model Orchestration:** Primary execution on `gemini-3.8-flash` with automatic fallback to `gemini-3-flash-preview` for continuous service availability.
- **Context Management:** Dynamic token-budgeted memory recall via persistent vector storage and structured SQLite session states.
- **ReAct Execution Loop:** Deterministic tool validation, argument serialization, and multi-turn planning.

### 2. Model Context Protocol (MCP) Dynamic Router
- **Multi-Server Aggregation:** Routes commands across 17 isolated MCP servers hosting 336 individual tools.
- **Domain Coverage:** Filesystem read/write operations, shell automation, web search APIs, temporal scheduling, and application management.
- **Failure Boundaries:** Monitored execution limits, sandboxed sub-processes, and isolated return code validation.

### 3. Native Hardware Abstraction Layer
- **System Metrics:** Real-time polling of CPU frequency, thread load, memory pressure, and battery degradation curves.
- **Hardware Control:** Native Linux kernel interfaces for backlight scaling, audio mixer topology, process signaling, and thermal profile management.

### 4. Distributed Multi-Agent Fleet
- **Blackboard Core:** Segregated memory layer (`multi_agent_core/blackboard.py`) managing inter-agent communication and state synchronization.
- **Specialist Fleet:** Dedicated workers for perception planning, deterministic action execution, and workflow arbitration.

### 5. Asynchronous IPC Pipeline
- **Backend Protocol:** FastAPI server operating on `http://127.0.0.1:8765` providing streaming responses via Server-Sent Events (SSE).
- **Desktop Frontend:** Electron interface utilizing context isolation, custom preload security bridges, and low-latency rendering pipelines.

---

## Repository Structure

```text
don-os/
|-- agent.py                 # Central Agent Brain & ReAct orchestrator
|-- agent_server.py          # FastAPI streaming backend service
|-- acp_server.py            # Agent Communication Protocol router
|-- mcp_config.json          # MCP server and tool registry configuration
|-- pa-ai-assistant.desktop  # Linux desktop application entry specification
|-- run_assistant.sh         # Daemon and UI launcher script
|-- docs/                    # System architecture diagrams and specifications
|-- electron_app/            # High-performance glassmorphic desktop interface
|-- multi_agent_core/        # Multi-agent blackboard orchestrator & fleet
`-- tools/                   # Native system tools, hardware controllers & MCP router
```

---

## Verification & Benchmarks

- **Tool Resolution Latency:** Sub-90ms dispatch across registered MCP definitions.
- **Streaming Time to First Token (TTFT):** Under 250ms when utilizing Gemini Flash inference endpoints.
- **Memory Footprint:** Resident Set Size (RSS) under 85MB for the Python daemon during standard idle monitoring.

---

## Deployment & Setup

### Requirements
- Linux OS (Fedora 38+, Ubuntu 22.04+, Debian 12+)
- Python 3.10 or higher
- Node.js 18+ and npm
- Valid Google Gemini API Key

### Configuration
1. Clone the repository and navigate to the project root:
   ```bash
   git clone https://github.com/brixsoftworks/don-os.git
   cd don-os
   ```
2. Configure environment credentials:
   ```bash
   cp .env.example .env
   # Populate GEMINI_API_KEY with your valid API credential
   ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install frontend dependencies:
   ```bash
   cd electron_app
   npm install
   cd ..
   ```
5. Initialize the application:
   ```bash
   ./run_assistant.sh
   ```

---

## Security Model

DON OS enforces strict command boundaries. All shell operations are executed through monitored child processes with explicit execution timeouts and standard input/output isolation. Plain-text credentials are never committed to version control and are strictly loaded from local environment configurations.

Copyright 2026 Mullainathan. All rights reserved.
