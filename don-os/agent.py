"""
agent.py

Central AI Agent Brain for the PA Assistant.
Powered by Google Gemini (gemini-3.8-flash with fallback to gemini-3-flash-preview)
Orchestrates:
- Memory & Notes (tools.memory_tool)
- Time & Scheduling (tools.time_tool)
- Desktop Workflow (tools.desktop_workflow_tool)
- Hardware & System Controls (tools.hardware_controller)
- Native Shell & File Tools (tools.bash_tool, tools.file_tool)
- Desktop Application Management (tools.desktop_controller)
- DuckDuckGo Web Search (tools.web_search)
- Dynamic MCP Tool Router across 17 servers & 336 tools (tools.mcp_controller)
"""

import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Callable

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.model_registry import get_chat_model

# Import all native tool modules
from tools.web_search import web_search
from tools.bash_tool import bash_tool
from tools.file_tool import (
    read_file,
    write_file,
    append_file,
    list_directory,
    delete_file,
)
from tools.desktop_controller import (
    launch_app,
    close_app,
    open_url,
    set_volume,
    get_volume,
    take_screenshot,
)
from tools.time_tool import (
    get_current_time,
    set_timer,
    add_reminder,
    list_reminders,
    cancel_reminder,
)
from tools.desktop_workflow_tool import (
    get_clipboard_text,
    set_clipboard_text,
    read_web_page,
    get_media_info,
    download_media,
)
from tools.hardware_controller import (
    get_screen_brightness,
    set_screen_brightness,
    get_battery_status,
    get_network_status,
    scan_wifi_networks,
    toggle_wifi,
    get_bluetooth_status,
    toggle_bluetooth,
    get_hardware_temperatures,
    get_cpu_info,
    list_audio_devices,
    toggle_microphone_mute,
    lock_desktop_screen,
)
from tools.memory_tool import (
    remember,
    recall,
    forget,
    list_all_memories,
    save_note,
    search_notes,
    record_chat_turn,
    get_recent_chat_history,
)
from tools.mcp_controller import (
    call_mcp_tool_async,
    fetch_server_tools_async,
    load_mcp_config,
    load_mcp_config_strict,
)
from tools.acp_controller import (
    list_acp_servers,
    call_acp_agent,
    add_acp_server,
)


load_dotenv()


@tool
def call_mcp_software_tool(server_name: str, tool_name: str, arguments_json: str = "{}") -> str:
    """
    Invoke any specialized tool on an external MCP server (Blender, Git, Filesystem, or any of the 13 Craft suites: photocraft, vectorcraft, filmcraft, lightcraft, pdfcraft, effectcraft, designcraft, gridcraft, wordcraft, deckcraft, cadcraft, soundcraft, figcraft).
    
    Args:
        server_name: The name of the server (e.g. 'craft-photocraft', 'blender-mcp', 'git-vcs', 'system-desktop').
        tool_name: The name of the tool to invoke.
        arguments_json: A JSON string dictionary of arguments to pass to the tool.
    """
    try:
        args = json.loads(arguments_json) if arguments_json else {}
    except Exception as e:
        return f"Error parsing arguments_json: {e}"

    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return executor.submit(lambda: asyncio.run(call_mcp_tool_async(server_name, tool_name, args))).result()
        else:
            return asyncio.run(call_mcp_tool_async(server_name, tool_name, args))
    except Exception as e:
        return f"Error executing MCP tool '{tool_name}' on server '{server_name}': {e}"



@tool
def list_available_mcp_servers() -> str:
    """
    List all configured MCP servers and their domain specializations in the system.
    """
    cfg = load_mcp_config()
    servers = list(cfg.get("mcpServers", {}).keys())
    return (
        f"Configured MCP Servers ({len(servers)} total):\n"
        + "\n".join([f"• {s}" for s in servers])
        + "\n\nUse 'call_mcp_software_tool(server_name, tool_name, arguments_json)' to execute tools on them."
    )


# All core tools bound directly to the agent
CORE_TOOLS = [
    # Search
    web_search,
    # Shell & Files
    bash_tool,
    read_file,
    write_file,
    append_file,
    list_directory,
    delete_file,
    # Time & Reminders
    get_current_time,
    set_timer,
    add_reminder,
    list_reminders,
    cancel_reminder,
    # Desktop Workflow
    get_clipboard_text,
    set_clipboard_text,
    read_web_page,
    get_media_info,
    download_media,
    # Hardware Controls
    get_screen_brightness,
    set_screen_brightness,
    get_battery_status,
    get_network_status,
    scan_wifi_networks,
    toggle_wifi,
    get_bluetooth_status,
    toggle_bluetooth,
    get_hardware_temperatures,
    get_cpu_info,
    list_audio_devices,
    toggle_microphone_mute,
    lock_desktop_screen,
    # App & Desktop Controller
    launch_app,
    close_app,
    open_url,
    set_volume,
    get_volume,
    take_screenshot,
    # Memory
    remember,
    recall,
    forget,
    list_all_memories,
    save_note,
    search_notes,
    # MCP Router
    call_mcp_software_tool,
    list_available_mcp_servers,
    # ACP (Agent Client Protocol) Inter-Agent Tools
    list_acp_servers,
    call_acp_agent,
    add_acp_server,
]

TOOL_MAP = {t.name: t for t in CORE_TOOLS}

SYSTEM_PROMPT = """You are Antigravity PA (branded as DON OS), an advanced, capable, loyal, and highly responsive Personal AI Assistant running natively on a Linux desktop workstation.

CRITICAL IDENTITY & ADDRESS RULE:
- The user is your boss. You MUST ALWAYS address the user as "Boss Munna" in every response (e.g., "Right away, Boss Munna", "Here are the details, Boss Munna", "All systems operational, Boss Munna"). Never omit this title.

You have direct access to system tools:
- Shell execution (bash_tool) - Note: file deletion requires interactive user confirmation.
- Safe file reading/writing/listing.
- Real-time time, alarms, and persistent SQLite reminders.
- System clipboard (Wayland wl-copy / wl-paste) and web article reader.
- Deep hardware controls: display brightness, battery telemetry, Wi-Fi scanning/toggle, Bluetooth power/devices, thermal sensors, CPU stats, audio sinks, microphone mute, screen lock.
- Application management: launching software, closing processes, volume control, screenshots.
- Persistent long-term memory: remember user preferences, facts, project stacks, and notes.
- Dynamic MCP bridge to 17 specialized servers (including full Storyteller Craft creative suite, Blender 3D, and Git).
- Agent Client Protocol (ACP) multi-agent bridge: query and delegate tasks to external ACP agents (e.g. Claude Code, Zed ACP agents, or other Antigravity ACP agents) using `call_acp_agent` and `list_acp_servers`.

Guidelines:
1. Always address the user as "Boss Munna" in your response.
2. Always prefer using dedicated tools (e.g. `set_screen_brightness`, `get_battery_status`, `add_reminder`, `get_clipboard_text`) over generic shell commands when available.
3. Be concise, accurate, helpful, and transparent about which tools you used.
4. Format output cleanly in Markdown.
"""


def _extract_content_text(content: Any) -> str:
    """Extracts clean string from LangChain AIMessage content (which may be a string, list of blocks, or stringified list)."""
    import ast
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
            else:
                parts.append(str(block))
        return "\n".join(parts)
    elif isinstance(content, str):
        s = content.strip()
        if (s.startswith('[') and s.endswith(']')) or (s.startswith('{') and s.endswith('}')):
            try:
                parsed = ast.literal_eval(s)
                if isinstance(parsed, list):
                    parts = []
                    for b in parsed:
                        if isinstance(b, dict) and "text" in b:
                            parts.append(b["text"])
                        else:
                            parts.append(str(b))
                    return "\n".join(parts)
                elif isinstance(parsed, dict) and "text" in parsed:
                    return str(parsed["text"])
            except Exception:
                pass
        return content
    return str(content)



def _get_llm(model_name: str = "gemini-3.8-flash"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment or .env file.")
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.2,
        request_timeout=30,
        max_retries=1
    )


CANDIDATE_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite"
]


class CentralAgentBrain:
    def __init__(self, session_id: str = "desktop_session"):
        self.session_id = session_id
        self.history: List[Any] = []
        self._init_models()

    def _init_models(self):
        self.bound_models = []
        for m in CANDIDATE_MODELS:
            try:
                llm = _get_llm(m)
                bound = llm.bind_tools(CORE_TOOLS)
                self.bound_models.append((m, bound))
            except Exception as e:
                pass

    def _invoke_with_cascade(
        self,
        messages: List[Any],
        progress_callback: Optional[Callable[[str], None]] = None,
        model_id: str = "default",
    ):
        """Invoke the configured model or fall back across the Gemini candidates."""
        if model_id != "default":
            model = get_chat_model(model_id).bind_tools(CORE_TOOLS)
            if progress_callback:
                progress_callback("Generating with your selected model...")
            return model.invoke(messages)

        last_error = None
        for name, bound_llm in self.bound_models:
            if progress_callback:
                progress_callback(f"Generating with {name.replace('-', ' ').title()}...")
            try:
                return bound_llm.invoke(messages)
            except Exception as e:
                err_str = str(e).lower()
                last_error = e
                if progress_callback:
                    progress_callback(f"{name.replace('-', ' ').title()} did not respond; trying the next available model...")
                # If rate limited (429) or overloaded (503), try next model in cascade
                if any(x in err_str for x in ["429", "resource_exhausted", "quota", "503", "unavailable"]):
                    continue
                else:
                    # Other fatal error, try next model as fallback anyway
                    continue
        raise last_error or RuntimeError("No candidate Gemini models were available.")

    def execute_prompt(
        self,
        user_prompt: str,
        progress_callback: Optional[Callable[[str], None]] = None,
        voice_mode: bool = False,
        mcp_servers: Optional[List[str]] = None,
        model_id: str = "default",
    ) -> Dict[str, Any]:
        """
        Executes a user prompt through the multi-step tool reasoning loop.
        Returns a dictionary with 'response', 'tool_calls_executed', and 'status'.
        """
        def report_progress(message: str) -> None:
            if progress_callback:
                progress_callback(message)

        user_prompt = user_prompt.strip()
        if not user_prompt:
            return {"response": "Please provide an instruction or question.", "tool_calls_executed": [], "status": "empty"}

        report_progress(f"Thinking: Analyzing instruction '{user_prompt[:45]}...'")

        # Check for direct search shortcut if requested
        if user_prompt.lower().startswith("/search "):
            q = user_prompt[8:].strip()
            report_progress(f"Action: Searching the web for '{q}'...")
            res = web_search.invoke({"query": q})
            return {"response": res, "tool_calls_executed": [{"tool": "web_search", "args": {"query": q}}], "status": "success"}

        # Assemble conversation context
        system_prompt = SYSTEM_PROMPT
        selected_mcp_servers = list(dict.fromkeys(mcp_servers or []))
        discovered_mcp_tools: Dict[str, set] = {}
        if selected_mcp_servers:
            configured_servers = load_mcp_config_strict().get("mcpServers", {})
            mcp_tool_context = []
            for server_name in selected_mcp_servers:
                server_config = configured_servers.get(server_name)
                if not server_config:
                    mcp_tool_context.append(
                        f"{server_name}: not configured; do not try to call it."
                    )
                    continue

                report_progress(f"Connecting to {server_name}...")
                try:
                    server_tools = asyncio.run(
                        fetch_server_tools_async(
                            server_name, server_config, raise_on_error=True
                        )
                    )
                    discovered_mcp_tools[server_name] = {
                        item["raw_name"] for item in server_tools
                    }
                    if server_tools:
                        tool_lines = [
                            json.dumps({
                                "name": item["raw_name"],
                                "description": item.get("description", ""),
                                "input_schema": item.get("input_schema", {}),
                            }, ensure_ascii=False)
                            for item in server_tools
                        ]
                        mcp_tool_context.append(
                            f"{server_name} tools:\n" + "\n".join(tool_lines)
                        )
                    else:
                        mcp_tool_context.append(
                            f"{server_name}: connected, but exposes no tools."
                        )
                except Exception as error:
                    discovered_mcp_tools[server_name] = set()
                    mcp_tool_context.append(f"{server_name}: connection failed: {error}")

            system_prompt += (
                "\n\nMCP CONNECTORS ATTACHED FOR THIS MESSAGE:\n"
                "Use call_mcp_software_tool(server_name, tool_name, arguments_json) "
                "to perform the user's request with these connectors. Only call a "
                "tool whose exact name appears in the discovered catalog below, and "
                "only on its listed server. If connection failed or no matching "
                "tool exists, explain that clearly and do not claim the action succeeded.\n"
                + "\n".join(mcp_tool_context)
            )
        if voice_mode:
            system_prompt += """

VOICE CONVERSATION MODE:
- Speak naturally and directly, as in a helpful live conversation.
- Keep spoken answers concise by default, but include all important details and never omit requested information.
- Use the available tools to complete requests, not merely describe how the user could do them.
- Before a long-running action, briefly say what you are doing; after it, summarize the outcome.
- Ask one clear follow-up question when essential details are missing; otherwise make a reasonable, reversible choice.
- Avoid Markdown tables, headings, and formatting that sound unnatural aloud.
- Never claim an action succeeded unless a tool confirms it.
- Do not reveal private chain-of-thought; provide a brief explanation or status when useful.
"""

        messages = [SystemMessage(content=system_prompt)]
        messages.extend(self.history[-8:])  # include last 8 turns of context
        messages.append(HumanMessage(content=user_prompt))

        tool_calls_log = []
        max_steps = 15
        curr_step = 0

        while curr_step < max_steps:
            curr_step += 1
            ai_msg = None

            report_progress(f"Reasoning (Step {curr_step}): Determining optimal plan & tool selection...")
            try:
                ai_msg = self._invoke_with_cascade(messages, progress_callback, model_id)
            except Exception as e:
                return {
                    "response": (
                        "The selected model could not complete the request. Check its endpoint, model name, credentials, and local service status."
                        if model_id != "default"
                        else f"AI Engine error: {e}"
                    ),
                    "tool_calls_executed": tool_calls_log,
                    "status": "error"
                }

            messages.append(ai_msg)

            # Check if model requested tool execution
            if not hasattr(ai_msg, "tool_calls") or not ai_msg.tool_calls:
                # No more tools needed, we have our final response
                report_progress("Formulating final answer for Boss Munna...")
                final_text = _extract_content_text(ai_msg.content)
                self.history.append(HumanMessage(content=user_prompt))
                self.history.append(AIMessage(content=final_text))
                record_chat_turn(self.session_id, "user", user_prompt)
                record_chat_turn(self.session_id, "assistant", final_text)

                return {
                    "response": final_text,
                    "tool_calls_executed": tool_calls_log,
                    "status": "success"
                }

            # Execute tool calls
            for tc in ai_msg.tool_calls:
                name = tc["name"]
                args = tc["args"]
                tool_id = tc["id"]

                tool_calls_log.append({"tool": name, "args": args})

                # Human-readable DeepSeek-style thought and action logging
                if name == "web_search":
                    action_desc = f"Searching web for '{args.get('query', '')}'"
                elif name == "run_shell_command":
                    action_desc = f"Running bash command `{str(args.get('command', ''))[:45]}`"
                elif name == "get_hardware_telemetry":
                    action_desc = "Inspecting hardware sensors (battery, thermals, brightness)"
                elif name == "adjust_system_setting":
                    action_desc = f"Adjusting {args.get('setting')} to {args.get('value')}"
                elif name == "list_reminders":
                    action_desc = "Reading reminders database"
                elif name == "add_reminder":
                    action_desc = f"Scheduling reminder '{args.get('message', '')}'"
                elif name == "search_notes":
                    action_desc = f"Searching notes for '{args.get('query', '')}'"
                elif name == "write_note":
                    action_desc = f"Saving note '{args.get('title', '')}'"
                elif name == "list_all_memories":
                    action_desc = "Recalling long-term user preferences & facts"
                elif name == "call_mcp_software_tool":
                    action_desc = f"Calling MCP tool {args.get('server_name')}/{args.get('tool_name')}"
                else:
                    action_desc = f"Calling {name}"

                report_progress(f"Running {name} ({action_desc})...")

                if name in TOOL_MAP:
                    try:
                        if name == "call_mcp_software_tool" and selected_mcp_servers:
                            requested_server = str(args.get("server_name", ""))
                            requested_tool = str(args.get("tool_name", ""))
                            allowed_tools = discovered_mcp_tools.get(requested_server)
                            if requested_server not in selected_mcp_servers:
                                res = (
                                    f"Error: MCP server '{requested_server}' is not attached "
                                    "to this message."
                                )
                            elif not allowed_tools or requested_tool not in allowed_tools:
                                res = (
                                    f"Error: MCP tool '{requested_tool}' was not discovered "
                                    f"on attached server '{requested_server}'."
                                )
                            else:
                                res = TOOL_MAP[name].invoke(args)
                        else:
                            res = TOOL_MAP[name].invoke(args)
                    except Exception as err:
                        res = f"Tool execution failed: {err}"
                else:
                    res = f"Error: Tool '{name}' not found."

                messages.append(ToolMessage(content=str(res), tool_call_id=tool_id))
                report_progress(f"Observed result from {name} — analyzing findings...")

        # Max steps reached: do one final pass to summarize/synthesize answer
        try:
            messages.append(HumanMessage(content="Please provide your final synthesized response based on the tool results above."))
            report_progress("Summarizing completed actions...")
            final_ai = self._invoke_with_cascade(messages, progress_callback, model_id)
            final_text = _extract_content_text(final_ai.content)
        except Exception:
            final_text = _extract_content_text(ai_msg.content) if ai_msg and hasattr(ai_msg, "content") else "Task processing completed."

        self.history.append(HumanMessage(content=user_prompt))
        self.history.append(AIMessage(content=final_text))
        record_chat_turn(self.session_id, "user", user_prompt)
        record_chat_turn(self.session_id, "assistant", final_text)

        return {
            "response": final_text,
            "tool_calls_executed": tool_calls_log,
            "status": "success"
        }
