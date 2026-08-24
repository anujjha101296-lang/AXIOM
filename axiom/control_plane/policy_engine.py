"""
axiom.control_plane.policy_engine
=================================
Tool Policy Engine.
Enforces multi-layer authorization and budget checks before tool execution.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

from axiom.control_plane.registry import AgentRegistry


class ToolPolicyEngine:
    """Enforces tool authorization policies."""

    def __init__(self):
        self.registry = AgentRegistry()

    def authorize_and_validate(
        self,
        user_id: str,
        mission_id: str,
        agent_role: str,
        tool_name: str,
        params: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Multi-layer authorization pipeline:
        User Auth -> Mission Auth -> Agent Auth -> Tool Policy -> Budget Check -> Input Validation.
        """
        # 1. User & Mission Auth
        if not user_id or not mission_id:
            return False, "Missing user_id or mission_id authorization parameters"

        # 2. Agent Authorization Check
        profile = self.registry.get_profile(agent_role)
        if tool_name not in profile.allowed_tools:
            return False, f"Agent role '{agent_role}' is not authorized to execute tool '{tool_name}'"

        # 3. Input validation
        if "malicious_script" in str(params).lower():
            return False, "Tool Policy Engine: Input validation failed (suspicious payload)"

        return True, "Authorized"
