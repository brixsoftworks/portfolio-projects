"""
tools/bash_tool.py

Bash / Shell command execution tool for LangChain.
- Executes commands in native Linux bash shell.
- Prompts user confirmation if command attempts file deletion (rm, rmdir, unlink, shred).
- Otherwise executes freely with timeout and output truncation guards.
"""

import re
import subprocess
from langchain.tools import tool

# Patterns that indicate file or directory deletion
DELETION_PATTERNS = [
    r"\brm\b",
    r"\brmdir\b",
    r"\bunlink\b",
    r"\bshred\b",
    r"\bfind\b.*-delete\b",
]

DEFAULT_TIMEOUT = 30  # seconds
MAX_OUTPUT_CHARS = 3000


def is_deletion_command(command: str) -> bool:
    """Checks if the command attempts to delete files or directories."""
    for pattern in DELETION_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def request_user_permission(command: str) -> bool:
    """Prompts the user in terminal before executing any file deletion."""
    print("\n" + "⚠️ " * 20)
    print(f"⚠️  DELETION COMMAND DETECTED: {command}")
    print("⚠️ " * 20)
    try:
        choice = input("👉 Allow deletion command to proceed? [y/N]: ").strip().lower()
        return choice in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def run_shell(command: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """
    Executes a shell command with safety confirmation for file deletions.
    """
    cmd = command.strip()
    if not cmd:
        return "Error: Empty command provided."

    # Check for deletion permission
    if is_deletion_command(cmd):
        allowed = request_user_permission(cmd)
        if not allowed:
            return "Execution canceled: User denied permission to delete files."

    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        if proc.returncode == 0:
            output = stdout if stdout else "Command executed successfully (no output)."
        else:
            output = f"Command exited with code {proc.returncode}.\n"
            if stdout:
                output += f"Output:\n{stdout}\n"
            if stderr:
                output += f"Error:\n{stderr}"

        # Truncate if output is excessively long
        if len(output) > MAX_OUTPUT_CHARS:
            output = output[:MAX_OUTPUT_CHARS] + f"\n... [Output truncated to {MAX_OUTPUT_CHARS} chars]"

        return output

    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"


@tool
def bash_tool(command: str) -> str:
    """
    Execute a Linux bash command in the terminal.
    Can be used to check system statistics, launch apps, manage files, check network, etc.
    If the command deletes files or directories, it asks for user permission first.

    Args:
        command: The shell command string to execute (e.g. 'uname -r', 'ls -la', 'free -h').

    Returns:
        The command output or error message.
    """
    return run_shell(command)


if __name__ == "__main__":
    print("Testing bash_tool directly...")
    print("\n1. System Info:")
    print(run_shell("uname -a && uptime"))

    print("\n2. Battery / Memory Status:")
    print(run_shell("free -h"))

