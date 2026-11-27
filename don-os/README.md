# ⚡ DON OS: Autonomous Multi-Agent Desktop Operating System

**DON OS** is an autonomous desktop AI operating system and personal assistant brain engineered by **Brix Softworks**. Built with a high-performance **FastAPI** backend, **Google Gemini 3.8 Flash** reasoning engine, **Electron** glassmorphic desktop interface, and dynamic **Model Context Protocol (MCP)** tool router spanning over 17 servers and 336 native system tools.

![DON OS Architecture](docs/DON%20OS%20System%20Architecture.png)

---

## 🌟 Key Capabilities

- **🧠 Central Agent Brain**: Powered by Google Gemini (`gemini-3.8-flash` with fallback to `gemini-3-flash-preview`), executing complex multi-turn reasoning, memory recall, and deterministic workflows.
- **⚡ Dynamic MCP Tool Router**: Seamless integration across 17 MCP servers and 336 tools, including filesystem, shell automation, web search, time scheduling, and desktop controls.
- **🖥️ Hardware & System Controllers**: Native Linux system controls (CPU, memory, battery, volume, screen brightness, process management).
- **🤖 Multi-Agent Fleet**: Distributed blackboard architecture with specialist agents, perception planner, and action gateway (`multi_agent_core/`).
- **🎨 Cinematic Desktop UI**: Electron-based interface with looping ambient orbs, dark-mode glassmorphic cards, syntax-highlighted code output, and real-time streaming responses.
- **🎙️ Voice & Audio**: Speech-to-text input processing and text-to-speech feedback via `tools/tts_speaker.py`.

---

## 📁 System Architecture

```text
don-os/
├── agent.py                 # Central Agent Brain & ReAct orchestrator
├── agent_server.py          # FastAPI streaming backend (http://127.0.0.1:8765)
├── acp_server.py            # Agent Communication Protocol server
├── mcp_config.json          # MCP server definitions & tool registrations
├── pa-ai-assistant.desktop  # Linux desktop application entry
├── run_assistant.sh         # One-click launcher for FastAPI + Electron
├── docs/                    # Architectural diagrams and shopping guide
├── electron_app/            # Modern glassmorphic desktop client (HTML/CSS/JS)
├── multi_agent_core/        # Multi-agent blackboard orchestrator & fleet
└── tools/                   # Native system tools, hardware controllers & MCP router
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Linux OS (Fedora / Ubuntu / Debian recommended)
- Google Gemini API Key

### 2. Environment Setup
Create a `.env` file in the root directory:
```bash
cp .env.example .env
# Edit .env and paste your Gemini API key:
# GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Electron UI Dependencies
```bash
cd electron_app
npm install
cd ..
```

### 5. Launch DON OS
Run the launcher script to start both the FastAPI backend and Electron desktop window:
```bash
./run_assistant.sh
```

---

## 🛡️ Security & Privacy
DON OS runs locally on your workstation. Shell commands and file operations are managed through monitored tool specifications with explicit execution limits and local state persistence.
