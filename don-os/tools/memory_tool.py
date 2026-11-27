"""
tools/memory_tool.py

Persistent Long-Term Memory and Note-Taking System for PA Assistant.
Backing Store: SQLite with Full-Text Search (FTS5) at ~/.local/share/pa_assistant/memory.db.

Features:
- Long-term memory store (key-value facts, user preferences, instructions)
- Full-text keyword recall using SQLite FTS5
- Note & snippet management with tags
- Persistent conversation history logging across restarts
"""

import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

DB_DIR = os.path.expanduser("~/.local/share/pa_assistant")
DB_PATH = os.path.join(DB_DIR, "memory.db")


def _init_memory_db():
    Path(DB_DIR).mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.cursor()
        # Memories table (facts, preferences, project info)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                information TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # FTS5 Virtual Table for fast search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                key,
                information,
                category,
                content='memories',
                content_rowid='id'
            )
        """)

        # Triggers to keep FTS index synchronized
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                INSERT INTO memories_fts(rowid, key, information, category)
                VALUES (new.id, new.key, new.information, new.category);
            END;
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
                INSERT INTO memories_fts(memories_fts, rowid, key, information, category)
                VALUES('delete', old.id, old.key, old.information, old.category);
            END;
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
                INSERT INTO memories_fts(memories_fts, rowid, key, information, category)
                VALUES('delete', old.id, old.key, old.information, old.category);
                INSERT INTO memories_fts(rowid, key, information, category)
                VALUES (new.id, new.key, new.information, new.category);
            END;
        """)

        # Notes table for longer-form documentation, snippets, code
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                tags TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Conversation turns table for persistent cross-session memory
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


_init_memory_db()


@tool
def remember(key: str, information: str, category: str = "general") -> str:
    """
    Store or update a persistent fact, preference, or piece of knowledge in long-term memory.
    
    Args:
        key: A concise identifier or topic name (e.g., 'user_name', 'favorite_ide', 'project_stack', 'wifi_ssid').
        information: The detailed fact, value, or instruction to remember.
        category: Optional category tag (e.g., 'preference', 'project', 'profile', 'fact'). Defaults to 'general'.
        
    Returns:
        Confirmation message.
    """
    clean_key = key.strip().lower()
    clean_info = information.strip()
    clean_cat = category.strip().lower() if category else "general"

    if not clean_key or not clean_info:
        return "Error: Both key and information must be non-empty."

    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO memories (key, information, category, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                information = excluded.information,
                category = excluded.category,
                updated_at = CURRENT_TIMESTAMP
        """, (clean_key, clean_info, clean_cat))
        conn.commit()

    return f"Successfully saved to long-term memory [{clean_cat}]: '{clean_key}' -> '{clean_info}'."


@tool
def recall(query: str, category: str = "") -> str:
    """
    Search and retrieve facts, preferences, or instructions from long-term memory.
    Uses SQLite Full-Text Search (FTS5) across keys and information contents.
    
    Args:
        query: Search keywords or question topic (e.g. 'editor', 'preferences', 'name', 'stack').
        category: Optional category filter (e.g. 'preference', 'project').
        
    Returns:
        Matching memories or a not found message.
    """
    clean_q = query.strip()
    clean_cat = category.strip().lower()

    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.cursor()

        # Try FTS5 match first
        try:
            # Escape quotes in query
            escaped_q = clean_q.replace('"', '""')
            if clean_cat:
                sql = """
                    SELECT m.key, m.information, m.category, m.updated_at
                    FROM memories m
                    JOIN memories_fts f ON m.id = f.rowid
                    WHERE memories_fts MATCH ? AND m.category = ?
                    ORDER BY rank
                    LIMIT 10
                """
                cursor.execute(sql, (f'"{escaped_q}"*', clean_cat))
            else:
                sql = """
                    SELECT m.key, m.information, m.category, m.updated_at
                    FROM memories m
                    JOIN memories_fts f ON m.id = f.rowid
                    WHERE memories_fts MATCH ?
                    ORDER BY rank
                    LIMIT 10
                """
                cursor.execute(sql, (f'"{escaped_q}"*',))
            rows = cursor.fetchall()
        except Exception:
            rows = []

        # Fallback to standard LIKE if FTS yielded 0 rows
        if not rows:
            like_pat = f"%{clean_q}%"
            if clean_cat:
                cursor.execute(
                    "SELECT key, information, category, updated_at FROM memories WHERE (key LIKE ? OR information LIKE ?) AND category = ? LIMIT 10",
                    (like_pat, like_pat, clean_cat)
                )
            else:
                cursor.execute(
                    "SELECT key, information, category, updated_at FROM memories WHERE key LIKE ? OR information LIKE ? LIMIT 10",
                    (like_pat, like_pat)
                )
            rows = cursor.fetchall()

    if not rows:
        return f"No memories found matching '{query}'" + (f" in category '{category}'." if category else ".")

    lines = [f"Found {len(rows)} memory item(s):"]
    for k, info, cat, updated in rows:
        lines.append(f"• [{cat}] **{k}**: {info} *(updated: {updated})*")
    return "\n".join(lines)


@tool
def forget(key: str) -> str:
    """
    Delete a specific piece of knowledge or fact from long-term memory by key.
    
    Args:
        key: The exact key identifier of the memory to remove.
        
    Returns:
        Status message.
    """
    clean_key = key.strip().lower()
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories WHERE key = ?", (clean_key,))
        conn.commit()
        if cursor.rowcount > 0:
            return f"Successfully deleted memory with key '{clean_key}'."
        return f"No memory found with key '{clean_key}'."


@tool
def list_all_memories(category: str = "") -> str:
    """
    List all stored long-term memories, optionally filtered by category.
    
    Args:
        category: Optional category filter (e.g., 'preference', 'project', 'profile').
        
    Returns:
        Categorized list of all stored memories.
    """
    clean_cat = category.strip().lower()
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.cursor()
        if clean_cat:
            cursor.execute("SELECT key, information, category, updated_at FROM memories WHERE category = ? ORDER BY key ASC", (clean_cat,))
        else:
            cursor.execute("SELECT key, information, category, updated_at FROM memories ORDER BY category, key ASC")
        rows = cursor.fetchall()

    if not rows:
        return "Long-term memory is currently empty." + (f" (No entries under category '{category}')" if category else "")

    lines = [f"Stored Long-Term Memories ({len(rows)} total):"]
    curr_cat = None
    for k, info, cat, updated in rows:
        if cat != curr_cat:
            curr_cat = cat
            lines.append(f"\n [{cat.upper()}]:")
        lines.append(f"  • {k}: {info}")
    return "\n".join(lines)


@tool
def save_note(title: str, content: str, tags: str = "") -> str:
    """
    Save or update a rich text/markdown note, snippet, or documentation.
    
    Args:
        title: Unique title for the note.
        content: The text/markdown body of the note.
        tags: Comma-separated tags (e.g. 'code, python, setup').
        
    Returns:
        Confirmation message.
    """
    clean_title = title.strip()
    clean_content = content.strip()
    clean_tags = tags.strip().lower()

    if not clean_title or not clean_content:
        return "Error: Title and content must not be empty."

    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notes (title, content, tags, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(title) DO UPDATE SET
                content = excluded.content,
                tags = excluded.tags,
                updated_at = CURRENT_TIMESTAMP
        """, (clean_title, clean_content, clean_tags))
        conn.commit()

    return f"Successfully saved note '{clean_title}'."


@tool
def search_notes(query: str = "") -> str:
    """
    Search saved notes by title, tag, or content keywords.
    
    Args:
        query: Search string or tag. Leave empty to list recent notes.
        
    Returns:
        Matching notes summary.
    """
    q = query.strip()
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.cursor()
        if q:
            pat = f"%{q}%"
            cursor.execute("""
                SELECT title, content, tags, updated_at FROM notes
                WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                ORDER BY updated_at DESC LIMIT 10
            """, (pat, pat, pat))
        else:
            cursor.execute("SELECT title, content, tags, updated_at FROM notes ORDER BY updated_at DESC LIMIT 10")
        rows = cursor.fetchall()

    if not rows:
        return f"No notes found matching '{query}'." if q else "No saved notes found."

    lines = [f"Found {len(rows)} note(s):"]
    for title, content, tags, updated in rows:
        snippet = content[:150].replace("\n", " ") + ("..." if len(content) > 150 else "")
        tag_desc = f" [{tags}]" if tags else ""
        lines.append(f"• **{title}**{tag_desc} ({updated}):\n  {snippet}")
    return "\n\n".join(lines)


# Helper functions for cross-session conversation persistence
def record_chat_turn(session_id: str, role: str, content: str):
    """Saves a conversation turn into SQLite history."""
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn, conn:
            conn.execute(
                "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            conn.commit()
    except Exception:
        pass


def get_recent_chat_history(session_id: str = "default", limit: int = 10) -> list:
    """Retrieves recent conversation turns for context initialization."""
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            return list(reversed(rows))
    except Exception:
        return []
