"""
test_memory.py

Tests for tools/memory_tool.py:
Verifies persistent long-term memory, FTS5 search, note-taking, and forgetting.
"""

from tools.memory_tool import (
    remember,
    recall,
    forget,
    list_all_memories,
    save_note,
    search_notes,
)


def test_memory():
    print("=" * 60)
    print("  Testing Memory Tool (Long-Term Memory & Notes)")
    print("=" * 60)

    # 1. Store facts
    print("\n1. Testing remember:")
    r1 = remember.invoke({"key": "user_name", "information": "Mullainathan", "category": "profile"})
    print(r1)
    assert "Successfully saved" in r1

    r2 = remember.invoke({"key": "favorite_editor", "information": "Visual Studio Code with Vim bindings", "category": "preference"})
    print(r2)
    assert "Successfully saved" in r2

    r3 = remember.invoke({"key": "pa_model", "information": "gemini-3.8-flash with LangChain", "category": "project"})
    print(r3)
    assert "Successfully saved" in r3

    # 2. Recall via FTS
    print("\n2. Testing recall:")
    rec1 = recall.invoke({"query": "editor"})
    print(rec1)
    assert "favorite_editor" in rec1

    rec2 = recall.invoke({"query": "Mullainathan"})
    print(rec2)
    assert "user_name" in rec2

    # 3. List all memories
    print("\n3. Testing list_all_memories:")
    all_mem = list_all_memories.invoke({})
    print(all_mem)
    assert "PROFILE" in all_mem
    assert "PREFERENCE" in all_mem

    # 4. Note management
    print("\n4. Testing save_note and search_notes:")
    n1 = save_note.invoke({
        "title": "PA Agent Architecture",
        "content": "The PA Agent uses Gemini 3.8 Flash, LangChain, Edge-TTS, and 17 MCP servers.",
        "tags": "architecture, agent, pa"
    })
    print(n1)
    assert "Successfully saved" in n1

    sn = search_notes.invoke({"query": "Architecture"})
    print(sn)
    assert "PA Agent Architecture" in sn

    # 5. Forget memory
    print("\n5. Testing forget:")
    f_res = forget.invoke({"key": "favorite_editor"})
    print(f_res)
    assert "Successfully deleted" in f_res

    rec_after = recall.invoke({"query": "favorite_editor"})
    print(rec_after)
    assert "No memories found" in rec_after

    print("\n" + "=" * 60)
    print("🎉 ALL MEMORY TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    test_memory()

