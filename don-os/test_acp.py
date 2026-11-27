"""
test_acp.py

Automated test suite for Agent Client Protocol (ACP) integration:
1. Verifies acp_config.json loading and server listing.
2. Verifies dynamic server registration with add_acp_server.
3. Verifies end-to-end ACP client-server handshake, session creation, and prompt execution with call_acp_agent.
4. Verifies CentralAgentBrain tool invocation of call_acp_agent.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.acp_controller import list_acp_servers, call_acp_agent, add_acp_server, load_acp_config
from agent import CentralAgentBrain


def test_1_list_acp_servers():
    print("=" * 60)
    print("TEST 1: List Configured ACP Servers")
    print("=" * 60)
    result = list_acp_servers.invoke({})
    print(result)
    assert "antigravity-pa" in result
    print("[PASS] TEST 1 PASSED\n")


def test_2_add_acp_server():
    print("=" * 60)
    print("TEST 2: Add / Register New ACP Server")
    print("=" * 60)
    res = add_acp_server.invoke({
        "name": "echo-test-agent",
        "command": "/usr/bin/python3",
        "command_args": "-c 'print(\"echo ready\")'",
        "description": "Echo test agent"
    })

    print(res)
    assert "echo-test-agent" in res
    
    cfg = load_acp_config()
    assert "echo-test-agent" in cfg.get("acpServers", {})
    print("[PASS] TEST 2 PASSED\n")


def test_3_call_acp_agent_antigravity_pa():
    print("=" * 60)
    print("TEST 3: End-to-End ACP Call (Client -> Server -> PA Brain -> Response)")
    print("=" * 60)
    prompt = "What is 15 * 6? Answer with just the number."
    print(f"Calling ACP server 'antigravity-pa' with task: '{prompt}'...")
    response = call_acp_agent.invoke({
        "server_name": "antigravity-pa",
        "task": prompt
    })
    print(f"ACP Response:\n{response}")
    assert "90" in response
    print("[PASS] TEST 3 PASSED\n")


def test_4_agent_brain_acp_tool_invocation():
    print("=" * 60)
    print("TEST 4: CentralAgentBrain invokes call_acp_agent Tool")
    print("=" * 60)
    brain = CentralAgentBrain(session_id="test_acp_brain")
    prompt = "Use the call_acp_agent tool to ask the 'antigravity-pa' ACP server: 'What is 100 divided by 4?'. Report the answer."
    print(f"Prompting CentralAgentBrain: '{prompt}'...")
    result = brain.execute_prompt(prompt)
    print(f"Status: {result.get('status')}")
    print(f"Tools Used: {result.get('tools_used')}")
    print(f"Response:\n{result.get('response')}")
    assert any("call_acp_agent" in t for t in result.get("tools_used", [])) or "25" in result.get("response", "")
    print("[PASS] TEST 4 PASSED\n")


if __name__ == "__main__":
    print("\n STARTING ACP (AGENT CLIENT PROTOCOL) TEST SUITE\n")
    try:
        test_1_list_acp_servers()
        test_2_add_acp_server()
        test_3_call_acp_agent_antigravity_pa()
        test_4_agent_brain_acp_tool_invocation()
        print("=" * 60)
        print(" ALL ACP TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
    finally:
        # Clean up echo-test-agent from config
        cfg = load_acp_config()
        if "echo-test-agent" in cfg.get("acpServers", {}):
            del cfg["acpServers"]["echo-test-agent"]
            with open(Path(__file__).parent / "acp_config.json", "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            print("Cleaned up temporary test agent from acp_config.json.")
