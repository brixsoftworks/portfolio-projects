"""
test_autonomous_project_lifecycle.py

Comprehensive End-to-End Autonomous Project Lifecycle Test:
Tests the CentralAgentBrain on a complete loop:
Scaffold Project -> Audit & Detect Bug -> Fix Code -> Verify Clean Tests -> Store Memory & Clipboard.
"""

import os
import sys
import time
import shutil
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from agent import CentralAgentBrain
from tools.desktop_workflow_tool import get_clipboard_text
from tools.memory_tool import search_notes


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f"   {title}")
    print("=" * 80)


def run_prompt_and_log(brain: CentralAgentBrain, prompt: str, step_label: str):
    print(f"\n [{step_label}] User Prompt:")
    print(f"   \"{prompt}\"")
    print("-" * 80)

    start = time.time()
    result = brain.execute_prompt(prompt)
    duration = time.time() - start

    status = result.get("status")
    tool_calls = result.get("tool_calls_executed", [])
    response = result.get("response", "")

    print(f"\n Execution Metrics:")
    print(f"   • Status: {status}")
    print(f"   • Duration: {duration:.2f}s")
    print(f"   • Tool Calls Executed ({len(tool_calls)}):")
    for idx, tc in enumerate(tool_calls, 1):
        print(f"      {idx}. {tc['tool']}({tc['args']})")

    print(f"\n[AI] Assistant Response:\n{response}")
    print("-" * 80)
    return result


def main():
    print("=" * 80)
    print("   AUTONOMOUS END-TO-END PROJECT CREATION, AUDIT & AUTO-FIX LOOP TEST")
    print("=" * 80)

    project_dir = Path(__file__).parent / "projects" / "quantum_calc"
    if project_dir.exists():
        shutil.rmtree(project_dir.parent)

    session_id = f"autonomous_loop_{int(time.time())}"
    brain = CentralAgentBrain(session_id=session_id)
    print(f"Session initialized: {session_id}\n")

    # --------------------------------------------------------------------------
    # MASTER AUTONOMOUS LIFECYCLE PROMPT
    # --------------------------------------------------------------------------
    master_prompt = (
        "You are acting as an autonomous software engineer. "
        "Perform this complete project engineering lifecycle in directory 'projects/quantum_calc':\n"
        "1. Check the system battery status and CPU info before starting.\n"
        "2. Scaffold a project in 'projects/quantum_calc' with two files:\n"
        "   - 'calculator.py': A Python module with class 'QuantumCalculator' containing methods: "
        "add(a, b), subtract(a, b), multiply(a, b), and divide(a, b). "
        "PURPOSELY introduce a bug: in divide(a, b), write 'return a * b' instead of 'return a / b'.\n"
        "   - 'test_calculator.py': A standard unittest test suite testing add, subtract, multiply, and divide(10, 2) == 5.\n"
        "3. Run the test suite using bash_tool ('python3 -m unittest projects/quantum_calc/test_calculator.py') "
        "to audit the code and observe the failing assertion.\n"
        "4. Fix the bug in 'projects/quantum_calc/calculator.py' using write_file so that divide correctly returns a / b (with zero division check).\n"
        "5. Re-run the test suite using bash_tool to verify that 100% of the tests pass with exit code 0.\n"
        "6. Save a note titled 'Quantum Calc Audit Report' using save_note with details of the bug found and the fix applied.\n"
        "7. Copy the text 'AUDIT COMPLETE: All tests passed.' to the desktop clipboard using set_clipboard_text.\n"
        "Report your step-by-step progress, the exact test failure observed, the fix applied, and the final verification."
    )

    print_banner("EXECUTING FULL AUTONOMOUS LOOP: CREATE -> AUDIT -> FIX -> VERIFY")
    res = run_prompt_and_log(brain, master_prompt, "AUTONOMOUS-MASTER-LOOP")

    # --------------------------------------------------------------------------
    # VERIFICATION OF ARTIFACTS AND POST-CONDITIONS
    # --------------------------------------------------------------------------
    print_banner("VERIFYING LOCAL ARTIFACTS AND STATE")

    calc_file = project_dir / "calculator.py"
    test_file = project_dir / "test_calculator.py"

    print(f"• Checking file existence: {calc_file}")
    assert calc_file.exists(), f"Expected {calc_file} to exist!"
    calc_code = calc_file.read_text(encoding="utf-8")
    print(f"  [calculator.py content preview]:\n{calc_code[:200]}...")

    print(f"\n• Checking file existence: {test_file}")
    assert test_file.exists(), f"Expected {test_file} to exist!"

    # Verify that the fix was applied (divide returns a / b or handles ZeroDivisionError)
    assert "/" in calc_code, "Expected fixed calculator.py to contain division operator '/'"
    print("  [PASS] Bug fix verified in code: division operator present.")

    # Verify test execution directly
    import subprocess
    cmd = [sys.executable, "-m", "unittest", "test_calculator.py"]
    test_run = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)

    print(f"\n• Running unittest independently on fixed code:")
    print(f"  Exit code: {test_run.returncode}")
    print(f"  Stdout/Stderr: {test_run.stderr.strip() or test_run.stdout.strip()}")
    assert test_run.returncode == 0, f"Tests should pass! Got: {test_run.stderr}"
    print("  [PASS] All unittests passed cleanly with exit code 0!")

    # Verify clipboard
    cb_text = get_clipboard_text.invoke({})
    print(f"\n• Checking clipboard content: '{cb_text}'")
    if "AUDIT COMPLETE" in cb_text:
        print("  [PASS] Clipboard contains verification status!")
    else:
        print("  ℹ Clipboard note: " + cb_text)

    # Verify note in database
    notes = search_notes.invoke({"query": "Quantum Calc"})
    print(f"\n• Checking saved memory notes:\n{notes}")
    assert "Quantum Calc" in notes or "Audit" in notes or "calculator" in notes.lower()
    print("  [PASS] Project audit note successfully saved and indexed in memory database!")

    # Cleanup test project directory
    if project_dir.parent.exists():
        shutil.rmtree(project_dir.parent)
        print(f"\n• Cleaned up temporary directory: {project_dir.parent}")

    print("\n" + "=" * 80)
    print(" FULL AUTONOMOUS PROJECT LOOP TEST PASSED WITH 100% SUCCESS!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

