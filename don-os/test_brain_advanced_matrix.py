"""
test_brain_advanced_matrix.py

Advanced Multi-Domain Stress and Integration Test Matrix for CentralAgentBrain:
- Test 1: Full System Diagnostics & Hardware Telemetry (Battery, CPU, Brightness, Network, Audio)
- Test 2: Chrono Pipeline (Current Time -> Calculation -> Reminder Creation -> Reminder Verification)
- Test 3: Inter-Agent ACP Delegation (List ACP servers -> Delegate prompt to ACP agent -> Verify)
- Test 4: Dynamic MCP Software Bridge (Query MCP server registry -> Execute MCP tool via stdio)
- Test 5: Cognitive Long-Term Memory & Note Search (Save note -> Search notes -> Recall facts)
- Test 6: Web Intelligence to Disk Synthesis (Web search -> Format summary -> Write file -> Verify read)
"""

import os
import sys
import time
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import CentralAgentBrain


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"   ADVANCED TEST: {title}")
    print("=" * 80)


def execute_and_log(brain: CentralAgentBrain, prompt: str, test_id: str):
    print(f"\n[Test {test_id}] User Request:")
    print(f"   \"{prompt}\"")
    print("-" * 80)

    start_time = time.time()
    result = brain.execute_prompt(prompt)
    elapsed = time.time() - start_time

    status = result.get("status")
    tool_calls = result.get("tool_calls_executed", [])
    response = result.get("response", "")

    print(f" Execution Summary:")
    print(f"  • Status: {status}")
    print(f"  • Latency: {elapsed:.2f}s")
    print(f"  • Tools Invoked ({len(tool_calls)}):")
    for idx, tc in enumerate(tool_calls, 1):
        print(f"     {idx}. {tc['tool']}({tc['args']})")

    print(f"\n[AI] Agent Response:\n{response}")
    print("-" * 80)
    return result


def main():
    print("=" * 80)
    print("   STARTING COMPREHENSIVE ADVANCED BRAIN TEST MATRIX")
    print("=" * 80)

    # Initialize a clean dedicated brain instance
    session_id = f"matrix_test_{int(time.time())}"
    brain = CentralAgentBrain(session_id=session_id)
    print(f"Initialized CentralAgentBrain session: '{session_id}'\n")

    test_results = {}

    # --------------------------------------------------------------------------
    # TEST 1: Full System Diagnostics & Hardware Telemetry
    # --------------------------------------------------------------------------
    print_header("1. Hardware Telemetry & Diagnostics Multi-Tool Chaining")
    res1 = execute_and_log(
        brain,
        "Perform a full system diagnostic audit: check battery level, screen brightness, network connection status, and CPU telemetry. Summarize everything in a neat report.",
        "1"
    )
    tools1 = [tc["tool"] for tc in res1.get("tool_calls_executed", [])]
    # Check that hardware tools were called
    has_hw_tools = any(t in tools1 for t in ["get_battery_status", "get_screen_brightness", "get_network_status", "get_cpu_info"])
    test_results["Test 1: Hardware Telemetry"] = "PASSED" if (res1.get("status") == "success" and has_hw_tools) else "FAILED"
    time.sleep(2)

    # --------------------------------------------------------------------------
    # TEST 2: Chrono Pipeline & Persistent Reminders
    # --------------------------------------------------------------------------
    print_header("2. Chrono Pipeline & Reminder Lifecycle")
    res2 = execute_and_log(
        brain,
        "What is the current time? Then add a reminder for '2026-12-31 23:59:00' with message 'New Year Hyperion Milestone', and list the active reminders to verify it was scheduled.",
        "2"
    )
    tools2 = [tc["tool"] for tc in res2.get("tool_calls_executed", [])]
    has_time_tools = any(t in tools2 for t in ["get_current_time", "add_reminder", "list_reminders"])
    test_results["Test 2: Chrono & Reminders"] = "PASSED" if (res2.get("status") == "success" and has_time_tools) else "FAILED"
    time.sleep(2)

    # --------------------------------------------------------------------------
    # TEST 3: Inter-Agent ACP Delegation
    # --------------------------------------------------------------------------
    print_header("3. Agent Client Protocol (ACP) Inter-Agent Communication")
    res3 = execute_and_log(
        brain,
        "First, list the available ACP servers using the list_acp_servers tool. Then use call_acp_agent to ask 'antigravity-pa' the following question: 'Calculate 25 * 25 and reply with the exact number'.",
        "3"
    )
    tools3 = [tc["tool"] for tc in res3.get("tool_calls_executed", [])]
    has_acp_tools = any(t in tools3 for t in ["list_acp_servers", "call_acp_agent"])
    has_correct_math = "625" in res3.get("response", "")
    test_results["Test 3: ACP Delegation"] = "PASSED" if (res3.get("status") == "success" and (has_acp_tools or has_correct_math)) else "FAILED"
    time.sleep(2)

    # --------------------------------------------------------------------------
    # TEST 4: Dynamic MCP Software Bridge
    # --------------------------------------------------------------------------
    print_header("4. Model Context Protocol (MCP) Software Tool Execution")
    res4 = execute_and_log(
        brain,
        "Check what external MCP servers are registered using list_available_mcp_servers, and then use call_mcp_software_tool to call the 'git_status' tool on the 'git-vcs' server.",
        "4"
    )
    tools4 = [tc["tool"] for tc in res4.get("tool_calls_executed", [])]
    has_mcp_tools = any(t in tools4 for t in ["list_available_mcp_servers", "call_mcp_software_tool"])
    test_results["Test 4: MCP Software Bridge"] = "PASSED" if (res4.get("status") == "success" and has_mcp_tools) else "FAILED"
    time.sleep(2)

    # --------------------------------------------------------------------------
    # TEST 5: Cognitive Long-Term Memory & Note Search
    # --------------------------------------------------------------------------
    print_header("5. Cognitive Long-Term Memory & Note Management")
    res5a = execute_and_log(
        brain,
        "Save a note titled 'Quantum Leap Project' with the content: 'Architecture: Rust + WebAssembly. Lead Researcher: Dr. Mullainathan. Target launch: Q3 2027.'",
        "5A"
    )
    time.sleep(1)
    res5b = execute_and_log(
        brain,
        "Search your saved notes for 'Quantum Leap' and tell me the lead researcher and target launch date.",
        "5B"
    )
    tools5 = [tc["tool"] for tc in res5b.get("tool_calls_executed", [])]
    has_mem_tools = any(t in tools5 for t in ["search_notes", "recall"])
    has_answer = "Mullainathan" in res5b.get("response", "") or "2027" in res5b.get("response", "")
    test_results["Test 5: Memory & Notes"] = "PASSED" if (res5b.get("status") == "success" and (has_mem_tools or has_answer)) else "FAILED"
    time.sleep(2)

    # --------------------------------------------------------------------------
    # TEST 6: Web Intelligence & Local File Export Pipeline
    # --------------------------------------------------------------------------
    print_header("6. Web Intelligence to File Export Pipeline")
    test_file = "test_reports/ai_landscape_report.txt"
    if os.path.exists("test_reports"):
        shutil.rmtree("test_reports")

    res6 = execute_and_log(
        brain,
        f"Search the web for 'Python 3.14 release features', write a 3-bullet summary into '{test_file}', and then read the file back to verify the content.",
        "6"
    )
    tools6 = [tc["tool"] for tc in res6.get("tool_calls_executed", [])]
    has_file_tools = any(t in tools6 for t in ["write_file", "read_file"])
    file_exists = os.path.exists(test_file)
    test_results["Test 6: Web Search & File Export"] = "PASSED" if (res6.get("status") == "success" and (has_file_tools or file_exists)) else "FAILED"

    # Cleanup test reports
    if os.path.exists("test_reports"):
        shutil.rmtree("test_reports")

    # --------------------------------------------------------------------------
    # Test Matrix Summary Scorecard
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(" FINAL TEST MATRIX SCORECARD")
    print("=" * 80)
    all_passed = True
    for test_name, status in test_results.items():
        emoji = "[PASS]" if status == "PASSED" else "[FAIL]"
        print(f"  {emoji} {test_name}: {status}")
        if status != "PASSED":
            all_passed = False

    print("=" * 80)
    if all_passed:
        print(" ALL ADVANCED BRAIN TESTS PASSED WITH 100% SUCCESS!")
    else:
        print("[WARN] Some tests encountered issues. Review logs above.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

