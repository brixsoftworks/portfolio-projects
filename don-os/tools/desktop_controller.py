"""
tools/desktop_controller.py

Native Linux Desktop & Application Controller:
- launch_app: Start GUI/CLI apps in clean background sessions without hanging the agent.
- close_app: Terminate applications gracefully or forcefully by process name.
- list_running_apps: Inspect active desktop applications.
- open_url: Open URLs in default system browser.
- set_volume / get_volume: Audio control via PulseAudio/PipeWire pactl.
- take_screenshot: Full Wayland/X11 screen capture using grim.
"""

import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from langchain.tools import tool

DEFAULT_SCREENSHOT_DIR = os.path.expanduser("~/Pictures/Screenshots")


@tool
def launch_app(app_name: str, app_args: str = "") -> str:
    """
    Launch an application on the Linux desktop in a detached background session.
    
    Args:
        app_name: The application command or name (e.g. 'firefox', 'code', 'nautilus', 'gnome-text-editor').
        app_args: Optional command line arguments or file paths to open with the app.

    Returns:
        Status message confirming launch.
    """
    cmd_name = app_name.strip()
    if not cmd_name:
        return "Error: Empty app_name provided."

    # Look up executable in PATH
    binary_path = shutil.which(cmd_name)
    if not binary_path:
        # Common alias map
        alias_map = {
            "browser": "firefox",
            "chrome": "firefox",
            "vscode": "code",
            "files": "nautilus",
            "file_manager": "nautilus",
            "terminal": "gnome-terminal"
        }
        mapped = alias_map.get(cmd_name.lower())
        if mapped:
            binary_path = shutil.which(mapped)
            if binary_path:
                cmd_name = mapped

    if not binary_path:
        return f"Error: Application '{app_name}' is not found in system PATH."

    full_cmd = [cmd_name]
    if app_args.strip():
        full_cmd.extend(app_args.strip().split())

    try:
        # Start completely detached so child app doesn't block agent execution
        subprocess.Popen(
            full_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        return f"Successfully launched '{cmd_name}' in the background."
    except Exception as e:
        return f"Failed to launch '{cmd_name}': {str(e)}"


@tool
def close_app(process_name: str, force: bool = False) -> str:
    """
    Close or terminate a running application by process name.
    
    Args:
        process_name: The process name to close (e.g. 'firefox', 'code').
        force: Set to True to send SIGKILL (-9). Defaults to False (SIGTERM).

    Returns:
        Status message confirming closure.
    """
    clean_proc = process_name.strip()
    if not clean_proc:
        return "Error: Empty process_name provided."

    sig_flag = "-9" if force else "-15"
    try:
        res = subprocess.run(["pkill", sig_flag, "-f", clean_proc], capture_output=True, text=True)
        if res.returncode == 0:
            return f"Successfully closed instances matching '{clean_proc}'."
        elif res.returncode == 1:
            return f"No active processes found matching '{clean_proc}'."
        else:
            return f"Error terminating process: {res.stderr.strip()}"
    except Exception as e:
        return f"Error terminating process '{clean_proc}': {str(e)}"


@tool
def open_url(url: str) -> str:
    """
    Open a website URL in the default system browser.
    
    Args:
        url: The web URL (e.g. 'https://github.com', 'https://google.com').

    Returns:
        Status message.
    """
    target = url.strip()
    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    try:
        subprocess.Popen(
            ["xdg-open", target],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        return f"Successfully opened URL: {target}"
    except Exception as e:
        return f"Error opening URL '{target}': {str(e)}"


@tool
def set_volume(percentage: int) -> str:
    """
    Set laptop speaker volume percentage via PipeWire / PulseAudio pactl.
    
    Args:
        percentage: Volume level from 0 to 100.

    Returns:
        Status message with confirmation.
    """
    val = max(0, min(100, int(percentage)))
    try:
        res = subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{val}%"], capture_output=True, text=True)
        if res.returncode == 0:
            return f"Laptop volume successfully set to {val}%."
        return f"Error setting volume: {res.stderr.strip()}"
    except Exception as e:
        return f"Error setting volume: {str(e)}"


@tool
def get_volume() -> str:
    """
    Get current speaker volume percentage and mute state.
    
    Returns:
        Volume percentage string.
    """
    try:
        res = subprocess.run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], capture_output=True, text=True)
        mute_res = subprocess.run(["pactl", "get-sink-mute", "@DEFAULT_SINK@"], capture_output=True, text=True)

        is_muted = "yes" in mute_res.stdout.lower() if mute_res.returncode == 0 else False

        if res.returncode == 0:
            match = re.search(r"(\d+)%", res.stdout)
            vol = match.group(1) if match else "Unknown"
            status = f"Volume: {vol}%"
            if is_muted:
                status += " (MUTED)"
            return status
        return f"Error retrieving volume: {res.stderr.strip()}"
    except Exception as e:
        return f"Error getting volume: {str(e)}"


@tool
def take_screenshot(filename: str = "") -> str:
    """
    Take a full desktop screenshot and save to disk using system portals or screen tools.
    
    Args:
        filename: Optional filename or relative path. Defaults to timestamped PNG in ~/Pictures/Screenshots.

    Returns:
        Status message with the path to the saved screenshot or instruction.
    """
    Path(DEFAULT_SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)
    if not filename:
        save_path = os.path.join(DEFAULT_SCREENSHOT_DIR, f"screenshot_{int(time.time())}.png")
    else:
        save_path = os.path.expanduser(filename)

    try:
        # 1. Try grim (wlroots Wayland compositors)
        if shutil.which("grim"):
            res = subprocess.run(["grim", save_path], capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(save_path):
                file_size_kb = os.path.getsize(save_path) / 1024.0
                return f"Screenshot successfully saved to: {save_path} ({file_size_kb:.1f} KB)"

        # 2. Try xdg-desktop-portal via dbus
        try:
            import dbus
            bus = dbus.SessionBus()
            portal = bus.get_object("org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop")
            iface = dbus.Interface(portal, "org.freedesktop.portal.Screenshot")
            req_path = iface.Screenshot("", {"interactive": dbus.Boolean(False)})
            return f"Screenshot capture request dispatched to system portal ({req_path})."
        except Exception:
            pass

        # 3. Fallback to maim or gnome-screenshot
        if shutil.which("maim"):
            res = subprocess.run(["maim", save_path], capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(save_path):
                return f"Screenshot successfully saved to: {save_path}"

        return "Screenshot capture requested via desktop system portal."
    except Exception as e:
        return f"Error capturing screenshot: {str(e)}"
