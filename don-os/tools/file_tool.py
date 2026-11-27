"""
tools/file_tool.py

File Operations Tool for LangChain Agent:
- read_file: Read text file contents with line/size bounds.
- write_file: Write text file (safe overwrite protection).
- append_file: Append text to existing file.
- list_directory: List files and subdirectories with sizes.
- delete_file: Safely asks user confirmation before deleting any file.
"""

import os
from pathlib import Path
from typing import Optional
from langchain.tools import tool

MAX_READ_CHARS = 10000


def request_delete_permission(path: str) -> bool:
    """Prompts user confirmation in terminal before deleting any file."""
    print("\n" + " " * 20)
    print(f"  FILE DELETION REQUEST: {path}")
    print(" " * 20)
    try:
        choice = input(f" Confirm deleting '{path}'? [y/N]: ").strip().lower()
        return choice in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


@tool
def read_file(file_path: str, max_chars: int = MAX_READ_CHARS) -> str:
    """
    Read the text content of a file.
    
    Args:
        file_path: Relative or absolute path to the file.
        max_chars: Maximum characters to read (defaults to 10,000).

    Returns:
        The content of the file as text.
    """
    p = Path(file_path).expanduser().resolve()
    if not p.exists():
        return f"Error: File '{file_path}' does not exist."
    if not p.is_file():
        return f"Error: Path '{file_path}' is a directory, not a file."

    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars + 1)

        if len(content) > max_chars:
            return content[:max_chars] + f"\n\n... [Content truncated at {max_chars} chars]"
        return content
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"


@tool
def write_file(file_path: str, content: str, overwrite: bool = False) -> str:
    """
    Create a new file or write content to a file.
    
    Args:
        file_path: Target file path.
        content: The text content to write.
        overwrite: Set to True to allow overwriting an existing file. Defaults to False.

    Returns:
        Confirmation message.
    """
    p = Path(file_path).expanduser().resolve()
    if p.exists() and not overwrite:
        return f"Notice: File '{file_path}' already exists. Pass overwrite=True if you wish to overwrite it."

    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{file_path}'."
    except Exception as e:
        return f"Error writing to '{file_path}': {str(e)}"


@tool
def append_file(file_path: str, content: str) -> str:
    """
    Append text content to the end of a file (creates it if it does not exist).
    
    Args:
        file_path: Target file path.
        content: The text content to append.

    Returns:
        Confirmation message.
    """
    p = Path(file_path).expanduser().resolve()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully appended {len(content)} characters to '{file_path}'."
    except Exception as e:
        return f"Error appending to '{file_path}': {str(e)}"


@tool
def list_directory(directory_path: str = ".") -> str:
    """
    List files and directories in the specified path.
    
    Args:
        directory_path: The directory path to inspect (defaults to current directory '.').

    Returns:
        A formatted list of entries with types and sizes.
    """
    p = Path(directory_path).expanduser().resolve()
    if not p.exists():
        return f"Error: Directory '{directory_path}' does not exist."
    if not p.is_dir():
        return f"Error: Path '{directory_path}' is not a directory."

    try:
        entries = sorted(os.listdir(p))
        if not entries:
            return f"Directory '{directory_path}' is empty."

        lines = [f"Contents of {directory_path} ({len(entries)} items):"]
        for entry in entries:
            full_item = p / entry
            if full_item.is_dir():
                lines.append(f" {entry}/")
            else:
                size_bytes = full_item.stat().st_size
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                lines.append(f" {entry} ({size_str})")

        return "\n".join(lines)
    except Exception as e:
        return f"Error listing directory '{directory_path}': {str(e)}"


@tool
def delete_file(file_path: str) -> str:
    """
    Delete a file after explicitly confirming with the user.
    
    Args:
        file_path: Path to the file to delete.

    Returns:
        Result message.
    """
    p = Path(file_path).expanduser().resolve()
    if not p.exists():
        return f"Error: File '{file_path}' does not exist."

    # Ask user permission first
    allowed = request_delete_permission(str(p))
    if not allowed:
        return f"Execution canceled: User denied permission to delete '{file_path}'."

    try:
        if p.is_file():
            p.unlink()
            return f"Successfully deleted file '{file_path}'."
        elif p.is_dir():
            p.rmdir()
            return f"Successfully deleted directory '{file_path}'."
    except Exception as e:
        return f"Error deleting '{file_path}': {str(e)}"
