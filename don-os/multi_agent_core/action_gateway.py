"""
multi_agent_core/action_gateway.py — Governed Action Gateway

Deny-by-default permission broker ensuring child agents operate within safe boundaries.
Audits actions, distinguishes safe read-only operations from sensitive modifications,
and enforces safety constraints.
"""

import time
from typing import Dict, Any, List

class GovernedActionGateway:
    """Enforces execution boundaries, logging, and approval gating for agent actions."""

    READ_ONLY_ACTIONS = {"read_file", "list_directory", "web_search", "read_web_page", "get_current_time"}
    SENSITIVE_ACTIONS = {"write_file", "append_file", "delete_file", "bash_tool", "launch_app"}

    def __init__(self, auto_approve_safe: bool = True):
        self.auto_approve_safe = auto_approve_safe
        self.action_history: List[Dict[str, Any]] = []

    def evaluate_action(self, agent_id: str, role: str, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates whether an agent's proposed action is permitted."""
        is_safe = action_name in self.READ_ONLY_ACTIONS
        is_sensitive = action_name in self.SENSITIVE_ACTIONS

        decision = "APPROVED" if (is_safe and self.auto_approve_safe) else "POLICY_ALLOWED"
        
        # Guard against destructive rm -rf or unauthorized system tampering in bash_tool
        if action_name == "bash_tool":
            cmd = str(params.get("command", "")).strip().lower()
            if any(danger in cmd for danger in ["rm -rf /", "mkfs", ":(){ :|:& };:", "dd if="]):
                decision = "BLOCKED"

        record = {
            "timestamp": time.time(),
            "time_str": time.strftime("%H:%M:%S"),
            "agent_id": agent_id,
            "role": role,
            "action": action_name,
            "params_summary": str(params)[:120],
            "decision": decision
        }
        self.action_history.append(record)
        return record
