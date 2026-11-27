"""
tools/acp_controller.py

Agent Client Protocol (ACP) Controller for Antigravity PA:
- Manages external and internal ACP agents configured in acp_config.json.
- Implements ACP client stdio communication using official agent-client-protocol (acp).
- Exposes LangChain tools: list_acp_servers, call_acp_agent, and add_acp_server.
"""

import asyncio
import concurrent.futures
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

import acp
from langchain_core.tools import tool

CONFIG_FILE = Path(__file__).parent.parent / "acp_config.json"


def load_acp_config() -> Dict[str, Any]:
    """Loads configured ACP servers from acp_config.json."""
    if not CONFIG_FILE.exists():
        default_config = {
            "acpServers": {
                "antigravity-pa": {
                    "command": "/usr/bin/python3",
                    "args": [str(Path(__file__).parent.parent / "acp_server.py")],
                    "description": "Antigravity Personal Assistant ACP Agent with 360+ tools and Gemini brain"
                }
            }
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ACP Config Error]: {e}")
        return {"acpServers": {}}


def save_acp_config(config: Dict[str, Any]) -> bool:
    """Saves configured ACP servers to acp_config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"[ACP Save Config Error]: {e}")
        return False


class SimpleACPClient:
    """
    Standard ACP Client interface implementation for collecting agent responses.
    """
    def __init__(self):
        self.conn = None
        self.received_chunks: List[str] = []

    def on_connect(self, conn) -> None:
        self.conn = conn

    async def session_update(self, session_id: str, update: Any, **kwargs: Any) -> None:
        """Collects streamed text chunks sent by the ACP agent."""
        if hasattr(update, "content"):
            content = update.content
            if hasattr(content, "text") and content.text:
                self.received_chunks.append(content.text)
            elif isinstance(content, str):
                self.received_chunks.append(content)
        elif isinstance(update, dict):
            content = update.get("content", {})
            if isinstance(content, dict) and "text" in content:
                self.received_chunks.append(content["text"])
            elif isinstance(content, str):
                self.received_chunks.append(content)
        elif hasattr(update, "text"):
            self.received_chunks.append(update.text)

    async def request_permission(self, *args, **kwargs) -> Any:
        # Default allow for standard automated interactions
        return None

    async def write_text_file(self, *args, **kwargs) -> None:
        pass

    async def read_text_file(self, *args, **kwargs) -> str:
        return ""


async def call_acp_agent_async(server_name: str, task: str, cwd: Optional[str] = None) -> str:
    """
    Connects to an ACP agent over stdio, sends the task, and collects response.
    """
    cfg = load_acp_config()
    servers = cfg.get("acpServers", {})

    if server_name not in servers:
        available = ", ".join(servers.keys()) if servers else "none"
        return f"ACP Server '{server_name}' not found. Available servers: {available}"

    server_cfg = servers[server_name]
    cmd = server_cfg.get("command")
    args = server_cfg.get("args", [])
    work_dir = cwd or str(Path(__file__).parent.parent)

    if not cmd:
        return f"ACP Server '{server_name}' has no command configured."

    # Verify command availability
    if not os.path.isabs(cmd) and not shutil.which(cmd):
        return f"Command '{cmd}' for ACP server '{server_name}' is not installed or not in PATH."

    client = SimpleACPClient()

    try:
        async with acp.spawn_agent_process(
            client,
            cmd,
            *args,
            cwd=work_dir,
        ) as (conn, process):
            # 1. Initialize
            await conn.initialize(protocol_version=1)

            # 2. Create new session
            sess_resp = await conn.new_session(cwd=work_dir)
            session_id = sess_resp.session_id

            # 3. Send prompt
            await conn.prompt(
                session_id=session_id,
                prompt=[acp.text_block(task)],
            )

            # 4. Gather result
            full_response = "".join(client.received_chunks).strip()
            if full_response:
                return full_response
            return "ACP agent completed task without returning text."

    except Exception as e:
        return f"Error communicating with ACP server '{server_name}': {e}"


def _run_sync(coro_fn, *args, **kwargs):
    """Helper to run async coroutines safely whether an event loop is running or not."""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return executor.submit(lambda: asyncio.run(coro_fn(*args, **kwargs))).result()
        else:
            return asyncio.run(coro_fn(*args, **kwargs))
    except Exception as e:
        return f"Execution error: {e}"



@tool
def list_acp_servers() -> str:
    """
    List all configured Agent Client Protocol (ACP) servers and agents.
    ACP allows this assistant to collaborate with other external coding and reasoning agents (e.g. Claude Code, Zed ACP, Antigravity PA ACP).
    """
    cfg = load_acp_config()
    servers = cfg.get("acpServers", {})

    if not servers:
        return "No ACP servers configured in acp_config.json."

    output = [f"Configured ACP Servers ({len(servers)} total):"]
    for name, s_cfg in servers.items():
        cmd = s_cfg.get("command", "")
        args = " ".join(s_cfg.get("args", []))
        desc = s_cfg.get("description", "No description")
        
        # Check command existence
        is_installed = os.path.exists(cmd) if os.path.isabs(cmd) else bool(shutil.which(cmd))
        status = "[PASS] Ready" if is_installed else "[WARN] Command not found"

        output.append(
            f"• **{name}** [{status}]\n"
            f"  - Command: `{cmd} {args}`\n"
            f"  - Description: {desc}"
        )

    return "\n\n".join(output)


@tool
def call_acp_agent(server_name: str, task: str) -> str:
    """
    Send a task or prompt to an Agent Client Protocol (ACP) server/agent and get the streamed response.
    
    Args:
        server_name: Name of the ACP server (e.g. 'antigravity-pa' or 'claude-code').
        task: The prompt, instructions, or coding task to execute.
    """
    return _run_sync(call_acp_agent_async, server_name, task)



@tool
def add_acp_server(name: str, command: str, command_args: str = "", description: str = "") -> str:
    """
    Register a new Agent Client Protocol (ACP) server into acp_config.json.
    
    Args:
        name: Unique identifier for the ACP server.
        command: Executable binary or path (e.g. 'python3', 'npx', or '/usr/bin/claude').
        command_args: Space-separated command arguments (e.g. 'acp_server.py' or '--print').
        description: Short description of the ACP agent's capability.
    """
    cfg = load_acp_config()
    servers = cfg.setdefault("acpServers", {})

    args_list = [a.strip() for a in command_args.split() if a.strip()] if command_args else []

    servers[name] = {
        "command": command.strip(),
        "args": args_list,
        "description": description.strip() or f"ACP agent {name}"
    }

    if save_acp_config(cfg):
        return f"Successfully registered ACP server '{name}' with command: {command} {' '.join(args_list)}"
    else:
        return f"Failed to save ACP server '{name}' to acp_config.json."

