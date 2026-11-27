"""
multi_agent_core/specialist_dot.py — Specialist Agent ("Dot") Instance

Encapsulates an isolated agent worker with a focused persona, scoped tools,
and independent context window.
"""

import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from multi_agent_core.blackboard import SharedBlackboard
from multi_agent_core.action_gateway import GovernedActionGateway

# Registry of curated roles with explicit boundaries
ROLE_CATALOG = {
    "researcher": {
        "title": "Intelligence & Research Dot",
        "description": "Deep literature, web, and documentation analysis specialist.",
        "system_prompt": (
            "You are the Intelligence & Research Agent. Your job is to gather accurate "
            "facts, explore data, synthesize findings, and produce structured analytical notes. "
            "Focus purely on factual evidence. Do not write implementation code."
        ),
        "allowed_tools": ["web_search", "read_web_page", "read_file"]
    },
    "coder": {
        "title": "Systems Software Dot",
        "description": "Code authoring, refactoring, and file modification specialist.",
        "system_prompt": (
            "You are the Systems Software Engineer. You write clean, robust, type-safe code. "
            "Inspect requirements thoroughly and produce production-ready implementations."
        ),
        "allowed_tools": ["read_file", "write_file", "append_file", "list_directory"]
    },
    "auditor": {
        "title": "Security & QA Auditor Dot",
        "description": "Verification, security auditing, and test validation specialist.",
        "system_prompt": (
            "You are the Security & QA Auditor. Your goal is to inspect code for vulnerabilities, "
            "verify edge cases, and run tests. Ensure all acceptance criteria are rigorously met."
        ),
        "allowed_tools": ["read_file", "bash_tool"]
    },
    "architect": {
        "title": "System Architect Dot",
        "description": "High-level design, schema definitions, and system topology specialist.",
        "system_prompt": (
            "You are the System Architect. You define component interfaces, data structures, "
            "and technical blueprints to coordinate engineering execution."
        ),
        "allowed_tools": ["read_file", "list_directory"]
    }
}


def _clean_content(content: Any) -> str:
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)

class SpecialistDot:
    """An autonomous specialist agent worker."""

    def __init__(
        self,
        agent_id: str,
        role_key: str,
        directive: str,
        model_instance: Any,
        all_tools: List[Any],
        blackboard: SharedBlackboard,
        gateway: GovernedActionGateway
    ):
        self.agent_id = agent_id
        self.role_key = role_key
        self.role_info = ROLE_CATALOG.get(role_key, ROLE_CATALOG["coder"])
        self.directive = directive
        self.model_instance = model_instance
        self.blackboard = blackboard
        self.gateway = gateway
        
        # Filter only tools authorized for this specialist
        allowed = set(self.role_info.get("allowed_tools", []))
        self.tools = [t for t in all_tools if getattr(t, "name", "") in allowed]
        self.tool_map = {getattr(t, "name", ""): t for t in self.tools}

        # Bind tools to the model
        if self.tools and hasattr(self.model_instance, "bind_tools"):
            self.llm = self.model_instance.bind_tools(self.tools)
        else:
            self.llm = self.model_instance

        self.status = "INITIALIZED"  # INITIALIZED, WORKING, COMPLETED, FAILED
        self.history: List[Any] = []
        self.output: str = ""

    async def run(self, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> str:
        """Executes the specialist agent's directive."""
        self.status = "WORKING"
        if progress_callback:
            progress_callback({
                "type": "agent_started",
                "agent_id": self.agent_id,
                "role": self.role_info["title"],
                "directive": self.directive
            })

        # Inject shared context from the blackboard
        context_digest = self.blackboard.get_context_summary()
        prompt_text = (
            f"### ASSIGNED DIRECTIVE:\n{self.directive}\n\n"
            f"### SHARED FLEET BLACKBOARD (Prior deliverables from other agents):\n"
            f"{context_digest}\n\n"
            f"Execute your directive using your tools if needed. Output your final synthesized result."
        )

        messages = [
            SystemMessage(content=self.role_info["system_prompt"]),
            HumanMessage(content=prompt_text)
        ]

        # Multi-turn tool execution loop (max 4 turns)
        for turn in range(4):
            try:
                ai_message = await asyncio.to_thread(self.llm.invoke, messages)
                messages.append(ai_message)

                # Check if tool calls were generated
                tool_calls = getattr(ai_message, "tool_calls", None) or []
                if not tool_calls:
                    # Final textual response reached
                    self.output = _clean_content(ai_message.content) if hasattr(ai_message, "content") else str(ai_message)
                    break

                for tc in tool_calls:
                    tool_name = tc.get("name")
                    tool_args = tc.get("args", {})
                    call_id = tc.get("id", f"call-{int(time.time()*1000)}")

                    # Audit and evaluate through the Governed Action Gateway
                    eval_record = self.gateway.evaluate_action(self.agent_id, self.role_key, tool_name, tool_args)
                    
                    if eval_record["decision"] == "BLOCKED":
                        tool_result = f"Error: Action '{tool_name}' was blocked by safety policy."
                    else:
                        tool_func = self.tool_map.get(tool_name)
                        if tool_func:
                            if progress_callback:
                                progress_callback({
                                    "type": "agent_tool_call",
                                    "agent_id": self.agent_id,
                                    "role": self.role_info["title"],
                                    "tool": tool_name,
                                    "args": str(tool_args)[:80]
                                })
                            try:
                                if hasattr(tool_func, "invoke"):
                                    tool_result = await asyncio.to_thread(tool_func.invoke, tool_args)
                                else:
                                    tool_result = await asyncio.to_thread(tool_func, **tool_args)
                            except Exception as ex:
                                tool_result = f"Tool Execution Error: {ex}"
                        else:
                            tool_result = f"Tool '{tool_name}' not available for {self.role_info['title']}."

                    messages.append(ToolMessage(content=str(tool_result)[:3000], tool_call_id=call_id))

            except Exception as e:
                self.output = f"Execution paused with notice: {e}"
                break

        if not self.output and messages:
            last = messages[-1]
            self.output = getattr(last, "content", str(last))

        self.status = "COMPLETED"

        # Publish this agent's deliverable to the Shared Blackboard
        page_title = f"{self.role_info['title']} Deliverable"
        self.blackboard.publish_page(
            page_id=f"page-{self.agent_id}",
            author_agent=self.agent_id,
            role=self.role_info["title"],
            title=page_title,
            content=self.output,
            tags=[self.role_key]
        )

        if progress_callback:
            progress_callback({
                "type": "agent_completed",
                "agent_id": self.agent_id,
                "role": self.role_info["title"],
                "deliverable": self.output[:150]
            })

        return self.output
