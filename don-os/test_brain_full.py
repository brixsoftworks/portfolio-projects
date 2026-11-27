"""
test_brain_full.py

Comprehensive End-to-End Test for the Central Agent Brain & FastAPI Server.
Verifies multi-step tool execution, memory, time, hardware control, and REST endpoints.
"""

import time
import json
import urllib.request
import subprocess
from agent import CentralAgentBrain


def test_brain_direct():
    print("=" * 70)
    print("  1. Testing Central Agent Brain Direct Execution")
    print("=" * 70)

    brain = CentralAgentBrain(session_id="test_suite")

    # Test 1: Tool execution (time & battery)
    prompt1 = "What time is it right now?"
    print(f"\nUser: {prompt1}")
    res1 = brain.execute_prompt(prompt1)
    print(f"Tool Calls: {res1.get('tool_calls_executed')}")
    print(f"Agent:\n{res1.get('response')}")
    assert any(tc["tool"] == "get_current_time" for tc in res1.get("tool_calls_executed", [])), "Failed to call get_current_time"

    # Test 2: Memory store & recall
    prompt2 = "Remember that my secret project code is 'PROJECT_NEBULA_99'."
    print(f"\nUser: {prompt2}")
    res2 = brain.execute_prompt(prompt2)
    print(f"Agent:\n{res2.get('response')}")

    time.sleep(2)
    prompt3 = "What is my secret project code?"
    print(f"\nUser: {prompt3}")
    res3 = brain.execute_prompt(prompt3)
    print(f"Tool Calls: {res3.get('tool_calls_executed')}")
    print(f"Agent:\n{res3.get('response')}")
    assert "PROJECT_NEBULA_99" in str(res3.get("response")), "Failed to recall stored memory"

    print("\n✅ Central Agent Brain Direct Tests Passed!")


def test_server_and_api():
    print("\n" + "=" * 70)
    print("  2. Testing FastAPI Server Endpoints (Electron Bridge)")
    print("=" * 70)

    # Launch server
    proc = subprocess.Popen(["python3", "agent_server.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for server to bind port
    server_ready = False
    for attempt in range(20):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen("http://127.0.0.1:8765/api/health", timeout=1) as r:
                if r.status == 200:
                    server_ready = True
                    break
        except Exception:
            pass

    assert server_ready, "Server failed to start within 10 seconds."

    try:
        # Health check
        with urllib.request.urlopen("http://127.0.0.1:8765/api/health", timeout=5) as r:
            assert r.status == 200
            print("• /api/health: OK")

        # Telemetry Status
        with urllib.request.urlopen("http://127.0.0.1:8765/api/status", timeout=5) as r:
            data = json.loads(r.read().decode())
            assert data["status"] == "online"
            print(f"• /api/status: OK ({data['mcp_servers']} MCP servers detected)")

        # Chat endpoint
        req_data = json.dumps({"prompt": "What is my screen brightness?", "speak": False}).encode()
        req = urllib.request.Request("http://127.0.0.1:8765/api/chat", data=req_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            chat_res = json.loads(r.read().decode())
            print(f"• /api/chat tool calls: {chat_res.get('tool_calls_executed')}")
            print(f"• /api/chat response: {chat_res.get('response')}")
            assert any(tc["tool"] == "get_screen_brightness" for tc in chat_res.get("tool_calls_executed", [])), "Brightness tool not called"

        print("\n✅ Server & REST API Endpoints Passed!")
    finally:
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    test_brain_direct()
    test_server_and_api()
    print("\n" + "=" * 70)
    print("🎉 ALL CENTRAL BRAIN & SERVER TESTS PASSED!")
    print("=" * 70)
