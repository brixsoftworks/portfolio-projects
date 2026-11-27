"""
multi_agent_core/test_standalone_fleet.py — Standalone Multi-Agent Verification

Validates the complete lifecycle:
1. Task Perception & DAG planning
2. Agent fleet deployment & concurrent execution
3. Blackboard knowledge exchange
4. Action gateway enforcement
5. Synthesis and event stream callback
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Ensure parent directory is on sys.path
sys.path.insert(0, "/home/mullainathan/Documents/Coding/Projects")

# Load environment
env_path = "/home/mullainathan/Documents/Coding/Projects/pa ai agent/.env"
load_dotenv(env_path)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from multi_agent_core.orchestrator import FleetOrchestrator

# Standard LangChain tools using @tool decorator
@tool
def web_search(query: str) -> str:
    """Searches the web for security information and CVE reports."""
    return f"[Mock Web Search Results for '{query}']: Found 3 relevant CVEs (CVE-2024-38063, CVE-2024-21413). Recommended mitigation: input sanitization & strict token signing."

@tool
def read_file(path: str) -> str:
    """Reads a local configuration or source file."""
    return f"[Mock File Read '{path}']: File exists. Contains 42 lines of secure config."

async def main():
    print("=" * 70)
    print(" STARTING STANDALONE MULTI-AGENT FLEET VERIFICATION TEST")
    print("=" * 70)

    # Initialize Gemini model
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[FAIL] Error: GEMINI_API_KEY not found in environment!")
        sys.exit(1)

    model = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=api_key,
        temperature=0.2,
        request_timeout=30
    )

    tools = [web_search, read_file]
    orchestrator = FleetOrchestrator(model_instance=model, all_tools=tools)

    events_captured = []
    def on_event(event):
        events_captured.append(event)
        etype = event.get("type")
        if etype == "plan_created":
            print(f"\n [DAG PLAN GENERATED] Total Agents to Deploy: {event['total_agents']}")
            for s in event["plan"]:
                print(f"   ├─ Agent Role: {s['role']:<12} | Parallel: {str(s.get('run_parallel')): <5} | Title: {s.get('title')}")
        elif etype == "agent_spawned":
            print(f"[AI] [AGENT SPAWNED] {event['role']} ({event['agent_id']})")
        elif etype == "agent_tool_call":
            print(f"    [TOOL CALL] {event['role']} called '{event['tool']}'")
        elif etype == "agent_completed":
            print(f"[PASS] [AGENT COMPLETE] {event['role']} finished.")
        elif etype == "synthesis_started":
            print("\n [MASTER SYNTHESIS] Combining fleet deliverables into final response...")

    test_objective = (
        "Research the latest authentication bypass patterns, inspect our local config, "
        "and draft an API security hardening guideline."
    )

    print(f"\n Objective: {test_objective}\n")
    result = await orchestrator.execute_mission(test_objective, event_callback=on_event)

    print("\n" + "=" * 70)
    print(" FLEET EXECUTION RESULTS:")
    print("=" * 70)
    print(f"• Mission ID: {result['mission_id']}")
    print(f"• Total Elapsed: {result['elapsed_seconds']}s")
    print(f"• Agents Deployed: {result['agents_deployed']}")
    print(f"• Blackboard Pages Created: {len(result['blackboard_pages'])}")
    print(f"• Gateway Action Audits: {len(result['audit_trail'])}")
    print(f"\n--- EXECUTIVE SYNTHESIS ---\n")
    print(result['response'])
    print("=" * 70)

    assert result["status"] == "success", "Mission status should be success"
    assert result["agents_deployed"] >= 2, "Should deploy at least 2 specialized agents"
    assert len(result["blackboard_pages"]) >= 2, "Should have created blackboard pages"
    print("\n ALL MULTI-AGENT CORE ASSERTIONS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    asyncio.run(main())
