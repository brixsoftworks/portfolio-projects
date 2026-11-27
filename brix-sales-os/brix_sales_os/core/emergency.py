"""
brix_sales_os/core/emergency.py
==============================
Global emergency stop kill-switch.
Halts all external outbound messages, campaigns, and automated actions instantly.
"""

from brix_sales_os.config import settings

def is_emergency_stop_active() -> bool:
    return settings.emergency_stop

def set_emergency_stop(active: bool):
    settings.emergency_stop = active

def enforce_not_stopped(action_name: str = "Outbound action"):
    if settings.emergency_stop:
        raise PermissionError(f"EMERGENCY STOP ACTIVE: {action_name} aborted.")
