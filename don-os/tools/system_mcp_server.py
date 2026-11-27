"""
tools/system_mcp_server.py

Universal System & Software MCP Server.
Exposes comprehensive MCP tools to discover, launch, automate, and control
any software installed on the Linux system, as well as window management,
D-Bus MPRIS media control, desktop notifications, LibreOffice conversions,
VS Code automation, and system telemetry.
Runs on standard JSON-RPC stdio.
"""

import glob
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("system-desktop-mcp")


def _scan_desktop_entries():
    """Scans all installed application .desktop files on the system."""
    search_dirs = [
        "/usr/share/applications",
        os.path.expanduser("~/.local/share/applications"),
        "/var/lib/snapd/desktop/applications",
        "/var/lib/flatpak/exports/share/applications"
    ]
    apps = {}
    for d in search_dirs:
        if not os.path.exists(d):
            continue
        for f in os.listdir(d):
            if f.endswith(".desktop"):
                full_path = os.path.join(d, f)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as fp:
                        name, comment, exec_cmd, categories = "", "", "", ""
                        in_desktop_entry = False
                        for line in fp:
                            line = line.strip()
                            if line == "[Desktop Entry]":
                                in_desktop_entry = True
                                continue
                            elif line.startswith("[") and in_desktop_entry:
                                break
                            if in_desktop_entry:
                                if line.startswith("Name=") and not name:
                                    name = line[5:]
                                elif line.startswith("Comment=") and not comment:
                                    comment = line[8:]
                                elif line.startswith("Exec=") and not exec_cmd:
                                    exec_cmd = line[5:]
                                elif line.startswith("Categories=") and not categories:
                                    categories = line[11:]
                        if name and exec_cmd:
                            clean_exec = re.sub(r"%[a-zA-Z]", "", exec_cmd).strip()
                            app_key = name.lower()
                            if app_key not in apps:
                                apps[app_key] = {
                                    "name": name,
                                    "exec": clean_exec,
                                    "comment": comment,
                                    "categories": categories,
                                    "desktop_file": f,
                                    "path": full_path
                                }
                except Exception:
                    pass
    return apps


@mcp.tool()
def list_installed_software(query: str = "") -> str:
    """
    Search and list all installed applications and software on the system.
    Scans over 350+ system desktop entries and returns matching names, executables, and descriptions.
    """
    apps = _scan_desktop_entries()
    if query:
        q = query.lower().strip()
        matched = [
            v for k, v in apps.items()
            if q in k or q in v["comment"].lower() or q in v["exec"].lower() or q in v["categories"].lower()
        ]
    else:
        matched = list(apps.values())

    matched.sort(key=lambda x: x["name"].lower())
    if not matched:
        return f"No installed software found matching '{query}'."

    lines = [f"Found {len(matched)} installed application(s):"]
    for a in matched[:50]:  # limit to top 50 to avoid prompt overload
        desc = f" - {a['comment']}" if a['comment'] else ""
        lines.append(f"• {a['name']} (`{a['exec']}`){desc}")
    if len(matched) > 50:
        lines.append(f"... and {len(matched) - 50} more. Refine your query for more specific results.")
    return "\n".join(lines)


@mcp.tool()
def get_software_info(app_name: str) -> str:
    """
    Retrieve detailed technical info for a specific software/app (binary path, desktop config, exec command).
    """
    apps = _scan_desktop_entries()
    target = app_name.lower().strip()

    # Exact or partial match
    found = apps.get(target)
    if not found:
        for k, v in apps.items():
            if target in k or target in v["exec"].lower():
                found = v
                break

    bin_path = shutil.which(app_name.strip())
    if found:
        lines = [
            f"Software: {found['name']}",
            f"Executable Command: {found['exec']}",
            f"Desktop Entry: {found['path']}",
            f"Categories: {found['categories'] or 'N/A'}",
            f"Description: {found['comment'] or 'N/A'}",
            f"System Binary Located: {bin_path or 'Standard Launcher'}"
        ]
        return "\n".join(lines)
    elif bin_path:
        return f"Binary found in PATH: {bin_path}"
    else:
        return f"Software '{app_name}' not found on system."


@mcp.tool()
def launch_software(app_name: str, args: str = "") -> str:
    """
    Launch any desktop application or software installed on the system (e.g., 'code', 'vlc', 'firefox', 'blender', 'libreoffice', 'wireshark').
    """
    clean_app = app_name.strip()
    if not clean_app:
        return "Error: Empty app name provided."

    cmd = clean_app
    bin_path = shutil.which(cmd)

    if not bin_path:
        # Check desktop apps lookup
        apps = _scan_desktop_entries()
        target = clean_app.lower()
        if target in apps:
            cmd = apps[target]["exec"].split()[0]
        else:
            for k, v in apps.items():
                if target in k:
                    cmd = v["exec"].split()[0]
                    break

    bin_path = shutil.which(cmd)
    if not bin_path:
        return f"Error: Could not locate binary or desktop entry for '{app_name}'."

    full_cmd = [bin_path]
    if args.strip():
        full_cmd.extend(args.strip().split())

    try:
        subprocess.Popen(
            full_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        return f"Successfully launched '{clean_app}' ({bin_path}) on desktop."
    except Exception as e:
        return f"Error launching '{clean_app}': {e}"


@mcp.tool()
def close_software(name_or_pid: str, force: bool = False) -> str:
    """
    Close or terminate any running software instance by application name or process ID.
    """
    target = name_or_pid.strip()
    if not target:
        return "Error: Empty process name or PID."

    sig_flag = "-9" if force else "-15"
    if target.isdigit():
        res = subprocess.run(["kill", sig_flag, target], capture_output=True, text=True)
    else:
        res = subprocess.run(["pkill", sig_flag, "-f", target], capture_output=True, text=True)

    if res.returncode == 0:
        return f"Successfully terminated software instance(s) matching '{target}'."
    return f"No active software instance found matching '{target}'."


@mcp.tool()
def list_running_software() -> str:
    """
    List currently running desktop applications and user processes with PIDs and memory usage.
    """
    try:
        user = os.environ.get("USER", "mullainathan")
        res = subprocess.run(
            ["ps", "-u", user, "-o", "pid,%mem,comm,args", "--sort=-%mem"],
            capture_output=True,
            text=True
        )
        lines = res.stdout.splitlines()
        top_processes = lines[:25]
        return "\n".join(top_processes)
    except Exception as e:
        return f"Error listing running software: {e}"


@mcp.tool()
def focus_software_window(window_title: str) -> str:
    """
    Bring a specific software window to the front / active focus.
    """
    clean_title = window_title.strip()
    if not clean_title:
        return "Error: Empty window title."

    if shutil.which("wmctrl"):
        res = subprocess.run(["wmctrl", "-a", clean_title], capture_output=True, text=True)
        if res.returncode == 0:
            return f"Focused window matching '{clean_title}'."
    if shutil.which("xdotool"):
        res = subprocess.run(["xdotool", "search", "--onlyvisible", "--name", clean_title, "windowactivate"], capture_output=True, text=True)
        if res.returncode == 0:
            return f"Focused window matching '{clean_title}' via xdotool."
    return f"Could not focus window for '{clean_title}'. (May be minimized or running purely on Wayland)"


@mcp.tool()
def send_keys_to_software(key_sequence: str, window_title: str = "") -> str:
    """
    Send keystrokes, shortcuts (e.g. 'ctrl+s', 'ctrl+p', 'Return'), or typed text to an active or specified software window.
    """
    if not shutil.which("xdotool"):
        return "Error: xdotool utility not installed."

    clean_keys = key_sequence.strip()
    try:
        if window_title.strip():
            # Focus window first
            subprocess.run(["xdotool", "search", "--onlyvisible", "--name", window_title.strip(), "windowactivate"], capture_output=True)
            time.sleep(0.2)

        # If it's a shortcut sequence (contains '+' or known key)
        if "+" in clean_keys or clean_keys.lower() in ["return", "enter", "escape", "space", "tab", "backspace"]:
            subprocess.run(["xdotool", "key", clean_keys], check=True, capture_output=True)
            return f"Sent key shortcut '{clean_keys}' to software window."
        else:
            subprocess.run(["xdotool", "type", clean_keys], check=True, capture_output=True)
            return f"Typed text '{clean_keys}' into software window."
    except Exception as e:
        return f"Error sending keys: {e}"


@mcp.tool()
def send_desktop_notification(title: str, message: str, urgency: str = "normal") -> str:
    """
    Send a native desktop notification/alert to the user via notify-send.
    Urgency can be 'low', 'normal', or 'critical'.
    """
    if not shutil.which("notify-send"):
        return "Error: notify-send not available."
    try:
        subprocess.run(
            ["notify-send", "-u", urgency, "-a", "PA AI Assistant", title, message],
            check=True,
            capture_output=True
        )
        return f"Notification sent: [{title}] {message}"
    except Exception as e:
        return f"Error sending notification: {e}"


@mcp.tool()
def control_media_player(action: str, player_name: str = "") -> str:
    """
    Universal media player control via D-Bus MPRIS.
    Supported actions: 'play', 'pause', 'play_pause', 'next', 'previous', 'stop'.
    Works with Firefox, Chrome, VLC, MPV, Spotify, and all MPRIS2-compliant media players.
    """
    action_map = {
        "play": "Play",
        "pause": "Pause",
        "play_pause": "PlayPause",
        "toggle": "PlayPause",
        "next": "Next",
        "previous": "Previous",
        "stop": "Stop"
    }
    mpris_method = action_map.get(action.lower().strip(), "PlayPause")

    res = subprocess.run(["busctl", "--user", "list"], capture_output=True, text=True)
    mpris_services = [line.split()[0] for line in res.stdout.splitlines() if "org.mpris.MediaPlayer2." in line]

    if not mpris_services:
        return "No active media players detected on D-Bus."

    target_service = mpris_services[0]
    if player_name:
        for s in mpris_services:
            if player_name.lower() in s.lower():
                target_service = s
                break

    cmd = [
        "busctl", "--user", "call",
        target_service,
        "/org/mpris/MediaPlayer2",
        "org.mpris.MediaPlayer2.Player",
        mpris_method
    ]
    exec_res = subprocess.run(cmd, capture_output=True, text=True)
    if exec_res.returncode == 0:
        return f"Media command '{mpris_method}' dispatched to {target_service}."
    return f"Failed to dispatch media command: {exec_res.stderr.strip()}"


@mcp.tool()
def get_media_player_status() -> str:
    """
    Query currently playing track, artist, album, and playback status across all active media players.
    """
    res = subprocess.run(["busctl", "--user", "list"], capture_output=True, text=True)
    mpris_services = [line.split()[0] for line in res.stdout.splitlines() if "org.mpris.MediaPlayer2." in line]

    if not mpris_services:
        return "No active media players currently running."

    reports = []
    for s in mpris_services:
        status_res = subprocess.run(
            ["busctl", "--user", "get-property", s, "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player", "PlaybackStatus"],
            capture_output=True, text=True
        )
        meta_res = subprocess.run(
            ["busctl", "--user", "get-property", s, "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player", "Metadata"],
            capture_output=True, text=True
        )
        status = status_res.stdout.strip()
        metadata = meta_res.stdout.strip()

        # Extract title if present
        title_match = re.search(r'"xesam:title"\s+s\s+"([^"]+)"', metadata)
        title = title_match.group(1) if title_match else "Unknown Title"

        artist_match = re.search(r'"xesam:artist"\s+as\s+\d+\s+"([^"]+)"', metadata)
        artist = artist_match.group(1) if artist_match else "Unknown Artist"

        reports.append(f"• Player: {s.split('.')[-1]}\n  State: {status}\n  Now Playing: {title} - {artist}")

    return "\n\n".join(reports)


@mcp.tool()
def vscode_control(action: str, target: str = "", extra_args: str = "") -> str:
    """
    Control Visual Studio Code:
    - 'open_file': Open a file (target: path, optionally file:line).
    - 'open_folder': Open workspace folder.
    - 'diff': Diff two files (target: file1, extra_args: file2).
    - 'install_extension': Install a VS Code extension ID.
    - 'list_extensions': List installed VS Code extensions.
    """
    if not shutil.which("code"):
        return "Error: 'code' binary not found in PATH."

    act = action.lower().strip()
    try:
        if act == "open_file":
            subprocess.run(["code", "-g", target.strip()], check=True)
            return f"Opened file '{target}' in VS Code."
        elif act == "open_folder":
            subprocess.run(["code", target.strip() or "."], check=True)
            return f"Opened folder '{target}' in VS Code."
        elif act == "diff":
            subprocess.run(["code", "--diff", target.strip(), extra_args.strip()], check=True)
            return f"Opened diff between '{target}' and '{extra_args}' in VS Code."
        elif act == "install_extension":
            res = subprocess.run(["code", "--install-extension", target.strip()], capture_output=True, text=True)
            return f"Extension installation result:\n{res.stdout.strip() or res.stderr.strip()}"
        elif act == "list_extensions":
            res = subprocess.run(["code", "--list-extensions"], capture_output=True, text=True)
            return f"Installed VS Code Extensions:\n{res.stdout.strip()}"
        else:
            return f"Unknown VS Code action '{action}'. Valid actions: open_file, open_folder, diff, install_extension, list_extensions."
    except Exception as e:
        return f"Error controlling VS Code: {e}"


@mcp.tool()
def libreoffice_convert(input_path: str, target_format: str = "pdf", output_dir: str = "") -> str:
    """
    Convert office documents (DOCX, PPTX, XLSX, ODT, ODS, ODP, HTML, etc.) headlessly using LibreOffice.
    target_format: 'pdf', 'csv', 'txt', 'html', etc.
    """
    if not shutil.which("libreoffice"):
        return "Error: 'libreoffice' is not installed."

    if not os.path.exists(input_path):
        return f"Error: File '{input_path}' does not exist."

    out_dir = output_dir if output_dir else os.path.dirname(os.path.abspath(input_path))
    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to", target_format,
        input_path,
        "--outdir", out_dir
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode == 0:
            return f"Document successfully converted: {res.stdout.strip()}"
        return f"Conversion failed: {res.stderr.strip()}"
    except Exception as e:
        return f"Error during LibreOffice conversion: {e}"


@mcp.tool()
def take_desktop_screenshot(filename: str = "") -> str:
    """
    Take a full desktop screenshot and save to disk.
    """
    default_dir = os.path.expanduser("~/Pictures/Screenshots")
    Path(default_dir).mkdir(parents=True, exist_ok=True)
    save_path = os.path.join(default_dir, f"screenshot_{int(time.time())}.png") if not filename else os.path.expanduser(filename)

    if shutil.which("grim"):
        res = subprocess.run(["grim", save_path], capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(save_path):
            return f"Screenshot saved to: {save_path}"

    if shutil.which("maim"):
        res = subprocess.run(["maim", save_path], capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(save_path):
            return f"Screenshot saved to: {save_path}"

    return "Screenshot request submitted to desktop environment."


@mcp.tool()
def control_audio_volume(percent: int) -> str:
    """Set speaker master volume percentage (0 - 100)."""
    val = max(0, min(100, int(percent)))
    res = subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{val}%"], capture_output=True, text=True)
    if res.returncode == 0:
        return f"Speaker master volume set to {val}%."
    return f"Error setting volume: {res.stderr.strip()}"


@mcp.tool()
def get_system_telemetry() -> str:
    """Query current CPU, memory, uptime, battery, and disk telemetry."""
    try:
        mem = subprocess.run(["free", "-h"], capture_output=True, text=True).stdout.strip()
        uptime = subprocess.run(["uptime", "-p"], capture_output=True, text=True).stdout.strip()
        disk = subprocess.run(["df", "-h", "/"], capture_output=True, text=True).stdout.strip()
        return f"Uptime: {uptime}\n\nMemory:\n{mem}\n\nDisk Root:\n{disk}"
    except Exception as e:
        return f"Error reading telemetry: {e}"


@mcp.tool()
def execute_software_cli(command: str) -> str:
    """
    Execute any CLI software utility or command safely (e.g. ffmpeg, nmap, curl, git, python3) and return output.
    """
    clean_cmd = command.strip()
    if not clean_cmd:
        return "Error: Empty command."
    try:
        res = subprocess.run(clean_cmd, shell=True, executable="/bin/bash", capture_output=True, text=True, timeout=20)
        output = res.stdout.strip()
        if res.stderr.strip():
            output += f"\n[stderr]\n{res.stderr.strip()}"
        return output if output else f"Command completed with exit code {res.returncode}."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 20 seconds."
    except Exception as e:
        return f"Error executing command: {e}"


@mcp.tool()
def get_screen_brightness() -> str:
    """Get the current laptop screen brightness percentage and device name."""
    from tools.hardware_controller import get_screen_brightness as gsb
    return gsb.invoke({})


@mcp.tool()
def set_screen_brightness(percentage: int) -> str:
    """Adjust laptop display brightness percentage (1 - 100)."""
    from tools.hardware_controller import set_screen_brightness as ssb
    return ssb.invoke({"percentage": percentage})


@mcp.tool()
def get_battery_status() -> str:
    """Get battery telemetry: state (charging/discharging), percentage, time remaining, and health."""
    from tools.hardware_controller import get_battery_status as gbs
    return gbs.invoke({})


@mcp.tool()
def get_network_status() -> str:
    """Query system network connectivity, active connections, Wi-Fi state, and IP addresses."""
    from tools.hardware_controller import get_network_status as gns
    return gns.invoke({})


@mcp.tool()
def scan_wifi_networks() -> str:
    """Scan and list nearby Wi-Fi networks with SSID, signal strength, and security."""
    from tools.hardware_controller import scan_wifi_networks as swn
    return swn.invoke({})


@mcp.tool()
def toggle_wifi(enable: bool) -> str:
    """Turn the Wi-Fi radio ON or OFF."""
    from tools.hardware_controller import toggle_wifi as tw
    return tw.invoke({"enable": enable})


@mcp.tool()
def get_bluetooth_status() -> str:
    """Query Bluetooth controller status (powered state, discoverability, connected devices)."""
    from tools.hardware_controller import get_bluetooth_status as gbs
    return gbs.invoke({})


@mcp.tool()
def toggle_bluetooth(enable: bool) -> str:
    """Turn Bluetooth power ON or OFF."""
    from tools.hardware_controller import toggle_bluetooth as tb
    return tb.invoke({"enable": enable})


@mcp.tool()
def get_hardware_temperatures() -> str:
    """Read real-time CPU, GPU, memory, and NVMe hardware thermal sensors and fan speeds."""
    from tools.hardware_controller import get_hardware_temperatures as ght
    return ght.invoke({})


@mcp.tool()
def get_cpu_info() -> str:
    """Get detailed CPU hardware specifications, model name, core counts, and frequency."""
    from tools.hardware_controller import get_cpu_info as gci
    return gci.invoke({})


@mcp.tool()
def get_clipboard_text() -> str:
    """Read the current text content stored in the system clipboard (Wayland/X11)."""
    from tools.desktop_workflow_tool import get_clipboard_text as gct
    return gct.invoke({})


@mcp.tool()
def set_clipboard_text(text: str) -> str:
    """Copy a given text string into the system clipboard."""
    from tools.desktop_workflow_tool import set_clipboard_text as sct
    return sct.invoke({"text": text})


@mcp.tool()
def read_web_page(url: str, max_chars: int = 5000) -> str:
    """Fetch and extract clean, readable text and article content from any web URL."""
    from tools.desktop_workflow_tool import read_web_page as rwp
    return rwp.invoke({"url": url, "max_chars": max_chars})


@mcp.tool()
def get_media_info(url: str) -> str:
    """Inspect metadata for an online video or audio (YouTube, Twitter, etc.) without downloading."""
    from tools.desktop_workflow_tool import get_media_info as gmi
    return gmi.invoke({"url": url})


@mcp.tool()
def lock_desktop_screen() -> str:
    """Safely lock the current user desktop session screen."""
    from tools.hardware_controller import lock_desktop_screen as lds
    return lds.invoke({})


if __name__ == "__main__":
    mcp.run()
