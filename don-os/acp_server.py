"""
acp_server.py

Official Agent Client Protocol (ACP) Server for the Antigravity PA Assistant.
Allows code editors (Zed, JetBrains, VS Code ACP) and other AI agents to connect
to Antigravity PA over standard ACP JSON-RPC stdio.
"""

import asyncio
import os
import sys
from typing import Any, List, Optional
from uuid import uuid4

import acp
from acp import Agent, InitializeResponse, NewSessionResponse, PromptResponse, run_agent
from acp.interfaces import Client
from acp.schema import Implementation, ClientCapabilities
from agent import CentralAgentBrain


class AntigravityACPAgent(Agent):
    def __init__(self):
        super().__init__()
        self._conn: Optional[Client] = None
        self.brain = CentralAgentBrain(session_id="acp_stdio")

    def on_connect(self, conn: Client) -> None:
        self._conn = conn

    async def initialize(
        self,
        protocol_version: int,
        client_capabilities: Optional[ClientCapabilities] = None,
        client_info: Optional[Implementation] = None,
        **kwargs: Any,
    ) -> InitializeResponse:
        return InitializeResponse(
            protocol_version=protocol_version,
            agent_info=Implementation(
                name="Antigravity PA",
                version="1.0.0"
            )
        )

    async def new_session(
        self,
        cwd: str,
        additional_directories: Optional[List[str]] = None,
        mcp_servers: Optional[List[Any]] = None,
        **kwargs: Any,
    ) -> NewSessionResponse:
        session_id = uuid4().hex
        return NewSessionResponse(session_id=session_id)

    async def prompt(
        self,
        session_id: str,
        prompt: list[Any],
        **kwargs: Any,
    ) -> PromptResponse:
        # Extract user prompt text from blocks
        prompt_parts = []
        for block in prompt:
            if isinstance(block, dict):
                prompt_parts.append(block.get("text", ""))
            elif hasattr(block, "text"):
                prompt_parts.append(block.text)
            elif hasattr(block, "content") and hasattr(block.content, "text"):
                prompt_parts.append(block.content.text)
            else:
                prompt_parts.append(str(block))

        full_prompt = " ".join([p for p in prompt_parts if p]).strip()
        if not full_prompt:
            return PromptResponse(stop_reason="end_turn")

        loop = asyncio.get_running_loop()
        progress_updates: asyncio.Queue[str] = asyncio.Queue()

        def report_progress(message: str) -> None:
            loop.call_soon_threadsafe(progress_updates.put_nowait, message)

        # Execute the agent off-loop while forwarding safe progress updates to the ACP client.
        work = loop.run_in_executor(
            None,
            lambda: self.brain.execute_prompt(full_prompt, progress_callback=report_progress),
        )

        while not work.done():
            try:
                status = await asyncio.wait_for(progress_updates.get(), timeout=0.2)
            except asyncio.TimeoutError:
                continue
            if self._conn:
                await self._conn.session_update(
                    session_id=session_id,
                    update=acp.update_agent_message_text(f"Working: {status}\n"),
                )

        res = await work
        while not progress_updates.empty():
            status = progress_updates.get_nowait()
            if self._conn:
                await self._conn.session_update(
                    session_id=session_id,
                    update=acp.update_agent_message_text(f"Working: {status}\n"),
                )
        response_text = res.get("response", "")

        # Stream update back to ACP client
        if self._conn:
            chunk = acp.update_agent_message_text(response_text)
            await self._conn.session_update(session_id=session_id, update=chunk)

        return PromptResponse(stop_reason="end_turn")


async def main():
    agent = AntigravityACPAgent()
    await run_agent(agent)


if __name__ == "__main__":
    asyncio.run(main())
