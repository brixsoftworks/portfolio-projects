"""
tools/hardware_controller.py

Comprehensive Hardware & System Controls Suite.
Controls:
- Screen brightness (brightnessctl)
- Battery & power supply telemetry (upower)
- Wi-Fi networking & scanning (nmcli)
- Bluetooth adapter & devices (bluetoothctl)
- Hardware temperatures & thermal sensors (lm-sensors)
- CPU specs & clock speeds
- Audio sinks / sources & microphone mute (pactl)
- Desktop lock & display power (loginctl)
"""

import os
import re
import shutil
import subprocess
from typing import Optional

from langchain_core.tools import tool


@tool
def get_screen_brightness() -> str:
    """
    Get the current laptop screen brightness percentage and device name.
    
    Returns:
        Current brightness percentage and device.
    """
    if not shutil.which("brightnessctl"):
        return "Error: brightnessctl utility not found."

    try:
        res = subprocess.run(["brightnessctl", "info"], capture_output=True, text=True)
        if res.returncode == 0:
            match = re.search(r"Current brightness:\s+\d+\s+\((\d+)%\)", res.stdout)
            dev_match = re.search(r"Device '([^']+)'", res.stdout)
            pct = match.group(1) if match else "Unknown"
            dev = dev_match.group(1) if dev_match else "Backlight"
            return f"Screen Brightness: {pct}% (Device: {dev})"
        return f"Error reading brightness: {res.stderr.strip()}"
    except Exception as e:
        return f"Error reading brightness: {e}"


@tool
def set_screen_brightness(percentage: int) -> str:
    """
    Adjust laptop display brightness percentage (1 - 100).
    
    Args:
        percentage: Target brightness level from 1 to 100.
        
    Returns:
        Confirmation status.
    """
    if not shutil.which("brightnessctl"):
        return "Error: brightnessctl utility not found."

    val = max(1, min(100, int(percentage)))
    try:
        res = subprocess.run(["brightnessctl", "set", f"{val}%"], capture_output=True, text=True)
        if res.returncode == 0:
            return f"Display brightness set to {val}%."
        return f"Error setting brightness: {res.stderr.strip()}"
    except Exception as e:
        return f"Error adjusting brightness: {e}"


@tool
def get_battery_status() -> str:
    """
    Get comprehensive battery telemetry: state (charging/discharging), percentage, time remaining, and health.
    
    Returns:
        Battery details from upower.
    """
    if not shutil.which("upower"):
        return "Error: upower utility not found."

    try:
        # Find battery device
        enum_res = subprocess.run(["upower", "-e"], capture_output=True, text=True)
        bat_dev = None
        for line in enum_res.stdout.splitlines():
            if "battery" in line.lower():
                bat_dev = line.strip()
                break

        if not bat_dev:
            return "No battery device detected (Desktop AC power)."

        res = subprocess.run(["upower", "-i", bat_dev], capture_output=True, text=True)
        lines = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if any(line.startswith(k) for k in ["state:", "percentage:", "time to empty:", "time to full:", "energy-rate:", "capacity:", "technology:"]):
                lines.append(f"• {line}")

        return f"Battery Status ({os.path.basename(bat_dev)}):\n" + "\n".join(lines) if lines else res.stdout
    except Exception as e:
        return f"Error querying battery: {e}"


@tool
def get_network_status() -> str:
    """
    Query system network connectivity, active connections, Wi-Fi state, and IP addresses.
    
    Returns:
        Network summary.
    """
    if not shutil.which("nmcli"):
        return "Error: nmcli not available."

    try:
        gen_res = subprocess.run(["nmcli", "general", "status"], capture_output=True, text=True)
        con_res = subprocess.run(["nmcli", "-t", "-f", "NAME,TYPE,DEVICE", "connection", "show", "--active"], capture_output=True, text=True)
        ip_res = subprocess.run(["ip", "-brief", "address", "show", "up"], capture_output=True, text=True)

        return (
            f"=== Network Status ===\n{gen_res.stdout.strip()}\n\n"
            f"Active Connections:\n{con_res.stdout.strip() or 'None'}\n\n"
            f"IP Addresses:\n{ip_res.stdout.strip()}"
        )
    except Exception as e:
        return f"Error reading network status: {e}"


@tool
def scan_wifi_networks() -> str:
    """
    Scan and list nearby Wi-Fi networks with SSID, signal strength, security, and bars.
    
    Returns:
        List of visible Wi-Fi access points.
    """
    if not shutil.which("nmcli"):
        return "Error: nmcli not available."

    try:
        res = subprocess.run(
            ["nmcli", "-f", "SSID,SIGNAL,SECURITY,BARS", "device", "wifi", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if res.returncode == 0:
            lines = res.stdout.splitlines()[:20]  # top 20 visible
            return "\n".join(lines) if lines else "No Wi-Fi networks found."
        return f"Error scanning Wi-Fi: {res.stderr.strip()}"
    except Exception as e:
        return f"Error scanning Wi-Fi: {e}"


@tool
def toggle_wifi(enable: bool) -> str:
    """
    Turn the Wi-Fi radio ON or OFF.
    
    Args:
        enable: True to turn Wi-Fi on, False to turn Wi-Fi off.
        
    Returns:
        Confirmation status.
    """
    if not shutil.which("nmcli"):
        return "Error: nmcli not available."

    state = "on" if enable else "off"
    try:
        res = subprocess.run(["nmcli", "radio", "wifi", state], capture_output=True, text=True)
        if res.returncode == 0:
            return f"Wi-Fi radio successfully turned {state.upper()}."
        return f"Error setting Wi-Fi radio: {res.stderr.strip()}"
    except Exception as e:
        return f"Error toggling Wi-Fi: {e}"


@tool
def get_bluetooth_status() -> str:
    """
    Query Bluetooth controller status (powered state, discoverability, connected devices).
    
    Returns:
        Bluetooth status report.
    """
    if not shutil.which("bluetoothctl"):
        return "Error: bluetoothctl not available."

    try:
        show_res = subprocess.run(["bluetoothctl", "show"], capture_output=True, text=True, timeout=3)
        devs_res = subprocess.run(["bluetoothctl", "devices", "Connected"], capture_output=True, text=True, timeout=3)

        powered = "Powered: yes" in show_res.stdout
        connected = devs_res.stdout.strip() if devs_res.stdout.strip() else "None"

        return f"Bluetooth Adapter: {'ON' if powered else 'OFF'}\nConnected Devices:\n{connected}"
    except Exception as e:
        return f"Error querying Bluetooth: {e}"


@tool
def toggle_bluetooth(enable: bool) -> str:
    """
    Turn Bluetooth power ON or OFF.
    
    Args:
        enable: True to power on, False to power off.
        
    Returns:
        Confirmation message.
    """
    if not shutil.which("bluetoothctl"):
        return "Error: bluetoothctl not available."

    cmd = ["bluetoothctl", "power", "on" if enable else "off"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            return f"Bluetooth power set to {'ON' if enable else 'OFF'}."
        return f"Error changing Bluetooth state: {res.stderr.strip() or res.stdout.strip()}"
    except Exception as e:
        return f"Error toggling Bluetooth: {e}"


@tool
def get_hardware_temperatures() -> str:
    """
    Read real-time CPU, GPU, memory, and NVMe hardware thermal sensors and fan speeds.
    
    Returns:
        Sensor temperature readings.
    """
    if not shutil.which("sensors"):
        return "Error: 'sensors' utility (lm_sensors) is not installed."

    try:
        res = subprocess.run(["sensors"], capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout.strip()
        return f"Error querying sensors: {res.stderr.strip()}"
    except Exception as e:
        return f"Error reading temperatures: {e}"


@tool
def get_cpu_info() -> str:
    """
    Get detailed CPU hardware specifications, model name, core counts, and frequency.
    
    Returns:
        CPU information summary.
    """
    try:
        res = subprocess.run(["lscpu"], capture_output=True, text=True)
        if res.returncode == 0:
            relevant = []
            for line in res.stdout.splitlines():
                if any(k in line for k in ["Model name", "CPU(s):", "Thread(s) per core", "Core(s) per socket", "CPU max MHz", "CPU min MHz", "Virtualization"]):
                    relevant.append(line.strip())
            return "CPU Hardware Specs:\n" + "\n".join(relevant)
        return "Could not retrieve CPU specifications."
    except Exception as e:
        return f"Error reading CPU info: {e}"


@tool
def list_audio_devices() -> str:
    """
    List all system audio output sinks (speakers, headphones, HDMI) and input sources (microphones).
    
    Returns:
        Available audio devices and the default sink.
    """
    if not shutil.which("pactl"):
        return "Error: pactl not available."

    try:
        sinks = subprocess.run(["pactl", "list", "sinks", "short"], capture_output=True, text=True).stdout.strip()
        sources = subprocess.run(["pactl", "list", "sources", "short"], capture_output=True, text=True).stdout.strip()
        def_sink = subprocess.run(["pactl", "get-default-sink"], capture_output=True, text=True).stdout.strip()

        return (
            f"Default Audio Sink: {def_sink}\n\n"
            f"Available Audio Outputs (Sinks):\n{sinks}\n\n"
            f"Available Audio Inputs (Sources):\n{sources}"
        )
    except Exception as e:
        return f"Error listing audio devices: {e}"


@tool
def toggle_microphone_mute(mute: Optional[bool] = None) -> str:
    """
    Mute, unmute, or toggle the system default microphone input.
    
    Args:
        mute: True to mute, False to unmute, or None to toggle mute state.
        
    Returns:
        Confirmation status.
    """
    if not shutil.which("pactl"):
        return "Error: pactl not available."

    try:
        arg = "toggle" if mute is None else ("1" if mute else "0")
        res = subprocess.run(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", arg], capture_output=True, text=True)
        if res.returncode == 0:
            # Check current status
            chk = subprocess.run(["pactl", "get-source-mute", "@DEFAULT_SOURCE@"], capture_output=True, text=True)
            status = chk.stdout.strip()
            return f"Microphone mute status: {status}"
        return f"Error modifying microphone state: {res.stderr.strip()}"
    except Exception as e:
        return f"Error toggling microphone: {e}"


@tool
def lock_desktop_screen() -> str:
    """
    Safely lock the current user desktop session screen.
    
    Returns:
        Status confirmation.
    """
    try:
        res = subprocess.run(["loginctl", "lock-session"], capture_output=True, text=True)
        if res.returncode == 0:
            return "Desktop session locked."
        return f"Failed to lock screen: {res.stderr.strip()}"
    except Exception as e:
        return f"Error locking screen: {e}"
