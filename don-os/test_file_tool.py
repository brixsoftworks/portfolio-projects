"""
test_file_tool.py

Automated unit test for file operations tool.
Verifies write, read, append, list, and safe overwrite checks.
"""

import os
from tools.file_tool import (
    write_file,
    read_file,
    append_file,
    list_directory,
)

TEST_DIR = "test_sandbox"
TEST_FILE = os.path.join(TEST_DIR, "sample_note.txt")

def test_file_operations():
    print("=" * 60)
    print("  Testing File Operations Tool")
    print("=" * 60)

    # Clean previous run
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    if os.path.exists(TEST_DIR):
        os.rmdir(TEST_DIR)

    # 1. Write file
    print("\n[Test 1] Writing new file:")
    w_res = write_file.invoke({"file_path": TEST_FILE, "content": "Line 1: Hello from DON OS AI.\n"})
    print("Result:", w_res)
    assert "Successfully wrote" in w_res

    # 2. Overwrite protection
    print("\n[Test 2] Overwrite protection (overwrite=False):")
    ow_res = write_file.invoke({"file_path": TEST_FILE, "content": "Replaced content", "overwrite": False})
    print("Result:", ow_res)
    assert "already exists" in ow_res

    # 3. Read file
    print("\n[Test 3] Reading file:")
    r_res = read_file.invoke({"file_path": TEST_FILE})
    print("Result:", r_res.strip())
    assert "Line 1: Hello from DON OS AI." in r_res

    # 4. Append to file
    print("\n[Test 4] Appending to file:")
    a_res = append_file.invoke({"file_path": TEST_FILE, "content": "Line 2: System initialized.\n"})
    print("Result:", a_res)
    assert "Successfully appended" in a_res

    # Verify both lines exist
    updated_content = read_file.invoke({"file_path": TEST_FILE})
    assert "Line 1" in updated_content and "Line 2" in updated_content
    print("Updated content:\n" + updated_content.strip())

    # 5. List directory
    print("\n[Test 5] Listing directory:")
    ls_res = list_directory.invoke({"directory_path": TEST_DIR})
    print(ls_res)
    assert "sample_note.txt" in ls_res

    # Clean up test artifacts
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    if os.path.exists(TEST_DIR):
        os.rmdir(TEST_DIR)

    print("\n" + "=" * 60)
    print("  All File Tool Tests Passed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_file_operations()

