"""
tools/time_tool.py

Time, Timers, Reminders, and Scheduling Tool Suite.
Provides real-time date/time queries, countdown timers, and persistent SQLite
reminders that trigger native desktop alerts and speech synthesis (Edge-TTS).
"""

import os
import re
import sqlite3
import subprocess
import threading
import time
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

DB_DIR = os.path.expanduser("~/.local/share/pa_assistant")
DB_PATH = os.path.join(DB_DIR, "reminders.db")


def _init_db():
    Path(DB_DIR).mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                due_time TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


_init_db()


def _fire_alert(title: str, message: str, speak: bool = True):
    """Triggers desktop notification and spoken alert."""
    try:
        subprocess.run(
            ["notify-send", "-u", "critical", "-a", "PA AI Assistant", title, message],
            capture_output=True,
            check=False
        )
    except Exception:
        pass

    if speak:
        try:
            from tools.tts_speaker import speak_text_sync
            speak_text_sync(f"{title}. {message}")
        except Exception:
            pass


def _timer_worker(seconds: int, label: str):
    time.sleep(seconds)
    _fire_alert("Timer Finished", f"Your timer for '{label}' has completed!", speak=True)


def _reminder_monitor_worker():
    """Background loop to check and fire due reminders."""
    while True:
        try:
            now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with closing(sqlite3.connect(DB_PATH)) as conn, conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, message FROM reminders WHERE status = 'pending' AND due_time <= ?",
                    (now_iso,)
                )
                due_items = cursor.fetchall()
                for r_id, msg in due_items:
                    cursor.execute("UPDATE reminders SET status = 'completed' WHERE id = ?", (r_id,))
                    conn.commit()
                    threading.Thread(
                        target=_fire_alert,
                        args=("Reminder Alert", msg, True),
                        daemon=True
                    ).start()
        except Exception:
            pass
        time.sleep(5)


# Start singleton background reminder checker
_reminder_thread = threading.Thread(target=_reminder_monitor_worker, daemon=True)
_reminder_thread.start()


@tool
def get_current_time(timezone_name: str = "") -> str:
    """
    Get the current system local date, time, day of the week, and timezone.
    
    Args:
        timezone_name: Optional timezone name (e.g. 'UTC', 'Asia/Kolkata', 'US/Eastern').
    
    Returns:
        Formatted date and time string.
    """
    now = datetime.now()
    day_name = now.strftime("%A")
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%I:%M:%S %p")
    local_tz = time.tzname[time.daylight] if time.daylight else time.tzname[0]

    return f"Current Time: {time_str}\nDate: {day_name}, {date_str}\nTimezone: {local_tz}"


@tool
def set_timer(seconds: int, label: str = "Focus Timer") -> str:
    """
    Set a non-blocking countdown timer that notifies you with sound and speech upon completion.
    
    Args:
        seconds: Duration in seconds (e.g. 60 for 1 minute, 1500 for 25-minute Pomodoro).
        label: Custom description for what the timer is for.
        
    Returns:
        Confirmation message.
    """
    if seconds <= 0:
        return "Error: Timer duration must be greater than 0 seconds."

    thread = threading.Thread(target=_timer_worker, args=(seconds, label), daemon=True)
    thread.start()

    mins, secs = divmod(seconds, 60)
    duration_desc = f"{mins}m {secs}s" if mins > 0 else f"{secs} seconds"
    return f"Timer started for '{label}' ({duration_desc}). You will receive a desktop notification and voice alert when it finishes."


def _parse_time_spec(time_spec: str) -> Optional[datetime]:
    """Parses relative and absolute time strings."""
    spec = time_spec.strip().lower()
    now = datetime.now()

    # Relative "in X minutes / mins / seconds / hours"
    rel_match = re.search(r"in\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hr|hour|hours)", spec)
    if rel_match:
        val = int(rel_match.group(1))
        unit = rel_match.group(2)
        if unit.startswith("s"):
            return now + timedelta(seconds=val)
        elif unit.startswith("m"):
            return now + timedelta(minutes=val)
        elif unit.startswith("h"):
            return now + timedelta(hours=val)

    # Shorthand: "10m", "2h", "45s"
    short_match = re.match(r"^(\d+)\s*(s|m|h)$", spec)
    if short_match:
        val = int(short_match.group(1))
        unit = short_match.group(2)
        if unit == "s":
            return now + timedelta(seconds=val)
        elif unit == "m":
            return now + timedelta(minutes=val)
        elif unit == "h":
            return now + timedelta(hours=val)

    # Absolute time: HH:MM or HH:MM AM/PM
    for fmt in ["%I:%M %p", "%I:%M%p", "%H:%M"]:
        try:
            t = datetime.strptime(spec, fmt).time()
            target = datetime.combine(now.date(), t)
            if target <= now:
                target += timedelta(days=1)  # next day
            return target
        except ValueError:
            pass

    # Full datetime: YYYY-MM-DD HH:MM
    try:
        return datetime.strptime(spec, "%Y-%m-%d %H:%M")
    except ValueError:
        pass

    return None


@tool
def add_reminder(time_spec: str, message: str) -> str:
    """
    Schedule a reminder. Fires a native desktop popup and voice alert at the specified time.
    
    Args:
        time_spec: When to remind (e.g., 'in 15 minutes', 'in 2 hours', '18:30', '10:00 AM', '2026-10-25 14:00').
        message: The reminder note or task description.
        
    Returns:
        Confirmation status with reminder ID and scheduled time.
    """
    due_dt = _parse_time_spec(time_spec)
    if not due_dt:
        return (
            f"Error: Could not parse time specification '{time_spec}'. "
            "Please use formats like 'in 10 minutes', 'in 1 hour', '18:30', or '9:00 PM'."
        )

    due_str = due_dt.strftime("%Y-%m-%d %H:%M:%S")
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (message, due_time, status) VALUES (?, ?, 'pending')",
            (message.strip(), due_str)
        )
        rem_id = cursor.lastrowid
        conn.commit()

    return f"Reminder #{rem_id} scheduled for {due_dt.strftime('%b %d, %I:%M %p')}: '{message}'."


@tool
def list_reminders(include_completed: bool = False) -> str:
    """
    List all pending (and optionally completed) reminders.
    
    Args:
        include_completed: Whether to include finished reminders. Defaults to False.
        
    Returns:
        Formatted table or list of reminders.
    """
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.cursor()
        if include_completed:
            cursor.execute("SELECT id, message, due_time, status FROM reminders ORDER BY due_time ASC")
        else:
            cursor.execute(
                "SELECT id, message, due_time, status FROM reminders WHERE status = 'pending' ORDER BY due_time ASC"
            )
        rows = cursor.fetchall()

    if not rows:
        return "No pending reminders."

    lines = ["Scheduled Reminders:"]
    for r_id, msg, due, status in rows:
        tag = "[Completed]" if status == "completed" else "[Pending]"
        lines.append(f"• #{r_id} {tag} Due: {due} -> {msg}")
    return "\n".join(lines)


@tool
def cancel_reminder(reminder_id: int) -> str:
    """
    Cancel an existing pending reminder by its ID.
    
    Args:
        reminder_id: The ID of the reminder to cancel.
        
    Returns:
        Status message.
    """
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ? AND status = 'pending'", (reminder_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return f"Successfully cancelled reminder #{reminder_id}."
        return f"No pending reminder found with ID #{reminder_id}."
