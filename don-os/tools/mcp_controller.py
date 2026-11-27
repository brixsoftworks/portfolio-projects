"""
tools/mcp_controller.py

Dynamic MCP (Model Context Protocol) Bridge for LangChain:
- Reads server configurations from mcp_config.json.
- Discovers and loads tools exposed by external application MCP servers via JSON-RPC stdio.
- Wraps them dynamically into native LangChain StructuredTools.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client
import httpx2
from langchain_core.tools import tool, StructuredTool
from pydantic import create_model, Field

CONFIG_FILE = Path(__file__).parent.parent / "mcp_config.json"


def load_mcp_config() -> Dict[str, Any]:
    """Loads configured MCP servers from mcp_config.json."""
    if not CONFIG_FILE.exists():
        default_config = {
            "mcpServers": {
                # Example:
                # "filesystem": {
                #     "command": "npx",
                #     "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/mullainathan/Documents"]
                # }
            }
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[MCP Config Error]: {e}")
        return {"mcpServers": {}}


def load_mcp_config_strict() -> Dict[str, Any]:
    """Read MCP configuration without hiding malformed or unreadable files."""
    if not CONFIG_FILE.exists():
        return {"mcpServers": {}}
    with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict) or not isinstance(config.get("mcpServers"), dict):
        raise ValueError("MCP configuration must contain an object named 'mcpServers'.")
    return config


def save_mcp_config(config: Dict[str, Any]) -> None:
    """Atomically persist MCP configuration without exposing partial writes."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=CONFIG_FILE.parent,
            prefix=f".{CONFIG_FILE.name}.",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            json.dump(config, temp_file, indent=2)
            temp_file.write("\n")
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, CONFIG_FILE)
    except OSError:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        raise


async def fetch_server_tools_async(
    server_name: str,
    config: Dict[str, Any],
    raise_on_error: bool = False,
) -> List[Dict[str, Any]]:
    """Connects to an MCP server over stdio or Streamable HTTP and lists its tools."""
    if config.get("transport") == "http" or config.get("type") == "http":
        url = config.get("url")
        if not url:
            if raise_on_error:
                raise ValueError(f"MCP server '{server_name}' has no URL configured.")
            return []
        try:
            async with httpx2.AsyncClient(headers=config.get("headers") or {}) as client:
                async with streamable_http_client(url, http_client=client) as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        tools_response = await session.list_tools()
                        return [
                            {
                                "name": f"{server_name}__{tool.name}",
                                "raw_name": tool.name,
                                "description": tool.description or f"MCP tool from {server_name}",
                                "input_schema": getattr(
                                    tool, "input_schema", getattr(tool, "inputSchema", {})
                                ),
                                "server_name": server_name,
                                "config": config,
                            }
                            for tool in tools_response.tools
                        ]
        except Exception as error:
            print(f"[MCP Warning]: Server '{server_name}' connection failed: {error}")
            if raise_on_error:
                raise RuntimeError(f"Could not connect to MCP server '{server_name}': {error}") from error
            return []

    cmd = config.get("command")
    args = config.get("args", [])
    env = config.get("env", None)

    if not cmd:
        if raise_on_error:
            raise ValueError(f"MCP server '{server_name}' has no command configured.")
        return []

    server_params = StdioServerParameters(
        command=cmd,
        args=args,
        env=env
    )

    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools_response = await session.list_tools()
                
                tool_list = []
                for t in tools_response.tools:
                    tool_list.append({
                        "name": f"{server_name}__{t.name}",
                        "raw_name": t.name,
                        "description": t.description or f"MCP tool from {server_name}",
                        "input_schema": getattr(t, "input_schema", getattr(t, "inputSchema", {})),
                        "server_name": server_name,
                        "config": config
                    })
                return tool_list
    except Exception as e:
        print(f"[MCP Warning]: Server '{server_name}' connection failed: {e}")
        if raise_on_error:
            raise RuntimeError(f"Could not connect to MCP server '{server_name}': {e}") from e
        return []


async def call_mcp_tool_async(server_or_config: Any, raw_tool_name: str, arguments: Dict[str, Any]) -> str:
    """Executes a specific tool on an MCP server over stdio session."""
    if isinstance(server_or_config, str):
        full_cfg = load_mcp_config()
        config = full_cfg.get("mcpServers", {}).get(server_or_config, {})
        if not config:
            return f"Error: MCP Server '{server_or_config}' not found in configuration."
    else:
        config = server_or_config

    cmd = config.get("command")
    args = config.get("args", [])
    env = config.get("env", None)

    # Provide smart defaults if required arguments were omitted
    clean_arguments = dict(arguments)
    if "git" in str(cmd) or "git" in str(args):
        if "repo_path" not in clean_arguments:
            clean_arguments["repo_path"] = os.getcwd()
    elif "filesystem" in str(args):
        if "path" not in clean_arguments:
            clean_arguments["path"] = os.getcwd()

    if config.get("transport") == "http" or config.get("type") == "http":
        url = config.get("url")
        if not url:
            raise ValueError("MCP HTTP server has no URL configured.")
        async with httpx2.AsyncClient(headers=config.get("headers") or {}) as client:
            async with streamable_http_client(url, http_client=client) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(raw_tool_name, arguments=clean_arguments)
    else:
        server_params = StdioServerParameters(command=cmd, args=args, env=env)
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(raw_tool_name, arguments=clean_arguments)

    output_texts = []
    for content in result.content:
        if hasattr(content, "text"):
            output_texts.append(content.text)
        else:
            output_texts.append(str(content))
    return "\n".join(output_texts) if output_texts else "Tool executed successfully (empty response)."


def get_all_mcp_tools() -> List[StructuredTool]:
    """
    Scans mcp_config.json, queries all live MCP servers, and converts them to LangChain tools.
    """
    config = load_mcp_config()
    servers = config.get("mcpServers", {})

    all_tools: List[StructuredTool] = []

    for s_name, s_cfg in servers.items():
        try:
            mcp_tool_defs = asyncio.run(fetch_server_tools_async(s_name, s_cfg))
            for item in mcp_tool_defs:
                raw_name = item["raw_name"]
                item_cfg = item["config"]

                def make_executor(t_cfg, t_raw_name):
                    def _sync_executor(**kwargs):
                        return asyncio.run(call_mcp_tool_async(t_cfg, t_raw_name, kwargs))
                    return _sync_executor

                structured_tool = StructuredTool.from_function(
                    func=make_executor(item_cfg, raw_name),
                    name=item["name"],
                    description=item["description"],
                )
                all_tools.append(structured_tool)
        except Exception as e:
            print(f"[MCP Server '{s_name}' skipped]: {e}")

    return all_tools


@tool
def list_mcp_servers() -> str:
    """
    List configured MCP servers and their active connection status.
    """
    cfg = load_mcp_config()
    servers = cfg.get("mcpServers", {})
    if not servers:
        return "No external MCP servers configured in mcp_config.json. Add entries to connect apps via MCP."

    summary = ["Configured MCP Servers:"]
    for s_name, s_cfg in servers.items():
        cmd = s_cfg.get("command", "")
        summary.append(f"• {s_name}: command '{cmd}'")
    return "\n".join(summary)
