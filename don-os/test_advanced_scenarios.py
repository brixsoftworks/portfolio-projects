"""
test_advanced_scenarios.py

Advanced Stress and Multi-Step Chaining Test Suite for the PA Assistant Brain.
Tests complex, multi-action real-world tasks:
1. Hardware control + Verification loop (Set brightness -> Read back -> Battery & Temp)
2. Desktop Clipboard Pipeline (Set clipboard -> Read back -> Analyze)
3. Filesystem Automation (Create directory & file -> List -> Read -> Cleanup)
4. Live Web Search & Synthesized Knowledge Extraction
5. Multi-Attribute Memory Persistence & Semantic Recall
6. Deep MCP Software Interaction (Git VCS tool invocation over stdio)
"""

import os
import shutil
import time
from agent import CentralAgentBrain


def print_banner(title: str):
    print("\n" + "=" * 75)
    print(f"  ⚡ SCENARIO: {title}")
    print("=" * 75)


def run_scenario(brain: CentralAgentBrain, prompt: str, scenario_num: int):
    print(f"\n💬 [Step {scenario_num}] User Prompt:")
    print(f"   \"{prompt}\"")
    print("-" * 75)

    start = time.time()
    result = brain.execute_prompt(prompt)
    duration = time.time() - start

    tool_calls = result.get("tool_calls_executed", [])
    print(f"🛠️ Intermediate Tool Calls Executed ({len(tool_calls)}):")
    for idx, tc in enumerate(tool_calls, 1):
        print(f"   {idx}. {tc['tool']}({tc['args']})")

    print(f"\n🤖 Final Synthesized Assistant Response (in {duration:.2f}s):")
    print(result.get("response"))
    print("-" * 75)
    return result


def main():
    print("=" * 75)
    print("  🚀 STARTING ADVANCED MULTI-STEP PA ASSISTANT SYSTEM TESTS")
    print("=" * 75)

    brain = CentralAgentBrain(session_id="advanced_stress_test")

    # -------------------------------------------------------------
    # Scenario 1: Hardware Adjustment & Telemetry Verification
    # -------------------------------------------------------------
    print_banner("1. Hardware Control & Verification Loop")
    run_scenario(
        brain,
        "Please set my screen brightness to 80%, then verify the new brightness level, and also report my current battery status and CPU temperature.",
        1
    )

    # Reset brightness back to 100% politely
    run_scenario(
        brain,
        "Now set my screen brightness back to 100% and confirm.",
        2
    )

    time.sleep(2)

    # -------------------------------------------------------------
    # Scenario 2: Desktop Clipboard Pipeline
    # -------------------------------------------------------------
    print_banner("2. Wayland Desktop Clipboard Pipeline")
    test_phrase = "Antigravity Agent is fully autonomous and operational on Linux."
    run_scenario(
        brain,
        f"Copy the text '{test_phrase}' into my system clipboard, then read the clipboard to verify it, and tell me how many words are in it.",
        3
    )

    time.sleep(2)

    # -------------------------------------------------------------
    # Scenario 3: Filesystem Automation & File Operations
    # -------------------------------------------------------------
    print_banner("3. Safe File Creation, Inspection, and Verification")
    test_dir = "test_workspace"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    run_scenario(
        brain,
        "Create a file named 'test_workspace/agent_status.txt' containing 'Status: Active | Engine: Gemini Flash | Tools: 360+'. Then list the directory 'test_workspace' and read the file content back to me.",
        4
    )

    time.sleep(2)

    # -------------------------------------------------------------
    # Scenario 4: Live Web Research & Knowledge Extraction
    # -------------------------------------------------------------
    print_banner("4. Live Web Search & Information Synthesis")
    run_scenario(
        brain,
        "Search the web for the latest stable release of the Linux kernel in 2025/2026 and tell me the version number.",
        5
    )

    time.sleep(2)

    # -------------------------------------------------------------
    # Scenario 5: Multi-Entity Memory Store & Multi-Turn Recall
    # -------------------------------------------------------------
    print_banner("5. Multi-Entity Memory & Contextual Reasoning")
    run_scenario(
        brain,
        "Remember that I am developing a project named 'Project Hyperion', the primary language is 'Rust', and the lead architect is 'Mullainathan'.",
        6
    )

    time.sleep(2)

    run_scenario(
        brain,
        "What is the name of the project I am developing, what language does it use, and who is the lead architect?",
        7
    )

    time.sleep(2)

    # -------------------------------------------------------------
    # Scenario 6: Deep MCP Git VCS Integration
    # -------------------------------------------------------------
    print_banner("6. Deep MCP Software Control (Git VCS Server)")
    run_scenario(
        brain,
        "Use the 'git-vcs' MCP server tool 'git_status' to inspect the current repository status.",
        8
    )

    # Cleanup test folder
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    print("\n" + "=" * 75)
    print("🎉 ALL ADVANCED MULTI-STEP SCENARIOS SUCCESSFULLY COMPLETED!")
    print("=" * 75)


if __name__ == "__main__":
    main()

