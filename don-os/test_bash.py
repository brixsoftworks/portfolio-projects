"""
test_bash.py

Tests the Bash Tool:
1. Normal system command execution (without confirmation)
2. Deletion detection logic (verifying permission check activates)
"""

from tools.bash_tool import bash_tool, is_deletion_command, run_shell

def test_bash():
    print("=" * 60)
    print("  Testing Bash Tool")
    print("=" * 60)

    # 1. Normal commands (runs immediately without prompting)
    print("\n[Test 1] Regular command: 'echo Hello from DON AI'")
    res = bash_tool.invoke("echo Hello from DON AI")
    print("Result:", res)
    assert "Hello from DON AI" in res

    print("\n[Test 2] System date & uptime:")
    res = bash_tool.invoke("date && uptime -p")
    print("Result:\n" + res)

    # 2. Verify deletion detection logic
    print("\n[Test 3] Deletion detection verification:")
    cmds = [
        ("ls -la", False),
        ("rm -f test.txt", True),
        ("rmdir my_folder", True),
        ("find . -name '*.tmp' -delete", True),
        ("unlink link.txt", True),
        ("cat file.txt", False),
    ]

    for cmd, expected in cmds:
        detected = is_deletion_command(cmd)
        status = "PASSED" if detected == expected else "FAILED"
        print(f"  [{status}] Command: '{cmd}' -> Deletion detected: {detected} (expected {expected})")
        assert detected == expected

    print("\n" + "=" * 60)
    print("  All Bash Tool Tests Passed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_bash()

